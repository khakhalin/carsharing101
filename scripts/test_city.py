"""Minimalistic test, mostly to avoid stupid syntactic mistakes that break the code."""

import pytest
from city_simulator import City, car_state

def test_city_creation():
    city = City({'name':'Wroclaw'})
    assert city.name == "Wroclaw"
    assert city.demand.max() > 0  # By now demand density should have been calculated

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
    assert city.car_xy.shape == (5,2)
    assert city.car_destinations.shape == (5,2)
    assert city.car_states.shape == (5,)
    assert city.car_timer_transit.shape == (5,)
    assert (city.car_xy == city.car_xy.astype(int)).all(), "Car coordinates should be integers"
    assert (city.car_xy >= 0).all() and (city.car_xy < city.grid_size).all()


def test_visualize_city():
    city = City()
    city.visualize()
    assert True  # If we reach this point, the visualization did not crash

def test_simulation():
    city = City({'n_cars':100, "p_rental":1})  # Make rentals very probable
    city.init_cars()
    original_car_xy = city.car_xy.copy()
    city.simulate(n_steps=1)
    # Now a bunch of probabilistic tests that MAY fail, but P is very low
    assert (city.car_states == car_state['rented']).any(), "At least one car should be in transit"
    assert (city.car_timer_transit > 1).any(), "At least one rental should last more than one tick"
    city.simulate(n_steps=4)
    assert city.car_xy.shape[0] == 100
    assert not (city.car_xy == original_car_xy).all(), "At least some cars should have moved"