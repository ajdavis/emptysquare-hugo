+++
type = "post"
title = "SIGMOD 2026 Recap"
description = "My notes from the database conference in Bangalore."
category = ["Programming"]
tag = []
draft = true
enable_lightbox = true
+++

Conference stats: 1000 total participants, 120 remote participants (Indian visa problems for Chinese people and others), 340 talks, 326 reviewers. A very large proportion of speakers were denied visas, mostly by India but occasionally other countries. (Some countries denied **exit** visas??) The organizers heroically reconfigured the conference over the last few weeks to permit hybrid sessions where necessary. Some talks were pre-recorded, or a second author presented the paper because the lead author couldn't get a visa. In the DBTest workshop a talk was presented by someone who wasn't an author at all, and one Chinese researcher sent an AI-generated video about his research using a fake American voice.  

{{< toc >}}

# Main conference

## Can AI assist in Mathematics and Computer Science research?

Prabhakar Raghavan, the Chief Technologist at Google.

The answer is "yes", he particularly describes an AlphaEvolve agent architecture for solving Erdos problems. It has many layers: an agent generates programs to solve the problem, another agent evaluates them, another agent evaluates the evaluations to make sure the agent isn't cheating! The best candidates are fed back to the LLM, which is told, "Make more of these." Reminiscent of Jeff Clune's series of papers like [Automated Design of Agentic Systems](/review-automated-design-of-agentic-systems/).

## AWS DevOps Agent

Sponsor talk, Mohammedfahim Pathan. Customers with very distributed apps with lots of microservices are complaining about increased time to resolve incidents. The AWS DevOps Agent is a service has subagents for root cause analysis, incidient triage, mitigation, etc. It's extensible through MCP servicers, it can be triggered via PagerDuty, webhooks, human prompts, etc.

The agent learns from experience: "Learns from investigation patterns, tool use, and topology. Builds skills based on team resolution  approaches." This seems interesting and vague in the talk. I grilled the speaker in Q&A (the session chair D. B. Phatak piled on when the speaker tried to dodge) and it sounds like no, the agent **doesn't** learn from experience, that slide was misleading. The agent has code search and other useful skills. The agent's knowledge and experience are somehow fed (via Kiro) to new-code development to prevent future outages from new code? Now I'm skeptical of that claim too.

## [PRISM: Navigating Cost-Accuracy Trade-offs for NL2SQL](https://dl.acm.org/doi/10.1145/3786679)

There's a standard natural language to SQL translation benchmark now. The authors evaluated some base models and inputs (more or less info about schema, data distribution stats, example result sets, etc.) and measured how good the results were vs. the dollar cost in LLM tokens. They have an ensemble strategy of generating many SQL candidates and actually executing them, then evaluating the query results with LLMs to decide which seems to match the NL query best.

## [Brook-2PL: Tolerating High Contention Workloads with A Deadlock-Free Two-Phase Locking Protocol](https://dl.acm.org/doi/10.1145/3769767)

Juncheng Fang (University of California, Irvine).

Static analysis eliminates deadlocks before transactions start, by doing static analysis of stored procedures. They represent txns as graphis with nodes that are either a locking node, operation node, or unlocking node, and edges can be ordering within a txn, or conflicts across txns. If they detect a deadlock-risking cycle, they can combine locking nodes together, or move a lock earlier in a txn, or notice when a conflict is actually commutative and not a real conflict. Aborts are now impossible, so do something called "partial transaction chopping" which I didn't understand. TODO CLAUDE: FILL IN. If there's a dynamic txn with unknown read/write sets, they use  a std deadlock detection and aborting protocol.

## [Sublime: Sublinear Error & Space for Unbounded Skewed Streams](https://dl.acm.org/doi/10.1145/3802116)

Niv Dayan (University of Toronto)

Common question about high-throughput streams: how often does each item appear? The 2005 algorithm "Count-Min Sketch" uses a fixed amount of RAM and has a bounded-error estimate of item frequency. This paper addresses problems with that data structure. Skew: common items' counts are estimated with too few bits, and uncommon items use too many bits. They use variable-length counters, with some bit-manipulation hacks to conserve space and CPU time. Stream growth: the error accumulates linearly with the number of stream items, so it grows over time. They start a new set of counters periodically, so error grows only as the sqrt of N instead of O(N). They allow other size-error tradeoffs too.

## [Focus! Fast On-disk Concurrency-control Using Sketches](https://dl.acm.org/doi/10.1145/3769793)

Alex Conway (Cornell Tech)

If a txn does a page fault while holding a lock, it's very slow (with 2PL). With OCC requires more metadata, like timestamps, which amplifies data size. If you want to do blind writes, checking and updating timestamps turns blind writes into read-modify-write ops. The goal of this paper is the best of 2PL and OCC: they separate timestamp storage from the concurrency control mechanism. Reduces metadata size of <1 MB. They use exact timestamps for hot keys, and "sketches" for the upper bound of timestamps of the cold keys, which might overestimate their timestamps and abort too many txns, but it's safe. 

## [Adaptive Sharding in Untrusted Environments](https://dl.acm.org/doi/10.1145/3769756)

Bhavana Mehta (University of Pennsylvania)

"Marlin: worikload-aware data placement with Byzantine fault tolerance". There exist static BFT sharding algorithms, but no dynamic sharding BFT algos. Nodes can lie about metrics, or they can disrupt data movement. There can't be a sharding coordinator, because it could be malicious, so re-sharding decisions need distributed agreement. It's important to re-shard and reduce cross-shard txns, because 2PC+BFT is very expensive. The paper has a horrifyingly complex decentralized resharding workflow that reduces cross-shard txns and tolerates some malicious nodes. It's much slower at resharding than a non-BFT equivalent, and requires a large quorum hence less fault-tolerant. There is a background monitor (also BFT?) that replaces crashed or malicious nodes.

## [Making LSM-Tree-based Key-Value Store Practical and Efficient for Multi-Tenant Serverless Cloud Databases](https://dl.acm.org/doi/10.1145/3786667)

Yingjia Wang (The Chinese University of Hong Kong)

LSM trees have synchronous foreground tasks: reads, WAL writes. And async background tasks: flushes, compactions. In serverless, the storage bandwidth is oversubscribed to save money, but there are still SLAs for tenants. Compaction can cause stalls. If you tune down the storage bandwidth during a quiet period and then the user load suddenly spikes, it can take 62s (in some experiment?) to bring bandwidth back up to meet load. Their solution is to reserve some always-available bandwidth for foreground tasks, even when idle, and scale the background tasks' bandwidth up and down with demand. I guess that by the time the LSM tree needs to flush, the bandwidth has scaled up to allow this. They somehow buy more time with tenant migrations, which I didn't understand: wouldn't migration cost even more bandwidth than LSM tree compaction? This has been integrated in Alibaba Tair ServerlessKV.

## [LeaseGuard: Raft Leases Done Right](https://dl.acm.org/doi/10.1145/3786663)

A. Jesse Jiryu Davis (MongoDB Research). [Read my blog](https://emptysqua.re/blog/leaseguard-raft-leader-leases-done-right/). Someone asked a good question: have we shown the protocol is correct during reconfig? Yes, Raft reconfig guarantees Leader Completeness, and that's what we rely on.

## [Predictive Translation: High-Performance Buffer Management Without the Trade-Offs](https://dl.acm.org/doi/10.1145/3786678)

Michael Zinsmeister (Technische Universität München)

Traditional database page buffers are basically hashtables. There are modern alternatives that are faster but they are very hardware-specific, not portable across OSes or CPU architectures. The authors want to make traditional, portable buffers faster by parallelizing hashtable lookup and page reading. They make page locations in RAM predictable, so the DB can speculatively read the page while simultaneously checking the hashtable to make sure the page is actually somewhere else. Cold pages are placed arbitrarily and often suffer mispredictions, but as they're accessed more often they're promoted to predictable positions. I asked whether this makes bad workloads worse, because all the cache misses are exacerbated by mispredictions. Zinsmeister replied that in that case I/O is the bottleneck anyway, so mispredictions don't make things worse.

## [**Scalable Leader Leases For Multi Consensus Groups in CockroachDB**](https://dl.acm.org/doi/abs/10.1145/3788853.3803081)

Ibrahim Kettaneh (Cockroach Labs)

Data is partitioned into ranges, each range has many replicas, which replicate with Raft. Each node has many ranges. A leaseholder is a distinguished replica in a range with a lease. In the past CRDB had "expiration leases" the leaseholder writes a record every 3 seconds to extend the lease, one per range. The range is unavailable after a leaseholder crash, until its lease expires. Downsides: a node can have 100k's of ranges, and must write a record every 3 sec for each. They could extend the lease duration to reduce load, but hurt availability after a crash.

They made a new protocol with fast failover, and better scalability. CRDB has an underlying "liveness fabric", a health-checking layer. Each node tracks the liveness of **every** other node in the system?? A node "supports" other nodes that it thinks are healthy. It supports the other node irrevocably for an epoch, with an expiration.

CRDB's new protocol has a "fortified leader", a leaseholding leader that knows it can't be replaced until a future timestamp. It sends a separate "fortify" request to followers periodically; followers promise not to be candidates or voters until a future timestamp. This somehow interacts with the liveness fabric, but there seems to me to be a ton of redundancy, layering violation, and needless complexity. I guess this is a symptom of the architectural history: they started off with both a Raft-per-range architecture, then added liveness fabric, then partly retired their Raft system in favor of the liveness fabric.

Their past lease protocol allowed gray failures: a leader with a disk stall could maintain the lease, blocking writes. Now, the liveness fabric detects the disk stall and prevents the leaseholder from maintaining its lease.

I asked about the n-squared cost of the liveness fabric, Kettaneh said they tested it with thousands of nodes and it's ok. Someone asked if they rely on synced clocks, Kettaneh said they rely on the same 500ms max skew that CRDB assumes in general.

## **CoddSpeed: Hardware Accelerated Query Processing in Microsoft Fabric**

Matteo Interlandi (Microsoft)

Best paper award. This is for analytic queries in MS Fabric, which is a big data analytics platform. They have a coprocessor abstraction layer (CAL) which lets multiple SQL execution engines use multiple hardware accelerations (GPUs, FPGAs, ...) through one API. Their GPU engine is based on Tensor Query Processor (VLDB 2022) that runs SQL via PyTorch, though they're starting to migrate to "custom CUDA kernels" whatever that means.

## Cortex AISQL: A Production SQL Engine for Unstructured Data

Benjamin Han (Snowflake), who is a climber, based on his laptop stickers

They add an `AI_COMPLETE` SQL operator that takes text prompt and outputs a completion. Also `AI_FILTER` that lets a model return true/false for a question about the input row. The inputs can be images or audio files, too. And `AI_AGG` can take many inputs and output a summary. The problem is that cost and selectivity of AI ops are not known to the query optimizer at compile time. Their main contributions are 3 optimizations:

* Predicate reordering: just tell the optimizer to assume that LLM ops are more expensive than all other ops, duh.... They have a paper in progress that's more sophisticated, dealing with optimizing queries that have multiple LLM ops and have to estimate their **relative** costs.
* Model cascades: use cheap inaccurate models as up-front estimators, then fall back to bigger models if uncertain.
* Query rewrites for semantic join: if you join tables A and B with an LLM call, don't ask the LLM |A|x|B| times whether rows are the same, instead restructure it as a classification task, asking the LLM what class each row belongs to and doing a regular join on classes.

They have a product CoWork where you can "talk with your data" that's powered by Cortex AISQL, and a coding product whose name I didn't catch.

## Teaching a New Dog Old Tricks: Reusing Data Management Principles in the Age of LLMs

Tova Milo (Tel Aviv University)

She begins with an example exploratory data analysis (EDA). Example: give an AI a prompt like "find a country with unusual Netflix viewing habits", AI writes a SQL query (I think that's what she's demonstrating). She concludes, "Formal specifications can constrain and guide AI exploration." It's striking that this is her conclusion about data analysis, since that's the conclusion everyone is reaching in the distributed/concurrent systems world, too. I.e., that's what practically every talk said at the Antithesis BugBash conference last month.

She describes tools from the last few decades of analysis: query languages, constraints, provenance, graph data, crowdsourcing. She says human analysts have used these before, now LLMs must.

E.g., RAG: embeddings miss some things, like multi-hop relations, there are inconsistent retrieved evidence, there are irrelevant results. There's an answer called GraphRAG, which includes graph edges, path reasoning, structured retrieval. The "semi-structured data" research of 20 years ago is relevant again. The consumer is an LLM instead of a human now. The same old problems are relevant again: query planning, provenance, privacy, data changes....

LLMs are great storytellers, they can give nice explanations of data patterns, but we have to force them to be **correct** explanations grounded in evidence. Embeddings from LLMs don't naturally include provenence necessary for checking validity. Validation must be part of the reasoning process. 

Can agents learn which tools to use? Can they autonomously validate their results before presenting them? We've spent decades creating tools to help humans analyze data, now we must teach agents the same thing.

> **Abstract:** Over the past decade, large language models (LLMs) have emerged as a powerful paradigm for interacting with data, often bypassing traditional data management pipelines. They can flexibly query, integrate, summarize, and explain data through natural language, creating the impression that many classical data management problems have been effectively solved. However, this shift comes with well-known limitations: LLMs may hallucinate facts, produce explanations that are fluent but not grounded in the data, ignore constraints and inconsistencies, and provide no guarantees on correctness, completeness, or reproducibility. These shortcomings are particularly critical in data-centric settings, where decisions rely on faithful representations of the underlying data and where subtle biases, inconsistencies, or errors can lead to misleading conclusions.
>
> In this talk, I argue that tools and techniques developed over decades of data management research can play a central role in addressing these challenges. Our field has produced a rich toolbox for selecting informative data representations, enforcing constraints, explaining results, and validating conclusions. While originally designed for human-driven workflows, these methods provide exactly the kinds of structure, guarantees, and control that are currently missing in AI-driven data analysis.
>
> Drawing on recent work from my group and the broader community, I will illustrate how ideas from query languages, data dependencies, explanation frameworks, and crowdsourcing can be reinterpreted as tools for guiding and constraining AI-driven analysis. I will highlight emerging opportunities for integrating these principles into modern AI systems, particularly in agent-based settings, and outline a research agenda for designing interfaces and abstractions that allow LLMs to leverage this toolbox effectively.
>
> The key message is that the future of data management lies not in competing with AI, but in equipping it with the structure, guarantees, and discipline needed to make its outputs trustworthy.

## [Automated Discovery of Test Oracles for Database Management Systems Using LLMs](https://dl.acm.org/doi/10.1145/3802017)

Suyang Zhong (National University of Singapore)

$10 of LLM usage can generate millions of DBMS test cases and discover bugs. Previous state of the art was SQLancer which generates pairs of equivalent queries and tests the DB gives same answer. A naive way to use an LLM is to generate equivalent queries, but this is expensive and unreliable. Instead, the LLM should generate test oracles, and the oracles generate queries. A constrained abstract query is a query template, which generates equivalent query pairs.  The authors created a "SQL equivalent decider" which is a sound (though not complete) reliable decider to check the oracle's output before using it as a test case. They also have a method for pushing the LLM to generate diverse oracles for wide test coverage. They combine LLM with a traditional grammar-based generator to cheaply create lots of valid test cases, which have found many bugs in Postgres, MySQL, and others.

In response to a question, there are nondeterministic queries, e.g. some SQL results have undefined order. They ensure such queries aren't tested, but this would be good future research.

## [Test Data Generation for Complex SQL Queries](https://dl.acm.org/doi/10.1145/3769832)

Sunanda Somwase (IIT Bombay, AMD)

XData is an existing test data generator. It uses an SMT solver to generate test data with some desired properties. It doesn't support every kind of property you might want, though. In this paper, it now supports multisets properties: you might want N rows with some property. XData had only supported N=0 or 1, now it supports arbitrary N. It also lets you specify complex query outputs: you might want to provide inputs that produce certain outputs after passing through a query with joins, group by, nested subqueries, etc. Now XData can do that. It uses the Z3 SMT solver to generate inputs that ought to produce the desired outputs if the complex query is evaluated correctly by the SQL system under test.

## [Understanding and Detecting Query Performance Regression in Practical Index Tuning](https://dl.acm.org/doi/10.1145/3769839)

Vivek Narasayya (Microsoft Research)

This is about a databe engine tuning advisor (DTA), which consults the query optimizer to do "what-if" scenarios: how would a query's performance change if there was a specific index created? The query optimizer returns a plan and predicted cost. The DTA produces index recommendations for the user. Modern DTAs at Microsoft also recommend materialized views and partitioning schemes. But sometimes the actual performance after creating the recommended index gets worse. The cause is the cardinality estimation or cost model was wrong. In this paper, they study regressions to learn more about the causes.

They ran some experiments with customer workloads and a DTA with various configurations. They discovered many regressions. Apparently the main problem is, the cost model underestimates the cost of nested loop joins. They developed a pattern-based regression detector to catch this mistake. No time for Q&A, but I would've asked: if the cost model is wrong, shouldn't they fix the cost model instead of the index advisor?

## **Aurora PostgreSQL Limitless Database: Building a Highly Scalable OLTP Database**

Uses time-based MVCC and lead-shard 2PC for strong consistency at scale. They want adaptive vertical and horizontal scaling, "no overprovisioning, no manual resharding." It's Postgres-compatible, reusing some Postgres components. Users explicitly choose shard keys. There are "reference tables" which are read-heavy and rarely written, they're replicated around the cluster for easy joins. They use bounded-error clocks plus HLC. They guarantee external consistency. Their sharding impl seems like ours: the query coordinator pushes down operators as much as possible, they skip 2PC for single-shard txns. The storage layer guarantees 3-AZ fault tolerance.

When you try to distributed Postgres, something is very hard about snapshotting; I didn't understand. Anyway they use synced clocks for snapshotting. He says AWS Time Sync has typical bound <1ms in every region and microseconds in "some regions". They use commit-wait for txns, in parallel with persistence to 4-of-6 Aurora quorum write, which is usually slower than commit-wait anyway, so it's free.

They say "we deliberately stopped short of serializability", commit order = visibility order via timestamps. They have limited customer demand for serializability. There's some conflict I don't understand, where Postgres's SSI doesn't match the consistency of Limitless. I also don't understand how they said "external consistency" which I thought was synonymous with "strict serializability" but then they say they're not even serializable.

## From JSON to Duality: Automated Application Migration from Document to Relational Databases

LOL, shots fired. The motivation is, denormalization creates duplicate data, cross-collections transactions are "painful", and analytics support is better in SQL. But apps expect JSON results, and JSON data is "high-entropy". They say there's a "duality" of access and storage: the tables are the source of truth, but there are multiple access shapes, views expose a JSON hierarchical structure. This is specifically about providing "Mongo API/REST" on top of tables. They infer a relational schema by analyzing docs, they preserve doc-based access, and transform the data into the relational schema.

Not every field in docs should be a column, sparse fields or type-inconsistent fields should go in a catchall column.

They use heuristics, statistics, LLMs. They find and discard inconsistent/sparse fields. They decompose docs into tables in the obvious way, then identify primary keys somehow with heuristics. They only decompose a relation when normalization makes a significant redundancy savings. They detect which columns are FK relations, even if there's some slight mismatches among values (his example: slight capitalization differences among denormalized usernames). Then they create a "duality view" which is a query that joins tables to recreate the old JSON docs.

They plan to use LLMs to rewrite and optimize access patterns.

Q: How do they improve perf, given that queries now require joins. A: He's only talking about analytics, not apparently OLTP. Q: How do you query on the flexible-JSON with the catchall fields? A: Work in progress. My Q: OK but what about OLTP? Most doc ops affect a single doc, now you've turned that into a join. A: There are some regressions, but the analytics speedup is worth it.

# DBTest

## JSON generation from JSON Schema

Giorgio Ghelli (University of Pisa)

This talk was about generating JSON docs as test data that matches some JSON schema. "Witness generation": deciding satisfiability by generating a witness, prove that a JSON Schema allows any docs at all. He and coauthors have solved witness generation. They convert the JSON schema to disjunctive normal form (DNF), using De Morgan dualities to eliminate all "not" operators, and a half-dozen other transforms, and produce a witness-generation structure. There are many other types of analysis that benefit from mock-data generation, e.g. testing and documentation.

Open problems:

* Generate docs to maximize "coverage" of the schema, where defining "coverage" is non-obvious. If you try to generate a doc for each combination of possible types, values, etc., the combinatorial explosion is too big. There are some papers about heuristics for generating a useful subset. There's also "information-gain-based generation": generate additional docs that add more value, where "value" is defined in various ways.
* Generate many conforming docs, satisfying some goal(s) in addition to schema conformance.
* Extract JSON Schema "distributional/correlational" properties from a set of examples?
* Generate JSON with LLMs. "Constrained decoding" forces the LLM to produce valid docs, by bitmasking the token space after each output, so that invalid tokens are masked out, and the next token produced must be one of the unmasked tokens. You can use an algorithm to generate the structural "frame" of a doc and a small LLM to fill in some realistic values.

My Q: Have you tried code-coverage-guided JSON generation combined with your JSON Schema algorithms? A: No, but it would obviously be useful. (Thought: MongoDB would be a good example system for doing this sort of test: try different variations of JSON generation and see how they affect code coverage in mongod.)

## Boosting DBMS Test Coverage via LLM-Driven SQL Generation

A. Sanghi, IIT Hyderabad

Their system, "Quover", aims to increase code coverage of an RDBMS. They start with a "seed workload" and measure code coverage. They maintain a map of queries to covered code, which the LLM uses to find uncovered code and try to generate queries that exercises it. They're only using gpt-40-mini for 3 hours so it's cheap. They compared to an existing LLM SQL workload generator SQLStorm as a baseline. Their dataset has TPC-H and they generated a bunch of SQL queries with Quover, and got somewhat better coverage than SQLStorm. 

## DIRT: Database-Integrated Random Testing

A. Keles, U. of Maryland, with a coauthor E. Chou who now works for Antithesis

They have an algorithm to randomly generate valid SQL that matches some desirable properties required for testing a particular feature or bug.

## Multi-Tiered Microbenchmark Regression Detection in a Production Database CI Pipeline

Herko Lategan (Cockroach Labs)

Benchmark regresssions are easy to find with change point detection and git bisect. But what if there's a very high-variance benchmark that has a slowly declining trend? The decline is always smaller than the variance, and no single commit is responsible. This is a "micro-regression".

They have a suite of 1000+ microbenchmarks, it runs after the fact, and it's noisy and prone to false positives. Engineers waste time diagnosing post-facto. They have a core microbenchmark suite they run for 15 minutes on 12 nodes before a PR is merged, it's based on Sysbench. It runs each several times for N samples>1 to measure variance and p-value. It comments on the PR with an analysis if it thinks it detects a regression (p-value < 0.025).

It's important to reduce benchmark variance in order to detect smaller regressions. They moved to compute-optimized GCP instances, reducing variance from 4-5% to 1-2%, although these instances cost more. They disabled hyperthreading and CPU scaling (recently-available options on GCP). They interleave different benchmarks on a machine, so if there's a period of bad performance, that event's effect is spread over the benchmarks somewhat evenly.

Since they do hundreds of PRs per day, any reasonable confidence interval will permit some false positives. They choose a "pass fast, fail slow" strategy. If the first benchmark run shows no regression, they let the PR through. If it shows a regression, they retry 3 times, giving it more chances to pass. They're strongly favoring negatives over positives. Their stats show a 21% false positive rate even so! But they're finding real regressions nevertheless.

They noticed a lot of "build variance", unpredictable differences in how the same code is compiled from build to build, which have measurable performance differences. They're working on this, presumably to choose the fastest build.

## Continuous Resilience Testing of a Distributed Database in Long-Running Clusters

S. Patel, C. Jain (Cockroach Labs)

They want to test the resilience of CRDB clusters that are running for **weeks** in a chaotic environment. Deterministic simulation testing (DST) is insufficient in their opinion because it doesn't run for weeks (why not?) and it doesn't simulate the real OS and hardware (why not?).

Their system can choose from a menu of 53+ ops using a PRNG. There's a dependency check (some ops must run after others) and a post-op cleanup step. Since 2023 they've found 87 critical bugs no other test could catch! E.g., after an upgrade, ranges (chunks of data) grow forever without splitting, so the DB eventually crashes. Or, if a node restarts in the middle of a compaction, it leaves orphaned files that consume disk space. This must happen many times before it's a detectable problem.

It's very hard to figure out the root cause of a failure in one of these tests, they've created a Claude skill to help. Future research: the AI launches more test runs to narrow down the cause.

It sounds like operations are run one at a time mostly, with some concurrency, and meanwhile a background workload is running continuously. My Q: How deterministic is this? If you start with the same PRNG seed will you reproduce the same bug? A: Somewhat deterministic. They mostly do post-hoc log analysis etc. for diagnosis. I infer this is because rerunning a test takes weeks, and their observability is good, and the bugs they've found are tractable.

## New researcher mentoring session with Matteo Interlandi

SIGMOD made some senior researchers accessible for mentoring sessions, I signed up to be mentored and randomly drew Matteo. Since he won Best Paper Award and I admired his presentation this year I was stoked.

I asked, how do you find a line of research that generates multiple papers over several years? he said, identify some niche where no one else is working. (but presumably not *so* niche that reviewers won't see the value of your work.)
write a benchmark paper about an unbenchmarked niche question, eval all the systems, find a place on the pareto frontier that's untapped or otherwise build a system that looks good on one's own benchmark

find workshops or vision papers to apply to instead of always targeting the hardest cfps like vldb and sigmod

matteo works at gray systems labs at microsoft. this isn't microsoft research, which is a siloed separate organization, it's a part of microsoft engineering. matteo's boss carlo at gray system labs is really good somehow at making periodic connections with the rest of MS engineering and finding their problems and the lab's solutions and making matchups

periodic (currently annual, might be 2x yearly) meetup with engineering managers, product managers, and labs people to swap ideas and roadmaps and find connections. they invite a rotating cast of engineers and PMs to get a variety of ideas and not take too much time
