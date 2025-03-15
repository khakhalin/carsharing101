# Car Sharing 101 (Introduction to Free-Floating Carsharing)
## Draft v0.2.0

## Abstract

Free-floating car-sharing is hard, and no company so far has convincently demonstrated that it can be profitable. This collection of conceptual models offers specific advice on how to make free-floating car-sharing profitable.

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

* Move "Is Gaussian city local?" to HA optimization, somehow preface it with "Does HA split into sub-HAs?" - and the answer is "no", both because of locality (that doesn't really exist - after 1-2 rentals car is completely mixed), but also because of cost structure. As HA within a single metropolitan area shrinks, it devolves into a collection of stations, a series of "highlights" with a strong interaction between them; it doesn't devolve into isolated HAs.
* Give titles to all figures
* Introduce a practice of "Bold business-related advice" every now and then, with quotation-like formatting. So that a person could jump and read only them, if so inclined.
* The maxim of "left to its own devices, cars end up standing in the worst possible place"
* At least the mental image of you "always get the worst car type" (mention in a different part that because of that car type is a good predictive variable to use)

# Editing principles

* Go through figures, and make sure that they are explained from scratch every time, in terms of how to read them.
* For rentals, use origin-destination
* For relocations, use source-target
* Check for consistent use between zones and stations, especially early on. Perhaps it makes sense to stick to "stations" until the city is introduced? Or at least be consistent within any given paragraph + make sure that both "stations" and "zones" are defined at first use.
* Check that during calculations, we don't talk about costs of car _ownership_, but "ownership or leasing"


