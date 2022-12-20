+++
category = ["Review"]
date = "2022-12-20T12:00:21.944100"
description = "Faster replication through the magic of partial order."
draft = false
enable_lightbox = true
tag = ["distributedsystems"]
thumbnail = "rex-06.png"
title = "Paper Review: Rex: Replication at the Speed of Multi-core"
type = "post"
+++

[Rex: Replication at the Speed of Multi-core](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/ppaxos.pdf) by Zhenyu Guo, Chuntao Hong, Mao Yang, Dong Zhou, Lidong Zhou, and Li Zhuang at EuroSys 2014.

Like the [C5 paper](/review-c5/) I just reviewed, Rex is about improving asynchronous replication performance on multi-core, but I thought the C5 paper was humdrum whereas Rex is thought-provoking.

![](rex-05.png)

<p style="text-align: center"><span style="color: gray">Warm up your neurons because they're going to get a workout.</span></p>

# Background

Usually in asynchronous replication, one server is the leader for a while and makes modifications to its data. It logs these modifications in a sequence, which it streams to followers. They replay these modifications to their copies of the data, in the same order. Thus there is a <u>total order</u> of states; any state that the leader passes through is eventually reflected on each follower in the same order. Clients can read from the leader or followers, and they'll see the same sequence of states, although the followers may lag.

![](asynchronous-replication.png)

So far so good. Distributed Systems 101.

But what if it didn't have to be that way?

![](rex-06.png)

<p style="text-align: center"><span style="color: gray">Galaxy brain.</span></p>

# Partial-Order Replication

The Rex paper's insight is, the leader only needs to guarantee a <u>partial</u> order of events. On the leader if two transactions are running on concurrent threads t<sub>1</sub> and t<sub>2</sub> and they attempt to modify the same data _x_, some concurrency protocol decides the outcome. For example, if your database wants to guarantee [serializability](https://jepsen.io/consistency/models/serializable), it might use [two-phase locking](https://en.wikipedia.org/wiki/Two-phase_locking). Let's say t<sub>1</sub> gets the write-lock L on _x_ first and updates _x_, then unlocks L. Then, t<sub>2</sub> locks L, updates _x_, and unlocks L. This sequence of events guarantees that t<sub>1</sub>'s write [happens-before](https://en.wikipedia.org/wiki/Happened-before) t<sub>2</sub>'s, and the value of _x_ after both transactions commit is the value t<sub>2</sub> wrote.

(Forgive me, this will get interesting in a second.)

![](lock-order-1.png)

<p style="text-align: center"><span style="color: gray">I adapted this from the author's Figure 2.</span></p>

On the other hand if a pair of threads t<sub>3</sub> and t<sub>4</sub> write to disjoint data, they'll share no locks and their writes are <u>concurrent</u>: neither one happened before or after the other.

(OK, now it's going to get interesting.)

The Rex leader logs all the lock/unlock events executed by t<sub>1</sub>, t<sub>2</sub>, t<sub>3</sub>, and t<sub>4</sub>. But it does <u>not</u> decide what order they occur! It only logs that t<sub>1</sub>'s unlock happens-before t<sub>2</sub>'s lock, then streams that information to the followers. So followers learn about a <u>partial</u> order of lock/unlock events, and replay them in some order that matches the leader's partial order. Each follower is free to replay them in whatever order it wants so long as it obeys the rule, "t<sub>1</sub> unlocks L before t<sub>2</sub> locks L". Thus followers can execute with as much parallelism as the leader did, allowing higher throughput than if they had to execute the writes in some total order.

My example above is for a database that guarantees serializability, and its mechanism is two-phase locking. But any guarantee and any mechanism would work with Rex. The point is that the primary decides what happens-before relationships must be obeyed, and the followers obey them.

The Rex authors observe that followers in most systems suffer low parallelism, because they're obeying a <u>total</u> order for the sake of consistency, but:

> This tension between concurrency and consistency is not inherent because the total ordering of requests is merely a simplifying convenience that is unnecessary for consistency.

We'll revisit this claim below; I have concerns about "consistency".

![](rex-01.png)

# Capturing Partial Order

How does the leader learn the partial order of writes and transmit it to the followers? In Rex, locks are wrapped with a shim which captures happens-before relationships on the leader, and enforces them on the followers. The Rex authors call these relationships "causal edges":

```c++
// Pseudocode of the Lock and Unlock wrappers.
class RexLock {
public:
  void Lock() {
    if (env::local_thread_mode == RECORD) {
      AcquireLock(real_lock);
      RecordCausalEdge();
    } else if (env::local_thread_mode == REPLAY) {
      WaitCausalEdgesIfNecessary();
      AcquireLock(real_lock);
    }
  }

  void Unlock() {
    if (env::local_thread_mode == RECORD) {
      RecordCausalEdge();
    }
    ReleaseLock(real_lock);
  }
};
```

So if t<sub>1</sub> unlocks L on the leader and then t<sub>2</sub> locks it, L records that the second event depends on the first, in `RecordCausalEdge`. Rex sends this information to the followers, who wait for t<sub>1</sub> to unlock L before t<sub>2</sub> locks it, with `WaitCausalEdgesIfNecessary`. This happens whether t<sub>2</sub> actually has to wait to lock L on the leader, or just locks L some time after t<sub>1</sub> unlocks it.

The paper doesn't describe the exact format of the log, but the log somehow expresses which threads executed which operations, and the order in which they acquired and released every lock. Visually it's a [DAG](https://en.wikipedia.org/wiki/Directed_acyclic_graph):

![](lock-order-2.png)

The lines labeled "c<sub>1</sub>" and "c<sub>2</sub>" are two possible cuts through the DAG. The authors say:

> A cut is _consistent_ if, for any causal edge from event e<sub>1</sub> to e<sub>2</sub> in the trace, e<sub>2</sub> being in the cut implies that e<sub>1</sub> is also included in the cut. An execution reaches only consistent cuts. Figure 2 shows two cuts c<sub>1</sub> and c<sub>2</sub>, where c<sub>1</sub> is consistent, but c<sub>2</sub> is inconsistent.

"Consistent" here seems a bad choice of jargon, we've so overloaded that poor word already. In any case, a cut is ready to be packed up and shipped to the secondaries so long as it doesn't slice across a causal edge the wrong way. If the primary sent all the events above c<sub>2</sub> to the secondary, the secondary thread t<sub>1</sub> would be stuck at its event 4, because it's waiting for t<sub>2</sub>'s event 3, which isn't included in the cut. No such hangup occurs if the primary uses the "consistent" cut c<sub>1</sub>.

For this definition to work, imagine that each cut includes all events to the beginning of time. In practice, of course, the primary only has to send events that are in the newest cut and not in previous cuts.

![](rex-07.png)

# Annoying Details

I skimmed Section 3, which buries the reader in Paxos junk. It describes how leaders are demoted or elected, how servers are added or removed, how intermediate states are checkpointed for the purposes of crash-recovery, rollback, and garbage collection. I sympathize with the authors: they had to describe their ideas in terms of Paxos, the main consensus protocol in 2014, and [Paxos has so much ambiguity and variation](/paxos-vs-raft/) that the authors must detail their choices about every aspect of the protocol. If they'd come just a bit later they could have built on Raft instead and taken a lot of these details for granted, focusing on their main contribution instead.

![](rex-04.png)

# My Evaluation

The Rex authors want to increase replication throughput by improving parallelism on secondaries. They claim Rex is "a new multi-core friendly replicated state-machine framework that achieves strong consistency while preserving parallelism in multi-thread applications." I agree that the protocol is multi-core friendly, but C5 is a simpler way to achieve that goal, and as in my [review of the C5 paper](/review-c5/), I'll warn that parallelism alone won't save you from replication lag.

What do the authors mean when they say Rex "achieves strong consistency"? That word is so pathologically abused, it has at least two meanings in this paper alone! In the sentence above, "consistency" seems to mean what we usually call "convergence": if you stop sending writes to the primary, eventually all replicas will have the same state. From a client's point of view this is "eventual consistency", and it's parsecs from the usual meaning of "strong consistency". See Pat Helland's [Don't Get Stuck in the "Con" Game](https://pathelland.substack.com/p/dont-get-stuck-in-the-con-game). I'll forgive the authors, there's been a lot of work since 2014 to clarify our jargon.

Leaving jargon aside, what's the user experience when querying a Rex secondary? There's no guarantee besides convergence. Independent events happen in different orders on different secondaries, temporarily producing states that never existed on the primary. Other systems such as MongoDB have weak guarantees on secondaries but we're able to build stronger consistency on top of them. For example, [MongoDB guarantees causal consistency on secondaries](https://www.mongodb.com/docs/manual/core/read-isolation-consistency-recency/#std-label-sessions) by reading at the majority-committed timestamp. We make this guarantee and <u>also</u> achieve high parallelism during replication (see the [C5 review](/review-c5/)), whereas this guarantee would be impossible with Rex.

The Rex paper expanded my mind with the idea of partial-order replication, but I don't immediately see a practical use for it. 

![](rex-02.png)

***

Images from [The Principles of Light and Color, Edwin D. Babbit 1878](https://archive.org/details/gri_c00033125011227010/).
