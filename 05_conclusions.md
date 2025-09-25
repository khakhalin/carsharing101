# 5. Conclusions

🔥 On how carsharing cannot replace public transit, and should never be positioned as such, because we fundamentally depend on cars being a cherry on top, a preferred, but not the only means of transportation. By nature how cars behave in space, we cannot guarantee a good **service** (availability), a good **price**, and a good **coverage** at the same time. 

* To guarantee a good service and a good price we would have to limit our offerings only to high-demand areas of the city, becoming a fancy "Drive-it-yourself" shuttle between a few fixed mobility stations.
* To offer a good service and high coverage with on-street parking, we would have to increase the fleet, and then somehow recuperate the costs, making the service expensive.
* Finally, we can offer a good price and a wide coverage by dropping the DFR and resigning to a shadow existence of a fun but unreliable means of transportation.

You can pick any two, but you cannot get all three!

![Pick any two KPIs](figures/venn.svg)


Of three business strategies outlined, only a "Pricey premium service" does not seem to be working in practice, as at this price point it becomes easier to get a taxy than to rent a car that you have to also drive itself. 🔥 An "opportunitistic approach" works if it's coupled with long-term rentals and car pre-booking, essentially becoming a "standard" rental car service where you can rent a car for a few days, and then drop it off almost anywhere. A mobility stations approach seems to be the most promising option so far, as it is also aligned with most progressive trends in modern urbanism and city planning that deprioritizes cars, while acknowledging an important functions that they can solve (rare unusual trips for most people, more regular service for a smaller circle of people with special needs). Relocations, and especially automated relocations by self-driving cars without a passenger (that would be possible at night, and at very low speeds) also offer a promising hybrid model where cars can be rented directly at only few locations, but can be dropped anywhere, or ordered to a particular location for a fee (to compensate the relocation cost). Personally, I believe that this "hybrid" mode is likely to be the future, and may end up finally hitting the magic center on the Venn diagram above.

# How lean a car-sharing business has to be?

🔥 The paradox of data-drivenness: Number of data scientists

🔥Let's assume that we are trying to create a lean team of skilled and highly motivated professionals. An average salary across a team like that, in Germany in 2024, will be around 5000 €/mo (less for junior people, more for seniors and management). Around 40% more will go into taxes and social security, and 20% more into health insurance and retirement contributions, leading to a total cost of about 8000 €/mo per employee.

🔥Estimate as profit-generatinc cars per data scientists (or any other skilled office worker). Estimate as data scientists per city. "The paradox of a data-driven business" - despite ultimately being a physical company, it does not scale easily, as it's so data-driven that the overhead is almost fixed. Although, look how Bsky developed an app at x100 fewer people than Twitter.

# The future of carsharing

🔥 set the problem. Does it have a future? at which point does car-sharing become profitable for households?

**

The most popular car in Germany in 2024 was VW Golf. The cost of owning it was ~300 €/mo for the car itself + about 50 €/mo for insurance, so ~350 €/mo, or about 10 €/day (basically the same calculation that we have for CM2 estimations in the appendix, just without rebates, but also without additional costs specific for carsharing).

On the other hand, a typical SN rental in Berlin costs ~10€. 🔥 - JUSTIFY? Probably based on current prices for some month, so just reference the appendix?

🔥 Can we do it simpler, and just say, CM2 is basically the same in both cases, assuming that the carsharing is just barely profitable, and a certain overhead, that's how much extra a customer would pay? There's a bit of a circular logic here of course, as even if we assume a certain overhead, the amoung of overhead that will go into an individual rental depends on total rentals per day, and these 

Of this 10€, fuel cost should be excluded, as a person owning a car pays it as well. VW Golf does 8L/100 km, fuel costs in 2023 were about 1.8 €/L, Berlin is about 30 km in size, so of a typical 10€ trip, the fuel will cost about 4€ per trip.

Which means that a customer would pay about 6€/trip for the car itself. Dividing the monthly cost of owning a car by this value, we get 350/6 = 58, or a threshold of about 2 trips a day. If a person does less than 2 trips a day (weekends included), owning a car becomes less profitable than using carsharing, in 2023 prices.

Now, on the other hand, according to our rough estimations from Chapter 2, a remote station becomes profitable once it reaches about 10 trips/day (although this assumes that trips are a poisson process, and not a daily commute)

It means that for desynchronized occasional commuters (those running random chores and getting to appointments), and assuming that some back-up transportation options (or our entire premise of less-than 100% DFR would shutter), a group of some 10 households switching to car-sharing would be a win-win (profitable) for both the carsharing provider and the customers. Putting things into perspective, 10 households is about 2-3 smaller than a typical middle-density residential building, and some 10 times smaller than a typical high-density building, meaning that from the purely financial perspective (putting the status consideration aside), and assuming irregular commute, in the long-term _every_ residential area of every city is a viable target for carsharing.

What happens if we want to cover regular commutes as well? If the customers commute for work, leaving the car inactive during the day, the car-sharing company would have  to charge them a bit more: the cost of a car (and as before, let us assume 20€ per day), plus the variable cost (about 5€ by 2 trips), so 30€/day. As we agreed that the default price in our sample city is about 10€ per trip, it means putting a 10€ drop-fee on this hub. Which, on one hand, is a huge drop-fee, but on the other hand, let's again run the profitability analysis for the household itself. With 30€ per working day in a carsharing scenario, and 350€/mo in the ownership scenario, it's more profitable for a working person not to own a car, if they commute less than 350/30 $\approx$ 12 times a month, which corresponds to working hybrid, with 3 days in the office. It is a rather specific requirement of course, but it is not on heard of, and is only likely to become more common in the future. In other words, remote hybrid work promotes car-sharing, as opposed to car ownership, by de-synchronizing car usage, reducing idle times, making car sharing options cheaper, and more competitive, compared to car ownership [^Wan2024].

The fact that all our earlier calculations rely on the possibility to keep DFR below 100%, and also that irregular  carsharing is way more profitable than regular car-sharing, both have strong implications for urbanism and urban mobility. Namely, that carsharing should not and cannot be seen as an alternative to public transportation, but more as an offer that completements it, catching odd and unprecitable mobility use cases. Carsharing in a modern city can only be successful if most of the regular, predictable commutes are covered by public transportatoin, and so city dwellers are very close to giving up on a car, and only need these remaining 10-5% of their use cases to be covered. From my first-hand experience in mobility, I can attest that it is also very noticeable on the city level: the profitability of an area correlates most strongly not with the population density, or socioeconomic status of this population, but with the reliability and availability of public transportation in the area.

🔥 It also means that it is the municipality.. _explain how policies, such as the limitation of parking spaces, are most critical, and so after programmers, data scientists, and operations, our imaginary company shoudl really invest in people supporting long-term relationships with municipalities, as ultimately it is the health of these relationships that defines whether a given city (and thus, also the company operating in this cities!) would make it financially in the long-term.

# References

[^Wan2024]:  Wan, L., & Chen, J. (2024). Flexible working and the future of urban mobility: a novel conceptual framework. In _Pandemic Recovery?_ (pp. 265-281). Edward Elgar Publishing.