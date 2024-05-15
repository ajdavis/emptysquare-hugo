+++
category = ["Review"]
date = "2024-01-29T21:02:14.834949"
description = "A 2023 paper about an interesting new consistency level for microservices."
draft = false
enable_lightbox = true
tag = ["distributedsystems"]
thumbnail = "ptolemy-map.png"
title = "Review: Antipode: Enforcing Cross-Service Causal Consistency in Distributed Applications"
type = "post"
+++

![](ptolemy-map.png)
_[Ptolemy Map, 1482](https://collections.leventhalmap.org/search/commonwealth:3f462s124)_

In 2015 some Facebook researchers [threw down a gauntlet](https://research.facebook.com/publications/challenges-to-adopting-stronger-consistency-at-scale/), challenging anyone who dared to provide stronger consistency in big, heterogeneous systems. In 2023, some researchers (mostly Portuguese) responded with [Antipode: Enforcing Cross-Service Causal Consistency in Distributed Applications](https://www.dpss.inesc-id.pt/~rodrigo/antipode-full.pdf). Antipode defines an interesting new consistency model, _cross-service causal consistency_, and an enforcement technique they claim is practical in such systems.

# Motivating Example

Here's an example from the paper. A social network is composed of services:

![](example.excalidraw.svg)
*My simplification of the paper's Figure 2*

This system has the following problematic workflow:

1. Author uploads a post; it's received by the Post-Upload service in Region A.
2. Post-Upload sends the post to Post-Storage,
3. ... which saves the post to a local replica of its datastore.
4. Post-Upload tells the post-id to Notifier,
5. ... which saves the post it a local replica of its (separate) datastore.
6. Both datastores eventually replicate to Region B in arbitrary order.
7. In Region B, as soon as Notifier replicates the notification,
8. ... it triggers Follower-Notify,
9. ... which retrieves the post from Post-Storage,
10. ... which retrieves it from its local replica of its datastore.
11. Once Follower-Notify has the post, it relays it to Follower.

The problem, as astute readers can predict, is if Notifier's datastore replicates sooner than Post-Storage's. In that case, Follower-Notify will learn about the post too soon; it'll try to retrieve it from Post-Storage but the post won't be there yet.

This is a consistency violation of some sort&mdash;the paper will define it exactly, in a moment. We could prevent the anomaly by making all datastores replicate _synchronously_. In that case, once Post-Storage has acknowledged storing the post in Region A, it has *also* replicated it to Region B, so it's certainly there by the time Follower-Notify tries to retrieve it. But this kills all parallelism. Maybe there's a better way?

# Causal Consistency Isn't Enough

What about Lamport-style causal consistency with [logical clocks](https://lamport.azurewebsites.net/pubs/time-clocks.pdf)? This wouldn't prevent the anomaly. The paper doesn't explain in detail why, so I'll try.

In [Lamport's algorithm](https://en.wikipedia.org/wiki/Lamport_timestamp#Algorithm), each process has a clock value (perhaps just an integer), which is incremented and propagated whenever processes exchange messages. Lamport clocks could prevent the anomaly if we had _one_ replicated datastore:

![](causal-consistency.excalidraw.svg)


1. Post-Storage in Region A saves the post, gets a Lamport clock value of 42 from the datastore.
2. Post-Storage in Region A *directly* notifies Post-Storage in Region B and tells it the clock value.
3. Post-Storage in Region B reads from its replica of the datastore. It tells the datastore to wait until it's replicated up to clock value 42 before executing the query:

Many datastores ([including MongoDB](https://www.mongodb.com/docs/manual/core/causal-consistency-read-write-concerns/)) support causal consistency this way, and it would prevent the anomaly described above. This doesn't work in the example from the paper's Figure 2, however. The problem is, there are two datastores replicating *concurrently* in Figure 2. Causal consistency is a only a partial order, not total; it allows the Post-Storage's or the Notifier's datastore to replicate first. With multiple replicated datastores, the anomaly is allowed by causal consistency, so we have to define a stricter consistency level. 

# Cross-service Causal Consistency

The Antipode authors define a new consistency level that prohibits the anomaly: "cross-service causal consistency". They abbreviate it "XCY", which perhaps makes sense in Portuguese. Cross-service causal consistency includes several ideas:

**Lineage**: A DAG of operations, partially ordered with Lamport's "happens-before" relation. A lineage begins with some "start" operation, such as a client request or a cron job, and proceeds until each branch completes with a "stop" operation.

In Figure 2 there are two lineages: one is spawned when Author uploads a post. I'll call this Lineage A. It has two branches (leading to Post-Storage and Notifier), and it includes concurrent replication of two datastores to Region B. The other lineage, which I'll call Lineage B, is spawned when Follower-Notify in Region B receives the notification. Lineage B then reads from Post-Storage in Region B, and notifies Follower.

![](lineages.excalidraw.svg)

The authors use a data set from Alibaba, where lineages are hairy: "User requests typically form a tree, where more than 10% of stateless microservices fan out to at least five other services, and where the average call depth is greater than four. Additionally, this tree contains, on average, more than five stateful services," i.e. services with datastores. 

**Reads-from-lineage**: An operation *b* reads-from-lineage *L* if *b* reads a value written by an operation in *L*.

**Cross-service causal order**: This is denoted with the squiggly arrow &rarrc;. For two operations *a* and *b*, if _a_ happens-before _b_ or _b_ reads-from-lineage _L_, where _L_ includes _a_, then _a_ &rarrc; _b_. Cross-service causal order is a transitive partial order, like happens-before.

**XCY**: This is the paper's new consistency level. An execution obeys XCY if you can find a serial order of operations obeying cross-service causal order.

XCY is the consistency level that Figure 2 violates! When Follower-Notify tries to read Author's post in Region B, that should happen _after_ all the events in Lineage A, including the replication of the post to Region B.

## My Feelings About Lineages

I feel uncomfortable, as if there's a purer mathematical concept obscured by the specifics of microservice architectures. Why are the borders between Lineages A and B drawn where they are? Could we split these operations into more than two lineages, or combine them into one?

I _think_ that a lineage is a general concept ("a DAG of operations"), but Antipode finds it convenient for microservice architectures to split lineages thus: Operations in a lineage are connected by happens-before. When a service reads a value from storage, this operation does *not* join the lineage that wrote the value. Instead, it's connected by reads-from-lineage. The goal of "cross-service causal consistency" is to make a partial order of lineages, such that replicated data stores appear not-replicated. (I was confused about this until I read the [paper's appendix](https://www.dpss.inesc-id.pt/~rodrigo/antipode-full.pdf). You should read the appendix, too.)

I think there's a more general idea of "recursive" or "nested" causal consistency trying to be born. This general idea would include lineages, defined however you want, and lineages could contain nested lineages. Cross-service causal consistency is a specialization of this general idea.

## Tracking And Enforcing Cross-Service Causal Consistency

This paper describes a system for enforcing XCY, called "Antipode", which means "[opposite side](https://en.wikipedia.org/wiki/Antipodes)"; maybe this refers to end-to-end consistency guarantees across geographic regions. Or maybe it [refers to mythical beings with reversed feet](https://en.wikipedia.org/wiki/Abarimon#/media/File:Schedel'sche_Weltchronik-Reverse_feet.jpg) for some reason.

![](reverse-feet.jpg)

Anyway, whenever services exchange messages as part of the regular functioning of the application, Antipode piggybacks lineage information. Since microservice architectures already piggyback info for distributed tracing, Antipode doesn't add much coding-time or runtime burden. Additionally, Antipode places shims in front of all datastores; the shims add lineage information to reads and writes. (Antipode borrows the technique from [Bolt-on Causal Consistency](http://www.bailis.org/papers/bolton-sigmod2013.pdf).) Lineage info accumulates along causal branches within a lineage, and gets dropped whenever a branch ends.

Developers can customize lineage tracking; they can explicitly add or remove dependencies. If one lineage depends on another in a way that Antipode doesn't detect, a developer can transfer lineage info between them.

(MongoDB drivers let you transfer causality info between sessions, too, although it's basically undocumented; [I explain it here](/how-to-use-mongodb-causal-consistency/).)

Antipode could enforce XCY automatically, on each read operation, but instead it provides an explicit `barrier` operation that developers must call to wait for dependencies to be satisfied. This seems error-prone, but it sometimes permits developers to reduce latency by carefully choosing where to place their `barrier` calls. The authors write,

> One argument that can be made against barrier is that it is as explicit as today's application-level solutions, since both of them require the developer to manually select its locations. What makes Antipode's approach better suited is not only barrier, but its combination with the implicit/explicit dependency tracking, which keeps services loosely coupled and does not require end-to-end knowledge of what to enforce.

This bit about "loose coupling" is insightful: you can place your `barrier` call somewhere, and if you later add dependencies, `barrier` will enforce them without code changes. On the other hand, having one `barrier` call for all dependencies requires you to wait for all of them at once, including those you don't need yet.

How does `barrier` know how long to wait?

> Antipode's `barrier` API call enforces the visibility of a lineage. It takes a lineage as an argument and will block until all writes contained in the lineage are visible in the underlying datastores. Internally, a `barrier` will inspect the write identifiers in the lineage and contact the corresponding datastores. For each datastore, barrier will call the datastore-specific `wait` API, which will block until the write identifier is visible in that datastore. Note that `wait` is datastore-specific because visibility depends on the design choices and consistency model of the underlying datastore. Once `wait` has returned for all identifiers in the lineage, `barrier` will return.

In our example, this means that before Follower-Notify retrieves Author's post from Post-Storage, it calls `barrier`, which queries the Post-Storage datastore and waits until it's sufficiently up-to-date.

![](barrier.excalidraw.svg)

This is an extra round trip (red arrow) even if the datastore is *already* up-to-date. I think this could be optimized away with something like [MongoDB's afterClusterTime](https://www.mongodb.com/docs/manual/reference/read-concern/#read-operations-and-afterclustertime), but Antipode's API would have to change. Luckily, you can limit the consistency check to nearby replicas:

> We implemented a practical optimization strategy specifically tailored for geo-replicated datastores. This involves implementing the wait procedure to enforce dependencies only from replicas that are co-located with its caller, thereby avoiding (whenever the underlying datastore allows it) global enforcement.

I don't fully understand `barrier` from the paper's description. If it's waiting for all writes from Lineage A to be visible in Region B, how does it know about writes that Lineage A hasn't even *started* yet? Must it wait for all branches of Lineage A to finish? If so, how? And what if an operation in Lineage A crashes or hangs?

# Their Evaluation

The authors evaluate Antipode with three benchmarks and a dozen brands of datastore, and ask 1) would there be XCY violations without Antipode, and 2) what is the cost of preventing them? The answer to question 1 is yes. For question 2:

* Lineage info adds 200 bytes to 14 kb per message in the authors' benchmarks (developers might need to explicitly prune lineages in their own systems).
* Waiting for consistency increases latency, by definition.
* Enforcing XCY decreases throughput by 2-15%.

# My Evaluation

Cross-service causal consistency is a neat concept. The chief argument for it, buried in the middle of the paper, is *decoupling*: it permits microservices to read consistently from multiple replicated data stores, without knowing the details of the microservices that wrote to them. This limits the impact of changes to any part of your system. With Death Star architectures like Alibaba or AWS, decoupling is crucial.

![](aws-deathstar.png)

_[The AWS microservices "death star" in 2008](https://twitter.com/Werner/status/741673514567143424)_

Antipode's API is higher-level than manually enforcing cross-service dependencies. I think it could be useful as part of an even higher-level "cloud programming language" that automatically decomposes, distributes, and parallelizes high-level logic, while detecting consistency requirements and enforcing them. I'm aware of cloud programming language projects like [Unison](https://www.unison-lang.org/), [Wing](https://www.winglang.io/), [Goblins](https://spritely.institute/news/spritely-goblins-v010-for-guile-and-racket.html), [Hydro](https://muratbuffalo.blogspot.com/2023/05/new-directions-in-cloud-programming.html), [Dedalus](https://www2.eecs.berkeley.edu/Pubs/TechRpts/2009/EECS-2009-173.pdf), [Gallifrey](https://www.cs.cornell.edu/andru/papers/gallifrey/snapl.pdf), and so on. They're at various stages of development and levels of abstraction. If this paper's definition of lineage were generalized to encompass more kinds of causal relations among operations, it could express the constraints of a variety of constructs in high-level cloud programming languages, and something like Antipode could enforce them.

# Further Reading

Other systems that strengthen the consistency of existing systems:
* [FlightTracker: Consistency across Read-Optimized Online Stores at Facebook](https://www.usenix.org/conference/osdi20/presentation/shi), and [Aleksey Charapko's summary](https://charap.co/reading-group-flighttracker-consistency-across-read-optimized-online-stores-at-facebook/).
* [Bolt-on Causal Consistency](http://www.bailis.org/papers/bolton-sigmod2013.pdf), and [Adrian Colyer's summary](https://blog.acolyer.org/2015/09/01/bolt-on-causal-consistency/).
