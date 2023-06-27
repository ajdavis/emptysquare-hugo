+++
category = ["Python"]
date = "2023-04-18T13:53:54.386617"
description = "My PyCon 2023 talk about using databases safely."
draft = false
enable_lightbox = true
tag = ["pycon"]
thumbnail = "Clv_PQeVAAAZOX4.jpg"
title = "Consistency and Isolation for Python Programmers"
type = "post"
+++

![Captain Kirk from Star Trek the original series. He's looking angrily at a computer, which is in the shape of a gray cylinder with a few lights, knobs, and antennae.](Clv_PQeVAAAZOX4.jpg)

<span style="color: gray; font-style: italic">Computers are infuriating.</span>

At PyCon 2023 I talked about consistency and isolation in databases, and showed [Python implementations of four isolation levels](https://github.com/ajdavis/consistency-isolation-pycon-2023). Here's [the PyCon video](https://www.youtube.com/watch?v=Y7WMav9fmUo&list=PL2Uw4_HvXqvY2zhJ9AMUa_Z6dtMGF3gtb) and [here's a Talk Python podcast interview](https://www.youtube.com/watch?v=FEcaG4_LY8E) with Michael Kennedy ([episode page](https://talkpython.fm/episodes/show/420/database-consistency-isolation-for-python-devs)).

The subject goes a bit deeper than I could cover in 30 minutes; here are links for further reading.

First, orient yourself with [Kyle "Aphyr" Kingsbury's map](https://jepsen.io/consistency).

# Isolation

## Basics

[Granularity of Locks in a Shared Data Base, Gray et. al. 1975](http://pages.cs.wisc.edu/~nil/764/Trans/13_P428.pdf), or the summary in the [Morning Paper part 1](https://blog.acolyer.org/2016/01/05/granularity-of-locks/) and [part 2](https://blog.acolyer.org/2016/01/06/degree-of-consistency/). This is the earliest paper I've read about isolation. It's fundamental.

[A Critique of ANSI SQL Isolation Levels, Berenson et. al. 1995](https://arxiv.org/pdf/cs/0701157.pdf), or the [Morning Paper](https://blog.acolyer.org/2016/02/24/a-critique-of-ansi-sql-isolation-levels/) summary.

## Advanced

[Generalized Isolation Level Definitions, Adya et. al. 2000](https://pmg.csail.mit.edu/papers/icde00.pdf), [Morning Paper](https://blog.acolyer.org/2016/02/25/generalized-isolation-level-definitions/).

Optional: [Seeing is Believing: A Client-Centric Specification of Database Isolation, Crooks et. al. 2017](https://www.cs.cornell.edu/lorenzo/papers/Crooks17Seeing.pdf), [Morning Paper](https://blog.acolyer.org/2020/11/30/seeing-is-believing/).

# Consistency

## Linearizability

[Linearizability: A Correctness Condition for Concurrent Objects, Herlihy & Wing 1990](http://cs.brown.edu/~mph/HerlihyW90/p463-herlihy.pdf).

[Linearizability versus Serializability on Peter Bailis's blog](http://www.bailis.org/blog/linearizability-versus-serializability/).

[Visualizing Linearizability, Michael Whittaker's blog](https://mwhittaker.github.io/blog/visualizing_linearizability/).

We often implement linearizability in a distributed system with a [consensus algorithm](https://en.wikipedia.org/wiki/Consensus_(computer_science)) such as [Paxos](https://en.wikipedia.org/wiki/Paxos_(computer_science)) or [Raft](https://raft.github.io/).

## Other consistency levels

[Morning Paper: Distributed Consistency and Session Anomalies](https://blog.acolyer.org/2016/02/26/distributed-consistency-and-session-anomalies/).

[MongoDB's "Read Concern" docs](https://www.mongodb.com/docs/manual/reference/read-concern/).
