# 4. Operating Area

# 4.1. The idea of an optimal OA

🔥 Is it critical to get the size of the OA right? (the basic principles of OA)* 

![The basic idea of optimal OA](figures/04oa_01optimality.svg)

> Revenue here proportional to the sum of distances between all points (total distance travelled). Gaussian city, circular OA. Sometimes no solution, sometimes a range. Interestingly, HA kinda collapses from a permissive situation (a whole range of options with very little effect on profitabiity) to "no solution at all". So perhaps counter-intuitively, if a city is profitable, and HA is decent, you probably cannot earn a lot of money by optimizing it. Optimizing OA is important for marketing (improving the image), and it is extremely important for relationships with the city; it is also important that you don't open in areas that are horrible, but beyond that, most natural growth will probably be net 0 effect on CM2 at first.

> Another phrasing: For a new city, OA is a all-or-nothing situation: are the city is profitable, and almost any reasonable OA will do, or the city is not profitable. it is very hard to cheat here, with a _continuous_ HA.

> Also an intersting side effect: if in doubt, pick an OA with about 2 sigmas (after approximating demand activity with a gaussian). That's the first HA size to become profitable.

* Opening remote stations in neithboring town if a different story, we are not covering this situation here. Tapping into a new long-distance flow may be very profitable, and a big driver of business. The maxim of "HA doesn't matter" is only true for gently tapering population density.
* An extreme example: opening an airport. Can be a revenue driver in the city, if public transportation doesn't connect the airport to some city areas very well.
* Optimization of the OA by means of "skeletizing it", turning it into a bunch of stations and "linear stations (🔥)" also isn't covered by this model. Skeletizing the OA and condensing the fleet cam improve the financials (but it can also make life harder for customers, and reduce ridership)

# 4.2. Strategic placement of stations

🔥 Minimalistic stations: a model that optimizes stations within a Gaussian city via explicit optimization of locations.

```python
city_width = 15 # km
grid_step = 0.1 # km
walking_distance = 0.2 # 200 meters of walking distance
sigma = 10 # Gaussian sigma
```

🔥 The rules of the game:

![Input curves for the station placement optimizer](figures/04oa_02stations_01gaussian_city.svg)
🔥 The results:

![Ideal station placement, for different numbers of stations](figures/04oa_02stations_02idealized.svg)

# 4.3. Shrinking the OA

🔥 Return to the idea of marginal CM2 values. Deciding to close the zone. Link back to the CM2 per zone formula, but rewrite it in marginal cases. Then discuss how not all waiting times are equal (night, rush hour). Discuss Acitivity-weighted, with 2 options: missed CM1 or weighted CM2. Argue that CM2-based is better, as preserves consistency with other formulas and city-level estimations (as arguably, it's the one that estimates the actual effect if we close the zone and re-optimize the fleet).

🔥 The algorithm of Shrinking

# 4.3.1. Concentrating fleet

🔥 The benefit of tendrils and stations (??? - at least describe the idea / hypothesis)

# 4.4. Expanding the OA

🔥 The main idea: Rework into a series of options:

1. Models based on demographics. Present as the most natural intuition; outline weak sides (dependency on stats data, hard to get, demographics is often secret etc.)
2. Pilots. (Or, in an extreme ase, expand drastically, then cut everything that didn't work)  Put here this story about how long to wait till numbers are clear. Customers are unhappy when closing. While it's good to be able to close, it's not a good idea to rely only on that.
3. Voting with feet. Stopovers + app activity. Either predicting CM2 directly, or predicting demand fo each pixel, and then running an optimization of OA (potentially with stations), with a fixed formula from "catchment demand" to CM2 (as already modeled above)
4. Placing some cars intentionally, bayesian updates for estimated demand, improve model
5. Continuous drop-fee. Although in a way relying stop-overs (above) can be considered an extreme case of this idea, as in this case we make the customer pay both for the drives there, and back, and waiting time. The moment we offer an OA there, some of the longer stop-overs will disappear, as customers would stop the rental, thus truly an upper estimate.

That I personally recommend 3.

But even withthis fancy model, there's a problem of extension from a narrow hub or sharp border (cannibalsation; a contradiction with the idea of concentrating fleet). Tricky; some other model is needed.

🔥 Can we sketch such a model, or would it be too weird? Using willingness to walk to map the decay?

## 4.4.1. Pilot projects

🔥 The process. That from the customer pov it's better to never close, so one has to be conservative. But also that it takes a while to build a following (even when competing prividers are present, and people are familiar with the business model!)

## 4.4.2. How long does it take to measure station performance?

🔥 Set up the story

As a mathematically simple, but practically important topic, let us check how many rentals are needed to make a good guess about the profitability of a newly opened station (or zone).

First, let's look at how a typical curve of "rentals rate to date" looks for a Poisson process. Below we can see one such curve, for a process with 5 rentals/day on average, accumulated over a course of the first 10 days. We can see that the estimation gradually improves, but it can have wild peaks (especially in the beginning) and deviations from the mean.

![A curve of observed average frequency of rentals, for a Poisson process](figures/04oa_04growth_02pilots_01cm1_single.svg)

Let's now roll the dice again and again, generating 1000 runs of this kind, for the first 60 days after this "new locaiton" was "opened"; then show all these runs on the same graph (below; light teal lines), together with a mean across all runs (solid black), and a 90% confidence interval around it (dotted lines). As expected, the spread of estimations for the "rentals/day" value becomes narrower with time. Still even after 60 days, or (in this case) about 300 rentals, we may easily be some 5-10% off in terms of estimating the "true" underlying demand in the new loation (the 90% confidence interval by the end of this curve consistutes ±9% of the mean value).

![An average of 1000 curves](figures/04oa_04growth_02pilots_02cm1.png)
As our estimation for the rentals-per-day converges, so will converge the estimations for revenue-per-day and CM1-per-day, as both are proportional to the number of rentals, at least when averaged over a longer period of time. But what about the development of our best estimations for CM2-per-day, for every day after a new location went live? Let's first model these curves for the first 30 days after opening, looking at 1000 different newly opened stations, **in the absence of relocations**. All of the stations have the same true average demand of 10 trips/day in one direction, and as usual, assuming that each trips generates 5€/trip in CM1. The solid black line shows the average; dotted lines show the 5% and 95% percentiles.

![A collection of CM2 curves](figures/04oa_04growth_02pilots_03cm2_norelo.png)
As discussed in Chapter 1, in the absence of relocations a new station tends to quickly accumulate an unfair number of cars, and until some sort of a long-term equilibrium is reached, different random curves for the number of cars at the location effectively diverge. As the cost part of the CM2-per-day formula is proportional to the number of cars at the location, it means that the estimations for CM2 at different, otherwise identical, "new stations" diverge as well! For a small station, of a kind modeled here, it means that this station quickly becomes unproftable, but also the scale of this "unprofitability" can range by 2 orders of magnitude from one experiment to another. The graph above may be described as the results of profitability tracking in 1000 identical new locations, but we can also think of it as profitability tracking of _one_ and same location in 1000 "alternative universes", characterizing our chances to measure the "true" potential profitability of a newly opened location correctly. With curves diverging like that, a meaningful measure is impossible. Putting it differently, in the absence of relocations, any spatial analysis of profitability of different parts of the city becomes completely unreasonable, as you end up detecting areas where relocations were not working, and that are now desperately in need of some intervention, to distribute random fluctuations of trapped fleet. The "actual" values of "spatial CM2" observed in different pats of a no-relocations city over a course of a month will give you almost no information about the potential performance of this area under ideal conditions. Without relocations, it is better to make decisions based on maps of CM1, and not CM2 values. as at least CM1 values will gradually converge.

With relocations enabled, we put an upper limit on the number of cars in each location, and the curves for consequtive estimations of CM2-per-day start to converge again. An example of 1000 such curves, for the same exact new location as above, but with relocations limiting its highest fleet at 2 cars, are shown below. We picked the value of 2 cars here, as in Chapter 2, section 2.1, we have shown that for a station receiving the average of 10 rentals a day, this is the optimal fleet limit to set, and that it is supposed to achieve the highest possible profitability, just above 0€/day in CM2 (so just above breaking-even).

![A collection of CM2 curves](figures/04oa_04growth_02pilots_04cm2_relos.png)
The graph above illustrates three important intuitions. 
* One, that with relocations doing their job, the CM2 values in different runs do indeed converge, and on a value that is not as ridiculously negative as in a laissez-faire city. 
* Second, that this convergence is nevertheless very slow. In the example above, the expected CM2/day for this station is about 2 €/day, but the actual 90% confidence interval extends from −13 to +16 €/day. It means that even though in theory, in the long-term, this new location is expected to be weakly profitable, in about half of cases we would see it losing money (in CM2) after a month of operating. 
* And finally, third, it is interesting that the very few days that the new location is started, it is more likely to seem profitable (the solid black line starts high, and only then decreases). The reason for this is rather straightforward: once you get your first rentals, you will have some profit generated, but it will take a few more rentals until the fleet trapped in the location increases from 0 to 1, to 2, and the first relocations kick in, making it likely that the very first days of operation for the hub would be profitable. However this phenomenon does not manifest itself in a real business: first, because it takes a while before customers notice that a new location appeared, so the first few rentals are alwas relatively slow to materialize, and second, because in practice companies often intentially relocate 1-2 vehicles TO a new station before opening it, to make it seem occupied and buzy, and to make it noticeable in the rental app.

The main learning point from this entire exercise is therefore rather cynical and underwhelming, but nevertheless very important. When starting a new location that is likely to be only slightly profitable, don't try to pronounce a judgment on it after a month or two. Let it be for at least 3 months, better half a year, or a year, then assess. The chances of "bad luck" during the first 1-2 months of activity, even under the assumption of _ideal_ operations, is quite high (in the extreme case of a breaking-even location, about 50%). So unless the new location seems horrible, or a superstar, it's better to be patient, and to wait for a few hundreds, maybe even thousands rentals to happen.

## 4.4.3. Probing customer interest

🔥 The idea of "Relocations as tests"

🔥 Continuous drop-fees

## 4.4.4. Predictive model

🔥 Sketch the predictive model

# Footnotes