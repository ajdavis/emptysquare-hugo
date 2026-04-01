+++
type = "post"
title = "Review: SysMoBench: Evaluating AI on Formally Modeling Complex Real-World Systems"
description = "Some TLA+ experts try to teach LLMs to write TLA+. The LLMs fail."
category = ["Review"]
tag = ["tla+", "ai"]
draft = true
enable_lightbox = true
+++


{{% pic src="tumblr_83912c4240955ebef038bc2801583ed3_a2869834_1280.jpg" alt="" /%}}

[SysMoBench: Evaluating AI on Formally Modeling Complex Real-World Systems](https://arxiv.org/abs/2509.23130), by authors from Nanjing University, Microsoft Research Asia, University of British Columbia, and University of Illinois Urbana-Champaign. (Disclosure: I've collaborated with two of the authors from UBC, Finn Hackett and Ivan Beschastnikh.) This is a useful and thought-provoking test of LLMs' ability to write TLA+ specs of existing code. My summary and thoughts are below. [See Murat's summary as well](https://muratbuffalo.blogspot.com/2026/03/sysmobench-evaluating-ai-on-formally.html).

# The Paper

Can LLMs write formal specifications of real software systems? Not toy examples or textbook algorithms, but actual distributed and concurrent systems? The authors built a benchmark called SysMoBench to find out. They take eleven real-world system codebases---e.g. the Raft consensus implementation in etcd, leader election in ZooKeeper, a spinlock in the Asterinas operating system---and ask AI agents to produce a TLA+ spec of each.

The benchmark evaluates AI-generated TLA+ specs on four increasingly strict levels:

1. **Does it compile?** Is the TLA+ syntactically valid?
2. **Does it run?** Can the TLC model checker execute it without errors?
3. **Does the code conform to the spec?** When you run the actual system and record traces of its behavior, does the model accept those traces?
4. **Does it satisfy correctness properties?** Do the safety and liveness invariants hold?

This is exciting. As we're all learning, coding agents work best when they're put in loops with test oracles or performance evaluations. DataDog's very impressive [harness-first engineering](https://www.datadoghq.com/blog/ai/harness-first-agents/) articles are the latest example. And people like me (distributed systems and formal methods nerds) would love to auto-extract formal specs from existing code. So here we have a harness for guiding an agent toward a good spec.

The benchmark tests three agent strategies for producing the spec, each with different inputs:

The **Basic Modeling Agent** gets the most help. It receives the source code and a detailed task definition that spells out exactly which actions to model and which to skip. Here's the human-written prompt for etcd Raft:

```plain
TLA+ Model Generation Prompt

You are an expert in formal verification and TLA+ models with
deep expertise in concurrent and distributed systems,
particularly etcd and Raft consensus.

Convert the following source code to a comprehensive TLA+
model.

System:  etcd distributed key-value store

<SOURCE CODE INSERTED HERE>

System-specific modeling requirements:

MANDATORY CORE ACTIONS (must include all):
1.  [Message Types] MsgHup (election timeout),
    MsgVote/MsgVoteResp (voting), MsgApp/MsgAppResp (log
    replication)
2.  [Node States] Four states:  StateFollower, StateCandidate,
    StateLeader, StatePreCandidate (prevote enabled)
3.  [Leader Election] Complete prevote + vote phases:
    PreCandidate → Candidate → Leader transitions
4.  [Log Operations] Log entry appending, consistency checks,
    commitment with majority quorum
5.  [Heartbeat/Timeout] Election timeouts triggering campaigns,
    heartbeat prevention of elections
6.  [Client Proposals] MsgProp message handling and log entry
    creation by leaders

EXPLICITLY EXCLUDED (do not model):
- Configuration changes and joint consensus (ConfChange
  messages)
- Log compaction and snapshots (MsgSnap)
- ReadIndex optimizations (MsgReadIndex)
- Async storage operations (LocalAppendThread,
  LocalApplyThread)
- Advanced flow control and progress tracking details

REQUIRED BEHAVIORAL SCOPE:
- Prevote phase (StatePreCandidate) must be modeled as it's
  enabled by default in etcd
- State transition constraints:  Follower → PreCandidate →
  Candidate → Leader (strict transitions)
- Message processing by state:  only valid message types
  handled in each node state
- Term advancement rules:  nodes advance term when receiving
  messages with higher term
- Voting restrictions: one vote per term, term must be current
  or newer
- Heartbeat mechanism: leaders send heartbeats, followers reset
  election timeout on receipt
- Log consistency checks:  prevLogIndex/prevLogTerm validation
  in MsgApp processing
- Majority-based leader election and log commitment
- Basic network message delays and losses

Generate a TLA+ model that accurately models the system's behavior.

CRITICAL OUTPUT REQUIREMENTS:
1.  The MODULE name must be exactly "etcdraft"
    (---- MODULE etcdraft ----)
2.  Return ONLY pure TLA+ model code - no markdown code blocks
    (no ```tla or ```)
3.  Do not include any explanations, comments, or formatting
    markers
4.  Start your response directly with:
    ---- MODULE etcdraft ----
5.  End your response with the closing ====
6.  **DO NOT define invariants** (like MutualExclusion,
    Invariant, etc.), focus on modeling the system behavior
7.  **MUST include EXTENDS statement**:  The model must extend
    at least these modules: TLC, Sequences, SequencesExt,
    Naturals, FiniteSets, Bags
```

This is a _lot_ of guidance! A human who'd gotten this far would be most of the way to writing the spec. The guidance encodes all the wisdom of an expert in Raft, etcd, and TLA+. I doubt I could write instructions this good unless I'd already written the spec myself, actually...

So that was the Basic Modeling Agent, the first of the three agents. The **Code Translation Agent** takes a more mechanical approach: it translates source code statement-by-statement into TLA+, then assembles the pieces into a model. It doesn't receive the task definition. Finally, the **Trace Learning Agent** ignores source code entirely. It receives only execution traces (logs of the system's runtime behavior) and tries to infer the model from those.

Here's my understanding of the data flow through SysMoBench:

{{%pic src="flowchart.svg" alt="Flowchart of the SysMoBench pipeline. Three agent strategies feed into an LLM: the Basic Modeling Agent takes source code and a task definition; the Code Translation Agent takes source code; the Trace Learning Agent takes execution traces. The LLM produces a TLA+ model, which is evaluated in four sequential steps: syntax correctness via the SANY parser, runtime correctness via TLC, conformance to the system via trace validation (using execution traces), and invariant correctness via model checking (using invariant templates). The pipeline ends with a score." %}}
{{% /pic %}}

Surprisingly, the spec-writing agents are told *not* to write invariants. The authors provide invariants and guidance on how to write them, but a separate agent concretizes invariant templates, isolated from the spec-writing agent. The invariants are used only during evaluation, to judge the generated spec. When I write TLA+, I develop the invariants and the state machine at the same time, using each to shape the other until I've hacked them into convergence. In SysMoBench, the LLM has to write a spec that upholds invariants it doesn't know about. I guess this makes sense: presumably the real system already upholds these invariants, so if the spec accurately models the system, it should uphold them too. The invariants become a blind test of whether the AI truly understood the system's behavior.

(But what if the system is buggy? Maybe those bugs become more obvious when they're lifted into the TLA+ spec. Or maybe the LLM's inability to make a spec that matches both the code and the invariants will lead you to the bug.)

{{% pic src="tumblr_67bdc61c37778a4fb1544c515f1f18ae_ff860f0e_1280.jpg" alt="" /%}}

# Results

The results are bad news for bots, good news for my job security.

The authors tested four models: Claude Sonnet 4, GPT-5, Gemini 2.5 Pro, and DeepSeek-R1. For the simple spinlock implementation (a few hundred lines of Rust), most LLMs do fine. They write TLA+ specs that compile, run, conform to the implementation, and satisfy invariants. But for distributed systems like etcd Raft (thousands of lines of Go), performance craters. In the Basic Modeling setup, of the four LLMs tested, only Claude Sonnet could even write a syntactically valid spec of etcd Raft. Its conformance score was less than 8% (the percentage of instrumented actions in the code whose behavior matched the spec). And remember how much human guidance it got!

{{% pic src="table-3.png" alt="Table comparing two AI agents (Basic Modeling and Code Translation) across four LLMs on two systems. For Asterinas Spinlock, all LLMs achieve 100% syntax and runtime correctness with both agents, and conformance and invariant scores are mostly 80-100%. For etcd Raft with Basic Modeling, only Claude Sonnet 4 passes syntax (100%) and reaches runtime (25%), conformance (7.69%), and invariant (69.23%) evaluation; GPT-5 gets 47.87% syntax, and Gemini and DeepSeek get 50% syntax. With Code Translation on etcd Raft, Claude and DeepSeek achieve 100% syntax, GPT-5 gets 100%, but Gemini gets only 44.44%. Only Claude reaches conformance (15.38%) and invariant (92.31%) evaluation." / %}}

The error analysis is interesting too. LLMs struggle much more with liveness properties (like "every thread eventually releases its lock") than safety properties (like "at most one thread holds the lock at a time"). Only about 8% of safety invariants were violated, but 42% of liveness properties were.

{{% pic src="tumblr_25a60eedcc53068a99df7059fcf65dce_fbc49663_1280.jpg" alt="" /%}}

# LLMs are still bad at specifying systems

I was surprised how much the authors spoon-feed instructions to the agents. The humans have already done most of the intellectual work before the AI even starts: they define which actions to model and what's in scope and out of scope. If a human gets that far, writing the actual TLA+ should be relatively easy. SysMoBench tests whether AI can translate a nearly-complete problem definition into TLA+ syntax, and even so, most models fail on anything nontrivial. The etcd code has already been curated to merely 2,159 relevant lines, what would an AI do confronted with the _whole_ etcd codebase? I'm not criticizing the paper; I'm saying its results are sobering.

Even with all this hand-holding, only Claude performed well among the LLMs tested, and that was Claude Sonnet, not the larger Opus. Gemini 2.5 Pro was arguably the frontier model in the study, and it failed badly. Claude's reputation as the best coder is confirmed.

That said, the task definitions themselves are a great template for how a human should approach writing a spec. Before you write any TLA+, define all the actions, define what's in scope and out of scope. You're most of the way there at that point. The paper demonstrates (inadvertently?) a superb process for specifying an existing codebase.

The LLMs used were from mid-2025, so they're almost a year old. Anecdotally, my colleagues are getting better results generating TLA+ from design documents with newer models. But those successes come from reading English-language design docs, not from reading thousands of lines of implementation code. Reading implementation code at scale seems to actually confuse the models to the point where they forget TLA+ syntax. And 5,000 lines of source code, the largest system in the benchmark, is trivial compared to real systems: MongoDB is half a million lines of C++. Ideally an LLM would figure out which parts of a large codebase to focus on and keep its context window tidy.

{{% pic src="tumblr_ff012cbcaff4f025e28669c4dffaffde_8d3d6f00_1280.jpg" alt="" /%}}

# How trustworthy is the spec?

An interesting open question: if you generate a spec from code, check conformance with some traces, and then model-check the spec against invariants over a much larger state space---what have you actually proven?

{{%pic src="conformance-checking.svg" alt="A flowchart: Code produces a TLA+ spec via the specifying agent, and trace checking connects the code and spec. Invariants plus the spec flow into a pass/fail outcome." %}}

{{% /pic %}}

Here's my visualization of the problem. <span style="color: #1971c2; font-weight: bold">The code has a big (usually infinite) set of possible behaviors.</span> By instrumenting and testing the code, you can record **a tiny subset of its behaviors as traces**. Trace-checking proves these traces are also a subset of <span style="color: #2f9e44; font-weight: bold">the spec's behaviors</span>. The model-checker can explore <span style="color: #2f9e44; font-weight: bold">a different subset of the spec's behaviors</span>, checking that they are a subset of <span style="color: #f08c00; font-weight: bold">the behaviors allowed by the invariants</span>. A proof system like TLAPS can prove facts about <span style="color: #2f9e44; font-weight: bold">all of the spec's behaviors</span>. But there still remain many unexplored areas of unknown size: **untested code behaviors** and **unimplemented spec behaviors**.

{{%pic src="behavior-spaces.svg" alt="" %}}
The space of all behaviors allowed by the code, spec, and invariants.
{{% /pic %}}

So all we know is that:

* The recorded traces conform to the spec.
* If we model-checked, then the model-checked spec behaviors uphold the invariants.
* If we proved, then _all_ spec behaviors uphold the invariants.

Is there any way to estimate the size of the other sets? [I've been thinking about these subset relationships among code and spec behaviors for a while](/mongodb-conformance-checking/), and [wondering how long to keep checking more behaviors](/how-long-must-i-test/). Further research is needed.

# What comes after SysMoBench?

The natural next steps seem like prompt engineering exercises. Can you improve benchmark scores by adding an intermediate "TLA+ expert" agent that breaks down the problem further? Can you automate the trace instrumentation, which is currently the main human effort (up to four person-days in the SysMoBench examples)? Can the AI think of invariants on its own? You'd also need to guard against gaming---an agent that sees its own score could learn to write invariants that always pass, instead of real correctness properties. Or it could manipulate the trace code to make trace-checking pass.

SysMoBench shows that LLMs have a long way to go before they replace human spec authors. They crush LeetCode problems, but they can't yet comprehend, abstract, and specify real-world distributed systems. That's encouraging for those of us who do this work for a living, at least for a few more months.

{{% pic src="tumblr_14f09c2a443b1ad76250915aae60833f_08062ea2_1280.jpg" alt="" /%}}

***

Images: [The Vault Of The Atomic Space Age](https://thevaultoftheatomicspaceage.tumblr.com/)
