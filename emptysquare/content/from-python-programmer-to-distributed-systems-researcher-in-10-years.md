+++
category = ["Programming"]
date = "2025-06-30T22:29:35.390204"
description = "How I wound up on MongoDB's research team."
draft = false
enable_lightbox = true
tag = ["distributedsystems"]
thumbnail = "cliff.png"
title = "From Python Programmer to Distributed Systems Researcher in 10 Years Without a PhD"
type = "post"
+++

Phil Eaton wrote "[From Web Developer To Database Developer In 10 Years](https://notes.eatonphil.com/2025-02-15-from-web-developer-to-database-developer-in-10-years.html)" recently. I was inspired to write my own version.

***

In high school, I wanted to be a modern dancer, with a company like [Pilobolus](https://pilobolus.org/) or [Streb](https://streb.org/company/). But I also kind of wanted to be a programmer. Pixar's Toy Story, the first 3D-animated feature film, was released when I was a high school sophomore. I was fascinated by this simulated world, revealed by simulated light to a simulated camera. How did they make it? I somehow learned (however I learned things before I had Internet access) that 3D graphics were rendered with linear algebra and C++. So I got books about both from my neighborhood library in Shaker Heights, Ohio. I don't recall much about the linear algebra book, but the C++ book is a core memory: a giant glossy volume, with a copy of Borland Turbo C++ for DOS on a CD in a slip attached to the inside back cover. I installed it on the family computer, a Tandy with a 386 processor, which looked like this:

![](tandy.png)

When I installed Turbo C++, the IDE looked like this:

![](turbo-c.png)

I taught myself basic C++, but on my own I didn't manage to learn 3D graphics.

Meanwhile, I reached my senior year of high school, and auditioned for the prestigious dance program at Ohio State University. I was admitted to the waitlist, but that was a superficial victory. I saw in that audition another man my age who was a true dancer. He was unselfconscious, emotional, natural, free. I would never dance like that. By the time I got a letter from OSU, saying I'd been accepted from the waitlist, I'd already decided to major in computer science and do 3D graphics for a living.

(Is this what really happened? It's been 28 years. This is how I remember and tell my life story now.)

I got my CS degree from Oberlin College with a focus on 3D graphics. For some reason I didn't apply to Pixar. Why didn't you follow your dream, young Jesse? I ended up in Austin, Texas, working for a tiny company that made flight safety analysis software. At least I was doing 3D graphics: our software turned data from jets' [flight recorders](https://en.wikipedia.org/wiki/Quick_access_recorder) into 3D animations, so airlines could review near-accidents and adjust their procedures.

Let's fast-forward. I bounced around from [a Zen monastery](/yokoji-zmc-august-2019/) to [an NYC education startup](https://en.wikipedia.org/wiki/Amplify_(company)), then freelanced for a few years, and joined MongoDB in 2011 ("10gen" at the time). I'd abandoned 3D graphics by now. I'd learned Python, and I used MongoDB at one of my freelance gigs&mdash;it was so much more fun than SQL, I thought the idea might have legs. MongoDB was unique in NYC at the time: the only company building technically demanding open-source software in the city. Google and Amazon hadn't yet opened offices here. MongoDB hired me as a developer advocate promoting MongoDB to the Python community. They called me a "Python evangelist"&mdash;my mom loved the title, she said it sounded like I was a snake handler.

![](snake-handling.png)

_[Handling serpents at the Pentecostal Church of God](https://en.wikipedia.org/wiki/File:Handling_serpents_at_the_Pentecostal_Church_of_God._(Kentucky)_by_Russell_Lee._-_NARA_-_541335.jpg), by Russell Lee_.

I made myself a minor celebrity in the Python world, speaking at PyCon many years in a row and publishing a lot of popular Python content on this blog. But mostly I was an engineer. I worked on [PyMongo](https://pymongo.readthedocs.io/), I created the async alternative Python driver [Motor](https://motor.readthedocs.io/), and for a while I led development of our [C](https://mongoc.org/) and [C++](https://www.mongodb.com/docs/languages/cpp/) drivers. I was promoted a few times, to Staff Engineer. [After 7 years on the Drivers Team, I hit a plateau](/choosing-the-adventurous-route-video/)&mdash;my learning had slowed and I didn't know how to get another promotion. So I decided to switch teams. I rotated through three MongoDB teams, trying each one for a month or two, until I settled on the Replication Team, which maintains MongoDB's consensus protocol, deep in the core database server.

The Replication Team transformed my career, because they read and wrote research papers about distributed systems. Before, I had deepened my knowledge by studying programming languages. Now, I was learning about much higher-level concepts: consensus, fault tolerance, causality, isolation and consistency. The team met regularly to read papers in our field, both new and old. I got excited and read more papers on my own, and joined [an external distributed systems reading group](https://charap.co/category/reading-group/). I also met TLA+ for the first time. With two colleagues, I published [my first research paper](/mongodb-conformance-checking/), about testing the conformance between TLA+ specifications and implementations. (I'm still researching this topic, 5 years later.) I made a plan to read dozens papers and a few textbooks; my boss and grandboss agreed that if I completed the curriculum I'd designed for myself, I'd be promoted to Senior Staff Engineer, and soon enough this actually happened.

![](cliff.png)

[In 2022 I took most of a year off to climb](/after-244-days-off/), and moved to New Paltz, [a world class climbing mecca](https://portfolio.emptysqua.re/rock-climbing). While I was away, I considered my reentry. How could I contribute best to MongoDB? And how could I keep my calendar clear of team standups and planning meetings and all the other cruft that would prevent me from running out to the cliff when the weather was good? MongoDB had a small research group, almost entirely in Australia at the time, led by [Michael Cahill](https://scholar.google.com/citations?user=9-arDNQAAAAJ&hl=en). I asked to join it when I returned, working four days a week at four fifths of my previous salary, and Michael assented. I was gambling with my career: I only had a BA, I had only published one paper, and my primary mentor would be on the other side of the world. On the other hand, I could use the writing and speaking skills I'd learned as a "Python evangelist", and devote myself to the distributed systems theory I enjoyed. I returned to MongoDB in December 2022 as a Senior Staff Research Engineer.

How did I get this coveted position&mdash;the freedom of academia with an industrial salary? I didn't have an advanced degree, but I had some advantages. My previous boss supported my decision to transfer. I'd been at MongoDB for 11 years, a long time at any company, especially a fast-growing one like ours. The one paper I'd published was good, and accepted by a top conference. I'd not only read a lot of papers, I'd spread my knowledge by leading discussions of them in reading groups. And I came to Michael with ideas he liked, such as [predictive auto-scaling](/mongodb-predictive-scaling-experiment/) or improving the consistency of [MongoDB's secondary reads](https://www.mongodb.com/docs/manual/core/read-preference/). 

So that's the story: that's how I progressed from Python programmer to distributed systems researcher in ten years, without a PhD. Since then, a lot has happened. Michael Cahill retired soon after I joined the research group, and I was unmentored for a year. Luckily I was able to hire a famous expert, [Murat Demirbas](https://muratbuffalo.blogspot.com/), to lead [MongoDB's distributed systems research](https://www.mongodb.com/company/research/distributed-systems-research-group). I'm still finding my stride in my new career, but at least I have guidance.
