+++
type = "post"
title = "Reasoning About Knowledge: Kripke Structures"
description = ""
category = []
tag = []
draft = true
enable_lightbox = true
+++

In the [previous three articles](/series/knowledge/) I reviewed the 1990 paper, "[Knowledge and Common Knowledge in a Distributed Environment](http://arxiv.org/abs/cs/0006009)", by Joseph Halpern and Yoram Moses. I'm now reading [Reasoning About Knowledge](https://direct.mit.edu/books/monograph/1825/Reasoning-About-Knowledge), a short book by Ronald Fagin, Joseph Halpern, Yoram Moses, and Moshe Vardi. I'm particularly interested in modeling knowledge with graphs, so my notes on the book focus on that.

# Kripke structures

First, another example of knowledge and possibility. There's a card game with two players, Agent 1 and Agent 2. There are only three cards, labeled A, B, and C. At the start of the game, Agent 1 has a card that she can see, but she hides it from the other player. Same for Agent 2. The third card is face down on the table. 

{{%pic src="card-game.excalidraw.svg" alt="On the left a stick-figure woman labeled Agent 1 holds card C, on the right a stick-figure man labeled Agent 2 holds card A, and card B is on the table" %}}

{{% /pic %}}

Let's label states like so: state (C, A) is where Agent 1 has card C and Agent 2 has card A. In this state, Agent 1 knows she has card C, but she doesn't know if Agent 2 has card A or B, so she considers states (C, A) and (C, B) possible.

Here's the indistinguishability graph. In each state, each player considers _two_ states possible. The states are connected by edges labeled "1" or "2" according to which agent _can't_ distinguish them:

{{%pic src="card-game-indistinguishability-graph.excalidraw.svg" alt="A hexagon with the points labeled as states in the card game and edges labeled either 1 or 2 depending on which agent can't distinguish the states" %}}

{{% /pic %}}

So far, this is the same as the indistinguishability graphs in the previous articles. Now let's look at the book's definition of a Kripke structure. To start, we have a set \(\Phi\) (capital letter phi) of "primitive propositions" like "Agent 1 has card C."

> A Kripke structure _M_ for _n_ agents over \(\Phi\) is a tuple \((S, \pi, \mathcal{K}_1, \ldots, \mathcal{K}_n)\), where _S_ is a nonempty set of *states* or *possible worlds*, \(\pi\) is an *interpretation* which associates with each state in _S_ a truth assignment to the primitive propositions in \(\Phi\) (i.e., \(\pi(s) : \Phi \to \{\text{true}, \text{false}\}\) for each state \(s \in S\), and \(\mathcal{K}_i\) is a binary relation on _S_, that is, a set of pairs of elements of _S_.

So the Kripke structure is just a state graph. At each state, some facts are true or false, according to the \(\pi\) function. But the graph doesn't express how the world _transitions_ from one state to another. Instead, the lines between states are defined by _indistinguishability_: if agent _i_ can't distinguish two states _s_ and _t_, then the pairs \((s, t)\) and \((t, s)\) are in the set \(\mathcal{K}_i\), and there's a line from _s_ to _t_.

The 

**Lemma 2.2.1:**

$$
(M, s) \models E_G^k \varphi
\;\textit{iff}\;
(M, t) \models \varphi
\textit{ for all } t \textit{ that are } G\text{-reachable from } s \textit{ in } k \textit{ steps.}
$$

**Proof:**

Let's start with the base case, \(k=0\). The lemma becomes:

$$
(M, s) \models E_G^0 \varphi
\;\textit{iff}\;
(M, t) \models \varphi
\textit{ for all } t \textit{ that are } G\text{-reachable from } s \textit{ in } 0 \textit{ steps.}
$$

But "\(E_G^0 \varphi\)" is the same as saying "\(\varphi\) is true", and the states G-reachable from _s_ in zero steps are just _s_, so this is:

$$
(M, s) \models \varphi \; \textit{iff}\ \; (M, s) \models \varphi
$$

...which is self-evident.

Now the induction step. Assume the lemma is true for some _k_. I must show it's true for _k_ + 1. I'll consider all states _u_ that are one step farther out from _s_:

$$
(M, s) \models E_G^{k+1} \varphi
\;\textit{iff}\;
(M, u) \models \varphi
\textit{ for all } u \textit{ that are } G\text{-reachable from } s \textit{ in } k + 1 \textit{ steps.}
$$

Each _u_ state is reachable from a _t_ state along one edge, so _u_ and _t_ are indistinguishable to at least one agent _i_. Thus \(K_i E^k \varphi\) in state _u_. This holds for all agents _i_, so \(E^{k+1} \varphi\). TODO JESSE finish this up


