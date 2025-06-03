+++
canonical_url = "https://www.mongodb.com/blog/post/engineering/conformance-checking-at-mongodb-testing-our-code-matches-our-tla-specs"
category = ["Programming"]
date = "2025-06-03T09:03:01.528626"
description = "Five years ago we tried to test conformance, and only half-succeeded. Here's what happened, and the view from 2025."
draft = false
enable_lightbox = true
tag = ["tla+"]
thumbnail = "state-space.excalidraw.png"
title = "Conformance Checking at MongoDB: Testing That Our Code Matches Our TLA+ Specs"
type = "post"
+++

[Cross-posted from the MongoDB engineering blog](https://www.mongodb.com/blog/post/engineering/conformance-checking-at-mongodb-testing-our-code-matches-our-tla-specs).

At MongoDB, we design a lot of distributed algorithms—algorithms with lots of concurrency and complexity, and dire consequences for mistakes. We formally specify some of the scariest algorithms in TLA+, to check that they behave correctly in every scenario. But how do we know that our implementations conform to our specs? And how do we keep them in sync as the implementation evolves?

This problem is called *conformance checking*. In 2020, my colleagues and I experimented with two MongoDB products, to see if we could test their fidelity to our TLA+ specs. Here's a video of my presentation on this topic at the VLDB conference. (It'll be obvious to you that I recorded it from my New York apartment in deep Covid lockdown.) Below, I write about our experience with conformance checking from 2025's perspective. I'll tell you what worked for us in 2020 and what didn't, and what developments there have been in the field in the five years since our paper.

<iframe width="560" height="315" src="https://www.youtube.com/embed/IIGzXX72weQ?si=_z2r0Y5W0S-Igob4" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

{{< toc >}}

# Agile modelling

Our conformance-checking project was born when I read [a paper](https://arxiv.org/abs/1111.2826) from 2011—"Concurrent Development of Model and Implementation"—which described a software methodology called *eXtreme Modelling*. The authors argued that there's a better way to use languages like TLA+, and I was convinced. They advocated a combination of agile development and rigorous formal specification:

1. Multiple specifications model aspects of the system.  
2. Specifications are written just prior to the implementation.  
3. Specifications evolve with the implementation.  
4. Tests are generated from the model, and/or trace-checking verifies that test traces are legal in the specification.

I was excited about this vision. Too often, an engineer tries to write one huge TLA+ spec for the whole system. It's too complex and detailed, so it's not much easier to understand than the implementation code, and state-space explosion dooms model checking. The author abandons the spec and concludes that TLA+ is impractical. In the eXtreme Modelling style, a big system is modeled by a collection of small specs, each focusing on an aspect of the whole. This was the direction MongoDB was already going, and it seemed right to me.

In eXtreme Modelling, the *conformance* of the spec and implementation is continuously tested. The authors propose two conformance checking techniques. To understand these, let's consider what a TLA+ spec is: it's a description of an algorithm as a *state machine*. The state machine has a set of variables, and each *state* is an assignment of specific values to those variables. The state machine also has a set of allowed *actions*, which are transitions from one state to the next state. You can make a *state graph* by drawing states as nodes and allowed actions as edges. A *behavior* is any path through the graph.

This diagram shows the whole state graph for some very simple imaginary spec. One of the spec's behaviors is highlighted in <span style="color: #2f9e44; font-weight: bold">green</span>.
 
<div style="text-align: center">
<img src="state-space.excalidraw.svg" style="max-width: 60%">
</div>

The spec has a set of behaviors *B*<sub>spec</sub>, and the implementation has a set of behaviors *B*<sub>impl</sub>. An implementation *refines* a spec if *B*<sub>impl</sub> ⊂ *B*<sub>spec</sub>. If the converse is also true, if *B*<sub>spec</sub> ⊂ *B*<sub>impl</sub>, then this is called *bisimulation,* and it's a nice property to have, though not always necessary for a correctly implemented system. You can test each direction:

* **Test-case generation**: For every behavior in *B*<sub>spec</sub>, generate a test case that forces the implementation to follow the same sequence of transitions. If there's a spec behavior the implementation can't follow, then *B*<sub>spec</sub> ⊄ *B*<sub>impl</sub>, and the test fails.  
* **Trace-checking**: For every behavior in *B*<sub>impl</sub>, generate a *trace*: a log file that records the implementation's state transitions, including all implementation variables that match spec variables. If the behavior recorded in the trace isn't allowed by the spec, then *B*<sub>impl</sub> ⊄ *B*<sub>spec</sub> and the test fails.

Here are the state spaces of a spec and an implementation. Non-conforming behaviors are highlighted in <span style="color: #e03131; font-weight: bold">red</span>:

![](state-spaces.excalidraw.svg)

Both techniques can be hard, of course. For test-case generation, you must somehow control every decision the implementation makes, squash all nondeterminism, and force it to follow a specific behavior. If the spec's state space is huge, you have to generate a huge number of tests, or choose an incomplete sample.

Trace-checking, on the other hand, requires you to somehow map the implementation's state back to the spec's, and log a snapshot of the system state each time it changes—this is really hard with multithreaded programs and distributed systems. And you need to make the implementation explore a variety of behaviors, via fault-injection and stress-testing and so on. Completeness is usually impossible.

We found academic papers that demonstrated both techniques on little example applications, but we hadn’t seen them tried on production-scale systems like ours. I wanted to see how well they work, and what it would take to make them practical. I recruited my colleagues [Judah Schvimer](https://www.linkedin.com/in/judahschvimer/) and [Max Hirschhorn](https://www.linkedin.com/in/maxhirschhorn/) to try it with me. Judah and I tried trace-checking the MongoDB server (in the next section), and Max tried test-case generation with MongoDB Mobile SDK (the remainder of this article).

![](two-techniques.excalidraw.svg)

# Trace-checking the MongoDB server

For the trace-checking experiment, the first step Judah and I took was to choose a TLA+ spec. MongoDB engineers had already written and model-checked a handful of specs that model different aspects of the MongoDB server (see [this presentation](https://www.youtube.com/watch?v=-eAktIBUhHA) and [this one](https://www.youtube.com/watch?v=x9zSynTfLDE)). We chose [RaftMongo.tla](https://github.com/mongodb/mongo/blob/master/src/mongo/tla_plus/Replication/RaftMongo/RaftMongo.tla), which focuses on how servers learn the *commit point*, which I'll explain now.

MongoDB is typically deployed as a *replica set* of cooperating servers, usually three of them. They achieve consensus with a [Raft-like protocol](https://www.usenix.org/conference/nsdi21/presentation/zhou). First, they elect one server as the leader. Clients send all writes to the leader, which appends them to its *log* along with a monotonically increasing logical timestamp. Followers replicate the leader's log asynchronously, and they tell the leader how up-to-date they are. The leader keeps track of the *commit point*—the logical timestamp of the newest majority-replicated write. All writes up to and including the commit point are *committed*, all the writes after it are not. The commit point must be correctly tracked even when leaders and followers crash, messages are lost, a new leader is elected, uncommitted writes are rolled back, and so on.

RaftMongo.tla models this protocol, and it checks two invariants: A *safety* property, which says that no committed write is ever lost, and a *liveness* property, which says that all servers eventually learn the newest commit point.

<div style="text-align: center">
<img src="commit-point.excalidraw.svg" style="max-width: 60%">
</div>

Judah and I wanted to test that MongoDB's C++ implementation matched our TLA+ spec, using trace-checking. Here are the steps:

1. Run randomized tests of the implementation.  
2. Collect execution traces.  
3. Translate the execution traces into TLA+.  
4. Check the trace is permitted by the spec.

![](pipeline.excalidraw.svg)

The MongoDB server team has hundreds of integration tests handwritten in JavaScript, from which we chose about 300 for this experiment. We also have randomized tests; we chose one called the "rollback fuzzer" which does random CRUD operations while randomly creating and healing network partitions, causing uncommitted writes to be logged and rolled back.

We added tracing code to the MongoDB server and ran each test with a three-node replica set. Since all server processes ran on one machine and communicated over localhost, we didn't worry about clock synchronization: we just merged the three logs, sorting by timestamp. We wrote a Python script to read the combined log and convert it into a giant TLA+ spec named Trace.tla with a sequence of states for the whole three-server system. Trace.tla asserted only one property: "This behavior conforms to RaftMongo.tla."

Here's some more detail about the Python script. At each moment during the test, the system has some state *V*, which is the values of the state variables for each node. The script tries to reconstruct all the changes to *V* and record them in Trace.tla. It begins by setting *V* to a hardcoded initial state *V*<sub>0</sub>, and outputs it as the first state of the sequence:

```tla+ code fragment
\* Each TLA+ tuple is
\* <<action, committedEntries, currentTerm, log, role, commitPoint,
\*   serverLogLocation>>
\* We know the first state: all nodes are followers with empty logs.
Trace == <<
  <<"Init",                               \* action name
    <<"Follower","Follower","Follower">>, \* role per node
    <<1, 1, 1>>,                          \* commitPoint per node
    <<<<...>>,<<...>>,<<...>>>>,          \* log per node
    "">>,                                 \* trace log location (empty)
\* ... more states will follow ...
```

The script reads events from the combined log and updates *V*. Here's an example where Node 1 was the leader in state *V*<sub>i</sub>, then Node 2 logs that it became leader. The script combines these to produce *V*<sub>i+1</sub> where Node 2 is the leader and Node 1 is now a follower. Note, this is a lie. Node 1 didn't *actually* become a follower in the same instant Node 2 became leader. Foreshadowing! This will be a problem for Judah and me.

![](state.excalidraw.svg)

Anyway, the Python script appends a state to the sequence in Trace.tla:

```tla+ code fragment
Trace == <<  
  * ... thousands of events ...  
    <<"BecomePrimary",                  * action name for debugging  
    <<"Follower","**Leader**","Follower">>, * role per node  
    <<1, 1, 1>>,                        * commitPoint per node  
    <<<<...>>,<<...>>,<<...>>>>,        * log per node  
    * trace log location, for debugging:  
    "/home/emptysquare/RollbackFuzzer/node2.log:12345">>,  
  * ... thousands more events ...  
>>
```

We used the Python script to generate a Trace.tla file for each of the hundreds of tests we'd selected: handwritten JavaScript tests and the randomized "rollback fuzzer" test. Now we wanted to use the model-checker to check that this state sequence was permitted by our TLA+ spec, so we know our C++ code behaved in a way that conforms to the spec. Following [a technique published by Ron Pressler](https://pron.github.io/files/Trace.pdf), we added these lines to each Trace.tla:

```tla+ code fragment
VARIABLES log, role, commitPoint
\* Instantiate our hand-written spec, RaftMongo.tla.
Model == INSTANCE RaftMongo
VARIABLE i \* the trace index

\* Load one trace event.
Read == /\ log = Trace[i][4]
        /\ role = Trace[i][5]
        /\ commitPoint = Trace[i][6]

ReadNext == /\ log' = Trace[i'][4]
            /\ role' = Trace[i'][5]
            /\ commitPoint' = Trace[i'][6]

Init == i = 1 /\ Read
Next == \/ i < Len(Trace) /\ i' = i + 1 /\ ReadNext
        \/ UNCHANGED <<i, vars>> \* So that we don’t get a deadlock error in TLC

TraceBehavior == Init /\ [][Next]_<<vars, i>>

\* To verify, we check the spec TraceBehavior in TLC, with Model!SpecBehavior
\* as a temporal property.
```

We run the standard TLA+ model-checker ("TLC"), which tells us if this trace is an allowed behavior in RaftMongo.tla. 

But this whole experiment failed. Our traces never matched our specification. We didn't reach our goal, but we learned three lessons that could help future engineers.

## What disappointment taught us

**Lesson one: It's hard to snapshot a multithreaded program's state.** Each time a MongoDB node executes a state transition, it has to snapshot its state variables in order to log them. MongoDB is highly concurrent with fairly complex locking within each process—it was built to *avoid* global locking. It took us a month to figure out how to instrument MongoDB to get a consistent snapshot of all these values at one moment. We burned most of our budget for the experiment, and we worried we'd changed MongoDB too much (on a branch) to test it realistically.

The 2024 paper "Validating Traces of Distributed Programs Against TLA+ Specifications" describes how to do trace-checking when you can only log *some* of the values (see my summary at the bottom of this page). We were aware of this option back in 2020, and we worried it would make trace-checking too permissive; it wouldn't catch every bug.

**Lesson two: The implementation must actually conform to the spec.** This is obvious to me now. After all, conformance checking was the point of the project. In our real-life implementation, when an old leader votes for a new one, *first* the old leader steps down, *then* the new leader steps up. The spec we chose for trace-checking wasn't focused on the election protocol, though, so for simplicity, the spec assumed these two actions happened at once. (Remember I said a few paragraphs ago, "This is a lie"?) Judah and I knew about this discrepancy—we'd deliberately made this simplification in the spec. We tried to paper over the difference with some post-processing in our Python script, but it never worked. By the end of the project, we decided we should have backtracked, making our spec much more complex and realistic, but we'd run out of time.

The eXtreme Modelling methodology says we should write the spec just *before* the implementation. But our spec was written long *after* most of the implementation, and it was highly abstract. I can imagine another world where we knew about eXtreme Modelling and TLA+ at the start, when we began coding MongoDB. In that world, we wrote our spec before the implementation, with trace-checking in mind. The spec and implementation would've been structured similarly, and this would all have been much easier.

**Lesson three: Trace-checking should extend easily to multiple specs.** Judah and I put in 10 weeks of effort without successfully trace-checking one spec, and most of the work was specific to that spec, RaftMongo.tla. Sure, we learned general lessons (you're reading some of them) and wrote some general code, but even if we'd gotten trace-checking to work for one spec we'd be practically starting over with the next spec. Our original vision was to gather execution traces from all our tests, and trace-check them against all of our specifications, on every git commit. We estimated that the marginal cost of implementing trace-checking for more specs wasn't worth the marginal value, so we stopped the project.

## Practical trace-checking

If we started again, we'd do it differently. We'd ensure the spec and implementation conform at the start, and we'd fix discrepancies by fixing the spec or the implementation right away. We'd model easily observed events like network messages, to avoid snapshotting the internal state of a multithreaded process.

I still think trace-checking is worthwhile. I know it's worked for other projects. In fact MongoDB is sponsoring a grad student [Finn Hackett](https://fhackett.com/), whom I'm mentoring, to continue trace-checking research.

Let's move on to the second half of our project.

# Test-case generation for MongoDB Mobile SDK

The MongoDB Mobile SDK is a database for mobile devices that syncs with a central server. (Since we wrote the paper, MongoDB has [sunsetted the product](https://www.mongodb.com/resources/resources/resource-library/docs-atlas-device-sync-getting-started?xs=494444).) Mobile clients can make changes locally. These changes are periodically uploaded to the server and downloaded by other clients. The clients and the server all use the same algorithm to resolve write conflicts: [Operational Transformation](https://en.wikipedia.org/wiki/Operational_transformation), or OT. Max wanted to test that the clients and server implement OT correctly, meaning they resolve conflicts the same way, eventually resulting in identical data everywhere.

Originally, the clients and server shared one C++ implementation of OT, so we knew they implemented the same algorithm. But in 2020, we'd recently rewritten the server in Go, so testing their conformance became urgent.

![](realm.excalidraw.svg)

My colleague Max Hirschhorn used *test-case generation* to check conformance. This technique goes in the opposite direction from trace-checking: trace-checking starts with an implementation and checks that its behaviors are allowed by the spec, but test-case generation starts with a spec and checks that its behaviors are in the implementation.

But first, we needed a TLA+ spec. Before this project, the mobile team had written out the OT algorithm in English and implemented it in C++. Max manually translated the algorithm from C++ to TLA+. In the mobile SDK, clients can do 19 kinds of operations on data; six of these can be performed on arrays, resulting in 21 array merge rules, which are implemented in about 1000 lines of C++. Those 21 rules are the most complex, and Max focused his specification there. He used the model-checker to verify that his TLA+ spec ensured all participants eventually had the same data. This translation was a gruelling job, but the model-checker caught Max's mistakes quickly, and he finished in two weeks.

There was one kind of write conflict that crashed the model-checker: if one participant swapped two array elements, and another moved an element, then the model-checker crashed with a Java StackOverflowError. Surprisingly, this was an actual infinite-recursion bug in the algorithm. Max verified that the bug was in the C++ code. It had hidden there until he faithfully transcribed it into TLA+ and discovered it with the model-checker. He disabled the element-swap operation in his TLA+ spec, and the mobile team deprecated it in their implementation.

To test conformance, Max used the model-checker to output the entire state graph for the spec. He constrained the algorithm to three participants, all editing a three-element array, each executing one (possibly conflicting) write operation. With these constraints, the state space is a DAG, with a finite number of behaviors (paths from an initial state to a final state). There are 30,184 states and 4913 behaviors. Max wrote a Go program to parse the model-checker's output and write out a C++ unit test for each behavior.

Here’s an example unit test. (It's edited down from three participants to two.) At the start, there's an array containing {1, 2, 3}. One client sets the third element of an array to 4 and the second client removes the second element from the array. The test asserts that both clients agree the final array is {1, 4}. The highlighted lines are specific to this generated test. The rest of the code is the same for all tests.

```c++ {hl_lines=[4,7,10,14,16,17]}
TEST(Transform_Array)
{
  size_t num_clients = 2;
  TransformArrayFixture fixture{test_context, num_clients, {1, 2, 3}};

  fixture.transaction(0, [](TableRef array) {
    array->set_int(0, 2, 4);
  });
  fixture.transaction(1, [](TableRef array) {
    array->remove(1);
  });

  fixture.sync_all_clients();
  fixture.check_array({1, 4});

  fixture.check_ops(0, {ArrayErase{1}});
  fixture.check_ops(1, {ArraySet{1, 4}});
}
```

These 4913 tests immediately achieved 100% branch coverage of the implementation, which we hadn't accomplished with our handwritten tests (21%) or millions of executions with the [AFL fuzzer](https://lcamtuf.coredump.cx/afl/) (92%).

# Retrospective

Max's test-case generation worked quite well. He discovered a bug in the algorithm, and he thoroughly checked that the mobile SDK's Operational Transformation code conforms to the spec. Judah's and my trace-checking experiment didn't work: our spec and code were too far apart, and adding tracing to MongoDB took too long. Both techniques can work, given the right circumstances and strategy. Both techniques can fail, too! We published our results and lessons as a paper in VLDB 2020, titled "[eXtreme Modelling in Practice](https://arxiv.org/abs/2006.00915)."

In the subsequent five years, I've seen some progress in conformance checking techniques.

**Test-case generation:**

* [Model Checking Guided Testing for Distributed Systems](https://dl.acm.org/doi/abs/10.1145/3552326.3587442). The "Mocket" system generates tests from a TLA+ spec, and instruments Java code (with a fair amount of human labor) to force it to deterministically follow each test, and check that its variables have the same values as the spec after each action. The authors tested the conformance of three Java distributed systems and found some new bugs. Their technique is Java-specific but could be adapted for other languages.  
* [Multi-Grained Specifications for Distributed System Model Checking and Verification](https://muratbuffalo.blogspot.com/2025/04/multi-grained-specifications-for.html). The authors wrote several new TLA+ specs of Zookeeper, at higher and lower levels of abstraction. They checked conformance between the most concrete specs and the implementation, with a technique similar to Mocket: a human programmer instruments some Java code to map Java variables to spec variables, and to make all interleavings deterministic. The model-checker randomly explores spec behaviors, while the test framework checks that the Java code can follow the same behaviors.  
* [SandTable: Scalable Distributed System Model Checking with Specification-Level State Exploration](https://github.com/tangruize/SandTable/blob/main/doc/SandTable-Paper.pdf). This system is *not* language-specific: it overrides system calls to control nondeterminism and force the implementation to follow each behavior of the spec. It samples the spec's state space to maximize branch coverage and event diversity while minimizing the length of each behavior. As in the "Multi-Grained" paper, the SandTable authors wisely developed *new* TLA+ specs that closely matched the implementations they were testing, rather than trying to use existing, overly abstract specs like Judah and I did.  
* Plus, my colleagues [Will Schultz](https://will62794.github.io/) and [Murat Demirbas](http://muratbuffalo.blogspot.com/) are publishing a paper in [VLDB 2025](https://vldb.org/2025/) that uses test-case generation with a new TLA+ spec of MongoDB's WiredTiger storage layer, the paper is titled "Design and Modular Verification of  Distributed Transactions in MongoDB."

**Trace-checking:**

* [Protocol Conformance with Choreographic PlusCal](https://dariusf.github.io/cpluscal.pdf). The authors write new specs in an *extremely* high-level language that compiles to TLA+. From their specs they generate Go functions for trace-logging, which they manually add to existing Go programs. They check that the resulting traces are valid spec behaviors and find some bugs.  
* [Validating Traces of Distributed Programs Against TLA+ Specifications](http://arxiv.org/pdf/2404.16075v2). Some veteran TLA+ experts demonstrate in detail how to trace-log from a Java program and validate the traces with TLC, the TLA+ model-checker. They've written small libraries and added TLC features for convenience. This paper focuses on validating *incomplete* traces: if you can only log some of the variables, TLC will infer the rest.  
* [Smart Casual Verification of the Confidential Consortium Framework](https://muratbuffalo.blogspot.com/2025/02/smart-casual-verification-of.html). The authors started with an existing implementation of a secure consensus protocol. Their situation was like mine in 2020 (new specs of a big old C++ program) and so was their goal: to continuously check conformance and keep the spec and implementation in sync. Using [the new TLC features](https://groups.google.com/d/msgid/tlaplus/2443fd1a-1c35-419a-95b8-72de361f28bdn%40googlegroups.com) announced in the "Validating Traces" paper above, they toiled for months, brought their specs and code into line, found some bugs, and realized the eXtreme Modelling vision.  
* [Finn Hackett](https://fhackett.com/) is a PhD student I'm mentoring, he's developed [a TLA+-to-Go compiler](https://www.cs.ubc.ca/~bestchai/papers/asplos23-pgo.pdf). He's now prototyping a trace-checker to verify that the Go code he produces really conforms to its source spec. We're doing a summer project together with [Antithesis](/notes-from-antithesis-bugbash/) to thoroughly conformance-check the implementation's state space.

I'm excited to see growing interest in conformance checking, because I think it's a serious problem that needs to be solved before TLA+ goes mainstream. The "Validating Traces" paper announced some new trace-checking features in TLC, and TLC's developers are [discussing a better way to export a state graph for test-case generation](https://github.com/tlaplus/tlaplus/issues/1073). I hope these research prototypes lead to standard tools, so engineers can keep their code and specs in sync.
