# CarSharing 101 
## (Introduction to Free-Floating Carsharing)

##### Version 0.3.3

## Abstract

Free-floating car-sharing is hard, and no company so far has convincently demonstrated that it can be profitable. This richly illustrated collection of python scripts offers a practical introduction to the topic, as well as a set of practical hints to make car-sharing profitable. Follow them, and make your city better! Your competitors will hate these simple tricks!

## Table of Contents

0. [Introduction](00_introduction.md)
1. [The natural behavior of cars](01_natural_behavior.md)
2. [Relocations](02_relocations.md)
3. [Pricing](03_pricing.md)
4. [Operating area](04_operating_area.md)
5. [Conclusion](05_conclusion.md)
6. [Appendix: Default parameters](06_appendix.md)
7. [References](07_references.md)

# Todo: Text 🔥

* Write how everything is intentionally in notebooks, to minimize and expose the code, **except for the city simulation**. Which is based on all the same principles, and uses same formulas, but optimized for performance, and so hides some of this unnecessary complexity from the viewer. Conceptually, the only difference between the city simulation and simplified models presented so far is that in the city simulation travel is not instantaneous, but car are assumed to be traveling at a constant speed of 30 km/h. Also mention that the simulation uses Gumbel-Max trick to vectorize Monte-Carlo operations (provide a ref), but that explaining the principles of this trick in detail is out of scope for this work.
* Give titles to all figures
* Add the maxim of "left to its own devices, cars end up standing in the worst possible place"

# Todo: Code 🔥

* Extract "flatter city" into a method (have a post-processing option)
* Extract "identify rentals" into a method - it's getting way too long
* Do we want to add at least some unit tests?
* Do we want an integration test that calculates city financials in 2-3 different ways, and checks that the stats are fully consistent?

# Notebooks

* Move pricing from one station notebook to a separate notebook

# Editing principles

* Go through all figures, and make sure that every figure explained from scratch, in terms of how to read it (at least as a single short sentence)
* For rentals, use origin-destination (terminology)
* For relocations, use source-target
* Check for consistent use of terms "zones" and "stations", especially early on. Perhaps it makes sense to stick to "stations" until the city is introduced? Or at least be consistent within any given paragraph + make sure that both "stations" and "zones" are defined at first use.

# Standards for illustrations
```python
plt.figure(figsize=(10, 4), facecolor='white')
plt.title("Fig. 0.0.0: Description", loc='left')
if accompanied_by_averages:
    plt.plot(x, y, '.', alpha=0.1, markersize=10)
    plt.plot(x.mean(axis=0), y.mean(axis=0), 'ks-')
elif scatterplot_alone:
	plt.plot(x, y, '.', alpha=0.3, markersize=10) 
plt.tight_layout()
```