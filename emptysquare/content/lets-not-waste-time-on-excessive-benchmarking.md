+++
category = ["Research"]
date = "2026-08-17T13:01:08.689640+00:00"
description = "Database research papers keep adding benchmarks every year, crowding out fundamental new research: stats from analyzing 800 published papers."
draft = false
enable_lightbox = true
tag = []
thumbnail = "hollander-cranial-measurements.jpg"
title = "Let's Not Waste Time on Excessive Benchmarking"
type = "post"
+++

*Originally published on the [MongoDB Research Blog](https://www.mongodb.com/company/research/distributed-systems-research-group/lets-not-waste-time-on-excessive-benchmarking).*

{{% pic src="brixton-treadmill.jpg" alt="Nineteenth-century broadside illustration of prisoners at Brixton Prison walking a treadmill, with an overseer looking on" %}}
{{% /pic %}}

There's an arms race in database research. Every year, papers have more and more benchmarks. Researchers are spending more effort, writing more words, and making more charts about benchmarking. This has gone far past the point of diminishing returns: much of this work is wasted effort that takes time away from real discoveries.

I'm not criticizing the competition for the best benchmark *results*---that's a different problem. Rather, I'm criticizing the ever-growing *number of benchmarks* per paper. This one-upmanship is taking time away from fundamental research. It's time to get back to basics.

{{< subscribe >}}

## The evidence

I analyzed a sample of 828 papers from VLDB, SIGMOD, OSDI, SOSP, and NSDI, spanning 1999 to 2025, using Claude to extract each paper's evaluation-section size, the benchmarks it ran, the number of performance figures, and the number of baseline systems it compared against. (More on the method below.) The trend is clear:

- Evaluation sections grew more than 40%. A quarter of a modern database paper is benchmark results.
- The average number of benchmarks per paper went from 1.8 to 4.
- The number of benchmark figures went from 2.8 to 7.
- The number of baseline systems compared against went from 1.4 to 4.1.

{{% pic src="trend_eval_words.svg" alt="Line chart of evaluation-section size in words from 1999 to 2025, trending upward" %}}
**Figure 1.** Evaluation sections keep growing. Size of evaluation sections in words, 1999--2025. The line is the mean (±standard error) per five-year period; the shaded band spans the 25th--75th percentile of papers.
{{% /pic %}}

{{% pic src="trend_total_benchmarks.svg" alt="Line chart of benchmarks per paper from 1999 to 2025, trending upward" %}}
**Figure 2.** Benchmarks per paper have more than doubled. The median paper had one benchmark in 1999--2000. Today the median is three, as many as a 75th-percentile paper back then.
{{% /pic %}}

{{% pic src="trend_baselines.svg" alt="Line chart of baseline systems compared against per paper from 1999 to 2025, trending upward" %}}
**Figure 3.** Papers compare against ever more baseline systems. Comparing to one alternative used to be normal; now four is typical.
{{% /pic %}}

Every year the bar rises. To publish in 2025, you must run more benchmarks against more baselines and include more charts than the 2024 papers did---and next year's authors will have to beat you.

## Much of this benchmarking is pseudoscience

I know: we want to do real science, and real science means experiments and numeric results. But quantity isn't rigor. A lot of our benchmarks aren't measuring anything useful.

{{% pic src="hollander-cranial-measurements.jpg" alt="Two photographs c. 1902 of the phrenologist Bernard Hollander measuring his own head, in profile with a tape measure and head-on with calipers" %}}
{{% /pic %}}

**Closed-loop benchmarks.** [The standard benchmarks are closed loop](https://emptysqua.re/blog/ycsb-is-obsolete/): a fixed number of client threads issue requests in a tight loop, each waiting for one response before sending the next request. Real-world traffic doesn't behave this way---real clients arrive independently and keep arriving whether or not the system is keeping up. That's why real systems experience overload and closed-loop benchmarks don't. Schroeder, Wierman, and Harchol-Balter warned about this in "[Open Versus Closed: A Cautionary Tale](https://www.usenix.org/legacy/event/nsdi06/tech/full_papers/schroeder/schroeder.pdf)": open- and closed-loop workloads get wildly different behavior from the same system. We've known this for two decades. We keep using the same closed-loop benchmarks anyway, because reviewers demand them.

**Unrepresentative workloads.** YCSB, the TPC family, and their kin are some past person's guess about what a representative workload looks like. They aren't recordings of real-world workloads, and papers rarely validate that a system's score on a standard benchmark predicts its performance in the intended application. We optimize for the benchmark because the benchmark is what reviewers check. YCSB has various knobs and options for tuning the workload, which is the worst of both worlds: it's not a consistent standard, but it *also* doesn't match real workloads. TPC is more rigid in theory, but in practice it is never implemented exactly the same twice.

**System-dependent results.** Benchmark results measure an implementation, not an idea. If you implement two algorithms in C++ and yours wins, that doesn't tell me which will win when I implement them in my system, in my language, with my storage engine. Mytkowicz et al. showed that factors as irrelevant as link order and environment-variable size can flip experimental conclusions ("[Producing Wrong Data Without Doing Anything Obviously Wrong!](https://dl.acm.org/doi/10.1145/1508284.1508275)"). And Raasveldt et al. describe how easily benchmarks mislead, by accident or design ("[Fair Benchmarking Considered Difficult](https://dl.acm.org/doi/10.1145/3209950.3209955)"). If your algorithm is a real breakthrough, that will be self-evident in the analysis. You won't need four benchmarks to prove it.

{{% pic src="benchmark_popularity.svg" alt="Bar chart of standard benchmark popularity, led by TPC-H, TPC-C, and YCSB" %}}
**Figure 4.** TPC and YCSB dominate the standard benchmarks. Two thirds of papers that use standard benchmarks use TPC or YCSB, closed-loop workloads designed decades ago.
{{% /pic %}}

## Why the ratchet only tightens

Reviewers are busy, and they often review papers outside their expertise. I've been on the program committee for several conferences and I know how hard it is. Too often, reviewers don't take the time to understand the substance of a paper, or they don't have the background; nevertheless they want to show their peers that they're making an effort, or they want to be hard on the authors. Top conferences have to be selective---VLDB and SIGMOD both reject about three quarters of submissions---so reviewers need some reason to eliminate most papers. The easy critique is, "You didn't do enough benchmarks." Reviewers reflexively ask for YCSB or TPC, or to compare against more systems. Only a very brave author says no.

Each year's papers spend a bit more effort and column inches on benchmarking, and that raises the bar for next year's papers. In the long run, our whole community's attention is increasingly focused on benchmarking. Benchmarks are clickbait: they grab reviewers' attention, whether or not they measure anything meaningful. The predictable result is that researchers go for safe, incremental improvements that look good on standard benchmarks, instead of bold ideas that open new lines of inquiry.

## Back to basics

We shouldn't abandon benchmarking. But let's think more carefully about the quality of our experiments and whether they are fit to purpose. In most cases we should prefer an open-loop latency-versus-throughput curve that shows behavior under overload, rather than a closed-loop measure of raw throughput like YCSB or TPC. We should reward realism over quantity: One trace from a real deployment is worth more than several synthetic benchmarks. When we're serving on program committees, we should ask for only a few high-quality experiments, and we should intervene when we see other reviewers pointlessly demanding more benchmarks. As authors, we should stand up to reviewers and explain why a few good benchmarks suffice.

Would a new standard benchmark suite solve the problem? Without a cultural shift, I doubt that it would. After all, YCSB was introduced in 2010 with the noble goal of fairly comparing NoSQL systems, but despite its flaws (closed-loop, unrealistic workloads) it's remained the dominant standard long past its usefulness. Any new standard might be an improvement for now, but it would quickly turn into a zombie, exactly like YCSB did. So long as reviewers ask for irrelevant benchmarks because they are "the standard," or because "more benchmarks are better," we'll be compelled to run too many benchmarks.

The real battle is to find new discoveries, go on eccentric quests, and ask questions that open whole new fields of research. Great performance breakthroughs are *asymptotic* improvements, not incremental. Futuristic systems solve problems no standard benchmarks measure yet. Let's quit ratcheting up the number of benchmarks and refocus on advancing the actual state of the art.

{{% pic src="pentonville-treadmill.jpg" alt="Photograph of prisoners at Pentonville Prison standing in a row on a treadmill, each in a separate stall" %}}
The treadmill at Pentonville Prison.
{{% /pic %}}

## Appendix: How I measured benchmarking

I scraped paper metadata from [DBLP](https://dblp.org/) for VLDB, SIGMOD, OSDI, SOSP, and NSDI in six year-pairs (1999-00, 2004-05, 2009-10, 2014-15, 2019-20, 2024-25), paired to balance the biennial conferences. I sampled one fifth of papers per venue-year. I used Claude Sonnet 4.5 to determine whether each paper is mostly about *database* research or some other topic. This yielded 828 database papers. Coverage is high for all five venues except pre-2004 OSDI and a handful of pre-2005 ACM papers with no digital-library PDFs. Sonnet measured word count, evaluation-section size in words, number of benchmarks and baselines, number of benchmark charts, and which standard or custom benchmarks were used.

## References

- Bianca Schroeder, Adam Wierman, Mor Harchol-Balter. "Open Versus Closed: A Cautionary Tale." NSDI 2006.
- Mark Raasveldt, Pedro Holanda, Tim Gubner, Hannes Mühleisen. "Fair Benchmarking Considered Difficult: Common Pitfalls In Database Performance Testing." DBTEST 2018.
- Todd Mytkowicz, Amer Diwan, Matthias Hauswirth, Peter F. Sweeney. "Producing Wrong Data Without Doing Anything Obviously Wrong!" ASPLOS 2009.

## Images

- [Treadmill at Brixton Prison in London, c. 1817](https://commons.wikimedia.org/wiki/File:Treadmill_at_Brixton_Prison_in_London_(cropped).jpg).
- The phrenologist Bernard Hollander illustrating with his own head his system of cranial measurements, 1902 ([profile](https://wellcomecollection.org/works/sqjvypsb/images?id=jhz7mcfn), [front](https://wellcomecollection.org/works/sqjvypsb/images?id=thgf4bpt)).
- [Pentonville Prison treadmill](https://commons.wikimedia.org/wiki/File:Pentonville_Prison_Treadmill_1895.jpg).
