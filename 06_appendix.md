# Appendix: Default values and parameters

In most models of this project we assumed the same set of simplified values for financial parameters of the model, namely:

* A CM2 cost of having a car in a carsharing fleet of 20 €/day
* A typical brutto revenue of a single rental of 10 €/trip, and a CM1 profit of 5 €/trip
* A relocation cost of 20 €/relocation

Below are a series of back-of-the-envelope calculations that justify these rough assumptions.

### CM2 costs of operating a car

To estimate the costs of owning and operating a carsharing car let's look into two electric vehicles that were popular in Europe in 2024: Renault Zoe and Volkswagen ID.3.

| Model                                                                                     | Renault Zoe | Volkswagen ID.3 |
|-------------------------------------------------------------------------------------------|-------------|-----------------|
| Purchase price, Eur                                                                       | 27000       | 30000           |
| Sell-in price after 2 years (60% of purchase cost), Eur                                   | 16200       | 18000           |
| Carsharing-specific equipment (telematics, security), rough guess for a 2-year lease, Eur | 2000        | 2000            |
| Subtotal: Daily amortization (car + equpiment) over 2 years, Eur/day                      | 17.53       | 19.18           |
| Insurance cost per year, Eur (guess)                                                      | 500         | 500             |
| Fixed (usage-independent) service & tune-up costs per year, Eur (guess)                   | 500         | 500             |
| Total: Cost of opearation, Eur/day                                                        | 20.27       | 21.92           |

For both cars we arrive at similar amounts of about **20 €/day in fixed CM2 costs** of owning (or leasing) a vehicle, so this is value that was assumed everywhere in this project. We have not included the parking costs in this estimation, even though parking costs are often negotiated with the city, and are paid per vehicle (are not based on actuals), thus making it count towards CM2. Let's assume that the city is modern, that it is trying to reduce car ownership, and so encourages carsharing. We also used a rather generous assumption for the sell-in price after 2 years of heavy usage. On the other hand, we used market estimations for the prices of both cars, while car-sharing operators may negotiate better, bulk prices, or may even be business-offshoots of a car manufacturer. With all of this in mind, 20 €/day feels like a reasonable estimation.

### Typical CM1 per rental

The average revenue brought by a single car rental is of course very fluid: it depends on the city, the car model, current pricing situation, the season, the weather, the part of the city, on whether the city government had recently negotiated good salaries with the local public transportation union, and many other parameters. At the same time, it's nice to have a very rough number to play with, so let's make some simplifying assumptions. Let's assume that a typical rental brings the user from one part of the city to another, and lasts for about 20-30 minutes, covering about 10-15 km of distance. Let's also assume that the customer picks the best carsharing provider for their use case[^calculator]. With these assumptions, **a typical trip would cost a user about 10 €**.

Calculating the amount of CM1 profit coming from this brutto revenue of 10€/trip is a bit trickier. As it is described in the Introduction section, we need to estimate the key costs proportional to car usage that are involved in car sharing.

Unlike for gasoline-driven cars, electric vehicles are surprisingly effective in city conditions, as they don't punish drivers for constant stops and accelerations inevitable in a modern city. A typical cost of electricity for a single trip for these cars won't exceed 1€.

| Model                                                   | Renault Zoe | Volkswagen ID.3 |
|---------------------------------------------------------|-------------|-----------------|
| Electricity consumption during city driving, kWh/100 km | 15          | 10              |
| Trip distance, km                                       | 15          | 15              |
| Electricity price, Eur/ kWh                             | 0.3         | 0.3             |
| Electricity cost per rental, Eur/trip                   | 0.7         | 0.5             |

The cost of electricity is however not the most important cost factor that is proportional to car use. One of the major psychological barriers that make people prefer car ownership to car sharing, despite car sharing being typically way cheaper for a city family, is the feeling that shared cars are "unclean", as they were previously used by unfamiliar people. Because of that, it is crucial to regularly clean shared cars, based both on their use (after a fixed number of rentals after the previous cleaning), and in response to complaints from users. A typical cleaning would take about 2 hours (30 min to get to the car, 30 min to drive it to a garage, 30 min to clean it, 30 min to deliver it back to the city and move on to another car). Assuming a hourly wage of 20 €/hour typical for general labor in Germany, it results in 40€ in pure human-power costs. A few more € would be spent on chemicals, consumables, equipment amortization and electricity. Assuming that we perform a cleaning every 20 rentals or so, we can amortize it to about 2-3€ per rental.

Another important cost that is proportional to car usage is the cost of "anonymous damages" that have to be repaired. Somewhat counter-intuitively, it is small damages that may often cost more to a car sharing business, as larger damages typically have a clear reason (starting from the user at whose rental they happened), and so can often be billed to a third-party (or the user), and be reimbursed. Small damages however can rarely be tracked to an "offender", and accumulate, until they have to be repaired. Let's assume a minor non-reimbursable (and uncovered by insurance) repair of 100€ every 100 rentals, resulting in 1€ per rental.

Finally, every now and then users have issues with a rental, that they are trying to resolve by calling the support service. These include technical problems, problems with the app, questions about ending a rental, questions about prices and payment etc. We should therefore assume that call center costs are proportional to usage, and include them in CM1 costs. A typical call lasts for about 10 minutes, which assuming 30k€ salary and 240 working days a year results with 3 €/call in salary alone. Assuming flexible staffing, 10 minutes waiting time, and 30% shrinkage we can use Erlang's C formula[^erlang] to calculate the inefficiency of a call center, and arrive at effective personnel costs of about 6 €/call. Renting space and equipment will bring the amortized cost to 10-20 €/call, even if the call center activity is outsourced to one of the cheaper regions. Assuming that calls happen in every 10th to 20th rental, we can budget up to 1 €/trip to support the call center.

Going through these costs, we arrive at about 5 €/trip in CM1 costs, or, comparing with the brutto revenue of about 10 €/ trip, to a **typical CM1 profit of 5€ per trip**. For a smooth, well-optimized operator this estimation can of course be driven further down, capturing not 50%, but up to 60-80% of the gross revenue, but it is a good starting point for our calculations.

Note that in all the calculations above we are only concerned with short-term rentals within the operating area. The long-term rentals bring in more revenue per rental, while typically having constant, or even lower CM1 costs, so they are more profitable on average. As mentioned previously, however, long-term rentals that originate and finish in the operating area of a carsharing operator constitute almost a different business that exists _on top_ of the main car-sharing business, and just happens to use the same infrastructure, and the same set of cars. It is really nice and helpful that long-term rentals exist, but they are not the main focus of this document.

For the "Gaussian City" simulator, in which trips of various distances are considered, we try to roughly follow the same typical value, and assume that 5€ is a CM1 profit from a 30 minute (15 km) trip. Revenues for other trips are scaled proportionally.

### Typical relocation cost

The calculation of a typical relocation cost is somewhat similar to the logic we sketched above for a cleaning service cost. To relocate a car, a person needs to get to it (which would take at least 30 minutes), and drive it to a new place (30 minutes), resulting in about 15 €/relocation in salary costs (assuming the rate for taxi drivers, which is slightly lower than that for general workers). In practice the logistics is a bit more complicated: typically a shuttle car with one driver and three "relocators" would arrive to place with too many cars; then 4 cars (the shuttle and three carsharing vehicles) will be driven to a "hot" place within the city, and then the shuttle would collect the drivers, and be ready for the next operation. Here we spent 4 human-hours (40 €) to relocate 3 cars, which, together with the electricity costs for all 4 cars and the amortization cost of the shuttle brings us to 20-25€ per relocation. In this work we generally assume **20 €/relocation**, which may be a bit optimistic.

# Footnotes

[^calculator]: See for example [https://carsharing.landozone.net/](https://carsharing.landozone.net/) developed by Bruno St-Jacques

[^erlang]: See [this worked example](https://www.callcentrehelper.com/erlang-c-formula-example-121281.htm), and this [online calculator](https://www.callcentretools.com/tools/erlang-calculator/)
