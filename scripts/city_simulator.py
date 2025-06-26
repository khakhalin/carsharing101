"""Simple city simulator, for free-floating carsharing purposes."""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import colormaps
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
            "speed": 20.0,  # Car speed, km/h
            "cm1_per_trip": 5,  # CM1 revenue per typical trip, Eur
            "cm2_per_day": 20,  # CM2 cost pre day of having a car on balance, Eur
            "typical_trip_duration_min": 20,  # Typical trip duration, min (to contextualize CM1)
            "tick_in_minutes": 10,  # Length of a tick in minutes
            "settle_down_steps": 0,  # Number of steps without stats collection,
                                     # for the initial conditions to wear off
            "trip_lambda":8,  # Km. The higher, the further cars travel, on average VERIFY!!!
            "initial_r": 2,  # Initial radius in which cars are placed, km
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
        self.total_steps_run = 0  # Total number of simulation steps run so far
        self.total_rental_time = 0  # Total rental time, in ticks, for all cars

        # Calculatable fields
        self.update_calculatable_fields()


    def update_calculatable_fields(self):
        """A separate method, just in case we ever change settings mid-simulation."""
        self.grid_size = int(np.ceil(self.city_width/self.grid_step))

        # Dynamic properties
        self.create_density_profile()
        # The calculation for cm1_per_rental_tick is a bit weird as we want to preseve consistency
        # with simpler models presented in this project, which means that we need to link
        # the per-tick revenue here to flat revenues per trip used elsewhere.

        # Spatial stats:
        self.stats_cm1 = np.zeros_like(self.demand, dtype=np.float32)  # CM1 profit
        self.stats_cm2 = np.zeros_like(self.demand, dtype=np.float32)  # CM2 profit
        self.stats_n_rentals = np.zeros_like(self.demand, dtype=np.int32)  # Number of rentals
        self.stats_n_arrivals = np.zeros_like(self.demand, dtype=np.int32)  # (for idle time calc)
        self.stats_idle_time = np.zeros_like(self.demand, dtype=np.int32)  # Idle time in ticks


    def create_density_profile(self):
        """Calculate a density profile."""
        logger.info(f"Calculating density profile for {self.n_cores} cores")
        # Reset density to zero
        self.demand = np.zeros(shape=(self.grid_size, self.grid_size))
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
                    self.demand[i,j] += np.exp(-distance_squared/(self.density_sigma)**2)

        self.demand = self.demand / np.max(self.demand)  # Normalize the grid to [0, 1] range

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
        self.flat_demand = self.demand.T.flatten()  # Without flattening indexes are confused
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

        self.car_xy = np.zeros(shape=(self.n_cars, 2), dtype=np.int32)
        for i in range(self.n_cars):
            success = False
            while not success:
                x = random_pixel(center)
                y = random_pixel(center)
                self.car_xy[i,:] = (x,y)
                if (x - center)**2 + (y - center)**2 < radius**2:
                    success = True

        self.car_destinations = np.zeros_like(self.car_xy)  # Where the car is going
        self.car_states = np.full(self.n_cars, car_state["idle"], dtype=np.int32)
        self.car_timer_transit = np.zeros(self.n_cars, dtype=np.int32) # Remaining ticks in transit
        self.car_timer_idle = np.zeros(self.n_cars, dtype=np.int32)  # Idle time in ticks


    def visualize(self, plots="all"):
        """Show visualizations of the city"""
        if isinstance(plots, str):
            if plots == "all":
                plots = ["cars", "cm1", "idle_times", "cm2"]
            else:
                plots = [plots]
        n_plots = len(plots)

        def _finalize(show_cbar=True):
            """Universal design elements."""
            plt.xticks([], [])
            plt.yticks([], [])
            plt.gca().set_aspect('equal', adjustable='box')
            if show_cbar:
                cbar = plt.colorbar(fraction=0.046, pad=0.04)
                cbar.ax.tick_params(labelsize=8)

        # Demand and current car positions:
        n_days = self.total_steps_run * self.tick_in_minutes / 60 / 24 + 0.001
        plot_counter = 0
        if "cars" in plots:
            if n_plots > 1:
                plot_counter += 1
                plt.subplot(1, n_plots, plot_counter)
                plt.title("Demand profile,\n car positions")
            plt.imshow(self.demand.T, aspect='auto', interpolation='none',
                extent=[0, self.grid_size, 0, self.grid_size], cmap='gray_r',
                vmin=0, vmax=1, origin='lower');

            # Visualize cars:
            if hasattr(self, 'car_xy'):
                # Cars were initialized
                plt.scatter(self.car_xy[:, 0] + 0.5, self.car_xy[:, 1] + 0.5,
                            c='red', s=2, label='Cars')
            _finalize(show_cbar=False)

        if "cm1" in plots:
            if n_plots > 1:
                plot_counter += 1
                plt.subplot(1, n_plots, plot_counter)
                plt.title("CM1, €/day")
            plt.imshow(self.stats_cm1.T / n_days, aspect='auto', interpolation='none',
                extent=[0, self.grid_size, 0, self.grid_size], cmap='Blues', origin='lower');
            _finalize()

        if "idle_times" in plots:
            if n_plots > 1:
                plot_counter += 1
                plt.subplot(1, n_plots, plot_counter)
                plt.title("Average idle time, days")
            # Move from total idle time to idle time per car
            value = self.stats_idle_time / np.maximum(self.stats_n_arrivals, 1)
            value = value * self.tick_in_minutes / 60 / 24  # Convert to days
            value[value==0] = np.nan  # This will help to show NaNs as gray
            # cmap = plt.cm.Blues.copy()
            cmap = colormaps.get_cmap('viridis_r').copy()
            cmap.set_bad(color='lightgray')
            vmax = np.nanpercentile(value, 90) # Avoid catering to outliers
            plt.imshow(value.T, aspect='auto', interpolation='none',
                extent=[0, self.grid_size, 0, self.grid_size], cmap=cmap, origin='lower',
                vmin=0, vmax=vmax)  # Set vmin and vmax to control color range;
            # Make the colorbar small and fixed in size, right from the plot
            _finalize()

        if "cm2" in plots:
            if n_plots > 1:
                plot_counter += 1
                plt.subplot(1, n_plots, plot_counter)
                plt.title("CM2, €/day")
            # Diverging colormap, red for negative, blue for positive, light gray for zero
            cmap = colormaps.get_cmap('RdBu')
            plt.imshow(self.stats_cm2.T / n_days, aspect='auto', interpolation='none',
                extent=[0, self.grid_size, 0, self.grid_size], origin='lower',
                # norm=plt.matplotlib.colors.CenteredNorm(),  # Center the colormap at zero
                vmin=-self.cm2_per_day*2, vmax=self.cm2_per_day*2,  # Visual empyrics
                cmap=cmap)
            # cm2_per_day just gives a reasonable range, and I want to see some blue color
            _finalize()

        plt.tight_layout()


    def simulate(self, n_steps=1):
        """Run a few simulation steps."""
        logger.info(f"Running simulation for {n_steps} steps")

        # TODO: Reset idle time counter for cars

        start_time_sim = time.time()
        idle_tick_cost = self.cm2_per_day / (24 * 60 / self.tick_in_minutes)  # CM2 cost of 1 tick
        cm1_per_rental_tick = (
            (self.cm1_per_trip / self.typical_trip_duration_min) * self.tick_in_minutes
        )

        for step in range(n_steps):
            idling_mask = (self.car_states == car_state["idle"])
            in_transit_mask = self.car_states == car_state["rented"]

            # At the beginning of the first real step (after settling down), reset stats
            if self.total_steps_run == self.settle_down_steps:
                self.car_timer_idle.fill(0)
                self.stats_idle_time.fill(0)
                # Increase the n_arrivals by one for every car already parked
                np.add.at(self.stats_n_arrivals,
                          (self.car_xy[idling_mask, 0], self.car_xy[idling_mask, 1]), 1)

            # Increment idle time and CM2 costs for pixels witn idling cars
            np.add.at(self.stats_idle_time,
                      (self.car_xy[idling_mask, 0], self.car_xy[idling_mask, 1]), 1)
            np.add.at(self.stats_cm2,
                      (self.car_xy[idling_mask, 0], self.car_xy[idling_mask, 1]), -idle_tick_cost)

            # --- 1. Arrivals

            if np.any(in_transit_mask):
                # Decrement timers for cars in transit
                self.car_timer_transit[in_transit_mask] -= 1

                # Identify cars arriving *this* tick
                arriving_mask = np.zeros(self.n_cars, dtype=bool)
                arriving_mask = in_transit_mask & (self.car_timer_transit <= 0)
                arriving_indices = np.where(arriving_mask)[0]

                if len(arriving_indices) > 0:
                    # Update states and positions for arriving cars
                    self.car_states[arriving_mask] = car_state["idle"]
                    self.car_xy[arriving_mask] = self.car_destinations[arriving_mask]
                    np.add.at(self.stats_n_arrivals,
                        (self.car_xy[arriving_mask, 0], self.car_xy[arriving_mask, 1]), 1)

            # --- 2. New rentals

            self.car_timer_idle[idling_mask] += 1  # They all idled for one more tick now

            if np.any(idling_mask):
                # --- Generate demand for rentals
                roll_for_attempts = np.random.rand(*self.demand.shape)
                rental_attempts = (roll_for_attempts < self.demand * self.p_rental).astype(np.int32)
                pixels_with_demand = np.where(rental_attempts > 0)

                # --- Pick which cars are be rented this step
                # Get a list of all idle cars
                all_idle_cars = np.where(idling_mask)[0]

                # List the flattened indices of pixels in which these cars are staying.
                # Then calculate flat indices of pixels with demand. Then match cars
                # to demand. it will mark the cars that can be rented (but we'll still
                # need to sample only some of them)
                pixels_with_idle_cars = np.ravel_multi_index(
                    (self.car_xy[all_idle_cars, 0], self.car_xy[all_idle_cars, 1]),
                    self.demand.shape
                )
                pixels_with_demand = np.ravel_multi_index(pixels_with_demand, self.demand.shape)
                car_might_be_rented = np.isin(pixels_with_idle_cars, pixels_with_demand)

                cars_that_might_be_rented = all_idle_cars[car_might_be_rented]
                pixels_of_cars_that_might_be_rented = pixels_with_idle_cars[car_might_be_rented]

                # Now we need to select the first car from every pixel with rental attempts,
                # then find global indices of those cars that are rented.
                # We'll use a fancy feature of np.unique() that returns not just unique values,
                # but also the indices of the first occurrence of each unique value.
                # So all we need now is to randomly shuffle cars within each pixel,
                # which we can do with lexicographic sorting, first by pixels index, then
                # by a random number.
                roll_the_dice = np.random.rand(len(cars_that_might_be_rented))
                sort_indices = np.lexsort((roll_the_dice, pixels_of_cars_that_might_be_rented))
                unique_pixels, unique_indices = np.unique(
                    pixels_of_cars_that_might_be_rented[sort_indices],
                    return_index=True
                )
                final_indices = sort_indices[unique_indices]
                car_indices_getting_rented = cars_that_might_be_rented[final_indices]

                if len(car_indices_getting_rented) == 0:
                    continue

                # --- Pick where these cars will move
                n_rented = len(car_indices_getting_rented)
                start_positions = self.car_xy[car_indices_getting_rented] # (n_rented, 2)

                # We will create a space of all possible movements, from our selected
                # subset of cars (axis 0), and to every possible destination (axis 1).
                # To use a Gumbel-Max trick we first need to calculate log-scores
                # of every possible move in this space (origin->destination), and then below
                # we'll randomly sample from this space.
                dx = start_positions[:, 0, np.newaxis] - self.flat_grid_coords[np.newaxis, :, 0]
                dy = start_positions[:, 1, np.newaxis] - self.flat_grid_coords[np.newaxis, :, 1]
                distances_km = np.hypot(dx, dy)*self.grid_step # Shape: (n_rented, N_cells)

                # Probability of a trip as a function of distance is assumed to be governed by:
                # y = distance*np.exp(-(distance**1.2)/8) / 2.11
                # But here we're taking a log of it, as a part of a Gumbel trick.
                log_scores = (
                    np.log(self.flat_demand[np.newaxis, :] + self.epsylon)  # Target demand
                    + np.log(distances_km + self.epsylon)
                    - (distances_km**1.2)/self.trip_lambda - np.log(2.11)
                )
                # Shape: (n_rented, N_cells)

                # Mask out starting locations to avoid "no distance travelled" rentals"
                start_flat_indices = np.ravel_multi_index(
                    (start_positions[:, 0], start_positions[:, 1]),
                    (self.grid_size, self.grid_size)
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
                    1, np.round(distances_km / self.speed * 60 / self.tick_in_minutes)
                    ).astype(np.int32)

                # Update state for cars starting the trip
                self.car_states[car_indices_getting_rented] = car_state["rented"]
                self.car_timer_transit[car_indices_getting_rented] = transit_time_ticks
                self.car_destinations[car_indices_getting_rented] = chosen_destinations

                # --- Stats collection
                if self.total_steps_run >= self.settle_down_steps:
                    x0, y0 = start_positions[:, 0], start_positions[:, 1]
                    x1, y1 = chosen_destinations[:, 0], chosen_destinations[:, 1]
                    np.add.at(self.stats_n_rentals, (x0, y0), 1)
                    self.total_rental_time += transit_time_ticks.sum()
                    cm1_increments = transit_time_ticks * cm1_per_rental_tick / 2
                    # logger.info(transit_time_ticks)
                    cm2_increments = cm1_increments - (transit_time_ticks * idle_tick_cost)/2
                    np.add.at(self.stats_cm1, (x0, y0), cm1_increments) # 50:50 start and finish
                    np.add.at(self.stats_cm1, (x1, y1), cm1_increments)
                    np.add.at(self.stats_cm2, (x0, y0), cm2_increments) # 50:50 start and finish
                    np.add.at(self.stats_cm2, (x1, y1), cm2_increments)
                    self.car_timer_idle[car_indices_getting_rented].fill(0)  # Reset idle times

            # --- 3. Relocations

            # For now, nothing here

            self.total_steps_run += 1
            # end loop

        end_time_sim = time.time()
        logger.info(f"Simulation completed in {end_time_sim - start_time_sim:.2f} seconds")
        n_days = n_steps  * self.tick_in_minutes / 60 / 24  # Days during this simulation bout
        n_days_full = self.total_steps_run * self.tick_in_minutes / 60 / 24
        logger.info(f"In-simulation time passed: {n_days:.0f} days")
        logger.info(f"Statistics gathered over: {n_days_full:.0f} days")
        n_rentals = self.stats_n_rentals.sum()
        logger.info(f"Cumulative rentals happened: {n_rentals}")
        logger.info(f"Average rentals per car per day: {n_rentals / self.n_cars / n_days_full:.2f}")
        logger.info("Average rental time per trip, min: "
                    f"{self.total_rental_time / n_rentals * self.tick_in_minutes:.2f}")
        logger.info("Average CM1 gain per trip, Eur: "
                    f"{self.total_rental_time / n_rentals * cm1_per_rental_tick:.2f}")
        logger.info("Overall CM2 profit per day, Eur: "
                    f"{self.stats_cm2.sum() / n_days_full:.2f}")

        # Update selected stats
        self.n_days = n_days_full