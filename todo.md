# Todo: Text 🔥

* Re-run and re-link existing operating area figures, to give them 3XX names (not 4XX)
* Write how everything is intentionally in notebooks, to minimize and expose the code, **except for the city simulation**. Which is based on all the same principles, and uses same formulas, but optimized for performance, and so hides some of this unnecessary complexity from the viewer. Conceptually, the only difference between the city simulation and simplified models presented so far is that in the city simulation travel is not instantaneous, but car are assumed to be traveling at a constant speed of 30 km/h.
* Mention that the simulation uses Gumbel-Max trick to vectorize Monte-Carlo operations (provide a ref), but that explaining the principles of this trick in detail is out of scope for this work.

# Todo: Notebooks

* Move pricing from one station notebook to a separate notebook

# Editing principles

* Go through all figures, and make sure that every figure explained from scratch, in terms of how to read it (at least as a single short sentence)
* Every figure should have a title
* Terminology:
    * For rentals, use origin-destination
    * For relocations, use source-target
    * Early on, for simulations, stick to "stations", never "zones". For cities, use "zones". Make sure that somewhere (at the earliest convenience) there's a paragraph that discusses how stations, zones, and pixel-based modeling interact

# Boilerplate for illustrations
```python
plt.figure(figsize=(10, 4), facecolor='white')  # For two subplots
plt.title("Fig. 0.0.0: Description", loc='left')
if single_points_accompanied_by_averages:
    plt.plot(x, y, '.', alpha=0.1, markersize=10)
    plt.plot(x.mean(axis=0), y.mean(axis=0), 'ks-')
elif scatterplot_alone:
	plt.plot(x, y, '.', alpha=0.3, markersize=10)
plt.tight_layout()
```