+++
category = ["Research"]
date = "2021-05-11T08:37:56.593394"
description = "Which consensus algorithm will win?"
draft = false
enable_lightbox = true
tag = ["distributedsystems", "best"]
thumbnail = "bennett-sisters.jpg"
title = "Paper review: Paxos vs Raft"
type = "post"
+++

![](bennett-sisters.jpg)

[Paxos vs Raft: Have we reached consensus on distributed consensus?](https://arxiv.org/pdf/2004.05074.pdf) Heidi Howard and Richard Mortier, [PaPoC 2020](https://papoc-workshop.github.io/2020/).

The Paxos algorithm, published by Leslie Lamport circa 1998, is foundational to distributed systems research and implementation. It permits a group of computers to reach consensus on a single decision, despite unreliable networks, failure-prone computers, and inaccurate clocks. The MultiPaxos variant permits a sequence of decisions: All computers in the group apply the same transitions to their identical state machines in the same order, thus eventually arriving at the same state. As Heidi Howard says, Paxos is "synonymous with distributed consensus". But Lamport first described it in [The Part-Time Parliament](http://lamport.azurewebsites.net/pubs/pubs.html#lamport-paxos) in an obfuscated literary style, which baffled readers then and has stymied comprehension ever since.

In 2014, Diego Ongaro and John Ousterhout presented Raft, a competing algorithm designed to solve the same problems more intelligibly. Indeed, they titled their paper [In Search of an Understandable Consensus Algorithm](https://raft.github.io/raft.pdf). They measured their students' ability to learn the algorithms and answer quiz questions, and found Raft was indeed more understandable than Paxos.

The distributed systems community is split between the two. Paxos has a head start but Raft might be overtaking it. It seems to me that recently-implemented systems are more likely to be Raft-based, and my (very approximate) count from Google Scholar shows more Raft citations in the last few years:

<table style="margin: auto; margin-bottom: 1em; font-size: 18px">
<thead>
<tr style="border-bottom: 1px solid black;">
<th></th>
<th>Paxos&nbsp;&nbsp;</th>
<th>Raft&nbsp;&nbsp;</th>
</tr>
</thead>

<tbody>
<tr>
<td>Citations</td>
<td>3600</td>
<td>1700</td>
</tr>

<tr>
<td>Citations since 2019&nbsp;&nbsp;</td>
<td>700</td>
<td>900</td>
</tr>
</tbody>
</table>

## Paxos and Raft are similar

In “Paxos vs Raft: Have we reached consensus on distributed consensus?”, Heidi Howard and Richard Mortier attempt to decide which is the better solution. Their main finding, however, is that Paxos and Raft are very similar. The paper takes MultiPaxos as the canonical variant of Paxos, and describes the common actions of that variant of Paxos and Raft:

- One of n servers is the leader. It accepts all writes and sends log entries to the followers.
- After a majority replicates an entry, the entry is "committed" and all members eventually apply the operation to their state machines.
- If the leader fails, a majority elects a new leader.

Both satisfy two essential properties, as described in the paper:

**State Machine Safety:** If a server has applied a log entry at a given index to its state machine, no other server will ever apply a different log entry for the same index.

**Leader Completeness:** If an operation op is committed at index i by a leader in term t then all leaders of terms > t will also have operation op at index i.

For me, one of the great values of the paper is this explanation of the two algorithms' shared foundation. From this perspective they're both simple, and similar. Since I know Raft much better than Paxos, this was the best Paxos description I've read so far. In the coming years, as more people learn Raft first, this "Paxos for Rafters" explanation will become even more valuable.

## Digression

My MongoDB colleague Siyuan Zhou pointed me to a complementary paper, [On the Parallels between Paxos and Raft, and how to Port Optimizations](https://dl.acm.org/doi/pdf/10.1145/3293611.3331595) (2019). It's a good read for anyone who wants to compare the two algorithms. Like Howard and Mortier, the authors of this paper observe that "in recent years, Raft has gradually overtaken Paxos as the consensus protocol of choice, esp. in the industry". They want to formally define how similar the two algorithms are, in [TLA+](https://lamport.azurewebsites.net/tla/tla.html). They claim that Raft could be considered a [refinement](https://www.microsoft.com/en-us/research/publication/the-existence-of-refinement-mappings) of Paxos. In fact, Raft genuinely differs from Paxos, but the authors consider these differences "superficial". They construct a new algorithm called Raft* by updating Raft to be more Paxosish in two ways:

**Elections:** Raft ensures a server can win election only if its log includes all committed entries. The winner will tend to be even more up-to-date than that, since servers vote only for candidates at least as up-to-date as themselves. In Paxos and Raft*, any server can win election. The winner transfers missing log entries from its peers before becoming leader. (This is not a "superficial" difference in my opinion; I'll say more below.)

**Log replication:** In Raft, all servers' copies of a log entry have the same index, term, and value. Paxos and Raft* can overwrite the term (aka "ballot number") of an index entry.

Once they've created Raft* and a TLA+ refinement mapping from Paxos, the authors can easily port optimizations from Paxos to Raft*. They show how to do it as a somewhat mechanical task in TLA+, and apply their method to two optimizations: Paxos Quorum Lease reads (a more efficient way to do linearizable reads) and Mencius (a sort of multi-master Paxos where more than one server accepts writes).

End of digression, back to the main paper, "Paxos vs Raft".

![](duel.png)

## Raft's advantages

According to Howard and Mortier, Raft's three benefits over Paxos are its presentation, its simplicity, and its efficient leader election protocol.

### Presentation

Leslie Lamport first explained Paxos, in "The Part-Time Parliament", as if he were describing the legislature of an ancient society. Further obscuring his meaning, he presented the paper as the recently rediscovered notes of an elusive archeologist, with commentary by the computer scientist [Keith Marzullo](https://en.wikipedia.org/wiki/Keith_Marzullo). In 2012, [Lamport recollected his error](https://www.microsoft.com/en-us/research/publication/part-time-parliament/):

> Inspired by my success at popularizing the consensus problem by describing it with Byzantine generals, I decided to cast the algorithm in terms of a parliament on an ancient Greek island. Writing about a lost civilization allowed me to eliminate uninteresting details and indicate generalizations by saying that some details of the parliamentary protocol had been lost. To carry the image further, I gave a few lectures in the persona of an Indiana-Jones-style archaeologist, replete with Stetson hat and hip flask.
>
> My attempt at inserting some humor into the subject was a dismal failure. People who attended my lecture remembered Indiana Jones, but not the algorithm. People reading the paper apparently got so distracted by the Greek parable that they didn't understand the algorithm. Among the people I sent the paper to, and who claimed to have read it, were Nancy Lynch, Vassos Hadzilacos, and Phil Bernstein. A couple of months later I emailed them the following question: "Can you implement a distributed database that can tolerate the failure of any number of its processes (possibly all of them) without losing consistency, and that will resume normal behavior when more than half the processes are again working properly?" None of them noticed any connection between this question and the Paxos algorithm.

Compare what Ongaro and Ousterhout wrote in the Raft paper:

> Our approach was unusual in that our primary goal was understandability: could we define a consensus algorithm for practical systems and describe it in a way that is significantly easier to learn than Paxos? Furthermore, we wanted the algorithm to facilitate the development of intuitions that are essential for system builders. It was important not just for the algorithm to work, but for it to be obvious why it works.

### Simplicity

If you peel back Paxos's Talmudic layers, is the actual algorithm any more complex than Raft? Howard and Mortier find that it is *slightly* more complex, in two ways. First, "Raft decides log entries in-order whereas Paxos typically allows out-of-order decisions but requires an extra protocol for filling the log gaps which can occur as a result." Second, as I mentioned above, all copies of a log entry in a Raft group have the same index, term, and value. In Paxos, the terms may differ. According to Howard and Mortier, the first of these differences is an important simplification, but the second is not.

### Efficient leader election

Each Paxos server has a unique integer id. When a Paxos server runs for election, it picks a unique term in the future, based on its id. When several servers run for election at once, the one with the higher id tends to win. But, if the new leader is missing log entries, it cannot accept writes immediately. It must first catch up by replicating some unpredictable number of log entries from the followers.

Raft elections have a disadvantage: If several equally up-to-date servers run, they might all get a minority of votes; they must wait for a random time then retry. On the plus side, if a server is more up-to-date than the other candidates, it tends to win. The new leader always has all majority-replicated entries and never needs to catch up. Thus the "Paxos vs Raft" authors claim Raft's election protocol is more efficient overall.

My experience with MongoDB is that servers can sometimes get very far behind, even days behind. For example, if one server is on a slower network than the others, and the system has been running at top speed for a while, the impaired server can lag arbitrarily. If the lagging server won election and needed to catch up before the system was available for writes it would be a catastrophe. However, MongoDB is Raft-based, so lagging servers are never elected. (And, as in Raft, some elections are inconclusive and must be retried.) This seems like a huge win for Raft in real life, but maybe real deployments of Paxos avoid this problem somehow.

![](samurai.jpg)

## Conclusion

Howard and Mortier conclude, "The Raft paper claims that Raft is significantly more understandable than Paxos, and as efficient. On the contrary, we find that the two algorithms are not significantly different in understandability but Raft's leader election is surprisingly lightweight when compared to Paxos'." Dr. Howard said [in a presentation](https://www.youtube.com/watch?v=JQss0uQUc6o), "It usually doesn't matter which you choose, they're incredibly similar and optimizations that apply to one are almost always applicable to the other." This jostles my priors, but it seems convincing after reading "Paxos vs Raft", as well as "On the Parallels between Paxos and Raft".

My own conclusions are:

First, widespread fear of Paxos's complexity is due to its originally obfuscated presentation. You only have one chance to make a first impression. No amount of re-explaining Paxos has overcome this.

But Paxos's obscurity is not just a surface matter; there are aspects of the original algorithm that have not, to my knowledge, been explained in conventional terms in later papers. For example, [when my colleagues and I were researching reconfiguration](https://arxiv.org/pdf/2102.11960.pdf) (the protocol for safely adding and removing servers), I read the relevant section of "The Part-Time Parliament". Of course, Lamport described it as legislators retiring according to some ancient Greek custom. He proposed an optimization where the retirement is announced three terms before it occurs, but he didn't explain why and I couldn't reconstruct his thinking.

Ben Horowitz (a comrade in the [Distributed Systems Reading Group](http://charap.co/category/reading-group/)) recently pointed out to me that Lamport cites Fred Schneider's 1990 paper, [Implementing Fault-Tolerant Services Using the State Machine Approach](https://www.cs.cornell.edu/fbs/publications/SMSurvey.pdf). Schneider wrote: "a configuration-change request must schedule the new configuration for some point far enough in the future so that clients, state machine replicas, and output devices all find out about the new configuration before it actually comes into effect."

In contrast, Raft has not one, but two lucidly described reconfig protocols. (One is in the paper, the other in [Ongaro's dissertation](https://web.stanford.edu/~ouster/cgi-bin/papers/OngaroPhD.pdf), with [a later bugfix](https://groups.google.com/g/raft-dev/c/t4xj6dJTP6E/m/d2D9LrWRza8J).) We didn't need to search for the Raft reconfig protocol at all, whereas Paxos's is buried in layers of sediment.

My second conclusion is that [Viewstamped Replication](http://pmg.csail.mit.edu/papers/vr-revisited.pdf) is underrated. It solved similar problems a decade before Paxos, and reading the paper is a pleasure. While I was reading about Paxos vs Raft, I was thinking, "What about VR? Why isn't it taught more?"

Finally, Raft's efficient elections seem like a huge win in practice. The canonical MultiPaxos election algorithm, it seems to me, could make the system unavailable for an abitrary period while the new leader replicates missing log entries from followers. I wouldn't deploy such a protocol without a solution to this problem.

![](boxing.jpg)

***

Further reading:

* [Aleksey Charapko's summary of the paper and our reading group's discussion](http://charap.co/reading-group-paxos-vs-raft-have-we-reached-consensus-on-distributed-consensus/).
* [Video of my presentation to the reading group](https://www.youtube.com/watch?v=WWRKZgJCwYM).
* [Heidi Howard's PaPoC 2020 presentation](https://www.youtube.com/watch?v=JQss0uQUc6o).

Images:

* [Boxing Bennett Sisters (circa 1910-1915)](https://www.loc.gov/resource/ggbain.11054/)
* [Paulus Hector Mair, "A Duel with Two Sickles" (1550)](https://commons.wikimedia.org/wiki/File:Paulus_Hector_Mair.-_A_Duel_with_Two_Sickles,_on_of_African_descent,_Arte_de_Athletica,_Germany,_c._1550.png)
* [Marco Crupi (2016)](https://www.flickr.com/photos/marcocrupivisualartist/32552725055/)
* [From "Fencing" (1890)](https://www.flickr.com/photos/internetarchivebookimages/14778126744/)
