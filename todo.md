# Todo: Text 🔥

* To the intro, add a call for "if you have found a mistake, or what to contribute something important, please reach out!"
* Re-run and re-link existing operating area figures, to give them 3XX names (not 4XX)
* Write how everything is intentionally in notebooks, to minimize and expose the code, **except for the city simulation**. Which is based on all the same principles, and uses same formulas, but optimized for performance, and so hides some of this unnecessary complexity from the viewer. Conceptually, the only difference between the city simulation and simplified models presented so far is that in the city simulation travel is not instantaneous, but car are assumed to be traveling at a constant speed of 30 km/h. Also mention that the simulation uses Gumbel-Max trick to vectorize Monte-Carlo operations (provide a ref), but that explaining the principles of this trick in detail is out of scope for this work.
* Replace "a City and a village" schematic - it's the first schematic in the entire book, make it look less insane

# Todo: Code 🔥

* Rework config: 
    * Move default config values and their processor (config intializer) out into `config.py`
    * Make it a mixin base class for the city (a city is not a config, but it has config functionality)
* Be able to show maps of relo sources and targets
* Take relocation algo out of the main loop into a subroutine
* Add some sort of uv requirements file to the repo to make the setup reproducible (also learn how)

Testing
* Do we want unit tests for rental cars selection and rental destination choice? On minimalistic mocks of like 2-3 cars in a ducktyped pseudo-city?
* Do we want an integration test that calculates city financials in 2-3 different ways, and checks that the stats are consistent?

Ideas that I'm not sure about
* Instead of making config a mixin, make it a separate pydantic dataclass, assigning params to it, and not to the simulation. In which case parameters will be referred not as `self.n_steps`, but as `self.cfg.n_steps` (for example)
* ❓Still allow calling city with a dict config, and then use this dict to fill up matching fields at init. If a field like that doesn't exist however, raise an error (not only on init, always. We want the list of fields to be closed.)
    * Write 1-2 unit tests for this functionality (init with a dict, existing field update, nonexistent field update)    
* ❓Make `maps` into a dataclass with pre-defined fields
    * Rename demand into map_demand
    * Rename current distribution of standing cars into a map_whatever

# Todo: Notebooks

* Move pricing from one station notebook to a separate notebook

# Editing principles

* Go through all figures, and make sure that every figure explained from scratch, in terms of how to read it (at least as a single short sentence)
* Every figure should have a title
* Terminology:
    * For rentals, use origin-destination
    * For relocations, use source-target
    * Early on, for simulations, stick to "stations", never "zones". For cities, use "zones". Make sure that somewhere (at the earliest convenience) there's a paragraph that discusses how stations, zones, and pixel-based modeling interact

# Standards for illustrations
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