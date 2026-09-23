+++
type = "post"
title = "The Humanoid Lesson, or, Will AI Leave Anything for Database Researchers To Do?"
description = "A review of 'What Happens When the Model Eats the Stack? Rethinking the Research Agenda for Data Agents to Withstand the Bitter Lesson.'"
category = ["Review"]
tag = ["ai"]
draft = true
enable_lightbox = true
+++

[What Happens When the Model Eats the Stack? Rethinking the Research Agenda for Data Agents to Withstand the Bitter Lesson](https://arxiv.org/abs/2609.03141), published on Arxiv by Berkeley and Stanford researchers. First software ate the world, now foundation models are eating software. Researchers have designed elaborate harnesses to boost LLMs' performance, and even [designed meta-harnesses to automate harness design](/review-automated-design-of-agentic-systems/). But every time we make a system to compensate for some weakness in LLMs, the next generation of models doesn't need it. We will never contradict [The Bitter Lesson](/ai-omg/#the-bitter-lesson); we just keep learning it. So if you don't work at OpenAI or Anthropic or NVIDIA, is there anything useful for a database researcher to do?

This paper's authors say yes, and propose a research agenda to adapt databases for usage by AI. It seems like a cope. I'm not convinced that AI will leave any software on its plate. What problems remain are the same ones humans have had since the start of the Information Age, because AIs and humans have similar difficulty accessing tribal knowledge.

{{< subscribe >}}

***

A previous paper, [Supporting Our AI Overlords: Redesigning Data Systems to be Agent-First](https://arxiv.org/abs/2509.00997), predicted that agents will bury databases under unoptimized, speculative queries, so we should redesign databases to deal with that. Two of the same authors wrote the current paper. Now they say:

> Moreover, newer models are rapidly improving the efficiency of general coding agents, drastically reducing the average number of turns and tokens required per query. This trend directly challenges the premise of recent work, which argues that future data systems will be bottlenecked by agentic speculation, a workload characterized by sheer scale and inefficiency of agent-issued queries, which data systems will need to optimize for. We instead see that newer models natively improve efficiency on a given task, solving each one with fewer actions and less frequent failures, on average, over successive model generations.

Fair enough, newer models flail less. But the Overlords paper also said agents make _varied_ queries. I see no new evidence that heterogeneity won't be a problem for today's databases, which are designed for repetitive OLTP.

{{% pic src="figure-1.png" alt="" %}}
Figure 1b from the paper, showing improved efficiency and accuracy on the [Data Agent Benchmark](https://arxiv.org/abs/2603.20576). I don't know why they measure only GPT, not Claude.
{{% /pic %}}

The authors find that, as models get smarter, their mistakes shift from botched tool use to ignorance about the environment:

> We find that execution errors due to incorrect tool use or execution decline as model capability increases. Meanwhile, the remaining errors for GPT-5.6 Sol are dominated by failures of environmental knowledge. Specifically, over 60% of failures arise from semantic misinterpretation, including misunderstanding task meaning or relying on invalid proxies, using the wrong data sources, tables, fields, or metrics, or incorrectly using entities, join keys, and identifiers.

So, they say, human researchers should study how to provide AIs with "persistent semantic context": curated knowledge about what data exists, what it means, and which sources are authoritative. Their example task:

> "Write a quarterly business review explaining why European revenue missed forecast, reconcile the discrepancy against Finance's official numbers, and recommend corrective actions" requires identifying authoritative datasets across multiple systems, resolving conflicting metric definitions, understanding organization-specific business conventions, interpreting semi-structured documentation, and validating intermediate results.

OK fine. But we've been talking about this "persistent semantic context" for decades: it's tribal knowledge. It's always been the case that a skilled engineer or analyst who just joined the company or switched teams has trouble finding things. AI changes nothing. 

# The Humanoid Lesson

Inspired by the Bitter Lesson, I propose the Humanoid Lesson: if you want to guess an LLM's strengths and weaknesses, a good first approximation is to anthropomorphize it. AIs have the same problems we do. Drop a genius into a large corporation and she'll spend most of her time discovering folk knowledge, particularly if she's an LLM and she gets total amnesia every few minutes. On the other hand, she's still a genius: she works better if you give her freedom, instead of imposing a rigid harness or process.

The paper's research agenda says:

> We outline key directions for the research community, which will require developing new techniques for semantic consistency, to ensure the correctness and integrity of persistent contexts, as well as optimized data structures, construction methods, physical designs, and compression techniques.

I'm skeptical that there is any useful research agenda. The corollary to the Humanoid Lesson is that whatever has worked for humans will work for LLMs: if you want semantic consistency, just keep the docs updated however humans have always done. We haven't done a good job, but this is not an LLM-specific problem. If you want a novel technique, just throw LLMs at the problem: whenever something changes, tell them to read all the docs and update them. Shrug emoji.

> When new knowledge is acquired, the system must determine who should observe the update, how it should propagate across overlapping scopes, and when conflicting semantic views should be reconciled or allowed to coexist.

I wonder, is this any different for clankers versus meatheads? The few interesting questions in this paper would be interesting even if LLMs didn't exist.

# Just Use Git

In an attempt to create a complicated and paper-worthy research question, the authors propose that persistent context is a database consistency problem:

> Determining the appropriate semantic consistency model---and understanding its implications for accuracy, latency, scalability, and maintenance cost---remains an open research question.

This is an invitation to overthink. In MongoDB's early days, we had code and we had a wiki, and they were always out of sync. You could ask interesting questions about the consistency between the two. Then we started [maintaining our architecture guides in Git](https://github.com/mongodb/mongo/blob/master/src/mongo/db/repl/README.md), and changing them in the same commit as the code they describe. We developed a process in our ticket tracker and our code reviews to check which docs were affected by code changes. Store your docs next to the code, version them together, and update them as soon as possible after a code change. The only difference betweeen humans and LLMs here is that humans are lazy and LLMs are maniacs.

The paper's authors ask whether outdated context should be updated immediately or on demand, and this is also overthinking. It's a sure bet that docs are read-heavy, so it's always worth updating them eagerly. If some bit of tribal knowledge were never read, you could cleverly avoid updating it. But in real life, good docs are updated often and read constantly. If you have a bit of context that isn't used, delete it, or else diagnose why no one can find it.

# Complement or Substitute?

The Humanoid Lesson means that AI doesn't have new problems, it has the same problems humans do. The more humanoid and then superhuman they become, the fewer problems they leave us to solve.

A general uncertainty they introduce is, for any technology, is it a complement to LLMs or a substitute? This February, investors decided Claude was a substite for existing software: it made all software worthless because it could build anything on demand. So they sold all their software-as-a-service stocks (the "SaaSpocalypse"). Then they decided some SaaS companies were actually complements to AI, and SaaS stocks went back up. They've been freaking out and seesawing ever since.

If we invent some technique that makes Claude Fable work better today, will it make the next model better too, so the gains multiply? Or will the next model subsume it? The "What Happens When the Model Eats the Stack" paper suggests that today's stack is near-obsolete but a new stack will provide enduring value. I'm skeptical. It's equally likely that future AIs will beat any existing system by writing new software from scratch for each application. That's a bitter lesson and I don't know how you and I will handle it.
