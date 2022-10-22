+++
category = ["Research"]
date = "2022-10-21T21:53:59.012139"
description = "I attended my first High Performance Transaction Systems conference, here are my messy inaccurate notes."
draft = false
enable_lightbox = false
tag = ["distributedsystems"]
thumbnail = "asilomar.jpeg"
title = "Notes from HPTS 2022"
type = "post"
+++

![A grassy walkway leading to a red shingled building on the Asilomar Conference Grounds](asilomar.jpeg)

I attended my first [High Performance Transaction Systems (HPTS)](http://www.hpts.ws/agenda.html) conference last week. Here are my notes on the talks. Please don't quote or trust me; these notes are based on what I heard, frantically typed, and minimally polished later. I have certainly misunderstood a lot, especially in areas outside my expertise. And even if I heard them correctly, treat researchers' claims skeptically!

{{< toc >}}

# Intro

## Keynote: HPTS Comes Full Circle - [James Hamilton](https://perspectives.mvdirona.com) (Amazon)

High performance transaction systems began on purpose-built hardware. Then we used horizontally scaled clusters of commodity servers. Now, systems span datacenters for scale and reliability, and once again providers are purpose-building hardware.

Starting in the late 90s systems reached a scale where "fault avoidance" doesn't scale, need "fault tolerance". In 2001 at HPTS, Bell & Dalzell presented "Obidos", an Amazon page rendering engine, a disastrously buggy and monolithic piece of software. Leaked memory so fast it required restart every 100-200 requests. (Comment from audience: really sometimes every 10 requests.) Someone called it "morally bankrupt software engineering" but Hamilton loved it. Example of reliable system built on highly unreliable parts. (But also one of the reasons Amazon went to Service Oriented Architecture (SOA) early!)

In 2005 Stonebraker presented "One Size Fits All: An Idea Whose Time Has Come And Gone". There were only 3 commercially relevant DBs at the time, Stonebraker says apps could be 10x faster with more specialized DBs appropriate to each app. But you must remove the admin overhead of many kinds of DBs, which cloud providers do. Now AWS offers 13 DBs.

In 2009 Barroso & Hilde presented "The Datacenter As Computer". Web search exceeds single cluster scale, then cloud computing exceeds web search. Apps span DCs for reliability, scaling, & latency. If you have two DCs you waste 50% capacity to ensure enough cap when a DC fails. But with 3 DCs you only waste 1/3. These days with advanced erasure coding and many DCs it's possible to ensure failover with very little spare capacity.

Now AWS makes lots of specialized kinds of servers. The uninterruptible power supply (UPS) is the flakiest component, so Hamilton proposed making an Amazon custom UPS. They use lots of small ones to minimize blast radius: each serves about 20 servers. They made more reliable UPSes by making them smaller and simpler, and iterating faster than when they bought them from suppliers. Also slightly cheaper than suppliers. They make custom switches, NICs, and CPUs. They also run their own power plants.

AI drives hardware specialization now. ML parameter counts were growing 2x per year until recently, now 10x. GPT-3 has 175 billion params. Tiny optimizations make a huge difference in training times. [EC2 p4de instance](https://aws.amazon.com/about-aws/whats-new/2022/05/amazon-ec2-p4de-gpu-instances-ml-training-hpc/) is an "ML training monster" optimized for the job, with 55k cores per machine. A typical training run took 21 days with 240 of these instances, 13m cores and several megawatts. Shaving some resources from such jobs would mean big savings. Hamilton says there's a great investment opportunity in making better ML hardware.

Hamilton thinks Amazon, Google, MS, and Ali Baba have the scale now to make significant amounts of custom HW, in the future it may be 10s of companies at most.

## 30 Students In 30 Minutes

[Jack Waudby hosts a CS research podcast called Disseminate](https://podcasts.apple.com/us/podcast/disseminate-the-computer-science-research-podcast/id1631350873).

# Scale (But Done Right), chair: Camille Fournier

## Dynamo At 15: What Worked And What's Next In Majority Quorum Databases - Scott Andreas (contributor, Apache Cassandra)

This talk was prepared before [Amazon published their own Dynamo retrospective](https://www.usenix.org/system/files/atc22-elhemali.pdf).

Dynamo original: a KV store, not a DB. Leaderless, incremental scalability, simple API, prioritize availability & latency. Sacrifice query language, transactions, indexes, MVCC, or even a storage engine (using pluggable storage). Sparked a discussion about "what is a DB?" Popularized non-relational and other "exotic" DB flavors.

Cassandra was co-authored by a Dynamo author, but at Facebook. LSM storage, majority quorum architecture. Shares with Dynamo many ideas like consistent hashing. Cassandra is for high scale, low latency, geo distribution. Now has strong consistency and linearizable transactions.

What worked: 

* Leaderless: avoids waiting for a distant / overloaded primary, localizes faults, avoids bottlenecks.
* Majority quorum: permits more flexible deployment topologies, you don't need electable nodes in special places. "Fault-domain-aware planning enables 99.9999% availability."

According to "[innovator's dilemma](https://en.wikipedia.org/wiki/The_Innovator%27s_Dilemma)" a disruptor like Cassandra starts as a cheap alternative in some niche, then adds features to compete with more expensive incumbents. Cassandra has added a query language, strong consistency, single key transactions, new storage engines, etc. There was a gap in feature development 2018-2022 when it "became a DB" by improving quality:

* Lots of property based testing.
* "Simulation: deterministic execution via managed executors / mutexes." (We discussed this after the conference, he linked me to the [proposal](https://lists.apache.org/thread/7gpfjd2zl94jrvnwvdkm0vbrob9qf172) and [Jira](https://issues.apache.org/jira/browse/CASSANDRA-16921) for further reading.)
* "Rethinking deprecation: lose features, lose users."
* "Linearizability is table stakes for modern applications."

Distributed transactions are coming to Cassandra, transact over any subset of the data, optional strict serializability. They wrote [Accord for leaderless transactions](https://is.gd/cassandra_accord). Obviously once they have transactions, it unlocks all sorts of things: consistent materialized views, enforced foreign key constraints, transactional changes to DB state....

## Who's Afraid Of Distributed Transactions? - Chuck Carman (Amazon)

Carman describes consensus view of "scale agnostic architecture" (what Carman doesn't believe in anymore): 

* Follow patterns that scale, only do small things and partition small things by key.
* Know your business and design for it, design for "right now", make copies of data to avoid slow pages.
* Apps need to scale, not DBs.

This talk is about Amazon's SABLE DB. It has a basic DB-like API. It contains customer transaction data (carts, orders), source data (merchants, offers, products), and intermediate aggregated data. A given Amazon product detail web page might query SABLE a hundred times.

SABLE prioritizes speed over correctness, "right now is more important than right". It has small plentiful entities, everything is partitioned to maximize local operations. All writes are "publishes" in a pub sub architecture? Every published message includes a partition key to allow parallel processing. Messages trigger serverless functions, which can be arranged into complex pipelines including fan-in and fan-out. Functions execute small localized consistent transactions, but the system as a whole is eventually consistent?

So SABLE isn't a DB, it's an "application engine" or "environment". Carman doesn't believe in distributed DBs as an API for users anymore, he believes in higher level data apis for users, which may be backed by a DB as an implementation detail.

What he believes now:

* High performance is specialization, business dictates what kind of correctness is required.
* For high performance data, build an application engine. Don't worry about generality, scale the business's specific logic.

(I'm not clear how this contradicts the "scale agnostic architecture" above, but it's interesting regardless.)

## Evolution Of The Spanner Storage Engine - David F. Bacon (Google)

Nearly all of Google's products run on Spanner, as well as their internal control plane. He notes that since the System R paper, top data sizes grew by 11 orders of magnitude, QPS by 7 orders. (Audience comment: "the data's getting colder!") 

Spanner in 2014:

* Colossus FS holds SSTable files
* SSTable: sorted string tables, held in an LSM?
* Not yet SQL, [became a SQL system ~2017](https://research.google.com/pubs/archive/46103.pdf)

This talk is about a new storage engine, "Ressi". They did a live migration of basically all of Google's data to Ressi over the course of 2 yrs 7 mos.

"Performance is a form of correctness": at Google's scale if an upgrade requires more of **any** kind of resource, it may cause an outage. How can we measure the impact of code changes on real data, quickly, at production scale, w/o risk to production, accurately, and preserving privacy?

They run experiments: transcode some data from old to new format, validate that it's uncorrupted, test performance. These experiments have no write access (thus no danger they'll corrupt prod), and they request resources at low priority (less danger of causing an outage, but somehow they get accurate performance numbers despite low priority). The experimental data obeys the same privacy rules as the source data, and experiment report has no private data, only aggregated. They can run experiments on 5-10% of all data over a few days. It sounds like their inability to look at customer data makes it hard to determine why an experiment gave negative results (e.g. new storage engine is bad at compressing some customer's data, but they can't look at it).

They basically can't handle writes in experiments now: they don't measure changes to write performance w/ this system, nor maintain consistency b/w old and new formats if there's concurrent writes during an experiment. Bacon proposes "meta synthetic" experiments that anonymize write data and replay it against new engine, wiping enough details to preserve privacy while retaining enough for a realistic experiment.

# Languages vs. Data, chair: Peter Alvaro

## Specifying Ourselves Out Of A Job - Margo Seltzer (The University Of British Columbia)

Program synthesis: specify a program's properties and use an SMT solver (Z3) to produce a conforming program ("counter example guided inductive synthesis", CEGIS, aka "guess and check"). Seltzer is involved in projects to synthesize an OS (which sounds foolhardy, and she described recent failures in this project), to synthesize IoT programs, to synthesize a compiler, to synthesize device drivers.

## Postmodern Systems And Datalog - Quinn Wilton (Fission)

"Dialog" is an edge-first DB, built of CRDTs. Each entity is a CRDT, plus lineage/causality data as a blockchain. These entities are called EAVC:

* Entity
* Attribute
* Value
* Causality

Each client involved can control its own data and other clients' access to it. A "global" view is eventually consistent? Or perhaps there's no authoritative single view? Wilton calls this a postmodern DB. A viewer can see the result of merging the EAVCs to which they've been granted access cryptographically.

The system is Byzantine fault tolerant. In response to a question, Wilton says this means an attacker can't introduce a causal cycle that can't be merged.

[DataLog](https://en.wikipedia.org/wiki/Datalog) (an old logic programming language) is the query language. More [details about Wilton's work here](https://slides.com/quinnwilton/deck-82cf38).

## A Data First, Hands-Free Distributed Programming Model - Achilles Benetopoulos (UCSC)

If you want to deploy a distributed algorithm using some existing framework like MapReduce or Spark, you have to map the app semantics to the mechanisms of the framework, usually short-lived computations over intermediate results. This is hard for most programmers.

Benetopoulos proposes two concepts:

* Object: some interrelated data that exists on exactly one machine
* Nanotransaction: a constrained data access mechanism

Both things are mobile, they can be shifted from machine to machine to bring compute to data or vice versa. Objects are immutable and have global refs to each other so they can be more easily moved. So all nanotransactions are on **local** data, which makes them easier to program correctly. We must ask users to factor their programs into "composable operations over local data". (I wonder, is this any different from the burden that MapReduce & friends impose on programmers?) In return he promises the runtime will do the right thing - maximize parallelism, minimize data movement, maintain correctness. "The runtime can peek into the application's semantics", I don't know how that works. Perhaps he explains by saying "each nanotransaction has a contract that communicates how it uses data." The framework would provide some CRDTs to the programmer as part of a standard library.

Benetopoulos shows examples of code that doesn't look distributed, but he claims they could be automatically distributed by a system like his proposal. So maybe users **don't** have to factor their programs into composable operations, the runtime automatically does it.

I think a common theme in research like this is, "Users somehow communicate their app semantic requirements to the runtime to permit automatic distribution with minimum coordination." But I haven't yet seen a great example of a syntax for users to do this&mdash;it should be something less error-prone than just writing Spark code yourself. Probably I just haven't been reading the right papers.

## Advanced Queries Over Programs - Anna Herlihy (EPFL)

(Formerly MongoDB; Anna and I worked together on MongoDB drivers.)

The amount of code in the world is growing exponentially, because there are more programmers, and because there's about to be much more machine-generated code. She proposes a "database of code", which can express static analyses as queries over volumes of code. E.g., a query could answer, "which functions have side effects?" "What type is X?" There are AI-based approaches but Herlihy doesn't think these are rigorous enough.

She proposes a far-future "CodeDB", which should be able to extract guarantees from a program without running it. She proposes to analyze code (in any language? in Scala specifically?) and transform it into Datalog "facts" about the program. Datalog has a query language over facts already. E.g. `is_reachable(x)`. The query language is composable, you can ask questions like "are all references to x in dead code?" So CodeDB would be built on Datalog capabilities. With CodeDB we could query programs for optimization opportunities, security vulnerabilities, etc.

# DB And OS: Back At It Again, chair: Justin Levandoski

## All RPCS Are Bad (At Least, By Themselves) - Daniel Bittman (UCSC)

RPCs are location-centric, call-by-value, require expensive serialization/deserialization (SerDe). Distributed shared memory (DSM) is an old idea that should be reconsidered.

Storage latency is getting faster (SSDs, NVMe) so we need fewer levels in the storage hierarchy? But that means OS and SerDe overhead for read/write persistent stores is **relatively** more expensive. In current OSes to read or write persistent data crosses many layers (app, std lib, kernel, device driver, ...), each layer has its quirks, and the app's intent/semantics get lost at various layers.

It would be better to operate directly on persistent data. Same story for RPCs - better to operate directly on distributed data instead of doing RPCs. We need something w/ the code mobility of RPC plus data mobility of DSM. A more flexible and effective method for decoupling in distributed computation.

Twizzler OS is a data centric OS. Provides global (cross machine) address space with invariant references (pointers are still valid after data moves). The OS knows (somehow) something about your app's data semantics so it can do smart things like pre-fetch.

Q: Data latency isn't uniformly improving, e.g. lots of systems still use spinning disks. Bittman: Twizzler OS should have enough info (provided by users, or other ways) to optimize data access in various situations.

Q: How can programmers deal with a distributed system, where every data access is potentially a network error, in a manner that hides these details and appears like a single machine? Bittman: hard problem!

## DBOS

### DBOS: A Database Oriented Operating System - Mike Stonebraker (MIT)

Aims for the same goals as Twizzler OS but Stonebraker claims it's further along in development.

The amount of state an OS must manage (CPUs, RAM, storage, threads, messages, files, etc.) has all grown by orders of magnitude since the 80s when most current system software was first built. Managing this state is naturally a DB problem, it should be managed transactionally using the new ideas in DBs. He proposes a new OS stack:

* Level 4: User programs
* Level 3: OS support routines written in SQL!
* Level 2: Distributed high availability in-memory SQL DB like VoltDB (his invention)
* Level 1: Microkernel: raw device support, low level memory management, minimum needed to run the DB and nothing else

His prototype uses VoltDB for level 2, uses Linux for the moment to simulate level 1. Replaces the "everything is a file" abstraction with "everything is a table".

Analytics, monitoring, HA are all much better/easier than current OSes. All OS operations are transactions. He claims it's fast enough, they implemented an FS, inter process communication (IPC), and schedulers on top of VoltDB. A scheduler is a SQL query for which process to run next. IPC is implemented as a table: sending a message is a SQL insert, reading a message is a SQL select followed by delete (in one transaction). Stonebraker claims FS performance is competitive with Linux (more overhead, so small ops are slower than Linux). IPC is competitive with gRPC.

He mentions VoltDB is "unbeatable" on single partition transactions but terrible at multi partition transactions, but this is being fixed. It now batches multi partition transactions and does them all at once, every few milliseconds, using special locking semantics. It's now apparently very fast at multi partition transactions too.

Security: DBOS would provide complete provenance for all OS state, and could restore to a previous state in seconds. You could monitor for bad events with SQL queries.

### The Design Of Apiary: A Programming Environment For DBOS - Peter Kraft (Stanford University)

DBOS's programming model should be FaaS. "Apiary tightly integrates function execution and data management. It wraps a distributed DBMS and executes functions transactionally as stored procedures." Avoids the usual re-execution problem of FaaS, devs don't need to make their functions idempotent. Guarantees exactly once. (Though in answer to a question, real-world side-effects like sending an email must still be somehow made idempotent.)

Automatic data provenance tracking for observability and security. All executions and data accesses are captured and stored to a log?! The overhead seems astronomical to me. I think that even if it's aggressively filtered, just deciding which events to capture would be expensive. But it would enable amazing time travel debugging. They show that Apiary outperforms some academic and open source FaaS systems like OpenWhisk, but I wonder if it could outperform AWS Lambda.

My thoughts: The DBOS proposals **seem** radical. "Ditch the OS, the DB is now the lowest-level software!" But perhaps they aren't radical. Let's start with the same objective they do: provide a distributed environment for running functions-as-a-service (FaaS). Naturally you'd use a distributed database to store state, e.g. the list of functions, the queue of tasks, the access control lists, billing info, etc. I'm sure all existing FaaS services depend on one or more distributed DBs. Thus the "scheduler" is naturally implemented as a DB query over the tasks table; this isn't radical. If you provide a distributed FS, then again it's natural to store FS metadata in a DB. Pretty soon you've built a system resembling DBOS, without the hype. The concept of DBOS is mostly a shift of perspective: Stonebraker & co. are pointing at a run-of-the-mill FaaS service and saying, "operating system." (Then they propose to replace Linux with a microkernel, but I don't see the purpose of that.)

### The Ultima Thule Of A DBMS Backed Operating System - Kostis Kaffes (Stanford University)

Prototype of bringing DBOS principles to Linux. Express fundamental OS operations, including **alterations** to state, as short SQL statements. Track provenance and log all events.

# Gong Show

## Firestore: NoSQL for Serverless

The "Be Real" app is an extreme use case for serverless. It notifies all users on a continent when it's "time to be real", and everyone uploads a photo within 2 minutes, causing a giant brief load spike. The app is backed by Firestore and proves that Firestore can handle this kind of spike. The local Firestore client caches to hide latency to the central DB. Good at offline workloads, syncs when online. Firestore uses Spanner for strong consistency etc. Provides notifications to subscriber apps for "continuous queries" for each mutation. Serverless, pay for what you use.

## Ballerina

An open source language for network services, from [wso2](https://wso2.com/). It's for integrating services together. It speaks many protocols. The IDE can auto-generate sequence diagrams from Ballerina programs.

## Building To Buy

From a Two Sigma engineer.

Build vs buy. No single answer to this dilemma. Once you've built you have to keep building to maintain your custom code. Once you buy you have to keep buying to scale up.

Two Sigma in 2005 needed distributed storage. S3 etc. weren't available yet, so they built their own, CelFS. In 2020 they could buy storage from the cloud, but their users have built to their CelFS API, **and** to their performance characteristics (they have lower latency than S3). Moral: once you build it's very difficult to migrate to off-the-shelf. (Sounds to me like [Hyrum's Law](https://www.hyrumslaw.com/), and I wonder if any farsighted providers slow down their APIs to preserve wiggle room.) 

## BigQuery

Google BigQuery was "serverless before serverless was a thing". Disaggregation of CPU, memory, and storage. Many features added over the years:

* Big Lake: query data lakes, supports many formats
* Big Query Omni: ship computation to data in **other** clouds, like to S3!

## Stop Fretting About Data Loss

Doug Terry of AWS.

Customers have gotten concerned about data loss lately, and there have been publicized AZ outages. Don't worry, AWS replicates data. But customers hate "RPO" (recovery point objective), data that hasn't been replicated yet. How to deal with RPO?

1. Live with it, especially for write heavy workloads
2. Reconcile it, with some merge algorithm
3. Prevent it, with synchronous replication, ensures zero RPO but adds latency

# Scale Session 2, chair: Randy Shoup

## Scaling Systems For Critical Infrastructure - Colin Breck (Tesla)

Tesla interacts with home battery banks using Kafka and Akka. It shares weather forecasts, energy market info, etc. from the central service to the homes. This enables California to request Tesla home batteries to charge in advance of a forecasted peak, then discharge during the peak to sell power back to the grid when it's needed most. Called the "Tesla Virtual Power Plant".

Making the grid smart opens new security vulnerabilities. Breck likes the [Consequence Driven Cyber Informed Engineering (CCE)](https://inl.gov/cce/) methodology for responding to this.

## Systems Architecture At Scale: The Unreasonable Effectiveness Of Simplicity - Randy Shoup

Large sites all start w/ monolithic apps and eventually become polyglot sets of microservices.

Simple principles for large scale systems:

**Simple components** - service boundaries match the problem domain, and encapsulate logic & data. No back doors to the data. Use stateless domain logic that's deterministic and testable in isolation. Use "straight line processing", single threaded, minimal branching. Teams and services split like cellular mitosis. Abstract out a common platform: shared infrastructure, standard frameworks, developer experience. "Large scale organizations invest more than 50% of engineering effort in platform capabilities."

**Simple interactions** - see the [Reactive Manifesto](https://www.reactivemanifesto.org/). Communicate state changes as a stream of events; the event driven model decouples domains & teams, enables simple event-processing components. Store state as an immutable log of events; this enables audit & replay. Compact old logs into snapshots. Embrace asynchrony; this decouples operations in time, e.g. services can interact even if some of them are temporarily unavailable. See [the Aurora paper](https://www.amazon.science/publications/amazon-aurora-design-considerations-for-high-throughput-cloud-native-relational-databases), [Netflix](https://www.infoq.com/articles/microservices-async-migration/), and [Walmart](https://videos.itrevolution.com/watch/485153969/).

**Simple changes** - he ran out of time.

## Snowflake Architecture: Scaling The Data Warehouse For The Cloud - Thierry Cruanes (Snowflake)

Snowflake Data Cloud was built to deal with modern data challenges: lots of machine-generated, semi-structured data; lots of people who want to use the data; demand for fast or real time analytics; many diverse data sources. Circa 2012 when they began, Snowflake expected an abundance of resources in the cloud: storage, compute, etc. would become very cheap and reliable. (Implication that this was over optimistic? I asked later and I think Cruanes said they've spent more time than they expected negotiating with cloud providers for resources and to ensure capacity.)

They wanted to build a dream system with unlimited & instant scaling, low cost, good for structured & semi-structured data, zero management, support ACID and SQL. Their architecture has centralized, scalable storage, and multiple independent compute clusters. Data is immutable, which simplifies many things, encourages caching, and permits instant cloning to create a dev or test environment. They use and integrate resources from AWS, GCP, and Azure.

They release weekly, worldwide, with a single version to maintain. (Must be nice.) "Virtuous cycle&mdash;data driven development to identify and prioritize feature development. Snowflake is extensively instrumented, we generate many terabytes of service data daily."

Their roadmap includes:

* Data warehouse: full SQL, ACID, UDFs, UDTs, data governance, stored procedures
* Data engineering: streaming ingest, external functions, data pipelines
* Data lake: semi structured data, unstructured data, external tables
* Data science: support Python dataframes, Java, Scala

They want to become a "data application platform" optimized for collaboration. Sharing raw data isn't enough, there must be access control and auditing, a way to execute trusted application code inside the Snowflake platform. Maybe they're also creating an app marketplace?

# Verification, Formal And Otherwise, chair: Marc Brooker

## Formal Modeling And Analysis Of Distributed Systems (Finding Critical Bugs Early!) - Ankush Desai (Amazon)

He's a senior applied scientist at AWS database systems (where my friend Murat Demirbas works too now).

"Formal methods: it's not just about the proofs, it's also about the process."

Lamport: "Coding is to programming what typing is to writing."

Formal methods aren't widely adopted in industry because

* Gap between design & implementation.
* Model & implementation go more out of sync over time.
* Model is hard to write because programmers think of distributed systems as communicating state machines, not a single state transition system as in TLA+.
* Model checking doesn't scale to the complexity of real world systems.

This talk is about [P](https://p-org.github.io/P/). A P program has [several parts](https://p-org.github.io/P/advanced/structureOfPProgram/): formal models "PSrc", specification "PSPec", and an environment or test harness "PTst". Claims to have a scalable model checker for large systems. Sounds more sophisticated than the TLA+ checker (TLC)?: it does symbolic execution (which is [experimental for TLA+](https://apalache.informal.systems/)), it does distributed model checking (which TLA+ supports, but I couldn't make it work). P specs are runtime monitors: state machines that track system history and assert global invariants. Specs are general programs just like models. Somehow they also check liveness, not just safety. PTst does "inputs and fault modeling".

[Case studies](https://p-org.github.io/P/casestudies/) for P.

Lessons learned: P is a good thinking tool early in design. Identifying the invariants is the most valuable part. It can find bugs through model checking. Boosts development velocity after initial investment in modeling.

Keeping model & implementation in sync: they've made trace checking work in both tests and production, [unlike me](https://dl.acm.org/doi/abs/10.14778/3397230.3397233).

## Jepsen XV: Unsafe At Any Speed - Kyle Kingsbury (Jepsen, LLC)

He tested a DB called Radix, distributed ledger for decentralized finance, a blockchain. It advertises high performance, 12 million TPS. Kingsbury finds they actually do more like 16 TPS! (Not 16 million: 16.) A single node fault makes latency increase 50x, because there's no fault detection and node eviction algorithm. He found hilarious consistency violations as usual, e.g. read uncommitted anomaly in 1/300 of reads of the public ledger. They fixed only some of the bugs he found.

He tested RedPanda, a distributed Kafka-compatible stream. It's Kafka but with Raft under the hood instead of Paxos. He found duplicate values, and values getting reordered in the log after commit. It sounds like he found bugs in both Kafka and RedPanda? RedPanda fixed all the bugs he found.

Conclusion: Jepsen keeps finding bugs in systems easily, we all need to be testing better. Transactions aren't just in SQL anymore, stream processing and blockchains have transaction-like things too. Kingsbury is trying to apply [Adya et. al.'s formalisms](https://pmg.csail.mit.edu/papers/icde00.pdf), we might need new formalisms to describe these things, and of course better documentation.

Q: How does he pick systems to test? A: He tests any system that someone pays him to test, but he rejects some clients e.g. environmentally damaging blockchains.

## Formal Methods Only Solve Half My Problems - Marc Brooker (Amazon)

He co-authored [the famous paper with Chris Newcombe et. al](https://lamport.azurewebsites.net/tla/formal-methods-amazon.pdf). Beyond TLA+ there's more going on at AWS:

* Using the Kani Rust verifier on the Firecracker hypervisor ([here](https://model-checking.github.io/kani-verifier-blog/2022/07/13/using-the-kani-rust-verifier-on-a-firecracker-example.html)?).
* See [lightweight formal methods](https://www.amazon.science/publications/using-lightweight-formal-methods-to-validate-a-key-value-storage-node-in-amazon-s3) paper.
* [Semantic-based Automated Reasoning for AWS Access Policies using SMT](https://www.cs.utexas.edu/users/hunt/FMCAD/FMCAD18/papers/paper3.pdf)

Brooker has come to think that safety & liveness aren't enough. Distributed systems are dynamical systems with feedback loops and emergent behaviors. We don't understand their dynamics. E.g. the AWS Lambda task scheduling system "eLSA". If there's a partial outage and they lose a lot of workers, there's lots of cold starts as new workers are added; eLSA tries to smooth this spike. Once upon a time, cold starts overwhelmed one of AWS's microservices, causing a retry storm that wedged Lambda until human intervention.

(I was reminded of "metastable failures", see [here](https://sigops.org/s/conferences/hotos/2021/papers/hotos21-s11-bronson.pdf) and [here](https://www.usenix.org/system/files/osdi22-huang-lexiang.pdf). As usual, the outage was caused by unintended interactions among mechanisms intended to make the system robust.)

Brooker says that diagnosing a particular outage like this is a "just so story" like "how the elephant got his trunk": it explains one event but doesn't teach how to avoid them in general. We need some formalism to reason about them. What about control theory? He says it can't handle complex distributed systems. He asks, "How do we understand system dynamics better? What research should we be doing?"

He proposes simulation: numerical simulators of stochastic control systems. Example: a single shard DB is overloaded, maybe it should split into two. Depending on workload, splitting could increase throughput, or have no effect (queries all become fan-out), or hurt throughput (more distributed transactions). He cites Watts & Strogatz 1998 [Collective dynamics of small-world networks](https://immorlica.com/socNet/watts-strogatz.pdf) as a way to model the system and predict the outcome.

Why build a simulator when we already have a spec in TLA+ or P? He proposes leveraging existing models by analyzing the state space for system dynamics (I didn't understand how). "Can we get more value from specs?"

Conclusion: distributed systems are dynamical systems, and we don't understand their dynamics. The resiliency mechanisms we add make them more complex, producing more emergent behavior that we don't understand. This is a problem. "We're not going to grow up until we solve it."

# Data Governance, Security, And Privacy: Computing With Seat Belts, chair: Jennie Rogers

## Toward Building Deletion Compliant Data Systems - Subhadeep Sarkar (Boston University)

Many systems now use "out of place" updates: not in-place updates, instead they just log the changes. Instead of deleting, log a tombstone. Merge lazily. But this doesn't handle delete-heavy workloads well. When there are lots of tombstones it hurts read performance badly. Delete-heavy workloads are in fact common, e.g.:

* Orphan cleanup after internal DB operations.
* GDPR and other privacy laws require timely, unrecoverable deletes.
* An auditing DB that deletes data after 30 days must delete 1/30 of its data daily.

Sarkar's research group envisions designing DBs from the start to be good at deletion.

Two kinds of regulatory requirements for **hard** deletes:

* Delete data within x days of a request for deletion
* Delete data that is more than x days old

Sarkar proposes new SQL operators to use with `DELETE` to specify the exact hard-delete requirements the DB must obey.

He described how to hard delete efficiently in an LSM tree. Today to hard delete from LSM is easy **if** your delete key is the same as your sort key. Otherwise you have to compact the whole tree to one level, which is very costly. [KiWi, part of a system called Lethe](https://cs-people.bu.edu/dstara/pdfs/Lethe.pdf), is his new data format that accelerates LSM compaction after hard deleting. It arranges data in a hybrid structure that uses both the sort key and the delete key.

## Towards Regulating Large Scale Multi Enterprise Environments With Privacy Guarantees - Mohammad Javad Amiri (University of Pennsylvania)

Mutually distrustful entities sometimes want to collaborate. He presented at VLDB 2019 [CAPER: A Cross-Application Permissioned Blockchain](https://www.vldb.org/pvldb/vol12/p1385-amiri.pdf) which does cross-firm transactions. Now he presents [Qanaat: A Scalable Multi-Enterprise Permissioned Blockchain System with Confidentiality Guarantees](https://arxiv.org/pdf/2107.10836.pdf), which handles cross-firm transactions where some collaborations are confidential to a subset of the firms involved.

Qanaat is Byzantine fault tolerant, it handles the case where some nodes are malicious. It uses quorums to prevent corruption, and firewalls to prevent malicious nodes from exfiltrating confidential data. Amiri said something like, "a malicious node can either read private data or talk to the client but not both", but I didn't understand the details.

Use case: Let's say Uber, Lyft, etc. want to collaborate to prevent drivers from working >40 hrs/wk total for all rideshare firms, for regulatory reasons. We want to protect each driver's privacy, Uber can't know if a driver also works for Lyft. Yet the regulation enforcement should be verifiable by the government.

Amiri et. al. have a [vision for regulated multi enterprise systems](https://arxiv.org/pdf/2005.01038.pdf). In this system, participants reserve crypto "tokens" distributed by an authority, the tokens represent e.g. hours of work. Participants and firms can request tokens, spend them, verify they've been spent, etc., while limiting who can see what data.

## Authenticated Concurrent Databases - Suyash Gupta (University of California, Berkeley)

Byzantine fault tolerance (BFT) is expensive, requires 3f+1 nodes to tolerate f faulty/malicious nodes. What about trusted computing (e.g. Intel [SGX](https://en.wikipedia.org/wiki/Software_Guard_Extensions) and trusted enclaves)? Led to "trusted BFT protocols" that assumes each node has a trusted component, which "attests" (signs?) each message. Requires only 2f+1 nodes. The client awaits acknowledgment from f+1 nodes. Gupta claims to have found 3 limitations to trusted BFT.

1. Loss of responsiveness. If one honest node hangs, the protocol hangs.
2. Trusted components can experience rollback, which leads to safety violation. Those that don't rollback are very slow.
3. No parallelism, can't run consensus on 2 transactions at once. (I guess you must wait for several rounds of messages for txn 1 to finish before txn 2 can start.)

[Flexi trust](https://arxiv.org/pdf/2202.01354.pdf) is a new suite of protocols that guarantee liveness, responsiveness, safety. This requires 3f+1 nodes again, and requires trusted hardware. But it only accesses the trusted component once per machine per transaction, which enables parallelism.

## Privacy Preserving Systems - Johes Bater (Tufts University)

Use case: several hospitals want to pool their aggregate statistics about patients so 3rd-party researchers can run analyses on the whole. "We want to ensure privacy while maintaining utility." Ordinarily you'd add noise to each hospital's data during export, but the noise compounds as you add more hospitals, degrading the final accuracy.

The solution is a "private data federation". The building blocks are differential privacy (DP, add noise in order to anonymize data), secure multiparty computation (MPC, aka encrypted computation). There are quantifiable privacy / accuracy / performance tradeoffs between these approaches, his system optimizes the tradeoffs automatically to produce fast, reasonably private and reasonably accurate results with simple knobs. "Greater than the sum of its parts."

# Making Hardware Work For Data, chair: Rebecca Taft

## How To Kill Two Birds With One Stone - Matteo Interlandi (Microsoft)

There are >4k ML+AI papers uploaded to arXiv a month now. Neural net sizes are growing exponentially. Huge amounts of AI hardware is being built. PyTorch is becoming a standard, and it has optimizations for all this AI hardware.

[Interlandi's project](https://arxiv.org/abs/2203.01877) compiles SQL to the popular "tensor" abstraction and runs it with PyTorch, to use all the PyTorch optimizations (e.g. GPUs), not for ML/AI but for transaction processing (or perhaps it's for analytics?). Given specialized hardware it can be very fast.

Future direction: "AI-centric DB". It would allow you to use SQL queries to access AI algorithms, e.g. `SELECT * FROM images WHERE image_similiarity("KFC receipt") > 10`, if you have a pretrained "KFC receipt" recognizer.

## Transparent Data Transformation - Manos Athanassoulis (Boston University)

"How to stop worrying about data layouts". How to have benefits of both row store and column store? [Athanassoulis's vision](https://www.bu.edu/rhcollab/projects/software-hardware/near-data-data-transformation/): "relational memory". He proposes keeping data in RAM, row-oriented, plus custom hardware that transforms it to a group of selected columns on the fly. The columns are stored in L2 cache on access. The custom hardware is called a relational memory engine (RME). He claims it's fast because it's so low level, it can exploit parallelism in the data bus, and it can pre-fetch.

There exists "programmable logic in the middle" tech today, which sits between CPU and RAM, it can implement an RME now.

Writes to columns hit the column-oriented cache first and eventually the row-oriented source data in RAM. He adds MVCC to the RME, to track which data is valid/invalid.

Doesn't work if the data is compressed in RAM. Of course it's ok if it's compressed on disk. Doesn't work with variable length columns?

## Mach: Breaking The Cpu Speed Barrier With In Flight Data Processing - Alberto Lerner (eXascale Infolab -- University of Fribourg, Switzerland)

CPU performance is now doubling only every **20** years. Lerner proposes to push DB processing to peripheral chips, e.g. the SSD controller, NIC, memory controller, etc. He cites a bunch of papers doing this already. E.g. he made "DB Annihilator" which generates a DB test workload directly from an FPGA attached to the network. "Harmonia" directs readonly transactions to sufficiently caught up secondaries, with all the logic in network hardware. "P4DB" serves indexes directly from the NIC.

Programmable devices are becoming more available and easier to use for non experts. SSD controllers now support eBPF (oddly&mdash;it was originally a packet filter language but apparently very flexible). This is all exciting because networks are getting faster, so are hard drive data buses, they will increasingly overwhelm CPUs unless we push more processing into the middle-layer specialized chips.

## Flash Based GPU Accelerated Queries - Hamish Nicholson (EPFL)

There used to be a clear storage hierarchy, but now it's an anarchy: NVMe is almost as cheap as SSDs and almost as fast as RAM, so there's overlap between the cost/perf of persistent and volatile storage. GPUs and CPUs have different speeds and strengths, and the buses between the various media and various chips have different speeds. Data can flow along a number of different paths with different advantages. The simple old heuristics like LRU caches aren't optimal now, it depends on each query's workload and the hardware's capabilities. Query planners must take into account the possible paths among various storage media and GPUs and CPUs.
