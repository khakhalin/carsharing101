"""Simple city simulator, for free-floating carsharing purposes."""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import time
from PIL import Image  # For image demand loading
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class City():

    def __init__(self, config=None):
        """Create a city object."""
        logger.info("Initializing city")
        default_config = {
            # City properties
            "name": "Verona",
            "n_cores": 1,  # Number of city cores
            "city_width": 21, # km
            "grid_step": 1, # km
            "density_sigma": 6, # Gaussian sigma

            # Simulation properties
            "n_cars": 100,
            "average_speed_kmh": 30.0,
            "trip_lambda":10,  # The higher, the further cars travel, on average,
            "initial_r": 1,  # Initial radius in which cars are placed, km
            "p_rental": 0.1,  # Rental probability is proportional to this. Tune it up.
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
                core_centers += [(center + np.random.normal()*self.density_sigma, center + np.random.normal()*self.density_sigma)]

        for i in range(self.grid_size):
            for j in range(self.grid_size):
                distance_squared = (((i+0.5)-center)**2 + ((j+0.5)-center)**2)*self.grid_step**2
                self.grid[i,j] = np.exp(-distance_squared/self.density_sigma**2)


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
        radius = self.initial_r

        def random_pixel(center):
            return center + (np.random.uniform()*radius*2 - radius)/self.grid_step

        self.cars_xy = np.zeros(shape=(self.n_cars, 2))
        for i in range(self.n_cars):
            x = random_pixel(center)
            y = random_pixel(center)
            self.cars_xy[i,:] = (x,y)

        # self.car_xy = np.stack((car_x, car_y), axis=1) # Current location IF available
        # car_destinations = np.zeros_like(car_positions)  # Where the car is going
        # car_states = np.full(N_CARS, ST_AVAILABLE, dtype=np.int8)
        # car_transit_timers = np.zeros(N_CARS, dtype=np.int32) # Remaining ticks in transit
        # car_current_trip_distance_km = np.zeros(N_CARS, dtype=np.float32) # Store distance for stats