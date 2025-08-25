+++
category = ["Review"]
date = "2025-08-25T10:42:25.358748"
description = "Graph theory and epistemology, oh my!"
draft = false
enable_lightbox = true
series = ["knowledge"]
tag = ["distributedsystems"]
thumbnail = "raft-states-combined.jpg"
title = "Knowledge and Common Knowledge in a Distributed Environment, Part 2"
type = "post"
+++

![Odin riding an eight-legged horse across water, flanked by two ravens.](odin-1.jpg)

_Odin, god of wisdom._

This is the second in [my series of articles about Knowledge and Common Knowledge in a Distributed Environment](/series/knowledge/), a beautiful and difficult 1990 paper about distributed systems and epistemology. So far, I analyzed the "muddy children puzzle," I defined levels of knowledge, and I used these levels of knowledge to analyzed the Raft protocol (which was published long after this paper). 

Now, the moment you've been waiting for: coordinated attack!

{{< toc >}}

# Coordinated attack

![](guan-yu.jpeg)

_Chinese general [Guan Yu](https://commons.wikimedia.org/wiki/File:Guan_yu_-Summer_Palace,_Beijing.JPG)._

Two generals are encamped on hilltops, on either side of the enemy army. If they attack simultaneously, they'll win, otherwise they'll fail. They have no initial plan, so they send messengers back and forth, to try to agree on a time to attack. Unfortunately, messengers can be unpredictably slow, or they can be caught by the enemy. How can the generals agree on a time?

(The paper's authors, Halpern and Moses, call this problem "coordinated attack" and they say it was introduced by Jim Gray in 1978. The puzzle may be older than that. Sometimes it's called "Chinese generals." The "Byzantine generals problem" is a more complex version that Lamport described later.)

As you probably know, the generals can never agree. If general _A_ sends a message saying, "attack at dawn," he doesn't know whether _B_ received it, so he risks attacking alone. So perhaps the protocol is, "attack if you proposed a time and received acknowledgment"? But if _B_ receives and acknowledges the message, she doesn't know whether _A_ got her acknowledgment, so she also risks attacking alone. And so on. No protocol in this asynchronous system can guarantee they attack simultaneously.

Halpern and Moses (citing earlier work) use a _many scenarios_ argument to prove that coordinated attack is impossible. If _A_ sent the message and hasn't observed an acknowledgment, there are many scenarios that fit his observations:

* The message was lost
* The message is still in transit
* The message was received and the acknowledgment was lost
* The message was received and the acknowledgment is still in transit

<br>

**General _A_'s knowledge is the set of facts that are true in all the possible scenarios that match his observations.**

So _A_ knows his message was sent, but that's it. If _B_ receives the message and sends an acknowledgment, she also has four scenarios she can't distinguish. The generals can't be sure they've agreed to attack unless _A_ knows that _B_ knows that ... infinitely. In other words, their attack time must be _common knowledge_, and common knowledge is impossible in an asynchronous system.

(Yes, this is related to [FLP impossibility](https://www.the-paper-trail.org/post/2008-08-13-a-brief-tour-of-flp-impossibility/).)

![Stylized drawing of a seated figure with two swords, wearing a cloak adorned with animal heads.](101729.jpg)

# Definition of knowledge

Here's my favorite part of the paper. It begins with a mathematical model of a distributed system, which will be familiar to people who use PlusCal, TLA+, or other formalizations. There are some processors (aka nodes or agents) called _p_<sub>1</sub>, _p_<sub>2</sub>, ..., _p_<sub>n</sub>. A _run_ of the system is just like a TLA+ _behavior_: a sequence of events starting at time 0 and continuing infinitely (perhaps reaching a final state and staying there forever). The system is characterized by the set of all possible runs, _R_. This is just like a TLA+ state graph. A _point_ (_r_, _t_) is a moment in a run _r_ at time _t_. At every point, each processor has its own _local history_, the events it has observed, including its own actions. E.g., a Raft node knows the actions it's taken and the messages it's received, but it has no direct knowledge of other nodes' histories. A _protocol_ is a function of a processor's local history: each processor deterministically chooses its next action based on its observations so far.

A processor _p_<sub>i</sub> _knows_ a fact \(\varphi\) at point (_r_, _t_) if \(\varphi\) is true at all points of _R_ that are _indistinguishable_ from (_r_, _t_). By indistinguishable points, I mean all points (_r_&apos;, _t_&apos;) where _p_<sub>i</sub>'s local history is the same as at (_r_, _t_). For example, if I observed my partner Jennifer go out the front door, and I haven't seen her come back in, then I know she's gone, based on my local history of observations. She might have taken the car or gone for a walk&mdash;since I haven't looked in the parking lot, those two scenarios are indistinguishable to me. But "Jennifer's gone" is true in both scenarios, so I _know_ that fact.

In Raft, if the leader has sent a log entry to both followers and only one follower has acknowledged it, then the leader can't distinguish between the scenarios where one or two followers received the entry. But "the entry is majority-replicated" is true in both scenarios, so the leader knows that fact.

![](raft.svg)

A processor's _view_ of the system is a function of its history. The view could just be the identity function&mdash;the processor's view is its history, i.e. the sequence of all its actions and observations. Or the processor's view could be a _summary_ of its history, e.g. the Raft election protocol requires a node to remember only the most recent vote it cast, not the sequence of _all_ its past votes. In TLA+ we usually have some variables for each node, which are updated when nodes take actions or receive messages: these are the nodes' _views_, their summaries of their local histories!   

Halpern and Moses more formally define a processor's view of the system, and how that relates to levels of knowledge, like distributed knowledge and common knowledge, in Section 6 of the paper. It's great, go read it.

![Norse-style panel with animal and serpent designs, labeled “Oden forskaper sig.”](102550.jpg)

# Indistinguishability graph

As a TLA+ guy, I usually think of a _state_ as an assignment of values to variables, and the _state graph_ connects states with directed edges representing possible state transitions. Let's consider the muddy children from the [previous episode](/review-common-knowledge-part-1/). Say there are two children. Our variables are:

* _a_, _b_: Whether child _a_ and/or _b_ is muddy.
* _m_: Whether the father has announced, "At least one of you is muddy."
* _q_: The number of times the father has asked, "Can you prove you're muddy?"

The initial state is:

\(a \in \{\text{true}, \text{false}\}
\land b \in \{\text{true}, \text{false}\}
\land m = \text{false}
\land q = 0\)

Then the father makes his announcement (_m_ becomes true), and then he starts asking his question (_q_ increases). We know at least one child is muddy; let's say that's child _a_ and the maybe-muddy one is _b_. Here are the states and transitions:

![](muddy-children-states.svg)

How can we use this graph to represent what the children _know_? For any two states, let's add a non-directed edge between them if some child has the same view in both states, i.e. the states are indistinguishable to that child. And let's label the edge with the name of the child who can't distinguish the states:

![](muddy-children-states-2.svg)

Child _b_ can't distinguish if it's muddy or clean in the initial state, so there's a blue "b" edge between the first two initial states. The two states are distinct in _a_'s eyes, because it can see whether _b_ is muddy, so we don't label the edge "a". After the father announces "at least one of you is muddy," _b_ still doesn't know if it's muddy, because it sees that _a_ is muddy so _a_ might be the only muddy child. Therefore the two next states are also indistinguishable to _b_. Finally the father asks, "can you prove you're muddy?" As I explained in the previous article, _a_ and _b_ now know if they're muddy, so the third states are distinct to both of them and there's no blue edge.

![Decorative border of three running bears, labeled as a variant from the Ynglinga Saga.](102593.jpg)

Can we do the same for Raft? The real Raft TLA+ spec has dozens of variables. Let's simplify. Let's say there's one log entry, there's a permanent leader, and there are two followers _f_<sub>1</sub> and _f_<sub>2</sub>. Here are our variables:

* _r_<sub>1</sub>, _r_<sub>2</sub>: Follower _f_<sub>1</sub> or _f_<sub>2</sub> has received the entry ("r" for "receive").
* _a_<sub>1</sub>, _a_<sub>2</sub>: The leader received an acknowledgment from _f_<sub>1</sub> or _f_<sub>2</sub> ("a" for "acknowledge").

At first all the variables are false. Then _f_<sub>1</sub> or _f_<sub>2</sub> receives the log entry, and some sequence of receiving and acknowledging leads to the final state, where both followers have received and acknowledged the entry. Here's a state-transition graph, false is white and true is red:

![](raft-states.svg)

<div style="text-align: center">
<p><span style="font-style: italic">A state transition graph.</span></p>
</div>

In the last article I defined two facts:

* \(\varphi\) (phi): the log entry exists
* \(\psi\) (psi): the log entry is majority-replicated

A follower knows \(\varphi\) if it received the entry, and the leader knows \(\psi\) if it knows at least one follower knows \(\varphi\), since the leader plus one follower is a majority of the three-node replica set. In other words:

$$K_{leader} \psi \Longleftarrow K_{leader} S_F \varphi$$

Let's analyze this with the graph. A follower *f* knows \(\varphi\), if \(\varphi\) is true in all the states indistinguishable to _f_ from this state. The only variable in _f_<sub>1</sub>'s view is _r_<sub>1</sub>, so all states with the same _r_<sub>1</sub> value are indistinguishable to _f_<sub>1</sub>. For _f_<sub>1</sub>'s indistinguishability graph, I'll draw edges between the nodes where _r_<sub>1</sub> is true, and edges between the nodes where _r_<sub>1</sub> is false:  

![](raft-knowledge-f1.svg)

<div style="text-align: center">
<p><span style="font-style: italic">The follower f<sub>1</sub>'s indistinguishability graph.</span></p>
</div>

The graph for _f_<sub>2</sub> is the same, but flipped vertically.

![](raft-knowledge-f2.svg)

<div style="text-align: center">
<p><span style="font-style: italic">The follower f<sub>2</sub>'s indistinguishability graph.</span></p>
</div>

The leader doesn't know whether a follower has received the entry, so states that differ only by their _r_<sub>1</sub> or _r_<sub>2</sub> values are indistinguishable to the leader. The leader knows what acknowledgments it received, so it _can_ distinguish states by their _a_<sub>1</sub> or _a_<sub>2</sub> values.

![](raft-knowledge-leader.svg)

<div style="text-align: center">
<p><span style="font-style: italic">The leader's indistinguishability graph.</span></p>
</div>

Putting it all together:

![](raft-states-combined.svg)

<div style="text-align: center">
<p><span style="font-style: italic">The combined indistinguishability graph.</span></p>
</div>

As I said earlier, "the leader knows \(\psi\)" is equivalent to "the leader knows that at least one follower knows \(\varphi\)." We can evaluate a property like this with the indistinguishability graph. The leader knows _f_<sub>1</sub> knows \(\varphi\) at a state _S_, if every path from _S_ along zero or one <span style="color: #2f9e44; font-weight: bold">leader edges</span>, then zero or one <span style="color: #1971c2; font-weight: bold">_f_<sub>1</sub> edges</span>, leads to a state where _f_<sub>1</sub> knows \(\varphi\):

![](leader-knows-f1-knows-phi.svg)

This is a graph-style way of saying:

* the leader knows _f_<sub>1</sub> knows \(\varphi\) in state _S_, if
* in all states *T* indistinguishable (to the leader) from _S_,
* _f_<sub>1</sub> knows \(\varphi\) in all states indistinguishable (to _f_<sub>1</sub>) from _T_&nbsp;!

The same goes for states where the leader knows _f_<sub>2</sub> knows \(\varphi\):

![](leader-knows-f2-knows-phi.svg)

Putting it all together:

![](leader-knows-f1-or-f2-knows-phi.svg)

As you'd expect, the leader knows \(\psi\) in states where _a_<sub>1</sub> or _a_<sub>2</sub> is true; i.e. states where one or the other follower has acknowledged the entry. But it's cool to see how it can be expressed as a graph query. This seems ripe for automatic verification. Halpern and Moses describe how various levels of knowledge, such as distributed knowledge, or "everyone knows," or "everyone knows that everyone knows," are properties of paths through the indistinguishability graph.

I'll stop here and let my brain cool off. Next time: agents in a distributed system can achieve common knowledge if they have reasonably reliable clocks. 

<div style="text-align: center; margin-bottom: 1em">
<img src="101730.jpg" style="max-width: 50%;" alt="Line drawing of Odin seated on a throne with animal head carvings, one arm outstretched."/>
</div>

Odin and other Norse images by [Gerhard Munthe](https://www.nasjonalmuseet.no/en/collection/producer/56446/gerhard-munthe).
