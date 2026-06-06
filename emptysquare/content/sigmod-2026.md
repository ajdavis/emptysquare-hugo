+++
type = "post"
title = "SIGMOD 2026 Recap"
description = "My notes from the database conference in Bangalore."
category = ["Programming"]
tag = []
draft = true
enable_lightbox = true
+++

This is one of the two top database research conferences (the other is VLDB). Our paper [LeaseGuard: Raft Leases Done Right](/leaseguard-raft-leader-leases-done-right/) was accepted, and I was excited to go present it, especially because this year the conference was in Bangalore. [I haven't been to India in 20 years](https://www.flickr.com/photos/emptysquare/albums/72157594463266389/). I prepended [a trip to Nepal](/nepal-trek/) so I could spend time outside in a cooler part of the subcontinent. 

Conference stats: 1000 total participants, 120 remote participants (Indian visa problems for Chinese people and others), 340 talks, 326 reviewers. A very large proportion of speakers were denied visas, mostly by India but occasionally other countries. (Some countries denied **exit** visas??) The organizers heroically reconfigured the conference over the last few weeks to permit hybrid sessions where necessary. For a lot of the talks, the presenter was not the one listed on the SIGMOD website. Some talks were pre-recorded, or a second author presented the paper because the lead author couldn't get a visa. In the DBTest workshop a talk was presented by someone who wasn't an author at all, and one Chinese researcher sent an AI-generated video about his research with a synthesized American narrator. That one wasn't very compelling, but overall I thought the presentations were strong.

I laughed when SIGMOD told me my slot was 9 minutes, with 2 minutes for Q&A. I thought, I'm flying 16 hours to talk for 9 minutes? And why give me 2 minutes for Q&A instead of an 11-minute slot? But for my talk and others, the format worked better than I expected. I discovered I could fit LeaseGuard into 9 minutes, with the problem statement, solution, and evaluation, and I got one good question. I think a 10-page paper *should* fit into 9 minutes, if you assume you're presenting to specialists and go straight to the essence. If you leave non-specialists in the dust, that's ok, they probably weren't going to read your paper anyway. A lot of these talks were too concise for me to understand, but when they were in my wheelhouse I learned enough in 9 minutes to decide whether to read the paper. Furthermore, there were some valuable discussions in those 2-minute Q&As. I stand by my assertion that [normal-length talks at industry conferences and open source conferences shouldn't have Q&A](/how-i-deliver-a-conference-talk/#no-questions-please).

{{< toc >}}

# Main conference

## Can AI assist in Mathematics and Computer Science research?

Prabhakar Raghavan, the Chief Technologist at Google.

The answer is "yes", of course. He particularly describes [AlphaEvolve](https://deepmind.google/blog/alphaevolve-a-gemini-powered-coding-agent-for-designing-advanced-algorithms/), Google DeepMind's evolutionary coding agent, and its application to [open Erdős problems](https://terrytao.wordpress.com/2025/11/05/mathematical-exploration-and-discovery-at-scale/). The architecture has many layers: a large language model (LLM) generates programs to solve the problem, then a cascade of automated evaluators verifies and scores them---cheap checks first to weed out invalid candidates, then progressively fuller evaluation, partly to keep the agent from gaming the scoring function. The best-scoring programs are stored and fed back to the LLM as inspiration, in effect telling it, "Make more of these." Reminiscent of Jeff Clune's series of papers like [Automated Design of Agentic Systems](/review-automated-design-of-agentic-systems/).

## AWS DevOps Agent

Sponsor talk, Mohammedfahim Pathan.

Customers with very distributed apps with lots of microservices are complaining about increased time to resolve incidents. The [AWS DevOps Agent](https://aws.amazon.com/devops-agent/) (a product built on Amazon Bedrock AgentCore, previewed at re:Invent 2025---there's no research paper) is a service that has subagents for root cause analysis, incident triage, mitigation, etc. It's extensible through Model Context Protocol (MCP) servers, and it can be triggered via PagerDuty, webhooks, human prompts, etc.

A slide claims that the agent learns from experience: "Learns from investigation patterns, tool use, and topology. Builds skills based on team resolution approaches." This seems interesting and vague in the talk, it's hard to make agents learn on the job. I grilled the speaker in Q&A (the session chair D. B. Phatak piled on when the speaker tried to dodge) and it sounds like no, the agent **doesn't** learn from experience, that slide was misleading. The agent has code search and other useful skills. Its mitigation plans are emitted as specs that feed development tools like [Kiro](https://kiro.dev/), AWS's agentic IDE, supposedly to prevent future outages from new code? Now I'm skeptical of that claim too.

## [PRISM: Navigating Cost-Accuracy Trade-offs for NL2SQL](https://dl.acm.org/doi/10.1145/3786679)

Gaurav Tarlok Kakkar (Georgia Tech), Yeounoh Chung and Fatma Özcan (Google), Steve Mussmann, Joy Arulraj (Georgia Tech).

The observation behind PRISM is that NL2SQL accuracy depends on a whole pipeline of interdependent choices---which LLM, the how the schema is presented to it (full schema vs. various pruning strategies), the prompting strategy (basic, chain-of-thought, or decomposition), how many few-shot examples, whether to retry on errors---and the best combination is schema-dependent and interacts in non-obvious ways, so manual tuning is impractical. PRISM treats it as a multi-objective configuration-tuning problem, optimizing execution accuracy against the dollar cost of LLM tokens.

It works in two phases. Offline, it uses cost-aware Bayesian optimization to explore the configuration space, and curates a pool of high-performing pipelines. Online, it deploys either a single cost-effective configuration (presenting the user a Pareto frontier of accuracy-vs-cost options to choose from) or, when accuracy matters more than cost, an ensemble of configurations.

How does it pick among candidate pipelines? Each configuration generates a candidate SQL query, all candidates are executed, and a fine-tuned selection model does pairwise comparisons to choose a winner. For each pair, the model is shown the NL question, the schema elements both queries reference, the two queries, **and their execution results**, and judges which better answers the question. PRISM adds two refinements over prior selection-model work: first, a vote counts only if the model prefers the same candidate when the pair is shown in both orders (filtering noisy comparisons). Second, if several queries give the same results, the queries are grouped together and collect votes as a team, so semantically-equivalent queries reinforce each other instead of splitting the vote. The result group with the most votes wins.

The natural-language-to-SQL (NL2SQL) field has a standard benchmark now, [BIRD](https://bird-bench.github.io/). PRISM slightly beats the state of the art (LongContext) on BIRD, and costs about a tenth as much!

## [Brook-2PL: Tolerating High Contention Workloads with A Deadlock-Free Two-Phase Locking Protocol](https://dl.acm.org/doi/10.1145/3769767)

Juncheng Fang (presenting, UC Irvine), Farzad Habibi (UC Irvine), Tania Lorido-Botran (Roblox), Faisal Nawab (UC Irvine).

This is about two-phase locking (2PL), the classic protocol where a transaction acquires all its locks before releasing any. Brook-2PL eliminates deadlocks before transactions start, by static analysis of stored procedures. They build an "SLW-graph" (static-locking-wait graph) in which nodes are operations, shared-lock acquisitions, exclusive-lock acquisitions, or unlocks; edges are either ordering within a transaction or lock conflicts across transactions. A deadlock corresponds to a cycle. When they find one, they can merge locking nodes together, move a lock earlier in a transaction to impose a consistent global lock order, or notice when a conflict is actually commutative and not a real conflict.

Because the analyzed transactions are now deadlock-free, they can release locks early instead of holding them all until commit---this is "partial transaction chopping." Classic [transaction chopping](https://www.researchgate.net/publication/200032116_Transaction_Chopping_Algorithms_and_Performance_Studies) splits a transaction into pieces that commit independently so locks release piece-by-piece; the trouble is the pieces are fully isolated, so on realistic workloads the safety constraints rarely hold. Brook-2PL's "partial" version relaxes that: a lock can persist across a chop boundary, and serialization is enforced by the consistent lock order rather than by isolating the pieces. The payoff is early write visibility, which cuts contention on hot keys. So aborts become impossible for the statically-analyzed transactions; if there's a dynamic transaction with unknown read/write sets, it falls back to a standard deadlock-detection-and-abort protocol (Wound-Wait).

## [Sublime: Sublinear Error & Space for Unbounded Skewed Streams](https://dl.acm.org/doi/10.1145/3802116)

Niv Dayan (presenting), Navid Eslami, Ioana Bercea (KTH), Rasmus Pagh (University of Copenhagen) (Dayan and Eslami at the University of Toronto). This won SIGMOD's Best Paper award.

Common question about high-throughput streams: how often does each item appear? The [Count-Min Sketch](https://doi.org/10.1016/j.jalgor.2003.12.001) uses a fixed amount of RAM and gives a bounded-error estimate of item frequency. This paper addresses two problems with that data structure.

1. Skew: a uniform counter width wastes bits storing the leading zeros of the many small counts, while large counts are cramped. The authors use variable-length counters that start short and elongate as they overflow, with some bit-manipulation hacks to conserve space and CPU time.
2. Stream growth: the error accumulates linearly with the number of stream items, so it grows over time. Instead they periodically grow the sketch in place---doubling each counter array and copying the existing counts over, with no rehashing---so error grows only as the square root of N instead of O(N). The growth rate is tunable for other size-error tradeoffs too.

## [Focus! Fast On-disk Concurrency-control Using Sketches](https://dl.acm.org/doi/10.1145/3769793)

Alex Conway (presenting, Cornell Tech), Deukyeon Hwang (University of Washington), and coauthors at CruxOCM, Datadog, Technion, and VMware Research.

If a transaction does a page fault while holding a lock, it's very slow (with 2PL). Optimistic concurrency control (OCC) requires more metadata, like timestamps, which amplifies data size; and checking and updating timestamps turns blind writes into read-modify-write ops. Rather than a new protocol, the paper decomposes timestamp-based concurrency control into two parts: a timestamp-storage layer and the concurrency-control protocol itself (they test it under several, including OCC- and MVCC-style ones). Their storage layer, FPSketch, is a hash table holding exact timestamps for currently-active (hot) keys plus a Count-Min-style sketch holding upper-bound timestamps for inactive (cold) keys. The sketch may overestimate a cold key's timestamp and so abort too many transactions, but it's always safe. When a cold key heats up, its timestamp moves back into the hash table and is tracked exactly. The headline result: as little as 32 KiB of sketch metadata for an 80 GB database, versus hundreds of MB to store every timestamp exactly.

## [Adaptive Sharding in Untrusted Environments](https://dl.acm.org/doi/10.1145/3769756)

Bhavana Mehta, Nupur Baghel, Boon Thau Loo, Ryan Marcus (University of Pennsylvania), Mohammad Javad Amiri (Stony Brook University).

Marlin is workload-aware data placement with Byzantine fault tolerance (BFT). There exist static BFT sharding algorithms, but no dynamic ones. Nodes can lie about metrics, or they can disrupt data movement. It's important to re-shard to reduce cross-shard transactions, because two-phase commit (2PC) on top of BFT is very expensive. The paper presents two designs: a centralized baseline with a trusted coordinator, and the main contribution, a decentralized variant with no coordinator (since a coordinator could be malicious), where each node locally monitors performance and proposes resharding, and the proposals pass through BFT consensus---a valid proposal needs a quorum (2f+1 of 3f+1 signatures), so even a malicious leader colluding with all f faulty nodes can't force an unsafe resharding, only waste work. A faulty *leader* is handled by the usual PBFT view-change (re-election); individual Byzantine *nodes* are tolerated rather than replaced. The decentralized variant converges more slowly than the centralized baseline. Note that the larger BFT quorums aren't a weakness: they're the price of tolerating a stronger (adversarial) fault class than a crash-only system, not less fault tolerance.

## [Making LSM-Tree-based Key-Value Store Practical and Efficient for Multi-Tenant Serverless Cloud Databases](https://dl.acm.org/doi/10.1145/3786667)

Yingjia Wang, Ming-Chang Yang (The Chinese University of Hong Kong), and a team at Alibaba including Feifei Li. Their system is called FlexEngine.

Log-structured merge (LSM) trees have synchronous foreground tasks---user reads and write-ahead-log (WAL) writes---and async background tasks: flushes and compactions. In serverless, the storage bandwidth is oversubscribed to save money, but there are still SLAs for tenants. Compaction can cause stalls and violate SLAs. FlexEngine is built on RocksDB, whose existing rate limiter auto-tunes a partition's bandwidth in 5%-per-step increments based on recent usage, so if it has wound the limit down to 5% during a quiet period and load suddenly spikes, climbing back to 100% takes as long as 62 seconds---during which the spike gets throttled.

The auto-tuner also lumps foreground and background I/O under a single limit, so FlexEngine's first idea is to disaggregate them, giving each partition two separate rate limiters. Foreground bandwidth is always reserved at maximum (never suppressed), while background bandwidth scales with demand. Compaction still runs continuously here---just at a rate that can never starve user reads and WAL writes.

That's per-partition. The harder problem is at the node level: even when every partition is within its own cap, a node runs short when many partitions burst at once (say, several fire compactions together) and their combined demand exceeds the node's physical bandwidth. The existing remedy is to migrate bandwidth-hungry partitions off the node. Migration is a separate, node-spanning mechanism that relocates whole partitions elsewhere; it reduces how many partitions compete on the node. And crucially, the migration I/O is done by the *replica-holding* nodes, not the overloaded one, so it relieves the shortage without spending the strained node's bandwidth. Migration is slow, though (hundreds of seconds), and write stalls would hit before it finishes. So FlexEngine buys time by deferring compactions to cut the node's background I/O until migration drains the load. You can't defer compaction forever, but migration ends the shortage in bounded time. Integrated in [Tair Serverless KV](https://www.alibabacloud.com/help/en/redis/product-overview/tair-serverless-kv/) on Alibaba Cloud.

## [LeaseGuard: Raft Leases Done Right](https://dl.acm.org/doi/10.1145/3786663)

A. Jesse Jiryu Davis, Murat Demirbas, Lingzhi Deng (MongoDB).

[Read my blog post about LeaseGuard,](/leaseguard-raft-leader-leases-done-right/) or watch [a video of a longer presentation](/leaseguard-presentation-video/). Someone asked a good question: have we shown the protocol is correct during reconfig? Yes, Raft reconfig guarantees Leader Completeness, and that's what we rely on.

## [Predictive Translation: High-Performance Buffer Management Without the Trade-Offs](https://dl.acm.org/doi/10.1145/3786678)

Michael Zinsmeister, Lam-Duy Nguyen, Viktor Leis, Thomas Neumann (Technische Universität München).

Traditional database page buffers are basically hashtables. There are modern alternatives that are faster but more invasive or hardware-coupled---the clearest example is vmcache, which leans on the OS page table and a kernel module and so isn't portable across OSes. The authors want to make traditional, portable buffers faster by parallelizing the hashtable lookup with the page read. They make a page's location in RAM predictable, so the DB can speculatively read the predicted frame while simultaneously running the hashtable lookup, then verify that the page really was where it predicted. A misprediction costs a second read from main memory. Cold pages are placed arbitrarily and often mispredict, but as they're accessed more they're (probabilistically) promoted to their predictable positions. I asked whether this makes bad workloads worse, because all the cache misses are exacerbated by mispredictions. Zinsmeister replied that in that case I/O is the bottleneck anyway, so mispredictions don't make things worse.

## [**Scalable Leader Leases For Multi Consensus Groups in CockroachDB**](https://dl.acm.org/doi/abs/10.1145/3788853.3803081)

[See my review here](/review-scalable-leader-leases-for-multi-consensus-groups-in-cockroachdb/).

## [CoddSpeed: Hardware Accelerated Query Processing in Microsoft Fabric](https://dl.acm.org/doi/abs/10.1145/3788853.3803077)

Matteo Interlandi, Nicolas Bruno, Brandon Haynes, Carlo Curino, and a large team at Microsoft.

Best Industry Paper award. This is for analytic queries in Microsoft Fabric, which is a big-data analytics platform. They have a Coprocessor Abstraction Layer (CAL), a hardware-agnostic API that lets the Fabric SQL engine offload query fragments to coprocessors, designed so that different accelerators (GPUs, FPGAs, ...) can plug in over time. So far the only built engine is the GPU one, based on the [Tensor Query Processor](https://arxiv.org/abs/2203.01877) (TQP, VLDB 2022), which runs SQL as tensor programs via PyTorch. They're now migrating the hot paths to custom CUDA kernels. The point of that: expressing relational operators as generic PyTorch tensor ops is wonderfully portable---you inherit every backend the ML ecosystem optimizes---but each op is its own GPU kernel launch with its own memory round-trip, and SQL's NULL and integer-overflow semantics don't map cleanly onto tensor math. Hand-written CUDA kernels (CUDA being NVIDIA's low-level GPU programming model) let them fuse operators into one pass, control memory layout, and bake in correct SQL semantics, at the cost of portability---which is exactly the tradeoff CAL is there to hide.

## [Cortex AISQL: A Production SQL Engine for Unstructured Data](https://arxiv.org/abs/2511.07663)

Benjamin Han (Snowflake), who is a climber, based on his laptop stickers. (The paper's first author is Paweł Liskowski; Han is second.)

They add an `AI_COMPLETE` SQL operator that takes a text prompt and outputs a completion. Also `AI_FILTER` that lets a model return true/false for a question about the input row. The inputs can be images or audio files, too. And `AI_AGG` can take many inputs and output a summary. The problem is that the cost and selectivity of AI ops are not known to the query optimizer at compile time. Their main contributions are 3 optimizations:

* AI-aware predicate reordering: treat LLM-inference cost as a first-class objective. Often that just means deprioritizing expensive LLM ops, but it can also do the opposite of textbook predicate pushdown---*elevating* an AI predicate above a selective join to slash the number of model calls (their example cuts 110,000+ calls to 330). <!-- REVIEW: I couldn't confirm the "paper in progress on multiple LLM ops / relative costs" detail---dropped it. Restore if it's from the talk and you're sure. -->
* Model cascades: use cheap inaccurate models as up-front estimators, then fall back to bigger models if uncertain.
* Query rewrites for semantic join: if you join tables A and B with an LLM call, don't ask the LLM |A|x|B| times whether rows are the same, instead restructure it as a classification task, asking the LLM what class each row belongs to and doing a regular join on classes.

They have a product, [CoWork](https://www.snowflake.com/en/developers/guides/getting-started-with-cowork/), where you can "talk with your data" (Cortex AISQL is one piece of its pipeline), and a coding product, [Snowflake CoCo](https://www.snowflake.com/en/product/snowflake-coco/) (formerly Cortex Code).

## Teaching a New Dog Old Tricks: Reusing Data Management Principles in the Age of LLMs

Tova Milo (Tel Aviv University)

She begins with an example exploratory data analysis (EDA). Example: give an AI a prompt like "find a country with unusual Netflix viewing habits", AI writes a SQL query (I think that's what she's demonstrating). She concludes, "Formal specifications can constrain and guide AI exploration." It's striking that this is her conclusion about data analysis, since that's the conclusion everyone is reaching in the distributed/concurrent systems world, too. I.e., that's what practically every talk said at the Antithesis BugBash conference last month.

Her argument: over the past decade LLMs have become a powerful way to interact with data, often bypassing traditional data-management pipelines, creating the impression that classical data-management problems have been solved. But LLMs hallucinate, produce fluent explanations that aren't grounded in the data, ignore constraints and inconsistencies, and give no guarantees on correctness, completeness, or reproducibility---exactly the things that matter in data-centric decisions. Decades of data-management research produced a rich toolbox for these problems: query languages, constraints and data dependencies, provenance, explanation frameworks, graph data, crowdsourcing. Built originally for human-driven workflows, they're now what's missing in AI-driven analysis, and can be reinterpreted to guide and constrain it, especially in agent-based settings.

E.g., retrieval-augmented generation (RAG): embeddings miss some things, like multi-hop relations; the retrieved evidence can be inconsistent or irrelevant. There's an answer called GraphRAG, which includes graph edges, path reasoning, structured retrieval. The "semi-structured data" research of 20 years ago is relevant again. The consumer is an LLM instead of a human now. The same old problems return: query planning, provenance, privacy, data changes.

LLMs are great storytellers, they can give nice explanations of data patterns, but we have to force the explanations to be **correct** and grounded in evidence. LLM embeddings don't naturally carry the provenance needed to check validity. Validation must be part of the reasoning process.

Can agents learn which tools to use? Can they autonomously validate their results before presenting them? We've spent decades creating tools to help humans analyze data; now we must teach agents the same thing. Her key message: the future of data management lies not in competing with AI, but in equipping it with the structure, guarantees, and discipline to make its outputs trustworthy.

## [Automated Discovery of Test Oracles for Database Management Systems Using LLMs](https://dl.acm.org/doi/10.1145/3802017)

Suyang Zhong (National University of Singapore), Qiuyang Mang, Runyuan He, Xiaoxuan Liu, Alvin Cheung (UC Berkeley), Huanchen Zhang (Tsinghua). The system is called Argus.

<!-- REVIEW: the program lists Qiuyang Mang (Berkeley) as lead author and designated presenter; I kept Suyang Zhong first per your note. -->
A modest amount of LLM usage can generate a great many DBMS test cases and discover bugs cheaply. (My notes said "$10 → millions of test cases," but that figure is from the author's blog/talk, not the paper, which says each oracle expands to "thousands" of concrete tests.) Previous state of the art was SQLancer, whose oracles generate pairs of equivalent queries and check the DB gives the same answer. A naive way to use an LLM is to have it generate the equivalent queries directly, but this is expensive and unreliable (hallucinated false-positive bug reports). Instead, the LLM should generate test *oracles*, and the oracles generate queries. A "constrained abstract query" is a query template with typed placeholders, which generates equivalent query pairs. They verify each LLM-proposed oracle with an existing sound (but incomplete) SQL equivalence prover before trusting it as a test case---so the prover only ever confirms true equivalences. They also have a method for pushing the LLM to generate diverse oracles for wide coverage, and they combine the LLM with a traditional grammar-based generator to cheaply instantiate lots of valid tests. This found dozens of previously-unknown bugs across Dolt, DuckDB, MySQL, PostgreSQL, and TiDB.

In response to a question, there are nondeterministic queries (e.g. `RANDOM`, `CURRENT_TIMESTAMP`, or results with undefined row order). They ensure such queries aren't tested, but handling them would be good future research.

## [Test Data Generation for Complex SQL Queries](https://dl.acm.org/doi/10.1145/3769832)

Sunanda Somwase (IIT Bombay, AMD), Parismita Das (IIT Bombay, Couchbase), S. Sudarshan (IIT Bombay).

<!-- REVIEW: the program lists S. Sudarshan as the designated presenter; I kept Sunanda Somwase first per your note. -->
XData is an existing IIT Bombay test-data generator. It uses an SMT (satisfiability-modulo-theories) solver to generate test data with some desired properties, but it didn't support every property you might want. Two contributions here. First, multiset semantics: the old XData couldn't represent duplicate rows and required relation sizes to be fixed in advance, so it had to retry with different sizes; now it represents each tuple with a count (0 means absent, higher means multiplicity), letting the solver choose the relation size itself. Second, complex queries: it represents the output of each subexpression and subquery as a table, built bottom-up, so it can now handle queries with joins, group-by, and nested or correlated subqueries modularly---generating inputs that produce a non-empty (mutation-killing) result if the query is evaluated correctly. It uses the Z3 SMT solver under the hood.

## [Understanding and Detecting Query Performance Regression in Practical Index Tuning](https://dl.acm.org/doi/10.1145/3769839)

Vivek Narasayya, Wentao Wu, Anshuman Dutt, Gaoxiang Xu, Surajit Chaudhuri (Microsoft Research).

<!-- REVIEW: the program lists Wentao Wu as lead author and designated presenter; I kept Vivek Narasayya first per your note. -->
This is about the Database Engine Tuning Advisor (DTA), which consults the query optimizer to do "what-if" scenarios: how would a query's performance change if a specific index were created? The optimizer returns a plan and predicted cost, and the DTA produces index recommendations (the production DTA also recommends materialized views and partitioning schemes, though this paper is only about indexes). But sometimes the actual performance after creating the recommended index gets worse, because the optimizer's cardinality estimate was wrong. They study these regressions to learn the causes.

They ran experiments with customer workloads and a DTA in various configurations, finding regressions about 10--15% of the time (and a regression can mean a 50--80% slowdown). The dominant pattern: a new index makes a nested-loop join *look* cheap to the optimizer because the optimizer underestimates that join's cardinality, when it's actually very expensive (one example: an estimated 53K rows that's really 4.4M). They developed a pattern-based regression detector that uses the *true* cardinalities from the before-plan to recost the candidate plan and flag these cases. No time for Q&A, but I'd have asked: if the estimates are wrong, why not fix the cost model instead of the advisor? The paper does address this: accurate cardinality estimation is a decades-old unsolved problem, and ML-based estimators are slow and give no accuracy guarantee, so they deliberately build a cheap detector that works *with* the existing (wrong) estimates, exploiting the one extra signal available at tuning time---the real cardinalities of the current plan.

## Aurora PostgreSQL Limitless Database: Building a Highly Scalable OLTP Database

A large team at AWS (the [accepted-papers list](https://2026.sigmod.org/sigmod_industry_papers.shtml) gives the full author roster).

It uses time-based multi-version concurrency control (MVCC) and lead-shard two-phase commit (2PC) for strong consistency at scale. They want adaptive vertical and horizontal scaling, "no overprovisioning, no manual resharding." It's Postgres-compatible, reusing some Postgres components. Users explicitly choose shard keys. There are "reference tables" which are read-heavy and rarely written, replicated around the cluster for easy joins. They use bounded-error clocks plus a hybrid logical clock (HLC), and guarantee external consistency. Their sharding looks like ours: the query coordinator pushes down operators as much as possible, and skips 2PC for single-shard transactions. The storage layer guarantees 3-availability-zone (3-AZ) fault tolerance.

Here's what I now understand about why snapshotting is hard. Single-node Postgres gives a read a consistent snapshot by capturing the set of currently-running transaction IDs; a tuple is visible if the transaction that wrote it had committed and isn't in that in-progress set. That works because there's one authority for "what's committed right now." Sharded, each shard has its own independent transaction-ID space and commit log, so a globally consistent snapshot would require simultaneously asking every shard for its in-progress set---a coordination bottleneck. Limitless sidesteps this with time-based MVCC: a transaction gets one snapshot *timestamp*, and each shard decides visibility locally by comparing each tuple's commit timestamp to it. Synced clocks (AWS Time Sync, with a bound they cited around a millisecond) plus HLC make those timestamps globally comparable, and commit-wait (delaying the ack until the commit timestamp is safely in the past) keeps it correct despite skew. They run commit-wait in parallel with the 4-of-6 Aurora quorum write, which is usually slower anyway, so it's effectively free. <!-- REVIEW: the paper isn't on ACM DL yet; the clock figures (<1ms / microseconds) and the "commit-wait is free" framing are from AWS docs/talk, unverified against the paper. -->

The "external consistency vs. serializability" puzzle resolves once you see they're two orthogonal axes. Isolation level (Read Committed / Repeatable Read / Serializable) governs which anomalies between concurrent transactions are allowed; external consistency governs whether commit order respects real (wall-clock) time. Strict serializability is *both* at maximum. Limitless supports Repeatable Read (snapshot isolation) and Read Committed but **not** Serializable, while being externally consistent---so commit order = visibility order via timestamps, but it's "externally consistent snapshot isolation," not strict serializability. The conflict with Postgres's serializable snapshot isolation (SSI) is exactly this: SSI detects dangerous read-write dependency cycles at runtime by tracking every transaction's read predicates globally, which would require a distributed predicate-lock manager---the kind of global coordination Limitless is designed to avoid. So they deliberately stopped short of serializability, citing limited customer demand.

## From JSON to Duality: Automated Application Migration from Document to Relational Databases

Shashank Gugnani, Shadab Ahmed, Shubham Pednekar, Sanju Gowda, Sarvesh Tandon, Sukhada Pendse (Oracle). The target is Oracle's [JSON Relational Duality](https://www.oracle.com/database/json-relational-duality/) feature (Oracle Database 23ai).

LOL, shots fired. The motivation is, denormalization creates duplicate data, cross-collection transactions are "painful", and analytics support is better in SQL. But apps expect JSON results, and JSON data is "high-entropy". They say there's a "duality" of access and storage: the tables are the source of truth, but there are multiple access shapes, views expose a JSON hierarchical structure. This is specifically about providing "Mongo API/REST" on top of tables. They infer a relational schema by analyzing docs, they preserve doc-based access, and transform the data into the relational schema.

Not every field in docs should be a column, sparse fields or type-inconsistent fields should go in a catchall column.

They use heuristics, statistics, LLMs. They find and discard inconsistent/sparse fields. They decompose docs into tables in the obvious way, then identify primary keys somehow with heuristics. They only decompose a relation when normalization makes a significant redundancy savings. They detect which columns are FK relations, even if there's some slight mismatches among values (his example: slight capitalization differences among denormalized usernames). Then they create a "duality view" which is a query that joins tables to recreate the old JSON docs.

They plan to use LLMs to rewrite and optimize access patterns.

<!-- REVIEW: the 2026 paper isn't public yet. Oracle's public docs describe the migrator using unsupervised ML + functional-dependency analysis (not LLMs), and document the catchall "flex columns." Your talk notes mention LLMs and fuzzy FK matching---plausible from the talk, but I couldn't confirm them in writing. -->


Q: How do they improve perf, given that queries now require joins. A: He's only talking about analytics, not apparently OLTP. Q: How do you query on the flexible-JSON with the catchall fields? A: Work in progress. My Q: OK but what about OLTP? Most doc ops affect a single doc, now you've turned that into a join. A: There are some regressions, but the analytics speedup is worth it.

# DBTest

## JSON generation from JSON Schema

Giorgio Ghelli (University of Pisa). This was a DBTest keynote.

This talk was about generating JSON docs as test data that matches some JSON Schema. "Witness generation": deciding satisfiability by generating a witness, i.e. proving that a JSON Schema allows any document at all. Ghelli and coauthors have an algorithm for it ([Attouche et al., "Witness Generation for JSON Schema", PVLDB 2022](https://www.vldb.org/pvldb/vol15/p4002-sartiani.pdf)): they convert the schema to disjunctive normal form (DNF), use De Morgan dualities to eliminate all "not" operators, and apply a half-dozen other transforms, then generate a witness bottom-up. (It's the first explicitly-described sound-and-complete algorithm for this; it covers the whole language except `uniqueItems`.) Many other kinds of analysis benefit from mock-data generation, e.g. testing and documentation.

Open problems:

* Generate docs to maximize "coverage" of the schema, where defining "coverage" is non-obvious. If you try to generate a doc for each combination of possible types, values, etc., the combinatorial explosion is too big. There are some papers about heuristics for generating a useful subset. There's also "information-gain-based generation": generate additional docs that add more value, where "value" is defined in various ways.
* Generate many conforming docs, satisfying some goal(s) in addition to schema conformance.
* Extract JSON Schema "distributional/correlational" properties from a set of examples?
* Generate JSON with LLMs. "Constrained decoding" forces the LLM to produce valid docs, by bitmasking the token space after each output, so that invalid tokens are masked out, and the next token produced must be one of the unmasked tokens. You can use an algorithm to generate the structural "frame" of a doc and a small LLM to fill in some realistic values.

My Q: Have you tried code-coverage-guided JSON generation combined with your JSON Schema algorithms? A: No, but it would obviously be useful. (Thought: MongoDB would be a good example system for doing this sort of test: try different variations of JSON generation and see how they affect code coverage in mongod.)

## Boosting DBMS Test Coverage via LLM-Driven SQL Generation

Anupam Sanghi (IIT Hyderabad), E. Abdelkarim, Carsten Binnig (the work done with Binnig's group at TU Darmstadt).

<!-- REVIEW: I could not find the system name "Quover" anywhere in writing (not in the DBTest program or any source), and there's no public paper for this talk yet. The model/3-hours/TPC-H/query-to-coverage-map details below are from your talk notes, unverified. -->
Their system (which my notes call "Quover," though I can't confirm the name) aims to increase code coverage of a relational DBMS (RDBMS). They start with a "seed workload" and measure code coverage, maintaining a map of queries to covered code, which the LLM uses to find uncovered code and generate queries that exercise it. They're only using gpt-4o-mini for 3 hours, so it's cheap. They compared against [SQLStorm](https://www.vldb.org/pvldb/vol18/p4144-schmidt.pdf), an existing LLM SQL workload generator, as a baseline. Their dataset has TPC-H, and they got somewhat better coverage than SQLStorm.

## [DIRT: Database-Integrated Random Testing](https://arxiv.org/abs/2604.16373)

Alperen Keles, Ethan Chou (Keles tells me Chou now works for Antithesis), Leonidas Lampropoulos (University of Maryland), Harrison Goldstein (University at Buffalo).

DIRT is random/property-based testing for databases that are still under active development, when many features are incomplete. Instead of pointing an off-the-shelf tester at a finished DBMS, you embed the test generator inside the database itself, so it evolves alongside the system and stops generating queries that hit unimplemented features (which off-the-shelf tools flag as false positives). The core abstraction is "generation actions," a small Rust DSL that lets the database's own developers---not testing experts---specify both how to randomly generate valid SQL that respects current state and which correctness properties to check. They reimplemented SQLancer's classic oracles atop this and evaluated on Turso (an actively-developed SQLite-compatible engine), finding 23 confirmed-and-fixed bugs with very few false positives, versus a 96.5% false-positive rate for stock SQLancer against the same target.

## Multi-Tiered Microbenchmark Regression Detection in a Production Database CI Pipeline

Herko Lategan (Cockroach Labs).

<!-- REVIEW: the DBTest 2026 proceedings aren't online yet, so I couldn't independently verify any of the figures here (15 min / 12 nodes, p < 0.025, 21% false-positive rate, the "pass fast fail slow" retry rule, the 4-5%→1-2% variance reduction). They're from your talk notes; no paper or blog post yet confirms them. -->
Benchmark regressions are easy to find with change-point detection and git bisect. But what if there's a very high-variance benchmark that has a slowly declining trend? The decline is smaller than the variance, and no single commit is responsible. This is a "micro-regression".

They have a suite of 1000+ microbenchmarks, it runs after the fact, and it's noisy and prone to false positives. Engineers waste time diagnosing post-facto. The solution: They have a core microbenchmark suite they run for 15 minutes on 12 nodes before a PR is merged, it's based on Sysbench. It runs each benchmark several times for N samples>1 to measure variance and p-value. It comments on the PR with an analysis if it thinks it detects a regression (p-value < 0.025).

It's important to reduce benchmark variance in order to detect smaller regressions. They moved to compute-optimized GCP instances, reducing variance from 4-5% to 1-2%, although these instances cost more. They disabled hyperthreading and CPU scaling (recently-available options on GCP). They interleave different benchmarks on a machine, so if there's a period of bad performance, that event's effect is spread over the benchmarks somewhat evenly.

Since they do hundreds of PRs per day, any reasonable confidence interval will permit some false positives. They choose a "pass fast, fail slow" strategy. If the first benchmark run shows no regression, they let the PR through. If it shows a regression, they retry 3 times, giving it more chances to pass. They're strongly favoring negatives over positives. Their stats show a 21% false positive rate even so! But they're finding real regressions nevertheless.

They noticed a lot of "build variance", unpredictable differences in how the same code is compiled from build to build, which have measurable performance differences. They're working on this, presumably to choose the fastest build.

## Continuous Resilience Testing of a Distributed Database in Long-Running Clusters

S. Patel (likely Shailendra Patel), C. Jain (Cockroach Labs).

<!-- REVIEW: again, the DBTest proceedings aren't online yet, so the "53+ operations" and "87 critical bugs since 2023" figures are from your talk notes and unverified by any public source. -->
They want to test the resilience of CRDB clusters that are running for **weeks** in a chaotic environment. Deterministic simulation testing (DST) is insufficient in their opinion because it doesn't run for weeks (why not?) and it doesn't simulate the real OS and hardware (why not?).

Their system can choose from a menu of 53+ ops using a PRNG. There's a dependency check (some ops must run after others) and a post-op cleanup step. Since 2023 they've found 87 critical bugs no other test could catch! E.g., after an upgrade, ranges (chunks of data) grow forever without splitting, so the DB eventually crashes. Or, if a node restarts in the middle of a compaction, it leaves orphaned files that consume disk space. This must happen many times before it's a detectable problem.

It's very hard to figure out the root cause of a failure in one of these tests, they've created a Claude skill to help. Future research: the AI launches more test runs to narrow down the cause.

It sounds like operations are run one at a time mostly, with some concurrency, and meanwhile a background workload is running continuously.

My Q: How deterministic is this? If you start with the same PRNG seed will you reproduce the same bug? A: Somewhat deterministic. They mostly do post-hoc log analysis etc. for diagnosis. I infer this is because rerunning a test takes weeks, and their observability is good, and the bugs they've found are tractable.

# New researcher mentoring session with Matteo Interlandi

SIGMOD made some senior researchers accessible for mentoring sessions, I signed up to be mentored and randomly drew Matteo. Since he won Best Paper Award and I admired his presentation this year I was stoked.

I asked, how do you find a line of research that generates multiple papers over several years? he said, identify some niche where no one else is working. (but presumably not *so* niche that reviewers won't see the value of your work.)
write a benchmark paper about an unbenchmarked niche question, eval all the systems, find a place on the pareto frontier that's untapped or otherwise build a system that looks good on one's own benchmark

find workshops or vision papers to apply to instead of always targeting the hardest cfps like vldb and sigmod

matteo works at gray systems labs at microsoft. this isn't microsoft research, which is a siloed separate organization, it's a part of microsoft engineering. matteo's boss carlo at gray system labs is really good somehow at making periodic connections with the rest of MS engineering and finding their problems and the lab's solutions and making matchups

periodic (currently annual, might be 2x yearly) meetup with engineering managers, product managers, and labs people to swap ideas and roadmaps and find connections. they invite a rotating cast of engineers and PMs to get a variety of ideas and not take too much time
