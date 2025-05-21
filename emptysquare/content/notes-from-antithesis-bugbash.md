+++
category = ["Programming"]
date = "2025-05-20T22:33:34.286237"
description = "A 2025 conference on autonomous testing and software correctness."
draft = false
enable_lightbox = true
tag = []
thumbnail = "image004.jpg"
title = "Jesse's Notes from the Antithesis BugBash Conference"
type = "post"
+++

![](image004.jpg)

Antithesis has pioneered "autonomous testing", a term they coined for their platform, which combines a [deterministic hypervisor](https://antithesis.com/blog/deterministic_hypervisor/) with coverage-guided fuzzing and fault injection. [My company MongoDB was one of their first customers](https://antithesis.com/case_studies/mongodb_productivity/)&mdash;I evaluated their platform for MongoDB in 2020. At the time we had several very rare replication bugs, including one that manifested once in many **years** of stress testing (tens of thousands of hours of compute), and Antithesis found them reliably in about 24 hours.

Antithesis was in quiet mode until mid-2024 when they suddenly turned on the marketing switch, started blogging, and announced the [BugBash](https://www.bugbash.antithesis.com/) conference. This is a small (about 200 attendees) conference with invited speakers (they accepted lightning talk proposals). MongoDB's distributed systems researcher Will Schultz gave a lightning talk on [Spectacle](https://github.com/will62794/spectacle), and our new Atlas Federation engineer Stephanie Wang gave a regular talk on lessons learned from her time building a cloud DB at MotherDuck.

The Antithesis CEO Will Wilson calls this "not a software testing conference, but a software *correctness* conference". Of course there was a fair amount of Antithesis marketing and education, but mostly the talks were about non-Antithesis software correctness topics.

![](image001.jpg)

# Talks

I attended almost all of the talks. Here are my notes from the ones I saw.

## Will Wilson

**Why is software buggy?** He's the Antithesis CEO. He offered various theories about why we tolerate bugs, including my favorite, "it's economically optimal to tolerate medium-quality software in most circumstances", and his own favorite, "software engineering is a young discipline whose major innovations in quality are yet to come&mdash;soon we hope".

![](image002.jpg)

## Zac Hatfield-Dodds

**Why is everything under-tested?** He's now at Anthropic, but he has a longer history as the author of the Python property-based testing library Hypothesis. I [covered his work](https://pyfound.blogspot.com/2020/05/property-based-testing-for-python.html) when I was a blogger for the Python Software Foundation. He described property-based testing and its advantages, and theorized that the main barrier to adoption is awareness and education. There has been a major uptick in Hypothesis usage recently.

Zac said something like, "coverage-guided fuzzing reduces the time to find a bug from exponential to polynomial". This sent me on [a side-quest, not yet completed, about the efficiency of randomized testing](/how-long-must-i-test/).

![](image003.jpg)

## Stephanie Wang

**Reliability lessons from building a cloud data warehouse from 0 to 1.** Stephanie was at MotherDuck until very recently, now at MongoDB on Atlas Data Federation. She described the challenges of layering a cloud DB on top of the DuckDB embedded columnar database.

![](image005.jpg)

## Ben Eggers

**You should test in prod.** This is like Netflix's "Chaos Engineering", though I guess that term is passé for obscure factional reasons. Eggers describes testing in prod at OpenAI: how to convince your manager, what to test, how to test it, how to do so safely. You should do it during waking hours, warn everyone ahead of time, and have a concrete hypothesis that you're testing. E.g., don't test "what happens when I take down this database?" Test, "I think when I take down this database that service X will go offline but service Y will stay up." 

![](image006.jpg)

## Kyle Kingsbury

**Jepsen 17: ACID jazz.** Standard Jepsen talk: he tested a few distributed services and found some interesting consistency violations. Extremely entertaining as always.

![](image007.jpg)

## Ryan Worl

**The Multi-Tenant Bill of Rights: observability for all.** An argument for investing in observability, with the twist that it helps "noisy neighbor" interference among tenants.

![](image008.jpg)

## Mitchell Hashimoto

**Can we test it? Yes, we can!** Hashimoto created Vagrant, Terraform, and other cloud infrastructure tech, now he's made a surprising pivot and develops a terminal emulator called Ghostty. He talked about refactoring code to make it unittestable and how to test GUIs.

![](image009.jpg)

## Lawrie Green

**Autonomous testing masterclass: How to succeed in software testing without really trying (or, a guide to autonomous testing).** Principles for using Antithesis. Don't test specific sequences of steps, test software *properties* and let Antithesis generate all the sequences. Properties can include "X is always true" or "never true" or "eventually true", or "a state is unreachable" or "a state is sometimes reachable".

I noticed that "always" and "eventually" are temporal operators in TLA+ (and other temporal logics) and they can be evaluated on a single *behavior* of a program. "Eventually" is a *liveness* property that in theory can only be evaluated on an infinitely-long behavior. But Antithesis lets you configure a test like, "once all fault-injection ceases, the system achieves state X before some timeout T". 

"Sometimes" and "unreachable" are [hyperproperties](https://www.hillelwayne.com/post/hyperproperties/) that must be evaluated on the *set of all possible behaviors*. They're not supported in TLA+. It's cool that Antithesis allows them.

![](image010.jpg)

## Ankush Desai

**Gain confidence in system correctness using formal and semi-formal methods.** Ankush talked about [P](https://p-org.github.io/P/whatisP/), his formal modeling language. Unlike TLA+, P has a very Pythonic syntax and an intuitive structure: communicating processes.

I think Ankush said that procedure bodies in P can actually be coded in Python, they don't just *look* like Python? Unclear.

P has two conformance-assurance features that interest me. 1) The docs say it can be compiled to C/C#/Java, but Ankush didn't mention this in his talk so maybe it's not fully implemented. 2) It supports trace-checking, you can add logging statements to your implementation and feed the logs to a trace-checking utility. I can't find any public mention of the trace-checking utility, though.

![](image011.jpg)

# Lightning talks

**Felicitas Pojtinger: Commoditize your CI compute.** She started with a nice idea from [Spolsky](https://www.joelonsoftware.com/2002/06/12/strategy-letter-v/): "Smart companies try to commoditize their products’ complements." She showed a technology from startup [Loophole](https://loopholelabs.io/) that makes cloud providers' spot instances an interchangeable commodity, by live-migrating onto and off of spot instances without losing state. You can have a long-running job jump from one spot instance to the next, across cloud providers, while maintaining TCP connections etc.

![](image012.jpg)

**William Schultz: Interactive formal specifications.** Will (MongoDB research) has renamed his tla-web tool to [Spectacle](https://github.com/will62794/spectacle), it's a partial implementation of TLA+ in JavaScript. You can interactively run a spec's actions forward and backward, choosing the next state at each transition and inspecting variables and visualizations, and share traces with your colleagues using a URL.

![](image013.jpg)

**Jayaprabhakar Kadarkarai: Modeling distributed systems.** "JP" has a new modeling language FizzBee. His language focuses on ease-of-use for engineers, which I agree is lacking in most other languages. He's made impressive progress developing solo for the last 2-3 years. FizzBee has a Pythonic syntax and a ton of features, like several builtin visualizations and interactivity, and a prototype of [probabilistic performance modeling](/are-we-serious-about-statistical-properties-tlaplus/).

![](image014.jpg)

**Marco Primi: The traveling anteater.** Entertaining talk about using Antithesis to "solve" the traveling salesman problem, just demonstrates that Antithesis is a heuristic tree-searcher.

![](image015.jpg)

# State of Reliability panel discussion

Five men with war stories, jokes, and conflicting opinions. One interesting idea: a goal of quality and testing is to reduce nondeterminism, but AI and ML are shifting us to a world where good software is legit nondeterministic. We'll have to develop a new testing philosophy.

![](image016.jpg)

# Evaluation

The conference organizers had an all-male speaker lineup when they first announced BugBash. They corrected this, but they still had no women on their panel. I complained about this, and I hope they do better next year.

I knew BugBash would be a relevant conference for me and the [MongoDB Distributed Systems Research Group](https://www.mongodb.com/company/research/distributed-systems-research-group), but it was far better and more relevant than I expected. Lots of people I know from distributed systems research and formal methods were there. I made useful connections with people, I learned valuable things, and I had some moments of inspiration that could become research projects.

![](image017.jpg)

***

Images by the sublime [Boris Artzybasheff](https://www.scaruffi.com/museums/artzybas/index.html).
