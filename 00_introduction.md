# 00. Introduction

As I am writing this in 2025, the public image of carsharing is not particularly stellar. At first, during the cheap money era of 2010s, the field was plagued by provider oversaturation, with some markets having 4-5 providers operating in a space that could only support 1-2 competing networks at best (ref). This period was followed by a series of unproductive mergers and acquisitions (ref), chaotic market exists and entries (ref brussels?) and even some legal scandals (ref Miles). Combined with the change in political climate, where at least in some cities the quality of life was threatened by reactionary governments (ref Berlin, Canada), it created a narrative of distrust in carsharing as a business model. The stronger version of this narrative claims that free-floating carsharing simply cannot be profitable, that it is a dead-end, akin to other fads of 2010s. A weaker version claims that it could be, but that so far no single company managed to make it profitable.

The main reason for me writing this little summary is that as an advocate of car minimalism, and as a data scientist, I don't think that these statements are true! I believe that it is absolutely possible to build a profitable free-floating carsharing business, and that all the necessary parts for that to happen already exist on the market, although not necessaritly within a single company.

🔥 Then go section by section, what they contain, to promise a brief overview

# Legal notice

While ultimately most of my personal experience with carsharing stems from my tenure at SHARENOW, where I worked from August 2021 to January 2024, the entirety of this text, and all of the code in the associated Jupyter notebooks, was written by me in late 2024 – early 2025, long after my leaving the company. Moreover, to the best of my knowledge, and at least by the time of my last interactions with my former colleagues, neither SHARENOW nor Free2Move (the company that purchased SHARENOW it in 2023) based their operations on the principles described here.

This work presents my vision of how I would have set up a car-sharing business if I could start it from scratch now, at least as far as Data Science and Business Intelligence are concerned. I sincerely hope that it will be hepful for all mobility companies out there.

# Terminology

🔥KPI

🔥CM1, CM2

How can we best calculate CM1 in practice, either in a model, or while building dashboards and quickly estimating KPIs for a real city? It would of course be nice to track every cost in real time, and link it to a rental that triggered this cost, or to have a full "digital twin" of a city for modeling purposes, but this approach is too complex and demanding to be unrealistic. Moreover, not all usage-related costs can be easily linked to a single rental: it may be easier to do for fuel costs or customer support calls, but harder for cleanings triggered by customer complaints, or routine maintenance of a car.

If we think of this problem, the simplest practical solution would probably be to aggregate the actual costs of running a car-sharing business for a long period of time (say, about a month), and then allocate these costs to rentals based on distance driven. "Distance driven" is a simple and easily available proxy for "usage" or "good sold", as far as vehicle rentals are concerned, and CM1 is by definition "Revenues minus cost of goods sold". For more precise calculations one use a regression model to allocate CM1 based on more than one usage factor (maybe something like "fixed cost per rental + costs proportional to distance driven + costs proportional to time"), or use different regression coefficients for something subproducts in the portfolio (different car models, different cities, usage packages etc.). Yet for the sake of this document, in most cases, we will just assume that a certaion fixed share of revenues (about half of them) become our CM1 profits. In other words, we will assume that the per-km or per-minute price that we use to sell our services to customers is set in such a way that it offsets our running costs with about 100% margin.

In the text of this manual, I would sometimes refer to **CM1 costs** and **CM2 costs**, meaning variable (usage-linked) and fixed (fleet-linked) costs respectively. This may be not a standard usage, but it is short and unambiguous, so I hope it will be clear enough. When we talk about CM1 and CM2 profits, we mean the full value of the "Total" line for this calculation. When we talk about CM1 and CM2 _costs_, we mean the costs (negative) part of this calculation.

🔥Discuss the merits of CM1 (missed revenue) and CM2 (fleet costs) calculations. For short-term calculations that are concerned with the fate of the car in the next few hours, CM1 calculations based on alternative scenarios work better. For long-term calculations however we can afford to use CM2, and use the fixed cost of fleet (leasing, insurance, parking etc.) over time, which makes the calculations simpler. The assumption here is that in the short-term we can change what the car is doing, but we cannot change the number of cars in the city, so the cost of fleet can be considered constant, and taken out of the equation. For long-term, strategic decisions however we can assume that the fleet size will be corrected for the volume of business that we observe in the city, so (🔥 _finish this_ 

🔥List typical prices and values (20, 10, 5) for CM1 and CM2, and refer to 06_appendix for justification.

🔥Operating area

🔥Zones, Stations (the way we'll be using these terms in this document)

🔥DFR

# Acknowledgements

🔥

# TEMP cellar (ideas that may or may not happen)

🔥 What this thing is - conceptual models, but once math is agreed upon, "all" that is left is data management, model delivery and versioning, and data delivery infrastructure. This is not covered here.

# Footnotes

