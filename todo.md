# Todo: Text 🔥

* Re-run and re-link existing operating area figures, to give them 3XX names (not 4XX)
* Write how everything is intentionally in notebooks, to minimize and expose the code, **except for the city simulation**. Which is based on all the same principles, and uses same formulas, but optimized for performance, and so hides some of this unnecessary complexity from the viewer. Conceptually, the only difference between the city simulation and simplified models presented so far is that in the city simulation travel is not instantaneous, but car are assumed to be traveling at a constant speed of 30 km/h.
* Mention that the simulation uses Gumbel-Max trick to vectorize Monte-Carlo operations (provide a ref), but that explaining the principles of this trick in detail is out of scope for this work.

# Todo: Notebooks

* Move pricing from one station notebook to a separate notebook

# Todo: Links to process

Optimal pricing and hybrid relocation in a free-floating carsharing system with battery swapping electric vehicles
https://www.sciencedirect.com/science/article/pii/S0968090X25002165

https://www.thirdlawreaction.com/are-ride-and-car-sharing-dying-out/
(from 2021 tho)

Car Sharing in Germany, 2018, a longer text
https://www.ecologic.eu/sites/default/files/publication/2019/2809-case-study-carsharing_final.pdf

Scale matters – Why the efficiency of free-floating vehicle sharing systems depends on the system’s scale (2025)
https://www.sciencedirect.com/science/article/pii/S0968090X25001731

Comparing Optimal Relocation Operations With Simulated
Relocation Policies in One-Way Carsharing Systems
https://dspace.mit.edu/bitstream/handle/1721.1/112401/2017_09_29_13_54_22.pdf?sequence=1&isAllowed=y

Carsharing business models in Germany: characteristics, success and future prospects (2017)
https://d-nb.info/1139610481/34

Analysis of business models for car sharing (2020)
https://stars-h2020.eu/wp-content/uploads/2019/06/STARS-D3.1.pdf

On the benefit of combining car rental and car sharing (2024)
https://www.econstor.eu/bitstream/10419/315426/1/11573_2024_Article_1204.pdf

CM1, CM2 etc.
https://cm3positive.com/ecommerce/guide-to-cm1-cm2-cm3-contribution-margins-must-know-if-you-work-in-e-commerce/
https://help.retentionx.com/hc/en-us/articles/15186937635868-Understanding-Contribution-Margins
https://blog.fabrichq.ai/a-guide-to-contribution-margin-what-it-is-how-to-calculate-it-and-why-its-importance-with-a-e46c2e113812

may be slop (but check)
https://moqo.de/post/who-benefits-from-carsharing

Car Sharing – An Overview of Benefits, Costs, and its Role in the Mobility
System of the Future
https://archives.marketing-trends-congress.com/2024/pages/PDF/85.pdf

Empirical analysis of free-floating carsharing usage: The Munich and Berlin case (2015)
https://danskedelebiler.dk/wp-content/uploads/2016/11/Empirical-analysis-of-free-floating-carsharing-usage.pdf

Enhancing carsharing pricing and operations through integrated choice models (2025)
https://www.sciencedirect.com/science/article/pii/S1366554525000341

https://www.sciencedirect.com/science/article/abs/pii/S0377221722009407
https://www.sciencedirect.com/science/article/abs/pii/S2213624X23001025
https://www.wiwi.uni-bonn.de/bgsepapers/boncrc/CRCTR224_2024_512.pdf
https://optimization-online.org/wp-content/uploads/2022/03/8848.pdf
https://www.sciencedirect.com/science/article/abs/pii/S0191261520304239
https://arxiv.org/html/2501.13843v1
https://liser.elsevierpure.com/en/publications/profit-and-utility-optimization-through-joint-dynamic-pricing-and
https://onlinelibrary.wiley.com/doi/10.1155/2023/6610624
https://athene-forschung.unibw.de/doc/112725/112725.pdf
https://www.sciencedirect.com/science/article/abs/pii/S0968090X99000212
https://www.sigmetrics.org/mama/2020/abstracts/Fricker.pdf

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