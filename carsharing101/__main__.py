"""Entry point for `python -m carsharing101` — quick smoke-test with debug plots."""

import sys
import os
import logging
import numpy as np
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for headless runs
import matplotlib.pyplot as plt

from .city_simulator import City, car_state
from .utils import LoggerFormatter

logger = logging.getLogger()


def main():
    # Set up pretty logging
    for h in logger.handlers:
        logger.removeHandler(h)
    ch = logging.StreamHandler(stream=sys.stdout)
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(LoggerFormatter(
        fmt="%(asctime)s: %(levelname)s: %(funcName)s: %(message)s", datefmt='%I:%M:%S'))
    logger.addHandler(ch)
    logger.setLevel(logging.DEBUG)

    # Ensure debug output folder exists
    debug_dir = os.path.join(os.path.dirname(__file__), "..", "figures", "_debug")
    os.makedirs(debug_dir, exist_ok=True)

    print("=" * 60)
    print("CarSharing 101 — smoke-test simulation")
    print("=" * 60)

    city = City({
        "seed": 1,
        "settle_down_steps": 1000,
        "n_cars": 200,
        "n_cores": 1,
        "do_relocations": True,
        "relo_cost": 20,
        "city_width": 21,
        "grid_step": 1,
        "density_sigma": 5,
        "p_factor": 0.22,
    })
    city.init_cars()
    city.simulate(n_steps=5000)

    # Save debug visualisation
    plt.figure(figsize=(12, 5))
    city.visualize(
        plots=["cars", "cm1", "idle_times", "cm2", "dfr"],
        title="Debug: smoke-test city after 5000 steps"
    )
    out_path = os.path.join(debug_dir, "smoke_test.svg")
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"\nDebug figure saved to: {os.path.abspath(out_path)}")

    # Print a compact summary
    n_days = city.n_days
    print(f"\n{'='*60}")
    print(f"  Simulated days (stats):  {n_days:.1f}")
    print(f"  Total rentals:           {city.map_n_rentals.sum()}")
    print(f"  Rentals/car/day:         {city.map_n_rentals.sum() / city.n_cars / n_days:.2f}")
    print(f"  Total CM2, €/day:        {city.map_cm2.sum() / n_days:.2f}")
    print(f"  Relocations/day:         {city.map_relo_sources.sum() / n_days:.2f}")
    print(f"  Mean DFR:                {city.map_n_rentals.sum() / max(1, city.map_n_appops.sum()):.3f}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
