"""Simple city simulator, for free-floating carsharing purposes."""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import time
from PIL import Image  # For image demand loading
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Console handdler for logging to become visible in notebooks
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


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
            "seed": None, # Random seed for reproducibility
            "n_cores": 1,  # Number of city cores
            "city_width": 21, # km
            "grid_step": 0.5, # km
            "density_sigma": 6, # Gaussian sigma, km

            # Simulation properties
            "n_cars": 100,
            "speed": 30.0,  # Car speed, km/h
            "cm1_per_trip": 5,  # CM1 revenue per typical trip, Eur
            "typical_trip_duration_min": 30,  # Typical trip duration, min (to contextualize CM1)
            "tick_length_min": 10,  # Length of a tick in minutes
            "settle_down_steps": 0,  # Number of steps without stats collection,
                                     # for the initial conditions to wear off
            "trip_lambda":8,  # Km. The higher, the further cars travel, on average VERIFY!!!
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

        if self.seed is not None:
            np.random.seed(self.seed)

        # Calculatable fields
        self.update_calculatable_fields()


    def update_calculatable_fields(self):
        """A separate method, just in case we ever change settings mid-simulation."""
        self.grid_size = int(np.ceil(self.city_width/self.grid_step))

        # Dynamic properties
        self.create_density_profile()
        # The calculation for cm1_per_tick is a bit weird as we want to preseve consistency
        # with simpler models presented in this project, which means that we need to link
        # the per-tick revenue here to flat revenues per trip used elsewhere.
        self.cm1_per_tick = (
            self.cm1_per_trip / self.typical_trip_duration_min * self.tick_length_min
        )

        self.stats_cm1 = np.zeros_like(self.grid, dtype=np.float32)  # CM1 profit
        self.stats_cm2 = np.zeros_like(self.grid, dtype=np.float32)  # CM2 profit
        self.stats_nrentals = np.zeros_like(self.grid, dtype=np.int32)  # Number of rentals
        self.stats_idle_time = np.zeros_like(self.grid, dtype=np.int32)  # Idle time in ticks


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
                # Pick a random core center within a circle inscribed in the grid
                angle = np.random.uniform(0, 2 * np.pi) # Random angle
                radius = np.random.uniform(center/4, center)  # Random radius within the circle
                core_centers += [
                    (center + radius * np.cos(angle), center + radius * np.sin(angle))
                ]

        for x0, y0 in core_centers:
            for i in range(self.grid_size):
                for j in range(self.grid_size):
                    # Distance in km
                    distance_squared = (((i+0.5)-x0)**2 + ((j+0.5)-y0)**2)*self.grid_step**2
                    self.grid[i,j] += np.exp(-distance_squared/(self.density_sigma)**2)

        self.grid = self.grid / np.max(self.grid)  # Normalize the grid to [0, 1] range

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


    def visualize(self, plots="all"):
        """Show a basic visualization of the city"""
        if isinstance(plots, str):
            if plots == "all":
                plots = ["cars", "cm1", "idle_times", "cm2"]
            else:
                plots = [plots]
        n_plots = len(plots)
        if n_plots == 3:
            n_plots = 4

        def cleanup():
            """Universal design elements."""
            plt.xticks([], [])
            plt.yticks([], [])
            plt.gca().set_aspect('equal', adjustable='box')

        # Demand and current car positions:
        plot_counter = 0
        if "cars" in plots:
            if n_plots > 1:
                plot_counter += 1
                plt.subplot(1, n_plots, plot_counter)
                plt.title("Demand profile and car positions")
            plt.imshow(self.grid.T, aspect='auto', interpolation='none',
            extent=[0, self.grid_size, 0, self.grid_size], cmap='gray_r',
            vmin=0, vmax=1, origin='lower');

            # Visualize cars:
            if hasattr(self, 'cars_xy'):
                # Cars were initialized
                plt.scatter(self.cars_xy[:, 0] + 0.5, self.cars_xy[:, 1] + 0.5,
                            c='red', s=2, label='Cars')
            cleanup()

        if "cm1" in plots:
            if n_plots > 1:
                plot_counter += 1
                plt.subplot(1, n_plots, plot_counter)
                plt.title("CM1 statistics")
            plt.imshow(self.stats_cm1.T, aspect='auto', interpolation='none',
            extent=[0, self.grid_size, 0, self.grid_size], cmap='Reds',
            vmin=0, vmax=np.max(self.stats_cm1), origin='lower');
            cleanup()
            plt.tight_layout()

        if "idle_times" in plots:
            if n_plots > 1:
                plot_counter += 1
                plt.subplot(1, n_plots, plot_counter)
            cleanup()

        if "cm2" in plots:
            if n_plots > 1:
                plot_counter += 1
                plt.subplot(1, n_plots, plot_counter)
            cleanup()


    def simulate(self, n_steps=1):
        """Run a few simulation steps."""
        logger.info(f"Running simulation for {n_steps} steps")

        # TODO: Reset idle time counter for cars

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

            # --- 2. New rentals

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
                start_positions = self.cars_xy[car_indices_getting_rented] # (n_rented, 2)

                # We create a space of all possible destinations (axis 1) for every car (axis 0)
                # Now to use a Gumbel-Max trick we first need to calculate log-scores
                # of every possible move in this space (origin->destination), and then below
                # we'll randomly sample from this space.
                dx = start_positions[:, 0, np.newaxis] - self.flat_grid_coords[np.newaxis, :, 0]
                dy = start_positions[:, 1, np.newaxis] - self.flat_grid_coords[np.newaxis, :, 1]
                distances_km = np.hypot(dx, dy)*self.grid_step # Shape: (n_rented, N_cells)

                def trip_probability(distance):
                    y = distance*np.exp(-(distance**1.2)/8) / 2.11
                    return y
                # Probability of a trip as a function of distance is assumed to be
                # distance*np.exp(-(distance**1.2)/8) / 2.11
                # But here we're taking a log of it
                log_scores = (
                    np.log(self.flat_demand[np.newaxis, :] + self.epsylon)
                    + np.log(distances_km + self.epsylon)
                    - (distances_km**1.2)/self.trip_lambda - np.log(2.11)
                )
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
                    1, np.round(
                        distances_km / self.speed * 60 / self.tick_length_min)
                    ).astype(np.int32)

                # Update state for cars starting the trip
                self.car_states[car_indices_getting_rented] = car_state["rented"]
                self.car_timer_transit[car_indices_getting_rented] = transit_time_ticks
                self.car_destinations[car_indices_getting_rented] = chosen_destinations

                # --- Stats collection

                if step >= self.settle_down_steps:
                    # We may be waiting for a few steps before collecting stats
                    x0, y0 = start_positions[:, 0], start_positions[:, 1]
                    x1, y1 = chosen_destinations[:, 0], chosen_destinations[:, 1]
                    self.stats_nrentals[x0, y0] += 1
                    cm1_increments = transit_time_ticks * self.cm1_per_tick / 2
                    self.stats_cm1[x0, y0] += cm1_increments  # CM1 goes 50:50 between start and finish
                    self.stats_cm1[x1, y1] += cm1_increments

            # --- 3. Relocations

            # For now, nothing here

        # Update stats for idle time before finishing the simulation

        end_time_sim = time.time()
        logger.info(f"Simulation completed in {end_time_sim - start_time_sim:.2f} seconds")