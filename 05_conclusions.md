# 5. Conclusions

* The paradox of data-drivenness: Number of data scientists
* The future of mobility: at which point does car-sharing become profitable for households?

# How lean a car-sharing business has to be?

Let's assume that we are trying to create a lean team of skilled and highly motivated professionals. An average salary across a team like that, in Germany in 2024, will be around 5000 €/mo (less for junior people, more for seniors and management). Around 40% more will go into taxes and social security, and 20% more into health insurance and retirement contributions, leading to a total cost of about 8000 €/mo per employee.

🔥

# Long-term potential

🔥 set the problem

**

The most popular car in Germany in 2023 was VW Golf. The cost of owning it was ~300€/mo for the car itself + some 50€/mo for insurance, so ~350€/mo.

On the other hand, a typical SN rental in Berlin costs ~10€.

Of this 10€, fuel cost should be excluded, as a person owning a car pays it as well. VW Golf does 8L/100 km, fuel costs in 2023 were about 1.8 €/L, Berlin is about 30 km in size, so of a typical 10€ trip, the fuel will cost about 4€ per trip.

Which means that a customer would pay about 6€/trip for the car itself. Dividing the monthly cost of owning a ccar by this value, we get 350/6 = 58, or a threshold of about 2 trips a day. If a person does less than 2 trips a day (weekends included), owning a car becomes less profitable than using carsharing, in 2023 prices.

Now, on the other hand, according to our rough estimations from Chapter 2, a remote station becomes profitable once it reaches about 10 trips/day (although this assumes that trips are a poisson process, and not a daily commute)

It means that for desynchronized occasional commuters (those running random chores and getting to appointments), and assuming that some back-up transportation options (or our entire premise of less-than 100% DFR would shutter), a group of some 10 households switching to car-sharing would be a win-win (profitable) for both the carsharing provider and the customers. Putting things into perspective, 10 households is about 2-3 smaller than a typical middle-density residential building, and some 10 times smaller than a typical high-density building, meaning that from the purely financial perspective (putting the status consideration aside), and assuming irregular commute, in the long-term _every_ residential area of every city is a viable target for carsharing.

What happens if we want to cover regular commutes as well? If the customers commute for work, leaving the car inactive during the day, the car-sharing company would have  to charge them a bit more: the cost of a car (and as before, let us assume 20€ per day), plus the variable cost (about 5€ by 2 trips), so 30€/day. As we agreed that the default price in our sample city is about 10€ per trip, it means putting a 10€ drop-fee on this hub. Which, on one hand, is a huge drop-fee, but on the other hand, let's again run the profitability analysis for the household itself. With 30€ per working day in a carsharing scenario, and 350€/mo in the ownership scenario, it's more profitable for a working person not to own a car, if they commute less than 350/30 $\approx$ 12 times a month, which corresponds to working hybrid, with 3 days in the office. It is a rather specific requirement of course, but it is not on heard of, and is only likely to become more common in the future. In other words, remote hybrid work promotes car-sharing, as opposed to car ownership, by de-synchronizing car usage, reducing idle times, making car sharing options cheaper, and more competitive, compared to car ownership [^Wan2024].

The fact that all our earlier calculations rely on the possibility to keep DFR below 100%, and also that irregular  carsharing is way more profitable than regular car-sharing, both have strong implications for urbanism and urban mobility. Namely, that carsharing should not and cannot be seen as an alternative to public transportation, but more as an offer that completements it, catching odd and unprecitable mobility use cases. Carsharing in a modern city can only be successful if most of the regular, predictable commutes are covered by public transportatoin, and so city dwellers are very close to giving up on a car, and only need these remaining 10-5% of their use cases to be covered. From my first-hand experience in mobility, I can attest that it is also very noticeable on the city level: the profitability of an area correlates most strongly not with the population density, or socioeconomic status of this population, but with the reliability and availability of public transportation in the area.

🔥 It also means that it is the municipality.. _explain how policies, such as the limitation of parking spaces, are most critical, and so after programmers, data scientists, and operations, our imaginary company shoudl really invest in people supporting long-term relationships with municipalities, as ultimately it is the health of these relationships that defines whether a given city (and thus, also the company operating in this cities!) would make it financially in the long-term.

# References

[^Wan2024]:  Wan, L., & Chen, J. (2024). Flexible working and the future of urban mobility: a novel conceptual framework. In _Pandemic Recovery?_ (pp. 265-281). Edward Elgar Publishing.