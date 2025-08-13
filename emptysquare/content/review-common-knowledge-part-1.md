+++
category = ["Review"]
description = "A profound 1990 paper about epistomology in distributed systems."
draft = true
enable_lightbox = true
tag = ["distributedsystems"]
thumbnail = "saraswati.jpg"
title = "Knowledge and Common Knowledge in a Distributed Environment, Part 1"
type = "post"
series = ["knowledge"]
+++

![This otherworldly painting centers upon a pale goddess dressed in white who is seated on a pink-tipped white lotus that hovers in an indeterminate space. Two massive red poppy plants in full bloom and bud, ultimately based on European botanical drawings that were adopted by Mughal artists and from there by Mewar artists and from there by a painter in Sawar, flank the goddess. The background is a solid field of rich chocolate brown.](saraswati.jpg)

_[Saraswati, goddess of knowledge](https://asia.si.edu/explore-art-culture/collections/search/edanmdm:fsg_S2018.1.40/)_

We usually reason about distributed systems by asking, what can one process _know_ about the state of the system? E.g., if a majority of [Raft](https://raft.github.io/) nodes tell the leader that they have replicated a log entry, the leader _knows_ the entry is durable. Therefore the leader can take various actions, like replying to the user who submitted the log entry. On the other hand, if a Raft follower hasn't heard from the leader in a while, it might _suspect_ the leader has crashed, but it can never know for sure. A process must somehow gather enough information to deduce the facts it must know to take the correct action. I think about knowledge all the time when I'm analyzing a distributed algorithm.

On the other hand, my main tool for checking the correctness of an algorithm is TLA+ and the TLC model-checker. There's no notion of knowledge in a TLA+ specification, just a mindless state machine obeying if-then instructions. When I read a TLA+ spec I might think, "In this state, the leader knows the log entry is majority-replicated." But that's anthropomorphism. The spec just says: if this, then do that.

I'm studying the 1990 paper, "[Knowledge and Common Knowledge in a Distributed Environment](http://arxiv.org/abs/cs/0006009)", by Joseph Halpern and Yoram Moses. They bring a theory of knowledge and belief to distributed systems. It's a hard paper for me, so I'll blog it as I read, a few sections at a time. My goals are to understand the material and explain it to you. I also want to explore a new direction: integrating knowledge into TLA+. This might be a dead end, we'll see!

{{< toc >}}

# Muddy Children

The paper begins with the muddy children puzzle, apparently a classic of epistemology:

> Imagine _n_ children playing together. The mother of these children has told them that if they get dirty there will be severe consequences. So, of course, each child wants to keep clean, but each would love to see the others get dirty. Now it happens during their play that some of the children, say _k_ of them, get mud on their foreheads. Each can see the mud on others but not on his own forehead. So, of course, no one says a thing. Along comes the father, who says, "At least one of you has mud on your head," thus expressing a fact known to each of them before he spoke (if _k_&nbsp;>&nbsp;1). The father then asks the following question, over and over: "Can any of you prove you have mud on your head?" Assuming that all the children are perceptive, intelligent, truthful, and that they answer simultaneously, what will happen?

Halpern and Moses introduce this puzzle to warm up the reader's thinking about knowledge in distributed systems. When is it important for one process to know what another process knows? What is "common knowledge" and when is it needed? 

The solution to the muddy children puzzle is: the first _k_&nbsp;-&nbsp;1 times the father asks the question, all children simultaneously reply "no": they can't prove they're muddy. The _k_<sup>th</sup> time, the muddy children say "yes" and the clean children say "no." But if the father hadn't announced "at least one is muddy" at the start, the muddy children would never figure out they're muddy. Even when _k_&nbsp;>&nbsp;1, and all the children can see with their own eyes that at least one is muddy, the father's announcement of this fact is crucial.

This result is well-known to logicians, so the paper doesn't explain it in depth. But I will. Let's work the problem for _k_ from 1 to 3. (The number of clean children is actually irrelevant.)

Here are our variables:
* _k_: the number of muddy children.
* _m_: the father's announcement, "at least one of you is muddy."
* _q_: the number of times the father has asked, "can you prove you're muddy?"

## One muddy child

<div style="text-align: center"><img src="k1.excalidraw.svg" alt="" style="max-width: 40%; margin: auto"></div>

The first time the father asks the question, the muddy child sees that all the other children are clean. Since the father announced _m_, the muddy child knows it must be the muddy one, and says "yes." Incidentally, the muddy child knows _k_&nbsp;=&nbsp;1. The other children see one muddy child. They don't know whether they're also muddy (they don't know if _k_ is 1 or 2), so they say "no". 

The purpose of the father's announcement _m_ is clear here: without it, the muddy child doesn't know if the reason it sees only clean children is because _k_&nbsp;=&nbsp;0, or because _k_&nbsp;=&nbsp;1 and it has mud on its face.

## Two muddy children

<div style="text-align: center"><img src="k2.excalidraw.svg" alt="" style="max-width: 40%; margin: auto"></div>

Here's where things get freaky. The father announces _m_, which all the children can already see is true, and yet his announcement is necessary for solving the puzzle.

When the father asks his question the first time, can Child _a_ answer "yes"? It sees that Child _b_ is muddy. It considers some possibilities:

* _a_ could have mud on its own face or not.
* _b_ could _think_ it has mud on its own face, or not.

These two _pairs_ of possibilities lead to four possible worlds in _a_'s mind:

<div style="text-align: center"><img src="k2-worlds-1.excalidraw.svg" alt="" style="margin: auto"></div>

But the father's announcement _m_ is "common knowledge": that is, everyone knows that _k_&nbsp;&ge;&nbsp;1, and everyone knows that everyone knows ... (ad infinitum) ... that _k_&nbsp;&ge;&nbsp;1. So _a_ knows _b_ knows the world where all children are clean is impossible:

<div style="text-align: center"><img src="k2-worlds-2.excalidraw.svg" alt="" style="margin: auto"></div>

Since _a_ could be muddy or clean, depending on which world is real, it replies "no" to the father's question. Child _b_ replies "no" for the same reason (swapping _a_ and _b_).

Child _a_ hears _b_'s answer, and now _a_ has learned something. Child _a_ knows that _b_ sees a muddy child! If _b_ hadn't seen a muddy child, then _b_ would've said "yes", because of _m_. This eliminates the other world where _b_ sees no muddy child:

<div style="text-align: center"><img src="k2-worlds-3.excalidraw.svg" alt="" style="margin: auto"></div>

All worlds where _a_ is clean are now eliminated, so the next time the father asks his question, _a_ replies "yes": it knows it's muddy. Child _b_ does the same.

So the father's announcement of _m_ is crucial to _a_, even though _a_ knows _k_&nbsp;&ge;&nbsp;1 already: _m_ ensures that _a_ knows _b_ knows _k_&nbsp;&ge;&nbsp;1.

## Three muddy children

<div style="text-align: center"><img src="k3.excalidraw.svg" alt="" style="max-width: 40%; margin: auto"></div>

I'll work this problem similarly, but without diagrams. At the start, before the father announces _m_, _a_ sees 2 muddy children, so:

```text
Initial condition, before father announces m:
a knows:
  k ∈ [2, 3]
  b knows:
    k ∈ [1, 3]
    c knows:
      k ∈ [0, 3]
```

The text above is my attempt to represent statements like, "_a_ knows _k_ is between 2 and 3 inclusive, and _a_ knows _b_ knows _k_ is between 1 and 3 inclusive," and so on. Why does _a_ know _b_ knows that? Because:

* _a_ knows _b_ sees mud on _c_ (definitely 1 muddy child)
* _b_ could think its own face is muddy (maybe 1 more muddy child)
* _b_ (in _a_'s mind) might see mud on _a_ (maybe 1 more muddy child)
 
Hence _b_ (in _a_'s mind) could think there are 1, 2, or 3 muddy children.

How could _a_ think _b_ thinks _c_ thinks there are 0 muddy children, even though _a_ knows _c_ sees the mud on _b_'s face? Well, if _a_ is clean (in _a_'s mind), and _b_ thinks its own face is clean (in _a_'s mind), then _b_ thinks _c_ might see no muddy children (still in _a_'s mind). So _a_ thinks it's possible for _b_ to think _c_ sees no muddy children, although _a_ knows that's wrong!

But then the father announces _m_. Now it's common knowledge that _k_&nbsp;&ge;&nbsp;1:

```text {hl_lines=[1,7]}
After father announces m:
a knows:
  k ∈ [2, 3]
  b knows:
    k ∈ [1, 3]
    c knows:
      k ∈ [1, 3]
```

The father asks the question, "can you prove you're muddy?", once:

```text {hl_lines=[1,5]}
After father announces m, and q=1:
a knows:
  k ∈ [2, 3]
  b knows:
    k ∈ [2, 3]
    c knows:
      k ∈ [1, 3]
```

Child _c_ says "no," which must mean it sees a muddy child. Child _a_ knows _b_ knows _c_ is muddy as well, so _a_ knows _b_ knows _k_&nbsp;&ge;&nbsp;2.

The father asks a second time:

```text {hl_lines=[1,3]}
After father announces m, and q=2:
a knows:
  k ∈ [3, 3]
  b knows:
    k ∈ [2, 3]
    c knows:
      k ∈ [1, 3]
```

Since _b_ said "no," and _a_ knows _b_ knew _k_&nbsp;&ge;&nbsp;2, _a_ knows _b_ sees 2 muddy children. Child _a_ also knows _b_ is muddy, so _a_ knows _k_&nbsp;&ge;&nbsp;3. Since _a_ only sees 2 muddy children, _a_ knows the third muddy child is itself and _k_&nbsp;=&nbsp;3. The third time the father asks, _a_ says "yes." The other muddy children are reasoning identically to _a_, so they also say "yes."

![The battle of wits in The Princess Bride](princess-bride.jpg)

_The battle of wits in The Princess Bride._

## _k_ muddy children

We've seen that for each _k_ from 1 to 3, when the father asks the question for the _k_<sup>th</sup> time, all muddy children answer "yes" and the others answer "no." Let's say _a_ sees 3 muddy children and assumes it has no mud on its own face, i.e. it assumes _k_&nbsp;=&nbsp;3. If the father asks 3 times and all children still answer "no," then _a_ knows its assumption was false, so _a_ knows it's muddy and _k_&nbsp;=&nbsp;4. Child _a_ then correctly answers "yes" to the 4<sup>th</sup> question. Same for the other children. And so on for all _k_&nbsp;&gt;&nbsp;4, inductively.

# A hierarchy of states of knowledge

We've seen a weird phenomenon, where the father's announcement of a fact that everyone already knows somehow gives the children useful information. I explained to myself and to you how this works in the muddy children puzzle. Halpern and Moses explain it in general, by defining a hierarchy of states of knowledge. To begin, they introduce the notation:

$$K_i \varphi$$

This is read, &ldquo;_i_ knows \(\varphi\).&rdquo; Some agent (or process or whatever) _i_ knows a fact \(\varphi\) (Greek letter "phi" for "fact"). I'll discuss the authors' definition of knowledge later, it's terrific, stay tuned! For now, let's just say an agent's knowledge can depend only on the agent's local history, i.e. its initial state and the actions it's taken and observed. Also, knowledge is always true. A _belief_ can be false, but if an agent _knows_ \(\varphi\), then \(\varphi\) is a true fact.

Here's the authors' hierarchy of knowledge, from weakest to strongest:

* \(D_G \varphi\)&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&ldquo;the group _G_ has distributed knowledge of \(\varphi\)&rdquo;<br><br>A fact \(\varphi\) is distributed knowledge if someone with a global view could infer \(\varphi\) from everything known by every agent in some group _G_, even if no individual agent in _G_ knows.

* \(S_G \varphi\)&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&ldquo;someone in _G_ knows \(\varphi\)&rdquo;<br><br>Defined as: \(K_i \varphi\) for some _i_ in _G_.

* \(E_G \varphi\)&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&ldquo;everyone in _G_ knows \(\varphi\)&rdquo;<br><br>Defined as: \(K_i \varphi\) for all _i_ in _G_.

* \(E_G^k \varphi\)&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&ldquo;\(\varphi\) is \(E^k\)-_knowledge_ in _G_&rdquo;<br><br>Everyone in _G_ knows that everyone in _G_ knows that ... everyone in _G_ knows \(\varphi\), where "everyone in _G_ knows that" is repeated _k_ times.

* \(C_G^k \varphi\)&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&ldquo;\(\varphi\) is _common knowledge_ in _G_&rdquo;<br><br>Defined as, \(E_G^k \varphi\) for all _k_&nbsp;&ge;&nbsp;1.

The authors point out, using this framework, that when the muddy children puzzle begins, \(E_G^{k-1} m\) is true. E.g., if there are two muddy children, then everyone knows _m_. If there are three muddy children, everyone knows that everyone knows _m_, because everyone sees at least 2 muddy children, so everyone knows everyone else sees at least 1 muddy child. But to _solve_ the puzzle, they must upgrade their knowledge from \(E_G^{k-1} m\) to \(E_G^k m\), which is what the father's announcement does. (The father's announcement goes farther, making _m_ common knowledge, but all he _must_ do is upgrade _m_ to \(E_G^k m\).)

This is a useful way to think about nodes in a distributed system: each has limited knowledge, but there is distributed knowledge implicit in the whole system. To correctly take certain actions, nodes need a certain level of knowledge or higher. Nodes exchange messages to promote their knowledge up the hierarchy. Each level in the hierarchy implies all the lower levels:

$$C_G \varphi \implies ... \implies E_G^{k+1} \varphi \implies E_G^k \varphi$$
$$\implies ... \implies E_G \varphi \implies S_G \varphi \implies D_G \varphi$$

# Knowledge hierarchies in Raft

Halpern and Moses don't talk much about actual distributed protocols, but I kept thinking about Raft&mdash;how does the Raft protocol look if it's recast as a flow of knowledge?

Let's say a Raft leader creates a log entry. I'll call the fact that the entry exists \(\varphi\), and right now only the leader knows \(\varphi\).

<div style="text-align: center"><img src="raft-knowledge-1.svg" alt="" style="max-width: 80%; margin: auto"></div>

The leader sends the log entry to its two followers, but they haven't acknowledged it yet:

<div style="text-align: center"><img src="raft-knowledge-2.svg" alt="" style="max-width: 80%; margin: auto"></div>

Now **everyone** knows \(\varphi\), but the leader doesn't know any follower knows \(\varphi\). Let's say _G_ is the set of all nodes and _F_ is the set of followers. Using Halpern and Moses's notation:

$$E_G \varphi$$
$$\neg K_{leader} S_F \varphi$$

Let's call the fact "the entry is durable" \(\psi\), the Greek letter psi. This fact is true if the entry is replicated to at least a majority of nodes, so it's certainly true if it's replicated by all nodes&mdash;that is, if everyone knows \(\varphi\) then \(\psi\) is true. But currently only God can see that all nodes have the entry, so \(\psi\) is **distributed** knowledge.

$$E_G \varphi \implies D_G \psi$$
$$\neg S_G \psi$$

Then the leader receives an acknowledgment.

<div style="text-align: center"><img src="raft-knowledge-3.svg" alt="" style="max-width: 80%; margin: auto"></div>

We can say the leader knows \(\psi\) if it knows any follower knows \(\varphi\):

$$K_{leader} \psi \impliedby K_{leader} S_F \varphi$$

(This is true because the leader + one follower is a majority. If there were more than 3 nodes we'd need a different rule.) Now \(\psi\) has been upgraded, from **distributed** knowledge to something that **someone** knows:

$$S_G \psi$$

The leader tells the followers that the entry is committed.

<div style="text-align: center"><img src="raft-knowledge-4.svg" alt="" style="max-width: 80%; margin: auto"></div>

Now \(\psi\) has been upgraded again, from a fact that **someone** knows to a fact that **everyone** knows.

$$E_G \psi$$

But (according to the [Raft paper](https://raft.github.io/)) followers don't tell the leader which entries they know are committed, so \(\psi\) doesn't become something that everyone knows that everyone knows, much less **common** knowledge.

$$\neg E_G^2 \psi$$
$$\neg C_G \psi$$

# Onward

This covers the first three sections of the paper. We've seen Halpern and Moses's knowledge hierarchy, and how it's useful for analyzing the muddy children puzzle and Raft. Next, we'll briefly visit the famous Byzantine Generals, who are still trying to decide when to attack their common enemy. After that we'll get into the meat of the paper, which offers a remarkably satisfying definition of knowledge. 

![Hindu goddesses Lakshami and Saraswati playing castanets and a tambura. Watercolour drawing.](lakshmi-saraswati.jpg)

_[Lakshmi and Saraswati](https://wellcomecollection.org/works/bxw2ajua/images?id=j6au7hbk)_
