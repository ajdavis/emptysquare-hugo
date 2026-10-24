+++
category = ["Research"]
date = "2026-10-24T12:52:17.036731+00:00"
description = "My notes on the International Symposium on Software Reliability Engineering."
draft = false
enable_lightbox = true
tag = ["conference"]
thumbnail = "IMG_7726.jpg"
title = "ISSRE 2026 Recap"
type = "post"
+++

{{% pic src="IMG_7726.jpg" alt="Silhouette of a wind-bent tree on the Cyprus shore at dusk, against a purple sky and calm sea" / %}}

I went to the International Symposium on Software Reliability Engineering (ISSRE 2026) in Cyprus, to present [The Polyglot's Dilemma: Conformance Testing a Dozen Specs in as Many Languages](/polyglots-dilemma/).

This conference seems to favor software engineering tips & tricks, empirical results, and industry experience reports. Compared to other conferences I've attended, there's less theoretical or foundational research. (Though there's some, like [Program Reversal for Error Reachability Analysis](#program-reversal-for-error-reachability-analysis).) Still, the conference is very academic: only 25% of papers had an industry coauthor, and someone at lunch told me I'm a valuable rarity because I work for a company.

{{< subscribe >}}

There were a number of talks about AI plus formal logic, which [my team](https://www.mongodb.com/company/research/distributed-systems-research-group) is also researching. See:

1. [The Prover Is the Judge](#the-prover-is-the-judge-verified-security-software-from-ai-coding-agents-in-ada-spark) ← **recommended**  
2. [LLM-Generated Specifications](#an-empirical-study-of-llm-generated-specifications-for-verifast)  
3. [Verified Code from Natural Language](#toward-verified-code-from-natural-language:-understanding-pipeline-design-for-formally-verified-rust-program-generation)

The conference accepted 167 papers, 37% of submissions. Not very selective; top conferences are more like 25%. The organizers said authors from China submitted the most papers and had the most accepted, closely followed by the USA. In the industry track specifically, China had slightly more submissions than the USA and somehow got 80% accepted vs. the USA's 23%. Engineers at Chinese companies are writing good papers! My theory: as AI demolishes the language barrier, Chinese authors are working through a backlog of good ideas that were too hard to submit to English-language conferences before? Now the papers are accepted, but the presenters can't get visas&mdash;[this was an epidemic at SIGMOD](/sigmod-2026/), which was hosted by China's rival India, but even in Cyprus this was a problem.

{{<toc>}}

# The most interesting talks

## Laurie Williams Keynote: Software Supply Chain Attacks

Most software is 80% OSS and third-party code. Many libraries are shared among many apps, and most apps have hundreds of dependencies. So attackers are increasingly targeting common libraries, so they can penetrate thousands of apps with a single exploit. Williams is researching supply chain security and running [a research center on that topic](https://s3c2.org/) at North Carolina State University. She names four attack vectors: code dependencies, build infrastructure, AI models and data, and humans.

Examples:

* [The Shai-Hulud supply chain attack in Sept 2025 compromised 500+ packages on NPM](https://www.cisa.gov/news-events/alerts/2025/09/23/widespread-supply-chain-compromise-impacting-npm-ecosystem).  
* LiteLLM: Attackers compromised a dependency of LiteLLM, so LiteLLM created a compromised build which was downloaded by all their users. LiteLLM then became a credentials exfiltrator.  
* Axios supply chain attack March 2026: Axios is a Node.js HTTP client lib. Its maintainer was invited to a malicious Teams meeting which had a "must update your software" popup that he clicked, installing a Trojan onto his machine, which then exfiltrated his NPM credentials, letting the attackers compromise Axios, so they then hacked anyone who installed Axios.

### Summits

The mission of her research center is to maintain the trustworthiness of OSS so industry doesn't build proprietary alternatives that they consider more secure. The research center has [held small summits of government and industry leaders to discuss the problem](https://s3c2.org/challenges/). Proposed solutions:

* Require 2 people to sign off on new package versions  
* Cooldowns, such as [Dependabot's 3-day min age rule](https://github.com/dependabot/dependabot-core/discussions/15582): don't auto-update dependencies to the *latest* version if it's too new

Other summit results: There's a lot of research into AI detection of supply chain attacks. AI is a solution and also a risk. Some people only trust certain models to write code. (Presumably they distrust the Chinese models?) A lot of companies are moving toward fully automated software factories, with adversarial AIs reviewing each other. Is this good enough or do we need a human in the loop? The human can't just be a "blame sink"&mdash;they must actually be able to review somehow.

There's concern about abandonware. There's no sure way to detect when a dependency is abandoned. Maintainers might abandon their projects *more* due to a flood of slop PRs. Maybe a tragedy of the commons: firms can reimplement dead dependencies with AI, which creates "local trust but collective loss."

We need reproducible builds with provenance recorded for each input. Build each component twice (on two systems) and check the outputs are bitwise equal, in case one system is compromised.

I learned a new term, "shadow AI": the unauthorized use of AI by employees, or PRs secretly authored by AI, or human reviewers secretly delegating to AI.

### Secure Software Supply Chain Center's Research

Pinned dependency versions prevent a build pipeline from instantly adopting a hacked or vulnerable version, but also prevent it from adopting a fixed version. E.g., there was a vulnerable version of Log4j that's still being downloaded years later due to pinned versions. (I wonder, why doesn't the maintainer delete that release?) The S3C2 researched how common each pinning strategy is, and recommends that libraries specify a version *range* for dependencies, and apps pin *exact* versions for all dependencies.

Abandabot: Detects that your code depends on an abandoned project, detects whether it matters, and recommends a maintained alternative.

Fake stars: Devs use GitHub stars to evaluate whether code is trustworthy, but [stars can be faked](https://arxiv.org/abs/2412.13459). AI agents can make a malware repository with lots of stars, commits, badges, and downloads; it's hard to guess which repos are trustworthy and maintained now. The S3C2 recommends you look for signed code, and recommends that package repositories stop displaying metrics that can be faked easily.

They're researching malicious skills in AI skill marketplaces!

**My question**: Is Williams seeing more use of formal methods, like AI-powered logical proofs of security? **Answer**: Yes, particularly in government.

## [The Prover Is the Judge: Verified Security Software from AI Coding Agents in Ada/SPARK](https://arxiv.org/pdf/2607.14340) {#the-prover-is-the-judge-verified-security-software-from-ai-coding-agents-in-ada-spark}

**Industry Track Distinguished Paper**

The author Tobias Philipp gave an agent a description of a security standard (e.g. RFCs) plus a skill file. The agent produces code, contracts, and tests, all in SPARK, which is a verifiable dialect of Ada. Its output is passed to GNATprove, which verifies the SPARK code. If GNATprove fails, its errors are passed back to the agent until it succeeds. After the whole project is finished, the agent improves the skill file for the next time. The projects are security algorithms like SHA-2, AES, SSH.... Most of the projects achieved proofs that the code was free of run-time errors; some were also proven to be constant-time.

The agent is fast, e.g. it implemented [FrodoKEM](https://frodokem.org/) in 6h compared to 240h for a junior SPARK developer. This project cost $150 in tokens and 16h of human review.

There can still be bugs! E.g. the agent generated SSH code that had two fields swapped. It was proven free of runtime errors and it seemed to work, but it didn't match the RFC and couldn't interoperate with existing SSH implementations.

The agent likes to cheat by disabling the proof-checker. You can instruct it not to do that, but it will search for new ways to cheat. (Will Schultz [has been experimenting with LLM-written proofs](https://will62794.github.io/formal-methods/2026/04/03/autonomous-protocol-proofs.html) in TLA+ and has told me that agents like to cheat there, too.)

Philipp's conclusions:

* "What an agent can be trusted to establish is bounded by the strength of its feedback."  
* "Verification stops being a luxury. Can we now afford its absence?"  
* [N-version programming](https://en.wikipedia.org/wiki/N-version_programming) was abandoned because engineering teams were so expensive, now it's practical again.

Audience suggestions to catch cheating:

* Give the output to a second agent that searches for cheats in the proof?
* Check that the proof involves all the variables and code statements that it ought to?

## Search-Based Software Aging Testing for Android Applications

"Software aging" is the bad things that happen when a process has been running a long time. (I thought we were talking about [bitrot](https://en.wikipedia.org/wiki/Software_rot), but that's different.) E.g. if there's a memory leak, it gets worse the longer the process is up. Mobile apps are particularly prone to this, since they stay resident a long time and have lots of UI events. It's hard to find aging bugs because the tests take a long time, and the root cause is hard to diagnose amidst everything that happened during the long test.

The authors propose to search for tests that trigger aging bugs thus: A test is a sequence of events. The sequence has triggered an aging bug if some metric (RAM usage, latency) increases with sequence length. The events are treated as genes, and the authors use an optimized genetic algorithm to search for sequences that trigger aging bugs. The reward function favors *short* sequences.

## Graceful Restart Testing for Distributed Systems via LLM-Based Test Transformation

The authors claim that most people running distributed systems don't test graceful restart (as part of planned maintenance) enough, because it's slow, expensive, and flaky to do a real restart in a multi-machine deployment. They propose a "mini-cluster": the entire system running on one host, and in their case it's all in one *process*. No mocking. (Except the network presumably.) They used LLMs to insert restarts into existing tests, intelligently restarting at moments that seem most likely to trigger bugs.

They think it's ok if the *client* must be restarted in order to handle the server's restart. They showed an HBase driver as an example: once you get a table reference, it goes stale if the server restarts. Their LLM inserts "reference replacements" after server restarts to deal with this, otherwise most of their tests would fail. I pointed out that MongoDB drivers [handle this silently](/driver-features-for-mongodb-3-6/#retryable-writes), so we can randomly restart servers and our tests still pass unmodified. The presenter Darko Marinov was surprised. Jeez, we implemented automatic reconnects and retries a decade ago, what's up with the HBase driver?

## [An Empirical Study of LLM-Generated Specifications for VeriFast](https://arxiv.org/pdf/2606.26490) {#an-empirical-study-of-llm-generated-specifications-for-verifast}

The authors want to verify C code that manipulates the heap, e.g. that a linked-list "append" function keeps the list acyclic. They want to use "[separation logic](https://en.wikipedia.org/wiki/Separation_logic)", which can express ownership and disjointness. There's prior research on other logics (Lean...) but not much on separation-logic verifiers such as [VeriFast](https://github.com/verifast/verifast).

They evaluated a few LLMs, making them write VeriFast specs of a corpus of C programs, offering a few levels of guidance to the LLM: natural language, or formal pre- and postconditions, or more. They gave the LLM some VeriFast syntax examples in a RAG system. The AIs preserved intended behavior in their specs 83% of the time from natural language and 97% of the time given stronger guidance. When the AI tried to one-shot the spec, the specs could be verified by VeriFast only 31% of the time overall, and 40% of the time given the strongest guidance. The best model, Gemini 2.5 Pro, verified 40% overall. LLMs had the most trouble with concurrency and generating loop invariants, with about 12% and 11% success. Putting the LLM into a repair loop (show it the VeriFast error message and try again) should be more successful but they haven't tested that yet, surprisingly.

## My Talk

I presented [The Polyglot's Dilemma: Conformance Testing a Dozen Specs in as Many Languages](/polyglots-dilemma/). The audience was very engaged, I got enough questions to fill the Q\&A period. The next day someone intercepted me in the lunch line to tell me my presentation was the clearest at the whole conference. The conference was only half over then, so he may have changed his mind by now. I saw some terrific talks on the final day.

# The less-interesting-to-me talks

## LLM-Driven Test Case Generation via Requirement Item Extraction and Stepwise Prompting

LLMs perform poorly at writing tests if you just give them a big document and say, "Write tests." The authors define a Requirement Item as the smallest unit to be extracted from a doc and turned into a test. They made a framework (quite complex it seems, based on the flowchart in the slide) to parse documentation into RIs. Each RI maintains its provenance: where in the doc the RI comes from. The framework generates tests, informed by [ISO 29119](https://en.wikipedia.org/wiki/ISO/IEC_29119). They compared their framework's performance vs. raw foundation model and some other frameworks, using the standards for Bluetooth and other protocols, and their framework did better. (Surprise!)

## Engineering Reliability into LLM Multi-Agent Systems: An Industrial Experience

Case study about a service, HorseReport: it estimates the money value of show-jumping horses by aggregating data sources e.g. pedigree, competition history, age, overall horse market. Produces a headline number and a 15-page PDF report. You can't just shove inputs into an LLM: its output is variable and doesn't match human experts, and often cheap models will produce invalid LaTeX that doesn't compile to PDF. The authors find that a multi-agent architecture is cheaper and more reliable: use the smallest model and most focused context possible for each subtask. For a given task, if the LLM fails, then show it the problem and let it try a few more times. Save state after each subtask to make recovery cheaper.

The presenter Marco Becattini said he notices common mistakes the models make, and writes deterministic algorithms to fix them. E.g., if the horses' names include accent characters, the cheap models predictably mess up character encoding. I asked, why not include in the prompt a warning about these common mistakes? He answered, cheap models have limited context and attention, adding a bunch of pitfall-warnings to the prompt will degrade their output, so if it's possible to fix a mistake with post-processing then that's the better way. He also said, it's hard to test whether updating a prompt has *totally* eliminated a common mistake: we don't yet know how to statistically verify the effect of prompt changes. Very interesting!

## Don Syme keynote: The agentic repository automation revolution

Don Syme is the F# inventor, now he's a distinguished engineer at GitHub doing AI stuff. He showed off GitHub's agentic workflow framework. You create a file in a similar format to GitHub triggers: the file specifies when the agent runs and defines strict, deterministic rules about what the agent can read, what tools it can use, and what outputs it can produce. He showed for example an agent that runs weekly: it can read the repo contents, it does some research about competing products (it has access to a web search tool), and its only permitted output is a new GitHub issue with its findings.

Syme described all the guardrails: the agent runs in a sandbox behind a firewall, and another AI monitors it. He says that strong guardrails permit powerful automations, in other words safety and productivity are complementary. In contrast, an individual working with an agent in an IDE always wants to disable guardrails for productivity's sake.

Syme showed an [agentic workflow zoo](https://github.github.com/gh-aw/blog/2026-01-12-welcome-to-pelis-agent-factory/), it's inspiring but overwhelming to imagine all these agents interacting in a repository....

## Program Reversal for Error Reachability Analysis {#program-reversal-for-error-reachability-analysis}

This is a solution for *reachability analysis*: checking whether a program state can be reached from a starting state (or any particular state). Useful for checking whether a *bad* state can be reached, implying a bug. The usual method is to start at the initial state and search for a path to the bad state, but the authors propose to search backward from the bad state. They model the program as a control flow automaton (CFA) and reverse it, and do symbolic execution of the reversed CFA. They do this on C programs at the LLVM IR level, then feed the reversed IR to a program verifier. Reversal doesn't support all C features (pointers, arrays, structs, recursions) but works for simple programs. On these programs, reversal is *usually* worse than forward verification, because there's a ton of nondeterminism in the reversed program. But there are a subset of forward programs that can *only* be verified once they're reversed. So the value proposition is to include program reversal in a portfolio of verification techniques.

## Revealing Transaction Bugs in DBMS Engines with Metamorphic Testing

[Metamorphic testing](https://en.wikipedia.org/wiki/Metamorphic_testing) (MT): generate test inputs, by taking a valid test input/output pair, and do validity-preserving transformations on the pair. These transformations obey metamorphic relations (MRs). Useful if it's hard to generate valid inputs/outputs from scratch but you have a corpus of valid tests already.

The authors make a framework to take a test (a sequence of transactions and the expected outcome) and apply four MRs to them. These are pretty simple, e.g. if you insert a transaction that ends in ROLLBACK, the outcome should be the same. If a transaction is running in SERIALIZABLE isolation, then duplicating a SELECT statement should have the same outcome twice (because SERIALIZABLE guarantees Repeatable Read).

They tried this on tests of MySQL, MariaDB, and TiDB. They detected a new bug in MariaDB and two in TiDB, which surprises me since the technique seems so shallow. A limitation is, if the original test is overfitted to a particular DB implementation (i.e. it asserts behavior that's not specified in the SQL standard) then a valid transformation might make the test fail.

## Toward Verified Code from Natural Language: Understanding Pipeline Design for Formally Verified Rust Program Generation {#toward-verified-code-from-natural-language:-understanding-pipeline-design-for-formally-verified-rust-program-generation}

They want to give an LLM a natural language spec and a function signature, and it should output a Verus program, which is executable Rust plus verifiable spec. Their question is whether it's better to ask the AI to directly output the whole Verus program at once, or to output a spec then Rust, or output Rust then the spec. This task was too hard for the LLMs: GPT-5.2 succeeded less than half the time, and the weaker models almost always failed. The spec-then-Rust pipeline performed better than the other two. My colleagues and I hypothesize the same thing with TLA+ instead of Verus: we think AI generates better code if it writes a spec first, just like humans do. In all cases, the main problem with the AIs is task misalignment: the program doesn't do what the natural language input requests.

{{% pic src="IMG_7735.jpg" alt="Pink and orange streaks of cloud over the sea at dusk, with waves breaking on a pebble beach" / %}}
