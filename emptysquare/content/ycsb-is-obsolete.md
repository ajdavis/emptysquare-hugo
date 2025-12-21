+++
category = ["Research"]
date = "2025-12-21T17:44:18.975579+00:00"
description = "Closed loop benchmarks are too polite, they don't push systems past their limits."
draft = false
enable_lightbox = true
tag = ["distributedsystems"]
thumbnail = "open-loop-coffeeshop.png"
title = "YCSB Is Obsolete, We Need New Benchmarks"
type = "post"
+++

Let's build a simulation of a coffeeshop. We'll have some resources, like baristas and espresso machines. As soon as the shop opens, a fixed number of patrons&mdash;maybe ten&mdash;all line up for coffee. Whenever a patron receives her coffee, she throws it away and instantly returns to the back of the line. If the barista is slow, that's okay: the line never grows longer than ten people.

{{< figure src="closed-loop-coffeeshop.svg" caption="A closed loop coffeeshop." alt="A stick figure drawing. Nine people stand in line to get coffee. A barista stands behind the counter. A tenth figure is tossing its cup in the trash and returning to the back of the line." >}}

Oh, that's not realistic, you say? You say that patrons arrive at random times, join the line, and leave when they get their coffee?

{{< figure src="open-loop-coffeeshop.svg" caption="An open loop coffeeshop." alt="A stick figure drawing. Four people stand in line to get coffee. A barista stands behind the counter. Four figures are arriving from several directions and joining the back of the line. Two figures are leaving in different directions, holding coffee cups." >}}

I agree, that is a better model of a coffeeshop. As you have guessed, the coffeeshop is a metaphor, and my actual topic is cloud databases. In the cloud, there's no fixed number of clients. New requests are mostly triggered by external events, not by the completion of previous requests. If the database can't keep up, requests continue to arrive and pile up or time out. But standard benchmarks like YCSB or TPC assume the first model, the unrealistic one, so they give unrealistic results.

# The Difference Between Open and Closed

The first model is an example of a "closed system model" or a "closed loop": there is a fixed number of outstanding tasks. Once the database server is saturated, a new task won't arrive until one of the outstanding tasks finishes. The second is an "open system model" or "open loop": new tasks arrive whenever they want to, independent of when outstanding tasks finish. In an open system, the interarrival time between tasks is usually randomly distributed. If the distribution is exponential, then the arrivals are a [Poisson process](https://ocw.mit.edu/courses/6-262-discrete-stochastic-processes-spring-2011/3a19ce0e02d0008877351bfa24f3716a_MIT6_262S11_chap02.pdf).  

The real world is open, but we stubbornly keep using closed loop benchmarks to test our databases!

A closed loop benchmark generates load like this:

```python
def client_func():
    for _ in range(OPERATION_COUNT):
        start = time()
        response = do_database_request()
        end = time()
        record_latency(end - start)
        sleep(INTERARRIVAL)

threads = [Thread(target=client_func) for _ in range(THREAD_COUNT)]
for t in threads:
    t.start()
for t in threads:
    t.join()
```

The latency of `do_database_request` affects how much load the benchmark generates&mdash;the database implicitly exerts backpressure. The longer requests take, the longer the time between requests.

An open loop benchmark generates load like this:

```python
def one_operation():
    start = time()
    do_database_request()
    end = time()
    record_latency(end - start)

for _ in range(OPERATION_COUNT):
    Thread(target=one_operation, daemon=True).start()
    sleep(INTERARRIVAL)
```

This code starts a new request whenever the interarrival time has passed, no matter how many requests are still outstanding. For a Poisson process, you just make the interarrival time exponentially distributed:

```python {hl_lines=[3]}
LAMBDA = 1000.0  # ops per second
next_time = time()
for _ in range(OPERATION_COUNT):
    next_time += random.expovariate(LAMBDA)
    Thread(target=one_operation, daemon=True).start()
    time.sleep(max(0, next_time - time()))
```

Is this any harder to code than the closed loop version? In 2025 we are all familiar with [multithreaded](/why-should-async-get-all-the-love/) or (better in this case) async programming, we can build open loop benchmarks easily. The time has come for us all to switch to open loop benchmarks.

# Years Of Warnings Ignored

In the 2006 paper [Open Versus Closed: A Cautionary Tale](https://www.usenix.org/conference/nsdi-06/open-versus-closed-cautionary-tale), some researchers (including [Mor Harchol-Balter](/review-queue-theory-book/)) benchmarked a Postgres server with TPC-W, the web commerce benchmark that's part of the [TPC suite](https://en.wikipedia.org/wiki/Transaction_Processing_Performance_Council). Like all the TPC benchmarks, TPC-W is closed loop, but the researchers also made a version that's open loop. They compared the standard TPC-W results with their open loop version:

{{< figure src="closed-versus-open.png" alt="Two charts with load on the horizontal axis and mean response time on the vertical axis. The left chart is labeled closed system. Mean response time never rises over 2 seconds. The right is labeled open system. Mean response time rises to 8 seconds." >}}

The closed loop benchmark can never overload the database, because it has a fixed number of threads that each wait politely for the database to respond before sending the next request. Mean response time never exceeds 2 seconds. The open loop benchmark is rude: it overwhelms the database, unfinished requests pile up and wait in the queue. Mean response time exceeds 6 seconds. This is the kind of realistic data we need to see when we test our databases, but the standard closed loop TPC won't show it to us.

(The PELJF, PS, and PESJF lines are for different scheduling algorithms&mdash;that's an interesting part of the paper, you should read it. [Or read Murat's summary](https://muratbuffalo.blogspot.com/2023/05/open-versus-closed-cautionary-tale.html).)

The authors list eight insightful principles about the behavior of closed and open systems. The very first is, "For a given load, mean response times are significantly lower in closed systems than in open systems." In other words, TPC is lying about cloud database performance.

This paper should've set the world on fire, but years passed and we all kept creating and using closed loop benchmarks. [The Yahoo! Cloud Serving Benchmark was released in 2010](https://dl.acm.org/doi/10.1145/1807128.1807152). It was a great innovation because, unlike the TPC family, it targeted the new generation of distributed key-value stores. Unfortunately, you guessed it: YCSB is a closed loop benchmark.

[Gil Tene coined the term "coordinated omission" around 2012](https://qconsf.com/sf2012/dl/qcon-sanfran-2012/slides/GilTene_HowNotToMeasureLatency.pdf). It describes how closed loop benchmarks interact with the systems they're testing to avoid measuring their behavior during overload. He said it's "a conspiracy we're all a part of."

In 2017, some University of Hamburg researchers published [Coordinated Omission in NoSQL Database Benchmarking](https://dl.gi.de/items/780bef9a-d6df-4776-80e3-e85ae0158e63), criticizing YCSB and introducing their own open loop benchmark, NoSQLMark. They point out that YCSB tried to fix the problem in 2015, but the fix is a flawed hack that doesn't really make YCSB a reliable benchmark. (See the paper for details, or just trust me&mdash;it's a flawed hack.) The authors' NoSQLMark does the obvious right thing: it uses an async framework, Akka. Requests' start times are independent of their latency, just like in the real world.

The NoSQLMark paper uses a slightly weird methodology: they try to demonstrate their benchmark's accuracy using a partially simulated database called SickStore, which doesn't fully prove NoSQLMark's value in my opinion. But they also benchmark Cassandra with both YCSB and NoSQLMark and show how the results differ. This is _actual science_ and we should all emulate it.  

In 2024&mdash;look, I know you're getting sad and tired. I'm sorry. I'm getting sad and tired too. We're almost done. [In 2024 some researchers announced KVBench](https://dl.acm.org/doi/10.1145/3662165.3662765). This solved one problem with YCSB: it doesn't generate diverse workloads, like a mix of point and range queries, queries with empty results, or deletes. KVBench is a good contribution, but once again, it's a closed loop. It can't push a database past its limits. 

Aside from research papers, some widely read bloggers have warned about coordinated omission. [Ivan Prisyazhynyy wrote about it in 2021 on the ScyllaDB blog](https://www.scylladb.com/2021/04/22/on-coordinated-omission/). In 2023, my colleague Murat Demirbas [reviewed the Cautionary Tale paper](https://muratbuffalo.blogspot.com/2023/05/open-versus-closed-cautionary-tale.html). This year, [Marc Brooker wrote](https://brooker.co.za/blog/2025/05/20/icpe.html) that "most cloud systems are open, most benchmarks are closed." He says that closed loop benchmarks are far too kind to systems: they reduce their load automatically when the system slows down. "The real world isn’t that kind to systems. In most cases, if you slow down, you just have more work to be done later."

# It's Time To Take A Stand

{{< figure src="joan-of-arc.jpg" caption="Joan of Arc by Edward Corbould, 1890" alt="Engraving of a woman in armor, holding a sword and banner, leading an army" >}}

Why do we persist in using closed loop benchmarks, even though their inaccuracy is now well-understood, and open loop alternatives exist, and async frameworks make new ones easy to write?

It reminds me of [Barbara Tuchman's diagnosis of self-defeating nations](https://www.goodreads.com/quotes/10244414-wooden-headedness-the-source-of-self-deception-is-a-factor-that-plays):

> Wooden-headedness, the source of self-deception, is a factor that plays a remarkably large role in government. It consists in assessing a situation in terms of preconceived fixed notions while ignoring or rejecting any contrary signs. It is acting according to wish while not allowing oneself to be deflected by the facts.

Part of the problem is when peer reviewers, out of habit, ask authors to use closed loop benchmarks. A few months ago I took a small risk. My colleagues and I had submitted our paper about [a Raft enhancement](/leaseguard-raft-leader-leases-done-right/) to a major conference, and one of the reviewers asked for some more benchmarks. They suggested YCSB or KVBench. We said "sure"&mdash;we wanted to publish the paper, and the reviewers have the final say. But then we reflected on these years of warnings about closed loop benchmarks, and we noticed that YCSB and KVBench are closed, and we changed our minds. I wrote a custom open loop benchmark in C++ using nonblocking I/O. When we submitted our revision, I explained why we didn't follow the revision plan. The sky didn't fall. Our revision was accepted, and it was better because it used an accurate benchmark.

I understand why reviewers ask for YCSB or KVBench or TPC, despite those benchmarks' inaccuracy: they're the only baseline we have. Researchers want to do science, and using established benchmarks is part of that. But established benchmarks don't promote scientific progress if they're wrong. The solution is to create new baselines with open loop benchmarks. There are a few good candidates. NoSQLMark is a natural successor to YCSB: it's the same thing but open loop. [Lancet](https://www.usenix.org/conference/atc19/presentation/kogias-lancet) is an interesting research project to measure the open loop tail latency of very fast systems, using clever sampling techniques. And someone should make a standard open loop version of the TPC suite, if that doesn't exist already.

Let's start a movement. As authors let's stop using closed-loop benchmarks, and as reviewers let's stop asking for them. Let's pledge that from now on, we will use open loop benchmarks to test cloud databases.
