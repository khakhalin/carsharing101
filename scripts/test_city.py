"""Minimalistic test, mostly to avoid stupid syntactic mistakes that break the code."""

import pytest
from city_simulator import City

def test_city_creation():
    city = City({'name':'Wroclaw'})
    assert city.name == "Wroclaw"
    assert city.grid.max() > 0  # By now demand density should have been calculated

def test_vectorize_demand():
    city = City()
    city.vectorize_demand()
    assert city.flat_grid_coords.shape[0] > 10  # Supposedly n_pixels by 2 (x,y coords)
    assert city.flat_grid_coords.shape[1] == 2
    assert city.flat_grid_coords[:,0].min() == 0
    assert city.flat_grid_coords[:,0].max() == city.grid_size - 1
    assert city.flat_demand.shape[0] == city.grid_size ** 2
    assert city.flat_demand.min() > 0

def test_init_cars():
    city = City({'n_cars':5})
    city.init_cars()
    assert city.cars_xy.shape == (5,2)
    assert city.car_destinations.shape == (5,2)
    assert city.car_states.shape == (5,)
    assert city.car_timer_transit.shape == (5,)
    assert (city.cars_xy == city.cars_xy.astype(int)).all(), "Car coordinates should be integers"
    assert (city.cars_xy >= 0).all() and (city.cars_xy < city.grid_size).all()


def test_visualize_city():
    city = City()
    city.visualize()
    assert True  # If we reach this point, the visualization did not crash

def test_simulation():
    city = City({'n_cars':10})
    city.init_cars()
    original_cars_xy = city.cars_xy.copy()
    city.simulate(n_steps=5)
    assert city.cars_xy.shape[0] == 10
    assert not (city.cars_xy == original_cars_xy).all()  # At least some cars should have moved