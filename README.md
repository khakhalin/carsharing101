# Car Sharing 101 
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

# Todo 🔥

* Write how everything is intentionally in notebooks, to minimize and expose the code, except for a city simulation. Which is based on all the same principles, and uses same formulas, but optimized for performance, and so hides some of this unnecessary complexity from the viewer. Conceptually, the only difference between the city simulation and simplified models presented so far is that in the city simulation travel is not instantaneous, but car are assumed to be traveling at a constant speed of 30 km/h. Also mention that the simulation uses Gumbel-Max trick to vectorize Monte-Carlo operations (provide a ref), but that explaining the principles of this trick in detail is out of scope for this work.
* Give titles to all figures
* Add the maxim of "left to its own devices, cars end up standing in the worst possible place"

# Editing principles

* Go through figures, and make sure that they are explained from scratch every time, in terms of how to read them.
* For rentals, use origin-destination (terminology)
* For relocations, use source-target
* Check for consistent use of terms "zones" and "stations", especially early on. Perhaps it makes sense to stick to "stations" until the city is introduced? Or at least be consistent within any given paragraph + make sure that both "stations" and "zones" are defined at first use.


