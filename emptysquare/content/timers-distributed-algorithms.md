+++
type = "post"
title = "Can We Rely On Timers For Distributed Algorithms?"
description = "I think the answer is yes, and I calculate the worst-case drift."
category = ["Research"]
tag = ["distributedsystems"]
draft = true
enable_lightbox = true
+++

![](clock3.jpg)

Leader-based consensus protocols like Raft try to elect one leader at a time, but it's possible to have multiple leaders for a short period. The classic cause of multiple leaders is a network partition: some server *S*<sub>0</sub> is the leader, then a network partition cuts it off from a majority of its peers, who elect a new leader *S*<sub>1</sub>, but *S*<sub>0</sub> still thinks it's in charge. (In theory, in a Raft group of 2*f*+1 servers, as many as *f* can be leaders at once!) In this situation, you risk violating [read-your-writes](https://jepsen.io/consistency/models/read-your-writes):

* A client updates some data on *S*<sub>1</sub>.
* *S*<sub>1</sub> majority-replicates the change and acknowledges it to the client.
* The same client reads the same data from *S*<sub>0</sub> and doesn't see its update.

A Raft leader always suspects that it's been deposed, so it acts paranoid, checking with a majority of the group before executing any query ([Raft paper](https://raft.github.io/raft.pdf) §8). This guarantees read-your-writes: the leader either confirms it was the newest leader at some point between receiving the query and responding, or else the leader discovers a newer leader, rejects the query, and steps down. But this guarantee comes at a high cost in communication latency.

Early research into distributed systems assumed an [_asynchronous system model_](https://citeseerx.ist.psu.edu/document?repid=rep1&type=pdf&doi=efc1ff91bc301c3d6344cb308b4f619914a0e871): servers have no access to clocks or timers, and any task or message can take an unbounded amount of time. This is a very general model, but it's hostile to distributed algorithms. In fact, in this model, no protocol is guaranteed to reach consensus on any decision in bounded time ([_FLP impossibility_](https://www.the-paper-trail.org/post/2008-08-13-a-brief-tour-of-flp-impossibility/)). I believe this means no protocol can both 1) always eventually elect one leader and 2) prevent multiple concurrent leaders. This is what makes Raft leaders paranoid.

But what if the asynchronous system model isn't accurate? Let's change one assumption: let's say servers have access to reliable timers. This is the [_timed asynchronous system model_](https://www.computer.org/csdl/journal/td/1999/06/l0642/13rRUwbs2fY). It allows us to use _leader leases_ to guarantee one leader at a time: a server receives promises from a majority of nodes that they won't permit another leader to take charge until some timeout has elapsed. Until then, the leaseholder can serve queries without communicating with its peers.

At the [MongoDB Distributed Systems Research Group](https://www.mongodb.com/company/research/distributed-systems-research-group) we're developing lease protocols for Raft and for MongoDB, so I'm curious how reliable timers are in real life. Below is the result of a few days of research and thinking. My conclusion is, max clock drift is about a millisecond per second. So after a timer expires on one server, if you wait a little extra, you can be sure it has expired on all servers.

![](clock1.jpg)

# Leases in Raft

In [Diego Ongaro's thesis](https://github.com/ongardie/dissertation), he proposes a simple lease mechanism for Raft. The leader starts a timer at time _t_, and sends heartbeat messages to all its followers. Once a majority has responded, the leader knows they won't vote for another leader until _t_ + _election timeout_ * _&epsilon;_, where _&epsilon;_ is the maximum rate of clock drift. Here's Figure 6.3 from Ongaro's thesis:

![](raft-lease.png)

At MongoDB we made a more sophisticated lease algorithm that improves availability. Stay tuned for our research paper. But just like Ongaro's, our algorithm needs to know the maximum rate at which any two servers' timers could drift apart.

![](clock2.jpg)

# Timer uncertainty

Leases guarantee consistency if we can enforce this rule:

> **Timer Rule:**
>
> Let's say server *S*<sub>0</sub> starts a timer *t*<sub>0</sub>,<br>
> then sends a message to server *S*<sub>1</sub>,<br>
> which receives the message and starts a timer *t*<sub>1</sub>. 
> 
> If *S*<sub>1</sub> thinks *t*<sub>1</sub> is ≥ *election timeout* * _&epsilon;_ old,<br>
> then *S*<sub>0</sub> thinks *t*<sub>0</sub> is ≥ *election timeout* old.

We should make the safety margin _&epsilon;_ large enough to guarantee this, but not unnecessarily large (which would hurt availability). Here are some sources of uncertainty:

![](clock4.jpg)

## Clock frequency error, a.k.a. "drift"

Any server's timer depends on a quartz oscillator ("XO") on its motherboard, even if the server is a VM. All XOs are manufactured with some inaccuracy, and their speed is affected by age and temperature. XOs slow down if they're too cold **or** too hot! Cloud providers control temperature fairly well in their data centers and they swap out components periodically, but not all servers are so well cared for.

NTP clients (ntpd or the more modern chronyd) measure oscillator drift over time (even across reboots) and compensate for it, [*disciplining* the oscillator to near-perfection](https://www.eecis.udel.edu/~mills/ntp/html/discipline.html). In the last couple years, [cloud providers have achieved clock synchronization within tens of microseconds](https://aws.amazon.com/about-aws/whats-new/2023/11/amazon-time-sync-service-microsecond-accurate-time/), implying minuscule clock drift. However, for maximum safety let's assume that NTP isn't functioning at all. The servers' timers are undisciplined and freely drifting.

It's weirdly hard to find the model numbers for XOs commonly used in servers, but I think I found some examples ([1](https://www.ti.com/document-viewer/LMK3H0102/datasheet), [2](https://abracon.com/Oscillators/ASEseries.pdf), [3](https://ecsxtal.com/store/pdf/ECS-2520MV.pdf)). They usually advertise a maximum drift of ±50 ppm (parts per million) over a vast range of operating temperatures. (See [this formula](https://en.wikipedia.org/wiki/Crystal_oscillator#Temperature_effects) for the accuracy of XOs in general.) This matches the [50 ppm value](https://github.com/aws/clock-bound/blob/main/clock-bound-d/README.md#chrony-configuration) that the AWS ClockBound engineers consider worst-case.

![](clock5.jpg)

## Clock slewing

When ntpd or chronyd make routine clock adjustments, they *slew* it gradually to the correct time instead of *stepping* it discontinuously. The max slew rate for ntpd is 500 ppm hardcoded, for chronyd it's 1000 ppm configurable.

Every few years the authorities announce a [leap second](https://en.wikipedia.org/wiki/Leap_second) to account for recent unpredictable changes in the earth's rotation. It is announced 6 months ahead. Leap seconds [will probably be canceled starting in 2035](https://engineering.fb.com/2022/07/25/production-engineering/its-time-to-leave-the-leap-second-in-the-past/), in favor of a leap *hour* every few thousand years. If there are any leap seconds before 2035, different time providers may unfortunately implement them differently. AWS and GCP are likely to slew the clock for 24 hours (a 7 ppm slew rate) and Azure [may ignore the leap second](https://www.libertysys.com.au/2024/03/mister-cloud-part-3/#not-leap-smeared), introducing a 7 ppm discrepancy between timers in Azure and non-Azure during the 24 hours. But we can ignore leap seconds; we only care about the max slew rate, regardless of the reason for slewing.

Bottom line: the max slew rate is 1000 ppm.

![](clock6.jpg)

## VM interruptions

Hypervisors have *paravirtual clocks*: the VM's clock is a passthrough to the host clock, so when the VM wakes from a pause its clock is still up to date. AWS and GCP use the KVM hypervisor, which has [kvm-clock](https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/7/html/virtualization_deployment_and_administration_guide/chap-kvm_guest_timing_management). Azure uses [Hyper-V, which has VMICTimeSync](https://learn.microsoft.com/en-us/azure/virtual-machines/linux/time-sync#:~:text=Virtual%20machine%20interactions%20with%20the,in%20Linux%20VMs%20to%20compensate). Xen is going out of style, but it has something poorly documented called pvclock. If a VM pauses and resumes, its paravirtual clock won't be affected. If it's [live-migrated to a different physical host](https://learn.microsoft.com/en-us/azure/virtual-machines/maintenance-and-updates#maintenance-that-doesnt-require-a-reboot), then presumably the accuracy of its timers across the migration depends on the clock synchronization between the source host and target host. Major cloud providers now sync their clocks to within a millisecond, usually much less.

[Martin Kleppmann warns](https://martin.kleppmann.com/2016/02/08/how-to-do-distributed-locking.html) about checking a timer and then acting upon the result: your VM could be paused indefinitely between the check and the action. But his article is about mutual exclusion with a lease, and we're just trying to guarantee linearizability. For linearizability, the server only needs to be a leaseholder *sometime* between receiving a request and replying.

![](clock6.jpg)

# So what's &epsilon;?

Ideally, clock slewing cancels out frequency error to approximately zero. After all, the NTP client slews the clock in order to get it back in sync. But let's pessimistically assume that clock slewing *adds* to frequency error. The sum of the errors above is 50 ppm (max frequency error) + 1000 ppm (chronyd's max slew rate) = 1050 ppm. If two servers' clocks are drifting apart as fast as possible, that's 2100 ppm. So if we set *&epsilon;* = 1.0021, we'll definitely obey the Timer Rule above. For example, if *election timeout* is 5 seconds (MongoDB's default in [Atlas](https://www.mongodb.com/products/platform/atlas-database)), this means waiting an extra 11 ms to be sure. 

![](clock7.jpg)

# How important is &epsilon;?

We could probably get away with ignoring drift, and set *&epsilon;* = 1, and still never violate the Timer Rule. Recall the scenario I care about: *S*<sub>0</sub> starts a timer and sends a message to *S*<sub>1</sub>, which starts its own timer. *S*<sub>1</sub>'s timer mustn't expire before *S*<sub>0</sub>'s. There's some builtin safety already, because *S*<sub>1</sub>'s timer will _start_ after *S*<sub>0</sub>'s. The delay depends on network latency and processing time on each server; it will probably be much larger than timer inaccuracy.

If we rely on leases for consistency, then even if *S*<sub>1</sub> thinks its timer expires too soon, it's still hard to observe a consistency violation. There's only a short time while *S*<sub>0</sub> thinks it still has a lease, but *S*<sub>1</sub> thinks *S*<sub>0</sub>'s lease expired. During this window all the following must happen:

* *S*<sub>1</sub> runs for election, and wins.
* *S*<sub>1</sub> receives a write command, majority-replicates it, and acknowledges it to the client.
* *S*<sub>0</sub> receives a query for some data that was just overwritten on *S*<sub>1</sub>.
* *S*<sub>0</sub>, thinking it still has a lease, runs the query on stale data and replies. 

This sequence would violate read-your-writes. It's hard to imagine all those events in the milliseconds or microseconds between the two timers' expirations. It seems more likely to me that the Timer Rule is violated, not because &epsilon; is a smidgen too small, but because some misconfiguration makes a timer wildly inaccurate. 

In MongoDB's version of Raft, the violation is even less likely, because the MongoClient [will know that *S*<sub>0</sub> has been deposed](https://github.com/mongodb/specifications/blob/master/source/server-discovery-and-monitoring/server-discovery-and-monitoring.md#using-electionid-and-setversion-to-detect-stale-primaries). You have to use multiple MongoClients, or restart your client application, to lose this information and observe the consistency violation. See [my causal consistency article](/how-to-use-mongodb-causal-consistency/) for a technique to handle this case.

In summary, a user would have to be very unlucky to observe a consistency violation with leases: they'd need a Raft group with two leaders due to a network partition, but the user can talk to both sides. They'd have to use two clients (to disable MongoClient's deposed leader check), write to the new leader, and quickly read the overwritten data from the old leader. The old leader would have to somehow fail to step down, while the new leader won election surprisingly quickly. And finally, the lease mechanism would have to fail because clock frequency error was worse than &epsilon;.

In meta-summary, I think distributed systems implementors should rely on timers more. Whenever I discuss leases with engineers, the first question is, "Can we rely on timers?" It's good to ask this question, but sometimes we have to take "yes" for an answer.

![](clock8.jpg)

***

Images: [Wellcome Collection](https://wellcomecollection.org/).
