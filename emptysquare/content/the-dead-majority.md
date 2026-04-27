+++
category = ["Uncategorized"]
date = "2026-04-06T02:41:08.900365+00:00"
description = "For how much of history have the dead outnumbered the living, and by how much? And when does that change?"
draft = false
enable_lightbox = true
tag = []
thumbnail = "02-joseph-sattler-modern-dance-of-death-1894.jpg"
title = "The Dead Majority"
type = "post"
+++

{{% pic src="02-joseph-sattler-modern-dance-of-death-1894.jpg" alt="" /%}}

The Latin poet Petronius wrote that when we die, we [join the majority](https://en.wikipedia.org/wiki/Silent_majority#Euphemism_for_the_dead). Indeed, "silent majority" might have meant the population of the dead, before it referred to a mute political constituency. I just encountered this phrase in [a terrific Public Domain Review essay](https://publicdomainreview.org/essay/the-great-majority/), and I was curious: what has been the historical ratio of dead to living?

{{% pic src="dead-living.png" alt="Two stacked line charts from 10,000 BCE to 2100 CE with log-scaled axes. The top chart shows cumulative dead (black) climbing from about a billion to about 116 billion, and the living population (red) climbing from a few million to about 10 billion. The bottom chart shows the dead-per-living ratio, starting near 225 at 10,000 BCE, rising to a peak around 240 near 1000 CE, then crashing during the last two centuries to about 14 today and stabilizing near 11 by 2100." /%}}

For most of history, each living generation wasn't much larger than the previous, but the deceased kept piling up, so the dead's domination grew. It might have peaked in the Middle Ages at 240 dead for every living person, or perhaps it was even higher in the Bronze Age. It fell off a cliff during the [demographic transition](https://en.wikipedia.org/wiki/Demographic_transition). We're at 14:1 today, and might reach 11:1 by 2100. The living fraction of all humans ever born has been rising for two centuries, and it will keep rising as our lifespans increase. But I can't imagine it ever reaching 1:1, unless some future generation has 200 billion immortal babies.

{{% pic src="20-joseph-sattler-modern-dance-of-death-1894_900.jpg" alt="" /%}}

{{< subscribe >}}

# Sources

I let Claude run this analysis with light guidance.

**Cumulative births** are based on the Population Reference Bureau's estimate: [about 117 billion humans have ever been born](https://www.prb.org/articles/how-many-people-have-ever-lived-on-earth/). They divide human history into eras, estimate a population at the end of each era, and estimate an era-specific crude birth rate:

- 190,000 BCE --- 8,000 BCE: 80 births per 1,000 people per year
- 8,000 BCE --- 1 CE: 80/1,000
- 1 CE --- 1750: 60/1,000
- 1750 --- 1950: declining from 50 to 35
- 1950 --- present: declining from 32 to 17

[Ancient birth rates were high because life expectancy was low](https://acoup.blog/2025/07/18/collections-life-work-death-and-the-peasant-part-ii-starting-at-the-end/). Ancient people had a lot of babies, and a lot of them died, joining the silent majority.

**Living population** numbers come from [McEvedy & Jones](https://www.census.gov/data/tables/time-series/demo/international-programs/historical-est-worldpop.html) before 1950 and the UN's [World Population Prospects 2024](https://population.un.org/wpp/) after. Claude log-linearly interpolated between benchmark years.

**Future projections** come from the same UN source, medium variant: population peaks around 10.3 billion in the mid-2080s and drifts down to ~10.2 billion by 2100. Life expectancy rises from 73.3 today to 81.7. Global fertility, currently 2.25 children per woman, falls below replacement (2.1) by the late 2040s. If fertility falls faster than the UN medium variant (and it has been falling faster than expected) the future ratio drops faster. If longevity gains stall, dead accumulate faster and the ratio falls more slowly.

The wobbles in the lines are probably an artifact of how Claude distributed the Population Reference Bureau's era-total births within each era. I'm not an expert, and even experts can only guess population statistics before recent centuries.

# The Shrinking Majority

We're in an unusual era, when more than 7% of those ever born are still breathing. And compared to the dead---who mostly died young---those living today own more than 7% of humanity's time alive. G. K. Chesterton called tradition [the democracy of the dead](https://www.chesterton.org/democracy-of-the-dead/), because it was chosen by our ancestors. Perhaps our quickening rejecting of tradition is a rational consequence of the Quick Party's growing numbers. Our bloc will always be a minority, though. Once the demographic transition completes all over Earth, presumably birth rates and lifespans will stabilize and the Dead Party's constituency will begin to grow again. Who knows?

{{% pic src="05-joseph-sattler-modern-dance-of-death-1894.jpg" alt="" /%}}

***

* [Code for the chart](https://gist.github.com/ajdavis/73d7d5fb3fd39dd7c75e0ef59241c2d4).
* Images: [A Modern Dance of Death](https://50watts.com/A-Modern-Dance-of-Death).
