+++
category = ["Research"]
date = "2025-12-18T23:27:58.747169+00:00"
description = "A new Raft enhancement for fast, consistent reads."
draft = false
enable_lightbox = true
tag = ["distributedsystems"]
thumbnail = "plate_21_19_27.jpeg"
title = "LeaseGuard: Raft Leases Done Right!"
type = "post"
+++

{{< figure src="plate_21_19_27.jpeg" alt="Black-and-white engraved plate from a historical horology treatise, showing multiple labeled diagrams of a complex mechanical clock or watch. The page is divided into numbered figures: circular clock dials with Roman numerals and concentric scales; exposed views of internal mechanisms with gears, pinions, levers, cams, and springs; and isolated components shown from different angles. Fine cross-hatching and lettered annotations identify parts. A French title at the bottom reads Horlogerie, indicating a clock with alarm, equation of time, concentric seconds, and displays for months and lunar quarters." >}}

Many distributed systems have a *leader-based consensus protocol* at their heart. The protocol elects one server as the "leader" who receives all writes. The other servers are "followers," hot standbys who replicate the leader's data changes. Paxos and Raft are the most famous leader-based consensus protocols.

These protocols ensure consistent [state machine replication](https://en.wikipedia.org/wiki/State_machine_replication), but reads are still tricky. Imagine a new leader \(L_1\) is elected, while the previous leader \(L_0\) thinks it's still in charge. A client might write to \(L_1\), then read stale data from \(L_0\), violating [Read Your Writes](https://jepsen.io/consistency/models/read-your-writes). How can we prevent stale reads? [The original Raft paper](https://raft.github.io/raft.pdf) recommended that the leader communicate with a majority of followers before each read, to confirm it's the real leader. This guarantees Read Your Writes but it's slow and expensive.

A *leader lease* is an agreement among a majority of servers that one server will be the only leader for a certain time. This means the leader can run queries without communicating with the followers, and still ensure Read Your Writes. The original description of Raft included a lease protocol that was inherited from the earlier Paxos, where followers refuse to vote for a new leader until the old leader's lease expires. This entangles leases and elections, and it delays recovery after a crash. Besides, lease protocols have never been specified in detail, for either Raft or Paxos. For all these reasons, many Raft implementations don't use leases at all, or their <a href="https://github.com/etcd-io/raft/issues/166" style="text-decoration: underline">leases</a> <a href="https://github.com/hashicorp/raft/issues/108" style="text-decoration: underline">are</a> <a href="https://aphyr.com/posts/316-jepsen-etcd-and-consul" style="text-decoration: underline">buggy</a>.

In the MongoDB Distributed Systems Research Group, we designed a simple lease protocol tailored for Raft, called LeaseGuard. Our main innovation is to rely on Raft-specific guarantees to design a simpler lease protocol that recovers faster from a leader crash.

[Here's a preprint of our SIGMOD &rsquo;26 paper](https://arxiv.org/abs/2512.15659). This is a joint blog post by [Murat Demirbas](http://muratbuffalo.blogspot.com/) and me, published on both of our blogs.

## A huge simplification: the log is the lease

In Raft, before the leader executes a write command, it wraps the command in a *log entry* which it appends to its *log*. Followers replicate the entry by appending it to their logs. Once an entry is in a majority of servers' logs, it is *committed*. Raft's Leader Completeness property guarantees that any newly elected leader has all committed entries from previous leaders. Raft enforces this during elections: a server votes only for a candidate whose log is at least as up to date as its own. (Paxos doesn't have this property, so a new leader has to fetch entries from followers before it's fully functional.)

When designing LeaseGuard, we used Leader Completeness to radically simplify the lease protocol. LeaseGuard does not use extra messages or variables for lease management, and does not interfere with voting or elections. 

In LeaseGuard, *the log is the lease*. Committing a log entry grants the leader a lease that lasts until a timeout expires. While the lease is valid, the leader can serve consistent reads locally. Because of Leader Completeness, any future leader is guaranteed to have that same entry in its log. When a new leader \(L_1\) is elected, it checks its own log for the previous leader \(L_0\)'s last entry, to infer how long to wait for \(L_0\)'s lease to expire.

In existing protocols, the log is not the lease: instead, the leader periodically sends a message to followers which says, "I still have the lease." But imagine a leader who couldn't execute writes or append to its log—perhaps it's overloaded, or its disk is full or faulty—but still has enough juice to send lease-extension messages. This lame-duck leader could lock up the whole system. In LeaseGuard, a leader maintains its lease only if it can make progress; otherwise, the followers elect a new one.

We're excited by the simplicity of this Raft-specific lease protocol. (We were inspired by some prior work, [especially this forum post from Archie Cobbs](https://groups.google.com/g/raft-dev/c/oO0NfgUVrjg/m/R1BnnbNcAwAJ).) In LeaseGuard, there is no separate code path to establish the lease. We decouple leases from elections. The log is the single source of truth for both replication and leasing.

## LeaseGuard makes leader failovers smoother and faster

Leases improve read consistency but can slow recovery after a leader crash. No matter how quickly the surviving servers elect a new leader, it has to wait for the old leader's lease to expire before it can read or write. The system stalls as long as 10 seconds in one of the Raft implementations we studied.

LeaseGuard improves the situation in two ways. First, *deferred-commit writes*. As soon as a new leader wins election, it starts accepting writes and replicating them to followers. It just defers marking any writes "committed" until the old lease expires. Without this optimization, writes enqueue at the new leader until the old lease expires; then there's a thundering herd. With our optimization, the new leader keeps up with the write load even while it's waiting.

Second, *inherited lease reads*. This is our biggest innovation, and it's a bit complicated. Consider the situation where \(L_1\) was just elected, but \(L_0\) is alive and still thinks it's in charge. Neither leader knows about the other. (Yes, this can <a href="https://www.usenix.org/system/files/osdi18-alquraan.pdf" style="text-decoration: underline">really</a> <a href="https://aphyr.com/posts/288-the-network-is-reliable" style="text-decoration: underline">happen</a> during a network partition.) Raft makes sure that \(L_0\) can't commit any more **writes**, but there's a danger of it serving stale **reads**. The whole point of leases is to prevent that, by blocking \(L_1\) from reading and writing until \(L_0\)'s lease expires. But what if there was a way for **both** leaders to serve reads, and still guarantee Read Your Writes?

When \(L_1\) was elected, it already had all of \(L_0\)'s committed log entries (Leader Completeness), and maybe some newer entries from \(L_0\) that aren't committed yet. ***L*****1 knows it has every committed entry, but it doesn't know which ones are committed\!** We call these ambiguous entries the *limbo region*. For each query, \(L_1\) checks if the result is affected by any entries in the limbo region—if not, \(L_1\) just runs the query normally. Otherwise, it waits until the ambiguity is resolved. (My MongoDB colleague Lingzhi Deng is the one who saw the need for this check, which is how he became a co-author.)

{{< figure src="limbo-range-blog.svg" caption="Logs on the old and new leader. Entries 1-5 were committed by <em>L</em><sub>0</sub>&#8202;, and <em>L</em><sub>1</sub> has them all, but it only knows that 1-3 are committed. It may not learn whether 4-6 are committed until it tries to commit an entry of its own." >}}

Inherited lease reads require synchronized clocks with known error bounds, but the rest of the protocol only needs [local timers with bounded drift](/timers-distributed-algorithms/). Our two optimizations preserve Read Your Writes and dramatically improve availability.

{{< figure src="availability.svg" caption="Transitions in the read/write availability of leaders with LeaseGuard. While the new leader waits for a lease, it can serve some consistent reads and accept writes. Meanwhile the old leader serves reads." alt="A flowchart showing when leaders can read or write with leases. There are two leaders. At first, Leader 1 can execute reads and writes. Then Leader 2 is elected. Now Leader 1 can execute only reads, while Leader 2 can execute reads unaffected by the limbo region, and it can stage writes. Once Leader 1's lease expires, Leader 2 can execute reads and writes freely." >}}

Here's the whole algorithm in pseudo-Python. For more details, read the paper.

<style>
.leaseguard-comment { color:#99A9A5 }
.leaseguard-keyword { color:#307919 }
.leaseguard-variable { color:#0000F5 }
.leaseguard-string { color:#AE3832 }
.leaseguard-infix { color:#9B2DF5 }
</style>

<pre>
<code>
<span class="leaseguard-comment"># Handle a write request from a client.</span>
<span class="leaseguard-keyword">def</span> <span class="leaseguard-variable">ClientWrite</span>(command):
    <span class="leaseguard-keyword">if</span> self.state != <span class="leaseguard-string">&quot;leader&quot;</span>: <span class="leaseguard-keyword">return</span> <span class="leaseguard-string">&quot;not leader&quot;</span>
    <span class="leaseguard-comment"># Create new entry, log it and record its index.</span>
    entry = (self.term, command, intervalNow())
    index = self.log.append(entry)
    <span class="leaseguard-comment"># Another thread replicates, commits, and applies the</span>
    <span class="leaseguard-comment"># command, and advances lastApplied, see CommitEntry.</span>
    <span class="leaseguard-keyword">await</span>(self.lastApplied &gt;= index)
    <span class="leaseguard-keyword">if</span> self.state != <span class="leaseguard-string">&quot;leader&quot;</span>:
        <span class="leaseguard-comment"># Deposed, don't know if command succeeded.</span>
        <span class="leaseguard-keyword">return</span> <span class="leaseguard-string">&quot;not leader&quot;</span>
    <span class="leaseguard-keyword">return</span> <span class="leaseguard-string">&quot;ok&quot;</span>


<span class="leaseguard-comment"># Handle a read request from a client for key k.</span>
<span class="leaseguard-keyword">def</span> <span class="leaseguard-variable">ClientRead</span>(k):
    <span class="leaseguard-keyword">if</span> self.state != <span class="leaseguard-string">&quot;leader&quot;</span>: <span class="leaseguard-keyword">return</span> <span class="leaseguard-string">&quot;not leader&quot;</span>
    <span class="leaseguard-comment"># Last committed entry's age is calculated using</span>
    <span class="leaseguard-comment"># bounded-uncertainty clock.</span>
    <span class="leaseguard-keyword">if</span> self.log[self.commitIndex].age &gt; delta:
        <span class="leaseguard-keyword">return</span> <span class="leaseguard-string">&quot;no lease&quot;</span>
    <span class="leaseguard-comment"># Prevent &quot;limbo&quot; reads.</span>
    <span class="leaseguard-keyword">if</span> self.term != self.log[self.commitIndex].term:
        <span class="leaseguard-keyword">if</span> any limbo region entry affects k:
            <span class="leaseguard-keyword">return</span> <span class="leaseguard-string">&quot;key affected by limbo region&quot;</span>
    <span class="leaseguard-keyword">return</span> self.data[k]


<span class="leaseguard-comment"># When this node learns some followers have replicated</span>
<span class="leaseguard-comment"># entries up to index i, advance the commitIndex.</span>
<span class="leaseguard-keyword">def</span> <span class="leaseguard-variable">CommitEntry</span>(i):
    <span class="leaseguard-keyword">if</span> self.state != <span class="leaseguard-string">&quot;leader&quot;</span>: <span class="leaseguard-keyword">return</span>
    <span class="leaseguard-keyword">if</span> <span class="leaseguard-infix">not</span> majorityAcknowledged(self.log[i]):
        <span class="leaseguard-keyword">return</span>
    <span class="leaseguard-comment"># Check for past-term entry &lt; Delta old.</span>
    <span class="leaseguard-comment"># In reality this loop is optimized away, Sec. 7.</span>
    <span class="leaseguard-keyword">for</span> e <span class="leaseguard-infix">in</span> self.log:
        <span class="leaseguard-keyword">if</span> e.term &lt; self.term <span class="leaseguard-keyword">and</span> e.age &lt; delta:
            <span class="leaseguard-keyword">return</span>
    self.commitIndex = max(self.commitIndex, i)
    <span class="leaseguard-keyword">while</span> self.lastApplied&lt;self.commitIndex:
        apply(self.log[self.lastApplied+1].command)
        self.lastApplied += 1
</code>
</pre>

## Tests and benchmarks

When we started this research, our main goal was to publish a detailed and correct specification, so Raft implementers everywhere could implement leases without bugs. We're [TLA+ fans](https://www.mongodb.com/company/blog/engineering/conformance-checking-at-mongodb-testing-our-code-matches-our-tla-specs) so obviously we [specified the algorithm in TLA+](https://github.com/muratdem/RaftLeaderLeases/blob/main/TLA/leaseGuard.tla) and checked it guaranteed Read Your Writes and other correctness properties. We discovered our two optimizations while writing the TLA+ spec. The inherited lease reads optimization was especially surprising to us; we probably wouldn't have realized it was possible if TLA+ wasn't helping us think.

We implemented the algorithm [in LogCabin](https://github.com/mongodb-labs/logcabin/tree/leaseguard), the C++ reference implementation of Raft. (For ease of exposition, we also provide an implementation in [a Python simulator](https://github.com/muratdem/RaftLeaderLeases/tree/main/Python).) 

In the following experiment, we illustrate how LeaseGuard improves throughput and reduces time to recovery. We crash the leader 500 ms after the test begins. At the 1000 ms mark, a new leader is elected, and at 1500 ms, the old leader's lease expires. We ran this experiment with LogCabin in five configurations:

* **Inconsistent:** LogCabin running fast and loose, with no guarantee of Read Your Writes.  
* **Quorum:** The default Read Your Writes mechanism, where the leader talks to a majority of followers before running each query, is miserably slow—notice that its Y axis is **one tenth** as high as the other charts\!  
* **Lease:** The "log is the lease" protocol with no optimizations. Its throughput is as high as "inconsistent", but it has a long time to recovery after the old leader crashes.  
* **Defer commit:** The log is the lease, plus our write optimization—you can see that write throughput spikes off the chart at 1500 ms, because the leader has been processing writes while waiting for the lease. As soon as it gets the lease, it commits all the writes at once.  
* **Inherit lease:** LeaseGuard with all our optimizations. Read throughput recovers as soon as a new leader is elected, without waiting for the old lease to expire.

{{< figure src="unavailability_experiment_logcabin.svg" caption="How fast does the system recover after a leader crash?" >}}

## Conclusion

Until now, the absence of a detailed specification for Raft leases led to many flawed implementations: they often failed to guarantee consistent reads, had very low read throughput, or recovered slowly from a leader crash. With LeaseGuard now specified, implemented, and published, we hope it will be readily adopted to enable Raft systems to provide fast reads with strong consistency and recover quickly after a crash.

We learned yet again the value of TLA+ during this project. TLA+ is useful not just for checking the correctness of a completed design, but for revealing new insights while the design is in progress. Also, we got interested in [reasoning about knowledge](/series/knowledge/), also known as epistemic logic. In Raft, servers can look in their logs and know that other servers know certain facts. For example, if a leader has a committed entry, it knows any future leader knows about this entry, but it doesn't know if a future leader knows the entry was *committed*. This is a different way for us to think about a distributed system: it's not just a state machine, it's a group of agents with limited knowledge. We're curious about this way of thinking and plan to do more research.

***

[Image: _Horlogerie_, 1765, Diderot and d'Alembert.](https://www.encyclopediaofdiderot.org/s/diderot/item/233773)
