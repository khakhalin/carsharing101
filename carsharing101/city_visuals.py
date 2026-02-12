"""Mixin with all methods related to visuals."""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import colormaps
import time
import logging

logger = logging.getLogger()

class CityVisuals():
    """Mixin class for city visualizations.

    This class doesn't carry its own properties, but entirely relies on the properties of the
    main "City" class. Only methods here, for purely organizational reasons.
    """

    @staticmethod
    def _finalize_plot(show_cbar=True):
            """Universal design elements that go in every plot."""
            plt.xticks([], [])
            plt.yticks([], [])
            plt.gca().set_aspect('equal', adjustable='box')
            if show_cbar:
                cbar = plt.colorbar(fraction=0.046, pad=0.04)
                cbar.ax.tick_params(labelsize=8)


    def visualize(self, plots="all", title=None, title_y=0.75):
        """Show visualizations of the city."""
        if isinstance(plots, str):
            if plots == "all":
                plots = ["cars", "cm1", "idle_times", "cm2", "dfr"]
            else:
                plots = [plots]
        n_plots = len(plots)

        n_days = self.total_steps_that_count * self.tick_in_minutes / 60 / 24 + 0.001

        # Below is a long-ish script with plots given one by one, just with each of them checking
        # if we want to see it (if its name is in "plots"). The sequence is fixed.
        plot_counter = 0
        # Demand and current car positions:
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
            CityVisuals._finalize_plot(show_cbar=False)

        if "cm1" in plots:
            if n_plots > 1:
                plot_counter += 1
                plt.subplot(1, n_plots, plot_counter)
                plt.title("CM1, €/day")
            plt.imshow(self.map_cm1.T / n_days, aspect='auto', interpolation='none',
                extent=[0, self.grid_size, 0, self.grid_size], cmap='Blues', origin='lower');
            CityVisuals._finalize_plot()

        if "idle_times" in plots:
            if n_plots > 1:
                plot_counter += 1
                plt.subplot(1, n_plots, plot_counter)
                plt.title("Average idle time, days")
            # Move from total idle time to idle time per car
            value = self.map_idle_time / np.maximum(self.map_n_arrivals, 1)
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
            CityVisuals._finalize_plot()

        if "cm2" in plots:
            if n_plots > 1:
                plot_counter += 1
                plt.subplot(1, n_plots, plot_counter)
                plt.title("CM2, €/day")
            # Diverging colormap, red for negative, blue for positive, light gray for zero
            cmap = colormaps.get_cmap('RdBu')
            clim_factor = 2.5  # To make profitable areas really blue
            plt.imshow(self.map_cm2.T / n_days, aspect='auto', interpolation='none',
                extent=[0, self.grid_size, 0, self.grid_size], origin='lower',
                # norm=plt.matplotlib.colors.CenteredNorm(),  # Center the colormap at zero
                vmin=-self.cm2_per_day*clim_factor, vmax=self.cm2_per_day*clim_factor,
                cmap=cmap)
            # cm2_per_day just gives a reasonable range, and I want to see some blue color
            CityVisuals._finalize_plot()

        if "dfr" in plots:
            if n_plots > 1:
                plot_counter += 1
                plt.subplot(1, n_plots, plot_counter)
                plt.title("DFR")
            plt.imshow(self.map_n_rentals / np.maximum(1, self.map_n_appops),
                aspect='auto', interpolation='none',
                extent=[0, self.grid_size, 0, self.grid_size], origin='lower',
                cmap="cividis")  # Either cividis or PuOr. But gray is prob a better neutral color
            CityVisuals._finalize_plot()

        if "relo_sources" in plots:
            if n_plots > 1:
                plot_counter += 1
                plt.subplot(1, n_plots, plot_counter)
                plt.title("Relo sources, /day")
            cmap_rs = colormaps.get_cmap('Oranges').copy()
            cmap_rs.set_bad(color='lightgray')
            value = self.map_relo_sources.astype(float) / n_days
            value[value == 0] = np.nan
            plt.imshow(value.T, aspect='auto', interpolation='none',
                extent=[0, self.grid_size, 0, self.grid_size], cmap=cmap_rs, origin='lower')
            CityVisuals._finalize_plot()

        if "relo_targets" in plots:
            if n_plots > 1:
                plot_counter += 1
                plt.subplot(1, n_plots, plot_counter)
                plt.title("Relo targets, /day")
            cmap_rt = colormaps.get_cmap('Greens').copy()
            cmap_rt.set_bad(color='lightgray')
            value = self.map_relo_targets.astype(float) / n_days
            value[value == 0] = np.nan
            plt.imshow(value.T, aspect='auto', interpolation='none',
                extent=[0, self.grid_size, 0, self.grid_size], cmap=cmap_rt, origin='lower')
            CityVisuals._finalize_plot()

        if title is not None:
            plt.suptitle(title, x=0, y=title_y, fontsize=13, ha="left")

        plt.tight_layout()
