+++
category = ["Programming"]
date = "2025-11-19T02:53:40.078968+00:00"
description = "Spoiler alert: it was both productive and annoying."
draft = false
enable_lightbox = true
tag = ["ai"]
thumbnail = "office.jpg"
title = "This Senior Staff Engineer Vibe-Coded for the First Time, What Happened Next Will Shock You"
type = "post"
+++

Actually it won't shock you. Spoiler alert: Coding with AI is a skill. It's annoying but efficient. My prior experience handwriting code helped.

![](medieval.jpg)

_By Gemini, obviously. This is the first and only post I'll ensloppify with AI "art."_

I started programming seriously when I was in college, in the late 90s. Basic autocomplete in Microsoft Visual C++ was the state of the art back then. I spent the next couple decades meticulously laying out my code like a 16th-Century typesetter, crafting each line with an artisan's pride.

[When I switched from engineering to research](/after-244-days-off/) I stopped coding regularly. Now I have spurts of programming when I prototype a new algorithm or benchmark it, and between spurts I go months without significant time in an IDE. Last year, IDEs didn't change by the month. This year, each month is a revolution. I wanted to experience the new reality for myself. So, for two recent personal projects, I tried going all-in on AI coding.

As I'll describe below, my first attempt was frustrating because I didn't embrace the vibe-coding lifestyle. I chose the wrong model, then micromanaged it, trying to make it write the code I would've written. The LLM implemented the wrong features, or wrote buggy code, or correct code that I thought was ugly. On my second attempt, I used the right model and treated it like an adult: I gave it high-level instructions and let it write all the code and run its own tests. I didn't type a single character of code&mdash;I hardly even looked at it&mdash;and I had an enjoyable day building a useful app.

# Act I: The Senior Staff Engineer is a Control Freak

![](office.jpg)

_Gemini doing a decent impression of the Blondie comic strip style._

For my first vibe-coding exercise, I turned a Python script into a web app and deployed it to the cloud. The script was something I'd developed over a few years to [optimize the schedule for a twice-annual Zen retreat](/optimizing-a-meditation-retreat-with-a-sat-solver/). My fellow Zen students suggested I turn it into an application they could use without me. I thought this was a perfect use case for AI. I opened VS Code and accepted the default model, GPT-5 mini, and conversed with it about my needs.

The model started off strong: it made useful suggestions for deploying to Google cloud. It proposed a mix of Google services that would save money and pay only for the resources I needed. It insisted I needed some complex web of Google accounts, roles, and auth tokens&mdash;I kept pushing back and asking it to simplify, but in the end it was right. I eventually followed all its instructions, after discovering there was no simpler alternative.

When it came time to write code, GPT-5 mini wrote a good first web page and Flask backend. It was much quicker than my own work would've been, and the web page was nicely styled.

I didn't care about the code style of the generated HTML, CSS, and JavaScript, but I'm a stickler for Python style and I made the mistake of reading its code. I hated it. 

GPT-5 mini really likes to write useless comments:

```python
# Return the square of x.
def square(x: int) -> int:
    ...
```

It also likes to write "defensive" code that only makes the program less predictable:

```python
# Return the square of x.
def square(x: int) -> int:
    if x is None:
        print("x wasn't set")
        return 0

    return x * x
```

I griped in `copilot-instructions.md` that it shouldn't do this, but it seemed to have no effect, so I started including in my prompts, "Just write the code, no comments, no error-checking." Hilariously, it then wrote comments like:

```python
def square(x: int) -> int:
    # Don't check whether x is None, just let the exception be thrown.
    return x * x
```

This is high-school-sophomore-style coding. Someone who's worked on large codebases for years knows that comments are tech debt and should be minimized. They should be addressed to a reader in the far future, not to the most recent code reviewer. Defensive coding like `if x is None` makes the code more complex, not more resilient: error-handling should be consolidated at a layer of the application that knows how to respond. I'm afraid that GPT has either seen too much sophomoric code from StackOverflow in its training set, or else OpenAI hired naïve coders to provide feedback, and they encouraged this sort of thing during [RLHF](https://en.wikipedia.org/wiki/Reinforcement_learning_from_human_feedback).

I got tired of fighting with GPT-5 mini over style and started coding small Python changes myself. But when I was ready to deploy to the cloud I turned to it for help again. We got the job done faster together, but I wasn't happy with my colleague. It hallucinated all sorts of command line options to the `gcloud` CLI. I got myself stuck in an exasperating loop, where GPT suggested a command, I pasted it into the terminal, the command failed because of GPT's mistakes, and I pasted the error back into GPT for diagnosis. I'd become the dumbest agent in a system of dumb agents.

# Act II: The Senior Staff Engineer Learns to Chill Out and Enjoy the Vibes

![](beach.jpg)

_Gemini still doesn't know how many arms humans have._

For my second attempt, I shamelessly embraced the vibe-coding lifestyle. I used AI to build an AI agent. The thing I wanted to build was an AI coach, who would look at my long-term goals (in some PDFs), my task list (using the Remember the Milk API), how I use my time (from the Toggl Track API), and what I've accomplished lately (in a text file where I track accomplishments). I'd read [an inspiring article about building agents](https://fly.io/blog/everyone-write-an-agent/) and thought, this looks surprisingly straightforward, I'll make an agent do it for me.

(Yes, I'm telling an AI to tell an AI to tell me what to do. A few months ago this was futuristic.)

In the weeks since my previous session, Microsoft [overhauled the coding agents in VS Code](https://code.visualstudio.com/updates/v1_106). Now there's a clear separation between a planning agent and a coding agent. This made my second vibe-coding project go more smoothly. Plus, instead of accepting the default model, I chose Claude Sonnet 4.5, based on rumors that it's good.

This might get confusing, since there are two LLMs in this story, so from now on:

* **Claude** is the LLM I used to write code for an "AI coach".
* **GPT** is the LLM that the AI coach used as its backend.

I began with Claude in planning mode and described what I wanted: an agent written in Python, using the GPT API, plus various APIs to track my work. Its main task would be to suggest what I should work on for the next 45 minute [pomodoro](https://en.wikipedia.org/wiki/Pomodoro_Technique). I wanted to chat with the agent in my terminal. Claude and I had a 20-minute conversation about my requirements. It asked me, should auth tokens be stored in the macOS keychain or a text file? How often should it refresh its data sources, such as Remember the Milk and Toggl? Whenever I start chatting with the coach, should it remember our past conversations? How should the coach prioritize tasks&mdash;due date only, or also priority, or how well they align with my long-term goals? Whenever I answered Claude's questions, it asked me four or five more. After a few rounds of this, I clicked the button VS Code provided me, which says, "start implementing." Claude stopped asking questions and started generating dozens of files. I don't know if the "planning mode" agent would ever have stopped asking for more details, or how I should decide when we've talked enough.

Claude worked for a few minutes autonomously. I occasionally had to click "ok" when it wanted to run a shell command or fetch a page of documentation from the web. The wait wasn't long enough for me to work on something else with any focus, so I watched YouTube in 30-second slices between AI interactions. It seems helpful to have something mindless to do in these gaps&mdash;listen to music, watch climbing or cooking videos, practice tying knots... Claude generated 30 Python files and 2800 lines of code, and spat out a summary of its work. It claimed it had built OAuth flows for RTM and Toggl, and a context-management system that stored recent messages in SQLite and asked GPT for summaries of older messages, to limit the size of the context window. I resisted the temptation to read the code: I just tried it out.

```plain
> python3 main.py
✓ All services authenticated
ℹ Refreshing all data sources...
✓ Data refresh complete

╔══════════════════════════════════════════════════════════════════╗
║              Professional Coaching Agent (GPT-5.1)              ║
╚══════════════════════════════════════════════════════════════════╝

Type your questions or commands. Use /help for available commands.

You: /help

┏━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Command        ┃ Description                          ┃
┡━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ /refresh       │ Refresh all data sources             │
│ /refresh-rtm   │ Refresh Remember The Milk tasks only │
│ /refresh-pdfs  │ Refresh PDF documents only           │
│ /refresh-toggl │ Refresh Toggl Track entries only     │
│ /refresh-logs  │ Refresh accomplishments log only     │
│ /help          │ Show this help message               │
│ /quit          │ Exit the agent                       │
└────────────────┴──────────────────────────────────────┘

You: what should i work on next?

Coach: Given what’s on your plate and that you’ve already spent a lot of time in “AI coding” and “driver testing paper”, I’d suggest one of these for your next 45-minute block:

**1. Review my current MongoDB development plan**
- Due: tomorrow (2025-11-19)
- Why: Directly tied to your long-term goals (publishing pipeline, collaborations, synced clocks, etc.).
- 45-minute plan:
  - 10 min: Skim the dev plan PDF and your recent accomplishments.
  - 25 min: Write/update concrete 2025–mid-2026 goals (papers, talks, collaborations) in a doc.
  - 10 min: Turn those into 3–5 actionable RTM tasks (e.g., “Draft driver testing paper intro,” “Outline synced-clocks survey sections”).

**2. Prep for “Meet about leases in new architecture”**
- Due: today
- Why: High-leverage research conversation; you just finished your leader leases paper, so consolidating your thinking is valuable.
- 45-minute plan:
  - 15 min: Jot down what you want from the meeting (questions, decisions, next experiments).
  - 20 min: Review any notes on leases + new architecture, and your “Leases”/“Data movement” tasks.
  - 10 min: Draft a short agenda and 2–3 concrete proposals to discuss.

If you feel a bit fried from heavy cognitive work, a lighter option:

**3. Shut down lease benchmark EC2 instances (prep + checklist)**
- Due: 2025-11-30
- Use 45 minutes to:
  - List all benchmark-related resources.
  - Decide what to snapshot/keep.
  - Draft the shutdown steps so the actual execution is quick later.

Which of these matches your current energy:
- (A) reflective/planning (dev plan),
- (B) focused technical prep (lease meeting), or
- (C) lighter operational cleanup (benchmark EC2)?
```

This was an impressive debut. Most of the coach's ideas were appropriate, and Claude's code for reading the data sources and connecting to GPT all worked the first time.

As I used the coach more, I found some bugs. E.g., Claude had only stubbed-out the code for _updating_ RTM tasks. If I asked the coach to "put off that meeting for 2 days," it crashed. I was smarter now than in my previous attempt, though. Instead of copying error messages from the terminal to my chat with Claude, I used VS Code's builtin terminal, so Claude could look at the terminal and see the error messages itself. I simply told Claude, "Look at the terminal and fix this bug," and with little further intervention it found the stubbed-out code, looked up the RTM API docs, and implemented the missing feature. I maintained my disciplined laziness, never typing or even reading any code. It only took a few hours of testing the coach and asking Claude for bugfixes or changes, and the thing I'd envisioned was fully built.

# Lessons learned

* Vibe-coding is a skill.
* Avoid reading and writing code??
* Claude Sonnet is far better than GPT-5 mini, obviously. In general, it's important to learn models' differences.
* Try to remove yourself from the agentic loop: give the AI the tools and permissions it needs to test its code and diagnose its mistakes autonomously.
* Eventually, you might need to intervene, especially (I found) when the AI doesn't know how to use a particular API and keeps hallucinating options. Fall back to searching Google and StackOverflow, like you did last year.
* I need a *very* wide monitor. At my age even 27" isn't enough to display the agent chat, file explorer, code, etc., all large enough for my eyes, so I've upgraded to an [ultrawide](https://www.nytimes.com/wirecutter/reviews/best-ultrawide-monitors/). 

I'm reminded of a more abstract lesson, the one from William Gibson: "The future is already here, it's just not evenly distributed." Sometimes the new technology works as advertised! Sometimes it doesn't. Revolutionary new time-saving technologies take practice to use well. 

Back in 2005, my mind was blown [watching David Heinemeier Hansson implement a blogging engine in 15 minutes with Ruby on Rails](https://www.youtube.com/watch?v=Gzj723LkRJY). Until I saw the demo, I wouldn't have believed such velocity was possible. Rails was so much more concise than anything before, and so was Ruby. And the code editor DHH used, TextMate, was so tricked out with templates and macros, it practically wrote the code for him. But when I tried Rails and TextMate myself, things didn't go so well. The new technologies really were transformative&mdash;looking back, it's clear that DHH was demonstrating the future of web development&mdash;but it took time for me and the world to catch up.
