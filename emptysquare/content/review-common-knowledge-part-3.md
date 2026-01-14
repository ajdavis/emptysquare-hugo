+++
type = "post"
title = "Knowledge and Common Knowledge in a Distributed Environment, Part 3"
series = ["knowledge"]
tag = ["distributedsystems"]
category = ["Review"]
draft = true
enable_lightbox = true
description = ""
+++

![](theseus-athena-amphitrite-louvre-g104-ba5a61-1024.jpg)

_Athena, goddess of wisdom._

This is the third in [my series of articles about Knowledge and Common Knowledge in a Distributed Environment](/series/knowledge/), a 1990 paper by Joseph Halpern and Yoram Moses. I've defined knowledge and levels of knowledge, and used this framework to analyze the muddy children puzzle and the Raft protocol. I got excited about the connection of knowledge to graph theory, so I took a self-guided detour, applying graph theory to knowledge in Raft. Now we'll return to the actual paper, with the authors' proof that "coordinated attack" is impossible in an asynchronous system, but possible in a synchronous one.

# Coordinated attack in an asynchronous system

![](generals.jpg)

[We saw the coordinated attack problem in the last article](/review-common-knowledge-part-2/#coordinated-attack). Two generals named _A_ and _B_ try to decide when to attack their common enemy, but their messages can be delayed indefinitely, or lost. We assume the generals are following correct protocols (they won't attack alone) and that they're deterministic: a general always makes the same decision given the same history (all its observations so far). Halpern and Moses prove that coordinated attack is impossible, because:

* If both generals are attacking,
* then they must both know they are both attacking,
* and this must be common knowledge,
* but common knowledge can't be achieved in an asynchronous system.

Let's walk through their proof. Throughout, \(\psi\) (the Greek letter psi) is the fact "both generals are attacking."

**Lemma 1:** "If both generals are attacking, then everyone knows they are both attacking." Or in formal notation: 

$$\psi \Rightarrow E \psi$$

**Proof:** Let's say that _A_ attacks at some point (_r_, _t_), which is a possible moment in a run _r_ at time _t_ in the system. Recall the definition of knowledge: _A_ knows the fact \(\psi\) if \(\psi\) is true in all scenarios that match _A_'s observations so far; i.e., all the points where _A_ would have the same history as it has at point (_r_, _t_). Since _A_'s protocol is deterministic, _A_ must attack in all these scenarios, and since _A_'s protocol is correct, _B_ must also attack in all these scenarios. Therefore _A_ knows \(\psi\). We can switch the names _A_ and _B_ to prove _B_ also knows \(\psi\), thus everyone knows \(\psi\).

**Lemma 2:** "If both generals are attacking, it's common knowledge that both are attacking," i.e.:

$$\psi \Rightarrow C \psi$$

The authors assert this based on "the induction rule," on page 15 of the paper:

$$\text{If } \varphi \Rightarrow E ( \varphi \land \psi ) , \text{then } \varphi \Rightarrow C \psi $$

For example, in [the muddy children puzzle](/review-common-knowledge-part-1/), \(\varphi\) is the father's _announcement_ that at least one child is muddy, and \(\psi\) is the _fact_ that at least one child is muddy. In Coordinated Attack, \(\varphi=\psi\), i.e., "both generals are attacking," which makes the induction rule:

$$\text{If } \psi \Rightarrow E \psi , \text{then } \psi \Rightarrow C \psi $$

They don't prove the induction rule, but I think I see how to do it.

* Assume that \(\psi \Rightarrow E^k\psi\). That is, \(\psi\) implies that everyone knows that everyone knows that everyone knows ... \(\psi\), where "everyone knows" is repeated _k_ times.
* Well, if \(\psi\) is true and I'm one of the agents in the system, I know \(\psi\) and I know its implication. Thus I know \(E^k\psi\), and so does everyone else.
* Therefore \(E^{k+1}\psi\).
* We can repeat this inductive step infinitely, therefore \(C\psi\).

**Lemma 3:** If achieving \(C\psi\) requires message-passing, then achieving it is impossible in an asynchronous environment where any message can be delayed indefinitely or lost.

Halpern and Moses's proof of this is baffling, with a dozen variables, some of which seem to be reused with different meanings in the same paragraph. Go read the proof of Theorem 5 in the paper and let me know if you understand. Here, instead, is my intuition about why common knowledge can't be attained.

* First, to achieve \(C\psi\), all agents must _simultaneously_ learn \(C\psi\): by definition, it's impossible for some agents to know \(C\psi\) and others not to know, so they must all learn at once.
* Second, we said that learning \(C\psi\) requires message-passing, so there must be some message _m_ that they all receive simultaneously, from which they learn \(C\psi\).
* But this is an asynchronous environment, so if agent _A_ receives _m_, it can't at that moment know whether _B_ has. The scenario where _B_ learns \(C\psi\) is indistinguishable to _A_ from the case where it doesn't. This is a contradiction, so \(C\psi\) can't be achieved in an asynchronous world.

(You can generalize to multiple messages. That is, _A_ must receive a message \(m_a\) at the same moment _B_ receives \(m_b\) to achieve \(C\psi\). The same argument holds.)

If \(C\psi\) doesn't require message-passing, then it can be achieved. For example, there might be a thunderstorm that _A_ knows _B_ must have noticed, and vice versa, so common knowledge of the thunderstorm is attainable. Or, if the agents have synchronized clocks, then at noon it's common knowledge that it's noon. But these exceptions don't help our generals, who didn't have the foresight to make a plan like, "attack during the next thunderstorm," or "attack at noon." So they're hosed.

Disappointingly, the only correct protocol for coordinated attack in an asynchronous environment is: "Never attack."

![](Terracotta_lekythos.jpg)

# What if message delay is bounded?

So we proved common knowledge is unachievable by passing messages if their delay is unbounded. What if it's bounded: what if message delivery is guaranteed with a maximum delay of \(\epsilon\) (Greek letter epsilon), and this maximum is common knowledge?

Let's say both generals have [reliable timers](/timers-distributed-algorithms/), but not necessarily synchronized clocks. General _A_ sends a message _m_ like "let's attack at noon tomorrow," and \(\epsilon\) is much shorter than the time between now and noon tomorrow. The messenger leaves General _A_'s camp at start time \(t_S\), a time known only to General _A_. Obviously, _A_ immediately knows he sent _m_:

$$now ≥ t_S \iff K_A sent(m)$$

But _A_ doesn't know how much delay his message will have. Once the current time is \(t_S + \epsilon\), he knows his message has been delivered, so he knows _B_ knows he sent it:

$$now ≥ t_S + \epsilon \iff K_A K_B sent(m)$$

General _B_ receives the message at delivery time \(t_D\), a time known only to her. She doesn't know how long _m_ was delayed, so she doesn't know \(t_S\), so she doesn't know when _A_ will know she got _m_. In the worst case, the delay was \(\epsilon\) but she worries it was zero, so she waits until \(t_D + \epsilon\), which is \(t_s + 2 \epsilon\). General _A_ can thus reason that _B_ knows _A_ knows _B_ got _m_ after a \(2 \epsilon\) delay. In other words:

$$now ≥ t_S + 2 \epsilon \iff (K_A K_B)^2 sent(m)$$

But General _B_ isn't sure the current time is at least \(t_S + 2 \epsilon\) until (in the worst case) it's actually \(t_S + 3 \epsilon\), so she has to wait another epsilon before she knows \((K_A K_B)^2 sent(m)\). General _A_ knows all this about General _B_, so now \((K_A K_B)^3 sent(m)\) is true. We can infer that for \(k > 0\):

$$now ≥ t_S + k \epsilon \iff (K_A K_B)^k sent(m)$$

We proved earlier that the generals can't attack together unless their plan is common knowledge, which means \((K_A K_B)^\infty\ sent(m)\), but that would take infinitely long. So not even guaranteed message delivery with bounded delay is enough to solve coordinated attack.

# Another indistinguishability graph

Let's look at this from another angle, with the [indistinguishability graph technique from the previous article](/review-common-knowledge-part-2/#indistinguishability-graph).

{{%pic src="generals-bounded-delay.excalidraw.svg" alt="" %}}

{{% /pic %}}

Here's a state graph, with timestamps in <span style="font-weight: bold; color: #1971c2">blue</span> going down the left side. The **black** arrows are possible state transitions. In the initial state, _m_ is unsent. In the next state, General _A_ sends it. Then there's a branch: _m_ is received after zero delay or \(\epsilon\) delay. Then the two branches continue separately, making a state transition after each \(\epsilon\) of time passes. The first two states are connected with a <span style="font-weight: bold; color: #2f9e44">green</span> line because they're indistinguishable to General _B_: she doesn't know if _A_ sent the message or not. After that, there are two possible states at each timestamp, and these two states are connected with <span style="font-weight: bold; color: #e03131">red</span> lines because they're indistinguishable to General _A_: he doesn't know if his message was received after zero delay or \(\epsilon\) delay. The diagonal <span style="font-weight: bold; color: #2f9e44">green</span> lines indicate the same thing about General _B_: she doesn't know if she received the message after a delay or not. (My drawing is a hybrid of a state graph and a Kripke structure.)

Like we saw in the last article, we can use properties of this graph to calculate agents' knowledge. For example, \(K_A K_B sent(m)\) is true in state _s_ iff all paths from _s_ that follow zero or one <span style="font-weight: bold; color: #e03131">_A_-indistinguishable edges</span>, then zero or one <span style="font-weight: bold; color: #2f9e44">_B_-indistinguishable edges</span>, end at a state where \(sent(m)\) is true.

Let's choose a particular state as a demonstration: the state where the current time is \(t_S\) and _B_ received _m_ with zero delay. We can follow <span style="font-weight: bold; color: #e03131">one _A_-edge</span>, then zero _B_-edges, and arrive at the state labeled "sent", where \(sent(m)\) is true. Or we can follow the same <span style="font-weight: bold; color: #e03131">one _A_-edge</span>, and then <span style="font-weight: bold; color: #2f9e44">one _B_-edge</span> and arrive at the state labeled "unsent," where \(sent(m)\) is false. Since both "sent" and "unsent" are reachable from the current state, \(K_A K_B sent(m)\) is false.

{{%pic src="generals-bounded-delay-2.excalidraw.svg" alt="" %}}
\(K_A K_B sent(m)\) is **false** in the state marked "current state."
{{% /pic %}}

But if you start from either of the states where the current time is \(t_S + \epsilon\) and follow zero or one <span style="font-weight: bold; color: #e03131">red</span> edges, then zero or one <span style="font-weight: bold; color: #2f9e44">green</span> edges, you always arrive at states where _m_ was sent. Thus \(K_A K_B sent(m)\) is true in those states.

{{%pic src="generals-bounded-delay-3.excalidraw.svg" alt="" %}}
\(K_A K_B sent(m)\) is **true** in the state marked "current state."
{{% /pic %}}

But if you want a state where \((K_A K_B)^2 sent(m)\), you need to start farther away, at one of the states where the time is \(t_S + 2 \epsilon\) or later. Otherwise there exists a path that follows a <span style="font-weight: bold; color: #e03131">red</span>, then <span style="font-weight: bold; color: #2f9e44">green</span>, then <span style="font-weight: bold; color: #e03131">red</span>, then <span style="font-weight: bold; color: #2f9e44">green</span> edge and arrives at a state where \(sent(m)\) is false. (I haven't drawn a picture of this.) Continuing inductively, we can see how the graph expresses the same thing we proved before: \((K_A K_B)^k sent(m)\) is true only if the current time is \(t_S + k \epsilon\) or later.

# What if the generals have synchronized clocks?

It seems weird to conclude that the generals can't coordinate, even with bounded message delays. Isn't it enough for _A_ to say, "attack at noon tomorrow" at least \(\epsilon\) before that time, with no acknowledgment from _B_? Yes, this works, but the *protocol itself* must be common knowledge at the start, and the generals must have perfectly synchronized clocks. If the generals have already agreed that _A_ will send a message proposing an attack at least \(\epsilon\) in the future, then when _B_ receives "attack at noon tomorrow," she knows:

- General _A_ sent this at least \(\epsilon\) before noon (that's the protocol)
- Therefore at noon, _A_ knows _B_ received it
- Therefore at noon, _B_ knows _A_ knows _B_ received it
- And so on...

At noon common knowledge is achieved, because both generals can reason about what the other knows *will* be true at the deadline.

Halpern and Moses don't propose this exact idea. They instead use timestamped messages: "The time is now \(t_S\), let's attack at noon." This removes General _B_'s uncertainty about \(t_S\), so at time \(t_S + \epsilon\) the plan becomes common knowledge. This is pretty much equivalent: my pre-agreed protocol and their timestamped messages both provide extra shared facts from which the two generals can reason.

Both solutions require perfectly synchronized clocks. If _A_ and _B_ have the slightest uncertainty about when noon arrives, they can't become sure of the plan simultaneously, so they can *never* achieve common knowledge.

![](Athena_owl_Met_09.221.43.jpg)

# Weaker forms of common knowledge

This still seems weird. In practice, I can arrange to meet someone for lunch, and a Raft system can reach consensus, so why is it impossible in theory? It's because Halpern and Moses's definition of common knowledge is impractically strong. So they define weaker forms of shared knowledge that are achievable and suffice for consensus or lunch.

**\(\epsilon\)-common knowledge** (\(C^{\,\epsilon}\phi\)): Instead of \(\phi\) becoming common knowledge simultaneously, \(\phi\) becomes "\(\epsilon\)-common knowledge" in an \(\epsilon\) time window. So if message delivery is guaranteed after some bounded delay, its contents are common knowledge a bounded time after it's sent.

**Timestamped common knowledge** (\(C^T\)): Everyone knows at time _T_ *on their own clock*. If clocks are perfectly synchronized, then \(C^T\) is equivalent to common knowledge. If they're synchronized within \(\epsilon\), then \(C^T\) is \(C^{\,\epsilon}\). You can discard clocks and substitute something like a Raft term number for the timestamp and say, "which node is the leader in term _t_ is timestamped common knowledge."

**Eventual common knowledge** (\(C^{\,\diamond}\)): Everyone will eventually know, though not necessarily at the same time. This suffices for actions that must eventually happen everywhere, without a deadline.

These form a hierarchy: \(C \Rightarrow C^{\,\epsilon} \Rightarrow C^{\,\diamond}\).

# Internal knowledge consistency

Another solution to the paradox---common knowledge is impossible in theory but possible in practice---is "internal knowledge consistency."

Every agent in the system has an _interpretation_ of its observations. Formally, an interpretation is a function that takes the agent's personal history and the current time, and outputs a set of facts the agent believes are true. For example, in the muddy children puzzle, after the children hear the father's announcement _m_, "at least one of you is muddy," each child believes it heard _m_. An interpretation is "knowledge consistent" if it produces only _true_ beliefs.

A knowledge consistent interpretation must say that _m_ isn't common knowledge, because in reality, the children _can't_ achieve common knowledge of _m_: How do they all know that they all understand English, and they were all paying attention, etc.? But an _internally_ knowledge consistent interpretation can say it is, so long as no observation will ever contradict this belief. This matches how we intuitively reason about knowledge and common knowledge in everyday situations.

This concludes my review of Halpern and Moses's "Knowledge and Common Knowledge in a Distributed Environment"! But I'll have more to say about epistemic logic and distributed systems. I'm now in a UCLA seminar with [Remy Wang](https://remy.wang/), reading [Reasoning About Knowledge](https://direct.mit.edu/books/monograph/1825/Reasoning-About-Knowledge), the short book Halpern and Moses wrote with Ronald Fagin and Moshe Vardi. My goal now is to marry epistemic logic with TLA+, by analyzing a TLA+ specification's state graph.

![](peleus.jpg)

Images:
* [Theseus Athena and Amphitrite](https://commons.wikimedia.org/wiki/File:Theseus_Athena_Amphitrite_Louvre_G104.jpg)
* [Oil flask with depiction of Athena, goddess of wisdom](https://upload.wikimedia.org/wikipedia/commons/0/03/Terracotta_lekythos_%28oil_flask%29_MET_DP161824.jpg)
* [Athena with an owl](https://commons.wikimedia.org/wiki/File:Athena_owl_Met_09.221.43.jpg)
* [Athena and Herakles](https://commons.wikimedia.org/wiki/File:Oedipus_Painter_ARV_441_185_Herakles_and_Athena_-_Peleus_subduing_Thetis_%2802%29.jpg)
