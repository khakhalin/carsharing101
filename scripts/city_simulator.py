"""Simple city simulator, for free-floating carsharing purposes."""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import time
from PIL import Image  # For image demand loading
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


# A list of car states, to be used in numpy arrays
car_state = {
    "idle": 0,  # Car is not moving, waiting for a rental
    "rented": 1,
    "pause": 2,  # Booked for service or relocation
    "relo": 3,  # Relocation in progress
}


class City():
    """A combo of a city, a simulator, and a visualizer."""

    def __init__(self, config=None):
        """Create a city object."""
        logger.info("Initializing city")
        default_config = {
            # City properties
            "name": "Verona",
            "n_cores": 1,  # Number of city cores
            "city_width": 21, # km
            "grid_step": 0.2, # km
            "density_sigma": 6, # Gaussian sigma, km

            # Simulation properties
            "n_cars": 100,
            "speed": 30.0,  # Car speed, km/h
            "trip_lambda":10,  # The higher, the further cars travel, on average,
            "initial_r": 1,  # Initial radius in which cars are placed, km
            "p_rental": 0.1,  # Rental probability is proportional to this. Tune it up.
            "epsylon": 1e-8,  # Small value for Gumbel-Max trick to avoid log(0) errors
        }

        # Set default values
        for key,value in default_config.items():
            self.__setattr__(key, value)
        # Immediately overwrite them with custom values (if any):
        if config is not None:
            for key,value in config.items():
                self.__setattr__(key, value)

        # Calculatable fields
        self.grid_size = int(np.ceil(self.city_width/self.grid_step))

        # Dynamic properties
        self.create_density_profile()


    def create_density_profile(self):
        """Calculate a density profile."""
        logger.info(f"Calculating density profile for {self.n_cores} cores")
        # Reset density to zero
        self.grid = np.zeros(shape=(self.grid_size, self.grid_size))
        center = self.grid_size / 2

        if self.n_cores == 1:
            core_centers = [(center, center)]
        else:
            core_centers = []
            for n_core in range(self.n_cores):
                core_centers += [
                    (center + np.random.normal()*self.density_sigma/self.grid_step,
                     center + np.random.normal()*self.density_sigma/self.grid_step)]

        for i in range(self.grid_size):
            for j in range(self.grid_size):
                # Distance in km
                distance_squared = (((i+0.5)-center)**2 + ((j+0.5)-center)**2)*self.grid_step**2
                self.grid[i,j] = np.exp(-distance_squared/(self.density_sigma)**2)

        # Pre-process demand for simulations
        self.vectorize_demand()


    def load_density_profile(self, filename):
        """Loads density profile from an image."""
        logger.info(f"Load density profile from image {filename}")
        img = Image.open(filename).convert('L') # Open and convert to grayscale
        # TODO: Maybe it's better to resize the grid, rather than the image?
        img_resized = img.resize((self.grid_size, self.grid_size), Image.Resampling.LANCZOS)
        img_array = np.array(img_resized, dtype=np.float32)

        # Invert (assuming 0=black, 255=white -> we want black=1, white=0)
        demand_map = 1.0 - (img_array / 255.0)
        demand_map = np.clip(demand_map, 0, 1) # Ensure values are in [0, 1]
        logger.info("Demand map loaded successfully")
        self.vectorize_demand()


    def vectorize_demand(self):
        """Prepare flattened vectorized values for a fast calculation."""
        self.flat_demand = self.grid.flatten()
        n = self.grid_size
        all_coords_flat_idx = np.arange(n * n)
        flat_y, flat_x = np.unravel_index(all_coords_flat_idx, (n, n))
        self.flat_grid_coords = np.stack((flat_x, flat_y), axis=1) # Shape: (N_cells, 2)


    def init_cars(self):
        """Initialize cars."""
        center = self.grid_size/2
        radius = self.initial_r / self.grid_step  # Convert km to grid pixels

        def random_pixel(center):
            return int(center + (np.random.uniform()*radius*2 - radius)/self.grid_step)

        self.cars_xy = np.zeros(shape=(self.n_cars, 2), dtype=np.int32)
        for i in range(self.n_cars):
            success = False
            while not success:
                x = random_pixel(center)
                y = random_pixel(center)
                self.cars_xy[i,:] = (x,y)
                if (x - center)**2 + (y - center)**2 < radius**2:
                    success = True

        self.car_destinations = np.zeros_like(self.cars_xy)  # Where the car is going
        self.car_states = np.full(self.n_cars, car_state["idle"], dtype=np.int32)
        self.car_timer_transit = np.zeros(self.n_cars, dtype=np.int32) # Remaining ticks in transit


    def visualize(self):
        """Show a basic visualization of the city"""
        # Don't call plt.figure() as the size of the figure is likely to be set in the client
        # Demand:
        plt.imshow(self.grid.T, aspect='auto', interpolation='none',
          extent=[0, self.grid_size, 0, self.grid_size], cmap='gray_r',
          vmin=0, vmax=1, origin='lower');

        # Visualize cars:
        if hasattr(self, 'cars_xy'):
            # Cars were initialized
            plt.scatter(self.cars_xy[:, 0], self.cars_xy[:, 1], c='red', s=2, label='Cars')

        plt.tight_layout()
        plt.xticks([], [])
        plt.yticks([], [])
        plt.gca().set_aspect('equal', adjustable='box')


    def simulate(self, n_steps=1):
        """Run a few simulation steps."""
        logger.info(f"Running simulation for {n_steps} steps")
        start_time_sim = time.time()
        for step in range(n_steps):
            # --- 1. Arrivals
            in_transit_mask = self.car_states == car_state["rented"]
            arriving_mask = np.zeros(self.n_cars, dtype=bool) # Track arrivals this step for stats

            if np.any(in_transit_mask):
                # Decrement timers for cars in transit
                self.car_timer_transit[in_transit_mask] -= 1

                # Identify cars arriving *this* tick
                arriving_mask = in_transit_mask & (self.car_timer_transit <= 0)
                arriving_indices = np.where(arriving_mask)[0]

                if len(arriving_indices) > 0:
                    # Update state and position for arriving cars
                    self.car_states[arriving_mask] = car_state["idle"]
                    self.cars_xy[arriving_mask] = self.car_destinations[arriving_mask]

                    # # Accumulate "traveled to" stats (if collecting)
                    # if collect_stats:
                    #     dest_y = car_positions[arriving_mask, 1]
                    #     dest_x = car_positions[arriving_mask, 0]
                    #     distances_arrived = car_current_trip_distance_km[arriving_mask]
                    #     np.add.at(km_traveled_to_map, (dest_y, dest_x), distances_arrived)

            # --- 2. Stats
            # --- 3. New rentals

            available_mask = (self.car_states == car_state["idle"])
            if np.any(available_mask):
                # --- Pick which cars are be rented this step
                available_indices = np.where(available_mask)[0]
                start_positions = self.cars_xy[available_mask]
                start_demand = self.grid[start_positions[:, 1], start_positions[:, 0]]
                move_probability = start_demand * self.p_rental
                roll_the_dice = np.random.rand(len(available_indices))
                trip_mask = (roll_the_dice < move_probability) # Mask relative to available cars
                car_indices_getting_rented = available_indices[trip_mask] # Absolute indices

                if not np.any(trip_mask):
                    continue

                # --- Pick where these cars will move
                n_rented = len(car_indices_getting_rented)
                start_positions = start_positions[car_indices_getting_rented] # (n_rented, 2)

                # We create a space of all possible destinations (axis 1) for every car (axis 0)
                # Now to use a Gumbel-Max trick we first need to calculate log-scores
                # of every possible move in this space (origin->destination), and then below
                # we'll randomly sample from this space.
                dx = start_positions[:, 0, np.newaxis] - self.flat_grid_coords[np.newaxis, :, 0]
                dy = start_positions[:, 1, np.newaxis] - self.flat_grid_coords[np.newaxis, :, 1]
                distances_km = np.hypot(dx, dy)*self.grid_step # Shape: (n_rented, N_cells)

                log_scores = (np.log(self.flat_demand[np.newaxis, :] + self.epsylon)
                            - np.log(1.0 + distances_km / self.trip_lambda))
                # Shape: (n_rented, N_cells)

                # Mask out starting locations to avoid "no distance travelled" rentals"
                start_flat_indices = np.ravel_multi_index(
                    (start_positions[:, 1], start_positions[:, 0]), (self.grid_size, self.grid_size)
                    )
                log_scores[np.arange(n_rented), start_flat_indices] = -np.inf

                # Use Gumbel-Max trick to sample destinations
                gumbel_noise = -np.log(-np.log(np.random.rand(
                    n_rented, self.grid_size ** 2) + self.epsylon) + self.epsylon)
                chosen_flat_indices = np.argmax(log_scores + gumbel_noise, axis=1) # (n_rented,)
                # These are indexes vs the space of rental possibilities, not across cars or pixels

                # --- Send the cars traveling
                new_y, new_x = np.unravel_index(
                    chosen_flat_indices, (self.grid_size, self.grid_size))
                chosen_destinations = np.stack((new_x, new_y), axis=1) # (n_rented, 2)

                # Calculate transit times
                distances_km = distances_km[np.arange(n_rented), chosen_flat_indices]

                # Calculate transit time in ticks (at least 1 tick)
                transit_time_ticks = np.maximum(
                    1, np.round(distances_km / self.speed)).astype(np.int32)

                # Update state for cars starting the trip
                self.car_states[car_indices_getting_rented] = car_state["rented"]
                self.car_timer_transit[car_indices_getting_rented] = transit_time_ticks
                self.car_destinations[car_indices_getting_rented] = chosen_destinations

            # --- 4. Relocations

            # For now, nothing here

        end_time_sim = time.time()
        logger.info(f"Simulation completed in {end_time_sim - start_time_sim:.2f} seconds")