+++
category = ["Programming"]
date = "2026-05-13T01:43:27.192875+00:00"
description = "You can go far without writing TLA+ syntax now, but you still need to understand temporal logic."
draft = false
enable_lightbox = true
tag = ["tla+"]
thumbnail = "robot-square.jpg"
title = "Intro to TLA+ for the LLM Era: Prompt Your Way to Victory"
type = "post"
+++

Most engineers' first objection to using TLA+ is, the syntax is hostile. It looks like LaTeX, not like code. But now, frontier LLMs can generate TLA+ easily. It's still your responsibility to understand your system and define what "correctness" means, and you need a high-level understanding of temporal logic. I'll explain temporal logic in this article. At the end I'll show an example prompt to start a TLA+ spec with Claude.

# A toy problem

{{% pic src="beans.jpg" alt="" / %}}

Here's a classic puzzle. You have a can of beans. Each bean is white or black. The can starts nonempty. While there are at least 2 beans:
- Choose 2 beans.
- If they're the same color: discard both, add 1 white bean.
- If they're different colors: discard both, add 1 black bean.

Two questions:

1. Can the number of beans ever reach zero?
2. If the algorithm terminates with b = 1, what must have been true at the start?

You could think really hard. Or you could write it down in TLA+ and let a model checker answer both questions automatically. The whole point is to avoid thinking---or at least, to have a machine verify that your thinking was correct. Or convince your friends that your thinking is correct, or convince the peer-review panel for your research paper.

# How logical formulae produce a state machine

TLA+ was invented by Leslie Lamport in the 1990s. TLA stands for "Temporal Logic of Actions," and TLA+ is the name of the specific language. TLA+ has basic boolean logic, and it has sets and functions, and quantification ("for all" and "there exists"). It also has _temporal_ operators, which we'll see soon.

When you write a specification in TLA+, you're writing a logical formula which defines a state machine. The machine has a fixed set of variables, and each _state_ is an assignment of values to the variables. For the can problem, there are variables: `w` (the number of white beans) and `b` (the number of black beans). Each state is an assignment of values to `w` and `b`. A _behavior_ is a sequence of states, and a _specification_ is the set of allowed behaviors.

## Initial state

We need an initial-state rule---a predicate that's true of exactly the states we're willing to start from. In English: "the can is initially nonempty," or `w + b > 0`. Which of these initial states matches the predicate?

```text
b = 0 /\ w = 0
b = 0 /\ w = 4
b = 6 /\ w = 1
b = 1 /\ w = "foo"
```

In TLA+ "/\\" means "and", so `b = 0 /\ w = 0` means "b = 0 and w = 0".

The second and third states match the predicate. The first doesn't, because `w` and `b` sum to zero, and the final state doesn't make sense because you can't add 1 and the string "foo". TLA+ has no type system, only sets, so there's nothing stopping `w` from being a string. Lamport calls something like that "silly." We prevent silly states by specifying that `w` and `b` must be natural numbers:

```text
EXTENDS Integers
Init == w \in Nat /\ b \in Nat /\ w + b > 0
```

`EXTENDS Integers` imports everything you need for handling integers, like the set of natural numbers `Nat`, and `\in` is the set-membership operator \(\in\). In TLA+, `==` means "defined as." This is confusing, because it's kind of the opposite of C: a single `=` tests for equality, and `==` names a formula (like a macro).

## State transitions

A state-transition rule is a predicate over *two* states---current and next---that says which transitions are legal. Let's turn our algorithm into a state-transition rule in TLA+.

Starting from English:
- 2 white beans: remove 2 whites, add 1 white → net effect: w -= 1
- 2 black beans: remove 2 blacks, add 1 white → net effect: b -= 2
- 1 of each: remove 1 white and 1 black, add 1 black → net effect: w -= 1

Notice the first and third cases have identical effects on the state: both just subtract 1 from `w` and leave `b` alone. This is the kind of insight that falls out naturally when you write things down precisely.

In TLA+ these become three **actions**:

```text
WW == w > 1 /\ w' = w - 1 /\ UNCHANGED b          \* Picked 2 white
BB == b > 1 /\ b' = b - 2 /\ w' = w + 1           \* Picked 2 black
WB == w > 0 /\ b > 0 /\ w' = w - 1 /\ UNCHANGED b \* Picked 1 of each
```

There are two operators that we're seeing for the first time here. The **prime** (`'`) operator means "the next value of this variable": `w' = w - 1` means "in the next state, w will equal the current w minus 1." `UNCHANGED b` is shorthand for `b' = b`. You have to account for every variable in every action---TLA+ won't assume that unmentioned variables stay the same. This is annoying, but it forces you to think about what each action does to the whole state.

The terms without primes are the **guard**: conditions that must hold *now* for the action to fire. The terms with primes are the **assignment**: what the next state looks like. If the guard is false, the action is disabled. The `\*` starts a comment (yes, it's a backslash and a star).

## A full TLA+ spec

Here's the full specification:

```text
-------------- MODULE beans -----------------
EXTENDS Integers
VARIABLES w, b
vars == <<w, b>> \* convenient list of all variables

Init == w \in Nat /\ b \in Nat /\ w + b > 0

WW == w > 1 /\ w' = w - 1 /\ UNCHANGED b          \* Picked 2 white
BB == b > 1 /\ b' = b - 2 /\ w' = w + 1           \* Picked 2 black
WB == w > 0 /\ b > 0 /\ w' = w - 1 /\ UNCHANGED b \* Picked 1 of each
Next == WW \/ BB \/ WB

Spec == Init /\ [][Next]_vars /\ WF_vars(Next)
==============================================
```

The formula `Next` is defined as the OR (`\/`) of all three actions---at any given state, whichever actions have their guards satisfied are enabled. This is **nondeterminism**: the spec doesn't say which action happens, just which are possible. The model checker explores all of them.

The `Spec` line is the spine of any TLA+ specification and you'll see it in basically every TLA+ spec you read. It says: "every behavior allowed by this spec starts from an initial state where Init is true, and every transition satisfies Next." The `WF_vars(Next)` part means "the algorithm must keep making progress---it can't stall forever when an action is enabled." That's called a [fairness constraint](https://www.hillelwayne.com/post/fairness/), stay tuned...

The `[][Next]_vars` part hides some complexity I'm going to skip. If you want to deeply understand it, read Lamport's "Specifying Systems." For prompting purposes, just know it goes there.

## States and behaviors

A **behavior** is an infinite sequence of states, starting from an initial state, where each step is allowed by `Next`. Behaviors are infinitely long by convention. If the algorithm terminates (reaches a state where no further actions are enabled), the final state just repeats forever. That repetition is called **stuttering**. So "termination" in TLA+ means the algorithm reaches a stuttering state and stays there.

There are infinitely many init states in our spec---any pair of natural numbers with `w + b > 0` is a valid initial state. Let's look at a subset of the state space, just the states that begin at b=3 and w=5:

{{% pic src="beans_state_graph.svg" alt="" / %}}

Each node is a state. Each edge is a valid transition, labeled with which action(s) apply. Some edges say "WW/WB"---that's because when `w > 1` and `b > 0`, both WW and WB are enabled and lead to the same next state (both just decrement `w` by 1). The model checker explores both actions but discovers the same successor state, so they collapse into one edge.

A **behavior** in this picture is a path from the initial node to a terminal node, followed by stuttering. Here's a behavior:

{{% pic src="behavior3.svg" alt="" / %}}

## Model-checking

The model-checker, TLC, starts from the set of initial states, applies the next-state relation to generate successor states, and uses hashing (it calls this "fingerprinting") to avoid revisiting states it's already seen.

As TLC discovers states, it checks invariants and properties. (We'll learn what those are in a minute, but for now: these are the assertions that show your spec is correct.) If TLC finds a violation, it reports the counterexample: a sequence of states that leads to the bad state. Because it's breadth-first search, it finds the **shortest** counterexample (or one of the shortest) for invariant violations. That's helpful for diagnosis---a 4-step trace is much easier to debug than a 100-step one.

## The spec and the config

TLA+ specs comprise two files, beans.tla with the temporal logic, and beans.cfg file with model-checking config. Why two files? A specification is an idealized description of a system, and its state space and behaviors are usually infinite. You can do many things with this spec: _prove_ it correct, or use it to document your algorithm and explain it to your friends, and so on. Model-checking is only one of several uses for the spec, so the model-checking config is in a separate file.

Of course, model-checking is impossible if there are infinitely many states. We usually have to artificially bound the state space by setting limits on the size of the init-state set, or limiting the number of actions taken, and so on. All these limits should be in the config file.

If there's a bug in your spec, you'll usually see it in a small bounded model. (We call this the "small-model hypothesis.") In practice, the first check catches obvious bugs in the first second or two. If you run for a few hours without a violation, you have higher confidence. How big does the bound need to be to find all bugs? That's hard to say. It has to come from your reasoning and intuition about the algorithm.

So, let's say this is beans.tla (same spec as I showed above):

```text
-------------- MODULE beans -----------------
EXTENDS Integers
VARIABLES w, b
vars == <<w, b>> \* convenient list of all variables

Init == w \in Nat /\ b \in Nat /\ w + b > 0

WW == w > 1 /\ w' = w - 1 /\ UNCHANGED b          \* Picked 2 white
BB == b > 1 /\ b' = b - 2 /\ w' = w + 1           \* Picked 2 black
WB == w > 0 /\ b > 0 /\ w' = w - 1 /\ UNCHANGED b \* Picked 1 of each
Next == WW \/ BB \/ WB

Spec == Init /\ [][Next]_vars /\ WF_vars(Next)
==============================================
```

This is unbounded and cannot be model-checked, because there are infinite init states. To bound the model, I can update `Init` like this:

```text
CONSTANTS WMAX, BMAX
Init == w \in 0..WMAX /\ b \in 0..BMAX /\ w + b > 0
```

Here's beans.cfg:

```text
CONSTANTS
  WMAX = 3
  BMAX = 3

SPECIFICATION Spec
```

Now there are 15 init states, and 17 states total. (Exercise for you: Can you figure out why those numbers?)

## Answering the questions

How do we use the model-checker, TLC, to answer our two questions without thinking too hard?

**Can the number of beans reach zero?** We write an **invariant**---a state predicate we claim is always true across every reachable state:

```text
NotEmpty == w + b > 0
```

We tell TLC to check this by defining it in beans.tla, and referencing it in beans.cfg:

```text
INVARIANT NotEmpty
```

TLC does a breadth-first search through the entire reachable state graph and confirms that no state violates it. The can of beans is never empty.

Why not? Look at the guards: every action requires at least 2 beans to be enabled (`w > 1`, `b > 1`, or `w > 0 /\ b > 0`). And every action decrements the total bean count by exactly 1. So once you're down to 1 bean, no action is enabled, and the algorithm terminates. You can never go from 1 to 0.

**If b = 1 at termination, what must have been true initially?** Look at BB, the only action that changes `b`. It decrements `b` by 2. That means `b`'s parity (odd or even) never changes from the init state to the end. So if we terminate with `b = 1` (odd), `b` must have been odd at the start. We can express this as a **temporal property**---a formula over an entire behavior, not just a single state:

```text
TerminationWithOneBlack == (b % 2 = 1) => <>[](b = 1 /\ w = 0)
```

Read this as: "if `b` is odd, then eventually-always `b` will be 1 and `w` will be 0."

This uses two **temporal operators**: `<>` (diamond, meaning "eventually") and `[]` (box, meaning "always"). Combined as `<>[]`, they mean "eventually reaches a state and stays there"---which is exactly termination.

We add the definition to beans.tla and reference it in beans.cfg:

```text
PROPERTY TerminationWithOneBlack
```

I used `PROPERTY` in beans.cfg because this is a temporal property (it uses temporal operators and it applies to whole behaviors), rather than `INVARIANT` like I did for `NotEmpty`. TLC verifies this property holds across all behaviors, confirming that any behavior starting from an odd `b` terminates with `b = 1`. 

But wait---is it _really_ true that if b is odd, then eventually b=1 and w=0? What if b is odd and then the state machine just sits there doing nothing? That's what the fairness constraint `WF_vars(Next)` ensures. It says that if `Next` is continuously enabled (i.e., one of the actions is enabled because there are at least two beans), then it will eventually execute. That's necessary for any "eventually" property to be true. 

## The temporal operators

Temporal logic adds two core operators on top of ordinary first-order logic, and you can combine them in interesting ways.

`<>P` (**eventually P**): at some point in this behavior, `P` is true. If `P` flickers on briefly and then stops, that still counts.

`[]P` (**always P**): at every point in this behavior, `P` is true. This is essentially what an invariant says, just expressed as a temporal formula.

The combinations:

`<>[]P` (**eventually always**): `P` eventually becomes true and stays true forever. This is how you express stable termination: the system reaches a good state and never leaves it.

`[]<>P` (**always eventually**): `P` keeps coming back infinitely often. There can be long gaps where `P` is false, but it always returns. This is how you express things like "the lock is always eventually acquirable" or "the queue is always eventually drained."

Note, `<>[]P` is strictly stronger than `[]<>P`. If `P` eventually stabilizes to true forever, it certainly keeps coming back. But `P` can keep coming back without ever stabilizing.

## TLA+ and AI

{{% pic src="robot.jpg" alt="" / %}}

I prompted Claude to write a spec for the can-of-beans problem:

```text
> write me a TLA+ spec for the following toy example.

there's a can of w white and b black beans, at least one bean initially.

at each step, if there are at least 2 beans, remove 2. if they're the same color, discard both and add 1 to w, if they're different, discard both and add 1 to b.

use the spec to reason: can the number of beans reach 0? what initial state is necessary to terminate with b=1? 

download TLC 1.8.0 and run the model-checker to find the answers.
```

I told it to download TLC 1.8.0, which is the current prerelease, since the last official TLC release was a couple years ago. As you'd expect, Claude one-shotted a spec that passes model-checking and answers the questions. But this was a very easy assignment.

LLMs have mostly removed the first barrier to entry of TLA+: its syntax. It's still your job to define what properties your system must uphold; [Hillel Wayne finds that they're bad at writing these](https://buttondown.com/hillelwayne/archive/llms-are-bad-at-vibing-specifications/). It's also your job to figure out how your existing system actually behaves. Even with intense handholding, [LLMs can't yet read the code of an existing system and translate it into a TLA+ spec](/review-sysmobench/). So you're not entirely excused from thinking yet. But LLMs have transformed TLA+ from an opaque thinking tool into a translucent one.
