"""Simple city simulator, for free-floating carsharing purposes."""

import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

import sys
import numpy as np
from scipy.signal import convolve2d
import time
from PIL import Image  # For image demand loading

# Mixins and utils
from utils import LoggerFormatter
from city_visuals import CityVisuals


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


class City(CityVisuals):
    """A combo of a city, a simulator, and a visualizer."""

    def __init__(self, config=None):
        """Create a city object."""
        logger.info("Initializing city")
        # Start with a default configuration (we'll customize it later)
        default_config = {
            # City properties
            "name": "Verona",  # Just a random pretty name
            "seed": None,  # Random seed (for when reproducibility is desirable)
            "n_cores": 1,  # Number of city cores
            "city_width": 21,    # km
            "grid_step": 0.5,    # km
            "density_sigma": 5,  # Gaussian sigma, km
            "do_flatten_demand": False,  # Whether the top of the gaussian is to be flattened
            "demand_flattening_threshold": 0.4,  # Threshold for demand flattening
            "demand_flattening_factor": 15,  # Strength of demand flattening
            "walking_distance": 0.3,  # Walking eagerness, km. For blurring, pricing etc.

            # Car trips
            "n_cars": 100,
            "initial_r": 5,  # Initial radius in which cars are placed, km
            "trip_lambda": 8,  # Km. The higher, the further cars travel, on average
            "p_factor": 0.2,  # Rental probability factor. Main way to adjust rentals/car/day
            "tick_in_minutes": 5,  # Length of a tick in minutes
            "speed": 20.0,  # Car speed, km/h

            "default_trip_duration_min": 20,  # Starting trip duration, min (to contextualize CM1)

            # Financials
            "cm1_per_trip": 5,  # CM1 revenue per typical trip, Eur
            "cm2_per_day": 20,  # CM2 cost pre day of having a car on balance, Eur
            "relo_cost": 20,    # Relocation cost, Eur

            # Simulation general parameters
            "settle_down_steps": 2,  # Number of steps without stats collection,
                                     # for the initial conditions to wear off
                                     # IRL should always be ~1000, but for testing 2-3 is good.
            "do_relocations": True,  # Whether to do relocations at all

            # Misc
            "learning_rate": 0.01,  # Exponential moving average factor for ongoing stats
            "epsylon": 1e-8,  # Small techincal value to avoid log(0) , 1/0 etc.
        }

        # Set default values
        for key,value in default_config.items():
            self.__setattr__(key, value)

        # Immediately overwrite them with custom values (if any):
        if config is not None:
            for key,value in config.items():
                self.__setattr__(key, value)

        if self.seed is not None:  # If we want reproducibility
            np.random.seed(self.seed)

        # -- Update calculatable fields --
        # Counters
        self.total_steps_run = 0  # Total number of simulation steps run so far
        self.total_steps_that_count = 0  # Steps in stats-collecting phase (after settling down)
        # Demand density and maps
        self.initialize_maps()
        # Ongoing stats
        self.total_rental_time = 0  # Total rental time, in ticks, for all cars
        self.total_cm1 = 0  # Total CM1 so far, Eur
        # For idle tick cost, we'll start with CM2-based estimation, then switch to CM1-based one
        self.global_cm1_per_tick = self.cm2_per_day / (24 * 60 / self.tick_in_minutes)


    def initialize_maps(self):
        """A separate method, just in case we ever change settings mid-simulation."""
        self.grid_size = int(np.ceil(self.city_width/self.grid_step))
        logger.debug(f"Grid size: {self.grid_size}x{self.grid_size}")

        # Dynamic properties
        self.create_demand_profile()
        # The calculation for cm1_per_rental_tick is a bit weird as we want to preseve consistency
        # with simpler models presented in this project, which means that we need to link
        # the per-tick revenue here to flat revenues per trip used elsewhere.

        self.map_cm1 = np.zeros_like(self.demand, dtype=np.float32)  # CM1 profit
        self.map_cm2 = np.zeros_like(self.demand, dtype=np.float32)  # CM2 profit
        self.map_n_appops  = np.zeros_like(self.demand, dtype=np.int32)  # Demand
        self.map_n_rentals = np.zeros_like(self.demand, dtype=np.int32)  # Outgoing rentals
        self.map_n_arrivals = np.zeros_like(self.demand, dtype=np.int32) # Incoming rentals
        self.map_idle_time = np.zeros_like(self.demand, dtype=np.int32)  # Idle time in ticks
        self.map_relo_sources = np.zeros_like(self.demand, dtype=np.int32)
        self.map_relo_targets = np.zeros_like(self.demand, dtype=np.int32)

        # Exponential blurring kernel
        # Kernel size: 3 sigmas
        kernel_size = int(np.ceil(self.walking_distance / self.grid_step))*3
        self.blur_kernel = np.zeros((2*kernel_size+1, 2*kernel_size+1), dtype=np.float32)
        logger.debug(f"Blur kernel size: {self.blur_kernel.shape}")
        for i in range(-kernel_size, kernel_size+1):
            for j in range(-kernel_size, kernel_size+1):
                distance = np.hypot(i, j)*self.grid_step
                self.blur_kernel[i+kernel_size, j+kernel_size] = np.exp(
                    -distance / self.walking_distance
                )
        self.blur_kernel /= self.blur_kernel.sum()  # Normalize


    def create_demand_profile(self):
        """Calculate a density profile."""
        logger.info(f"Calculating density profile for {self.n_cores} core(s)")
        # Reset density to zero
        self.demand = np.zeros(shape=(self.grid_size, self.grid_size))
        center = self.grid_size / 2

        if self.n_cores == 1:
            core_centers = [(center, center)]
        else:
            core_centers = []
            for i_core in range(self.n_cores):
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

        # Flatten the demand profile a bit, to avoid too extreme differences
        if self.do_flatten_demand:
            flattener = lambda x: 1/(1+np.exp(
                self.demand_flattening_factor*(self.demand_flattening_threshold-x))
            )
            self.demand = flattener(self.demand)

        # Normalize demand to [0, 1] range
        self.demand = self.demand / np.max(self.demand)

        # Pre-process demand for simulations (produce fields flat_demand and flat_grid_coords)
        self.vectorize_demand()


    def load_demand_profile(self, filename):
        """Loads demand profile from an image."""
        logger.info(f"Load demand profile from image {filename}")
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
            i = int(center + (np.random.uniform()*radius*2 - radius)/self.grid_step)
            return max(0, min(self.grid_size-1, i))

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

        self.reset_parked_map()


    def reset_parked_map(self):
        """Reset the parked cars map."""
        self.cars_per_pixel = np.zeros(shape=(self.grid_size, self.grid_size), dtype=np.int32)

        # Update the current map of parked cars
        for x,y in self.car_xy[self.car_states != car_state["rented"]]:
            self.cars_per_pixel[x,y] += 1


    def simulate(self, n_steps=1):
        """Run a few simulation steps."""
        logger.info(f"Running simulation for {n_steps} steps")

        # TODO: Reset idle time counter for cars

        start_time_sim = time.time()
        cm1_per_rental_tick = (
            (self.cm1_per_trip / self.default_trip_duration_min) * self.tick_in_minutes
        )
        global_cm1_per_tick = self.cm2_per_day / (24 * 60 / self.tick_in_minutes)  # Starting value

        for step in range(n_steps):
            logger.debug(f"Sim step {step} of {n_steps}")
            if (step > 0) and (step % 5000) == 0:
                logger.info(f"..Simulating step {step} of {n_steps}")
            idling_mask = (self.car_states == car_state["idle"])
            in_transit_mask = self.car_states == car_state["rented"]

            # At the beginning of the first real step (after settling down), reset stats
            if self.total_steps_run == self.settle_down_steps:
                self.car_timer_idle.fill(0)
                # Increase n_arrivals stats by one for every car already parked
                np.add.at(self.map_n_arrivals,
                          (self.car_xy[idling_mask, 0], self.car_xy[idling_mask, 1]), 1)

            # ------------------ 1. Arrivals

            if not np.any(in_transit_mask):
                arriving_mask = np.zeros(self.n_cars, dtype=bool)  # No arrivals
            else:
                # Decrement timers for cars in transit
                self.car_timer_transit[in_transit_mask] -= 1

                # Identify cars arriving *this* tick
                arriving_mask = np.zeros(self.n_cars, dtype=bool)
                arriving_mask = in_transit_mask & (self.car_timer_transit <= 0)
                arriving_indices = np.where(arriving_mask)[0]

                if len(arriving_indices) > 0:
                    # Update states and positions for arriving cars
                    logger.debug(f"Cars {arriving_indices} arriving at {
                        [(int(a), int(b)) for a,b in self.car_destinations[arriving_indices]]}")
                    self.car_states[arriving_mask] = car_state["idle"]
                    self.car_xy[arriving_mask] = self.car_destinations[arriving_mask]
                    # update cars_per_pixel:
                    np.add.at(self.cars_per_pixel,
                              (self.car_xy[arriving_mask, 0], self.car_xy[arriving_mask, 1]), 1)

            # ------------------ 2. New rentals

            self.car_timer_idle[idling_mask] += 1  # Idling cars have idled for one more tick now

            # --- Identify new rentals:
            app_openings, car_indices_getting_rented = self.identify_new_rentals(idling_mask)

            if len(car_indices_getting_rented) != 0:
                logger.debug(f"Cars {car_indices_getting_rented} rented from {
                    [(int(a), int(b)) for a,b in self.car_xy[car_indices_getting_rented]]}")
                rental_start_positions = self.car_xy[car_indices_getting_rented] # (n_rented, 2)

                # --- Pick where the rented cars will move:
                chosen_destinations, transit_times = \
                    self.pick_rental_destinations(rental_start_positions)

                # Update the states of cars starting the trip
                self.car_states[car_indices_getting_rented] = car_state["rented"]
                self.car_timer_transit[car_indices_getting_rented] = transit_times
                self.car_destinations[car_indices_getting_rented] = chosen_destinations
                self.car_timer_idle[car_indices_getting_rented].fill(0)  # Reset idle times
                # Subtract departing cars from the parked map
                self.cars_per_pixel[
                    self.car_xy[car_indices_getting_rented, 0],
                    self.car_xy[car_indices_getting_rented, 1]
                ] -= 1

            # ------------------ 3. Relocations
            relo_happened = False
            if self.do_relocations:
                # Update idling mask as some cars have just been rented
                idling_mask = (self.car_states == car_state["idle"])
                if np.any(idling_mask):  # If there are any idling cars
                    # Find relocation source
                    # TODO: Technically here demand should be blurred, but it's irrelevant
                    # untilwe start modeling OAs, boosting demand near the border
                    demand_source = self.demand / np.maximum(self.cars_per_pixel, 1)
                    # Mask out pixels without idling cars
                    demand_source[ self.cars_per_pixel == 0 ] = np.inf
                    index_source = np.argmin(demand_source)
                    # To make things simpler, we only try to relocate one car per tick
                    best_demand_source = demand_source.flat[index_source]

                    # Find relocation target (a pixel with highest demand/(n+1))
                    self.cars_per_pixel_blurred = convolve2d(
                        self.cars_per_pixel,
                        self.blur_kernel,
                        mode='same', boundary='fill', fillvalue=0
                    )
                    demand_target = self.demand / (self.cars_per_pixel_blurred + 1)
                    index_target = np.argmax(demand_target)
                    best_demand_target = demand_target.flat[index_target]
                    # Calculate CM2 effect: take the delta of expected idle times
                    # (inversely proportional to demand per car), convert from ticks to days,
                    # convert from days to Eur using cm2_per_day, then subtract relocation cost
                    predicted_cm2 = (
                        (1/best_demand_source - 1/best_demand_target)
                        * self.tick_in_minutes / 60 / 24
                        * self.cm2_per_day
                        - self.relo_cost
                    )

                    if predicted_cm2 > 0:  # Relo is expected to be profitable, let's do it
                        source_x, source_y = np.unravel_index(index_source, self.demand.shape)
                        target_x, target_y = np.unravel_index(index_target, self.demand.shape)
                        logger.debug(
                            f"Relo from ({source_x}, {source_y}) to ({target_x}, {target_y}) "
                            f"offers cm1 of {predicted_cm2:.2f} Eur")

                        # Find a car to relocate from the source pixel
                        cars_in_source_pixel = np.where(
                            idling_mask & (self.car_xy[:,0] == source_x)
                                         & (self.car_xy[:,1] == source_y)
                        )[0]
                        logger.debug(f"Cars in source pixel: {cars_in_source_pixel}")
                        car_to_relocate = np.random.choice(cars_in_source_pixel)

                        # Relocate it to the target pixel (instanteously, for simplicity)
                        self.car_xy[car_to_relocate] = (target_x, target_y)
                        self.cars_per_pixel[source_x, source_y] -= 1
                        self.cars_per_pixel[target_x, target_y] += 1
                        self.car_timer_idle[car_to_relocate].fill(0)  # Reset idle time
                        relo_happened = True


            # ------------------ 4. Stats collection
            if self.total_steps_run >= self.settle_down_steps:
                # Critically, we don't collect stats in the "settle down" phase; this is one
                # it's important to have all stats collection happen in one place (here).
                self.total_steps_that_count += 1
                self.map_n_appops += app_openings

                # Idling cars
                np.add.at(self.map_idle_time,
                        (self.car_xy[idling_mask, 0], self.car_xy[idling_mask, 1]), 1)
                np.add.at(self.map_cm2,
                        (self.car_xy[idling_mask, 0], self.car_xy[idling_mask, 1]), -global_cm1_per_tick)

                # Rental departures (including all financial effects)
                if len(car_indices_getting_rented):
                    # These are self.car_xy[car_indices_getting_rented], calculated above
                    x0, y0 = rental_start_positions[:, 0], rental_start_positions[:, 1]
                    np.add.at(self.map_n_rentals, (x0, y0), 1)

                    self.total_rental_time += transit_times.sum()

                    # cm1, cm2 for cars that got rented
                    cm1_increments = transit_times * cm1_per_rental_tick / 2
                    cm2_increments = cm1_increments - (transit_times * global_cm1_per_tick)/2
                    x1, y1 = chosen_destinations[:, 0], chosen_destinations[:, 1]
                    np.add.at(self.map_cm1, (x0, y0), cm1_increments) # 50:50 start and finish
                    np.add.at(self.map_cm1, (x1, y1), cm1_increments)
                    np.add.at(self.map_cm2, (x0, y0), cm2_increments) # 50:50 start and finish
                    np.add.at(self.map_cm2, (x1, y1), cm2_increments)
                    # A minor inconsistency is that we update rental cm1 at destination
                    # at the start of a rental, but update map_n_arrivals at the end of it.
                    # That's because we want to use map_n_arrivals as a denominator
                    # in per-parked-car formulas, so we can't book them in advance.

                # Rental arrivals (number only)
                np.add.at(self.map_n_arrivals,
                          (self.car_xy[arriving_mask, 0], self.car_xy[arriving_mask, 1]), 1)

                # Relocations
                if relo_happened:
                    # We rely on the fact that relo source and target coordinates were
                    # recently calculated. As we do only one relo per tick, += is safe.
                    self.map_relo_sources[(source_x, source_y)] += 1
                    self.map_relo_targets[(target_x, target_y)] += 1

            # Consistency checks
            if not (self.cars_per_pixel >= 0).all():
                negative_pixels = np.where(self.cars_per_pixel < 0)
                raise ValueError(
                    f"Negative number of cars in pixels {negative_pixels} at step {step}"
                )

            self.total_steps_run += 1
            # End simulation loop

        end_time_sim = time.time()
        logger.info(f"Simulation completed in {end_time_sim - start_time_sim:.2f} seconds")
        # Days during this simulation bout (both technical and those that count):
        n_days = n_steps  * self.tick_in_minutes / 60 / 24
        # Total days within simulation (both technical, then stats-collecting)
        n_days_full = self.total_steps_run * self.tick_in_minutes / 60 / 24
        # Total days with stats collection
        n_days_that_count = self.total_steps_that_count * self.tick_in_minutes / 60 / 24
        logger.info(f"In-simulation time passed: {n_days:.0f} days")
        logger.info(f"Overall, statistics gathered over: {n_days_that_count:.0f} days")
        n_rentals = self.map_n_rentals.sum()
        logger.info(f"Cumulative rentals happened: {n_rentals}")
        logger.info("Average rentals per car per day: "
                    f"{n_rentals / self.n_cars / n_days_that_count:.2f}")
        logger.info("Average rental time per trip, min: "
                    f"{self.total_rental_time / n_rentals * self.tick_in_minutes:.2f}")
        logger.info("Average CM1 profit per trip, Eur: "
                    f"{self.total_rental_time / n_rentals * cm1_per_rental_tick:.2f}")
        logger.info("Overall CM2 profit per day, Eur: "
                    f"{self.map_cm2.sum() / n_days_that_count:.2f}")
        logger.info("Average relocations per day: "
                    f"{self.map_relo_sources.sum() / n_days_that_count:.2f}")

        self.n_days = n_days_that_count  # Used in jupyter analyses


    def identify_new_rentals(self, idling_mask):
        """Identify which cars get rented this tick."""
        # --- Generate demand for rentals
        roll_for_attempts = np.random.rand(*self.demand.shape)
        rental_attempts = (roll_for_attempts < self.demand * self.p_factor).astype(np.int32)
        pixels_with_demand = np.where(rental_attempts > 0)

        # If no idling cars, then no cars to rent, but app openings will still happen
        if not np.any(idling_mask):
            return rental_attempts, np.array([], dtype=np.int32)

        # --- Pick which cars are be rented this step
        # Get a list of all idle cars
        all_idle_cars = np.where(idling_mask)[0]

        # List the flattened indices of pixels in which idlinig cars are staying.
        # Then calculate flat indices of pixels with rental demand. Then match cars
        # to demand. It will mark all cars that may be rented at this step
        # (but we'll still need to roll a dice and move only some of them)
        pixels_with_idle_cars = np.ravel_multi_index(
            (self.car_xy[all_idle_cars, 0], self.car_xy[all_idle_cars, 1]),
            self.demand.shape
        )
        pixels_with_demand = np.ravel_multi_index(pixels_with_demand, self.demand.shape)
        indices = np.isin(pixels_with_idle_cars, pixels_with_demand)
        cars_that_might_be_rented = all_idle_cars[indices]
        pixels_of_cars_that_might_be_rented = pixels_with_idle_cars[indices]

        # Now select the first car from every pixel with rental attempts,
        # then find global indices of those cars that are rented.
        # We'll use a feature of np.unique() that returns not just unique values,
        # but also the indices of the first occurrence of each unique value.
        # So all we need to do, to sample random cars, is to randomly shuffle cars
        # within each pixel, which we can do with lexicographic sorting,
        # first by pixels index, then by a random number.
        roll_the_dice = np.random.rand(len(cars_that_might_be_rented))
        sort_indices = np.lexsort((roll_the_dice, pixels_of_cars_that_might_be_rented))
        _unique_pixels, unique_indices = np.unique(
            pixels_of_cars_that_might_be_rented[sort_indices],
            return_index=True
        )
        final_indices = sort_indices[unique_indices]
        car_indices_getting_rented = cars_that_might_be_rented[final_indices]
        return rental_attempts, car_indices_getting_rented


    def pick_rental_destinations(self, start_positions):
        """Use Gumbel-Max trick to pick rental destinations for rented cars."""
        n_rented = len(start_positions)

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

        # Calculate expected transit time in ticks, for every car
        distances_km = distances_km[np.arange(n_rented), chosen_flat_indices]
        transit_times = np.maximum(
            1, np.round(distances_km / self.speed * 60 / self.tick_in_minutes)
            ).astype(np.int32)

        return chosen_destinations, transit_times


if __name__ == "__main__":
    # A simple test run

    formatter = LoggerFormatter(
        fmt="%(asctime)s: %(levelname)s: %(funcName)s: %(message)s", datefmt='%I:%M:%S')
    hnd = logging.StreamHandler(stream=sys.stdout)

    # Remove default logging handler:
    for h in logger.handlers: logger.removeHandler(h)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG) # Normally it's way to verbose, but in the console we want it so
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    logger.setLevel(logging.DEBUG)

    city = City({
        "seed": 1,
        "settle_down_steps": 10,
        "n_cars": 3,
        "n_cores": 1,
        "do_relocations": True,
        "relo_cost": 1,
        "city_width": 3,     # 3 width with 0.5 grid step means a 6x6 grid
        "grid_step": 0.5,
        "density_sigma": 0.8,
    })
    city.init_cars()
    city.simulate(n_steps=100)