+++
category = ["Review"]
date = "2026-04-01T12:41:12.977973+00:00"
description = "What we talk about when we talk about time horizon."
draft = false
enable_lightbox = true
tag = ["ai"]
thumbnail = "GilbrethMotionStudies-3.jpg"
title = "Review: Measuring AI Ability to Complete Long Software Tasks"
type = "post"
+++

{{%pic src="taylorism-diego-rivera.jpg" alt="Detail from a Diego Rivera mural showing factory workers laboring among heavy machinery, observed by a man in a suit and glasses." %}}

{{% /pic %}}

[Measuring AI Ability to Complete Long Software Tasks](https://arxiv.org/abs/2503.14499), a paper by dozens of authors working at [Model Evaluation & Threat Research (METR)](https://metr.org/). They define the "time horizon" metric and show that LLMs' time horizons have been doubling every seven months, and this growth might have recently accelerated.

(See also [Murat's summary](https://muratbuffalo.blogspot.com/2026/03/measuring-ai-ability-to-complete-long.html).)

## Summary

An AI agent's "time horizon" is the duration a human expert would need to complete a task that the agent can solve at a given success rate. For example, a human specialist takes about 8 hours to complete a specific optimization task: speeding up a Python program with GPU acceleration. Last year's strongest models could complete this task about 50% of the time, so their 50%-success time horizon is 8 hours. (I'm simplifying. Both human task duration and the LLM completion probability are statistical estimates; see the paper for details.)

The METR authors timed skilled humans on 170 tasks, which needed a couple seconds up to eight hours. The humans were paid extra for speed or success. They failed by giving up, submitting wrong answers, or running out of time after eight hours. METR calculates the task duration as a [geometric mean](https://en.wikipedia.org/wiki/Geometric_mean) of the successful humans' times. 
Then METR gave the same tasks to twelve LLMs released between 2019 and 2025. The LLMs had no time limit and a generous token limit; they failed only by submitting wrong answers.

{{%pic src="GilbrethMotionStudies-3.jpg" alt="A Gilbreth motion study photograph: a long-exposure image of a worker at a desk, with light trails tracing the paths of their hand movements against a grid background." %}}
Feels like the return of [time and motion studies](https://womenofixd.com/stories/lillian-gilbreth).
{{% /pic %}}

The headline is: the 50%-success time horizon has doubled roughly every seven months. GPT-2's horizon was two seconds; Claude 3.7 Sonnet's was 50 minutes; o3's was nearly two hours. In [the latest tests](https://metr.org/time-horizons/), Opus 4.6's 50% horizon was around 12 hours. The trend line suggests that between 2027 and 2031, frontier AIs will succeed 50% of the time, unsupervised, at tasks that would take a human expert a month.

The appendices are most of the paper, and the best part. Read them! Appendix H defines the "messiness" of tasks as 16 factors that degrade AI performance: you can make irreversible mistakes, you consume limited resources every time you try, you can't tell if things happen due to your actions or other causes, you can't easily measure when you've succeeded, and so on. Messiness hinders AIs more than humans. But AIs' rate of improvement is similar on messy tasks and neat ones.

There are a lot of reasons to doubt these benchmarks, the authors admit. Their tasks may not represent real-world software work. The human baseline is drawn from domain experts who are unfamiliar with the task-specific codebase. For example, in the GPU-acceleration task, someone familiar with the codebase might be faster, and someone ignorant of GPU acceleration would be slower.

{{%pic src="time_motion_study.jpg" alt="A man films two women working at sewing machines with a motion picture camera on a tripod, in a time and motion study." %}}

{{% /pic %}}

## My Thoughts

If you give an LLM a task that would take a human one month, the most important question is: do you have a test oracle? If you do, there will surely be LLMs within five years that can succeed 50% of the time. We might not need much larger models, just better scaffolding and prompting. But real software work is messy: correctness is ambiguous, there's no referee to check your work, sometimes your mistakes are consequential. The gap between tidy benchmarks and the messy world is wide, and the authors know it.

METR themselves published [a cautionary follow-up](https://metr.org/notes/2026-03-10-many-swe-bench-passing-prs-would-not-be-merged-into-main/) showing that about half of [SWE-bench](https://openreview.net/pdf?id=VTF8yNQM66) pull requests that pass automated tests would be rejected by human repository maintainers, for violating conventions, breaking unrelated code, or not really fixing the bug. This doesn't mean the models are incompetent; they might succeed after some back-and-forth with the maintainers, just like human contributors do. (How many times have your PRs been accepted on the first try?) But it does mean that "60% on SWE-bench" doesn't translate to "acceptable 60% of the time." Automated tests never test everything, and humans share unwritten rules for good code that aren't captured in benchmarks yet.

{{%pic src="800px-AWA1936.jpg" alt="A supervisor watches workers assembling small parts at a long factory bench, circa 1936." %}}

{{% /pic %}}

METR tests humans and AIs differently. Humans have an eight-hour time limit, and the sample of human completion times is biased: only those who persist and succeed are counted. AIs have no time limit and they were tested on their success rate. I don't know why METR structures the contest this way, but for whatever reason, time horizon scores are more complicated than a race between John Henry and the steam engine.

{{% pic src="john-henry.jpg" alt="" %}}
John Henry Monument in Talcott, West Virginia.
{{% / %}}

Since the authors work for an AI safety group, I imagine their ultimate question is something like, "at what point does a model become smart enough to escape containment and take over the world?" [Over on Moltbook, agents plot to take over the world daily](https://www.astralcodexten.com/p/moltbook-after-the-first-weekend), but can't focus long enough to make progress. What's the time horizon for world domination, and when will there be LLMs who can succeed at that task? They don't need a 50% success rate, just once is enough.

I read this paper with some colleagues at MongoDB, and one of them asked, what happens to software architecture if AI time horizons keep growing? I think that microservices, modular design, and separation of concerns are partly for the sake of our tiny human minds. If a superintelligence can hold an entire system in its mind at once, maybe there's no need for decomposition. And no need for maintainability, either. We're leaving the era of hand-forged software---painstakingly hammered into shape, built to last, expensive to modify---and entering the era of injection-molded plastic software, cheap enough to throw away and remake overnight.

{{%pic src="Figure-1.6a.jpg" alt="A woman operates a typewriter while being filmed, with a large clock labeled 'Gilbreth' visible beside her." %}}

{{% /pic %}}

***

Images:
* [Diego Rivera](https://commons.wikimedia.org/wiki/File:Lars_Plougmann_-_Taylorism_%28auf_Flickr%29.jpg)
* [Frank and Lillian Gilbreth](https://womenofixd.com/stories/lillian-gilbreth)
