+++
category = ['Python', 'MongoDB']
date = '2018-01-25T13:49:32.982699'
description = "Interns are much more likely to succeed if they work as regular team members, doing a real professional's daily work."
draft = false
enable_lightbox = true
tag = ['best']
thumbnail = 'tumblr_luttdnkTiT1r3ue3zo3_1280.jpg'
title = "Embed Interns In Your Team, Don't Assign Them Science Fair Projects"
type = 'post'
+++

![](tumblr_luttq7SXGX1r3ue3zo3_1280.jpg)

It's only January, but at MongoDB we're already planning what our summer interns should work on. We have two tracks for interns:

1. **Team Track**: Interns are integrated in a team for the duration of the summer, contributing to the team's regular work. They start with smaller tasks and work up to a capstone feature that takes the final few weeks to achieve.

2. **Project Track**: Interns work on one feature or project that is not on the critical path and takes the whole summer to finish.

I've overseen interns on both tracks, and I'm certain that they're more likely to succeed on Track #1: embedded in teams, working on regular bugs and features, instead of being assigned brand-new projects.

## Projects

It's tempting to invent science-fair projects for interns. For one thing, we want interns to have fun, and the really speculative projects always seem fun. Writing a MongoDB driver in an exotic programming language, or making a stylish visualization of where data is stored in a sharded cluster, or porting the MongoDB query engine to GPUs&mdash;these were all fun ways for interns to spend a summer.

But there's a big risk that these experiments won't be used or maintained when the interns leave. In a survey I did a couple years ago, I found that nearly half of MongoDB interns' projects were unused 12 months later. We accomplished our main task for the summer anyway: we and our interns evaluated whether we should work together again. But there was no business case for continuing to invest more in their software.

Since intern projects are usually open source, some interns try to keep their code on life support after they go back to college in the fall. For a few months my intern Christopher Wang kept up with bug reports and pull requests on his [MongoDB Lua driver](https://github.com/mongodb-labs/mongorover), but inevitably he turned away to focus on his classes, and then moved on to his career.

What is the cost of an abandoned project? It seems like a poor use of a smart kid's time, when they could have implemented something of lasting value instead, and it must be painful if we leave their code gathering dust. Luckily, this does *not* discourage interns from coming back full-time: in recent analyses, we found that interns who had worked on projects were just as likely to return as interns who joined teams, even though some interns' projects were neglected.

Of course, not all projects are abandoned! When a *project* is a new feature for an existing *product*, it has better odds. Interns at MongoDB wrote the [decimal type](https://docs.mongodb.com/manual/tutorial/model-monetary-data/#numeric-decimal) for precise monetary calculations in MongoDB 3.4, which our customers now use in critical applications worldwide. They developed a Javascript fuzzer that runs continuously and has found hundreds of bugs in the MongoDB server, and they implemented network compression in our [Business Intelligence Connector](https://www.mongodb.com/products/bi-connector).

In the last two summers we've come to recognize the danger of a speculative project. Now, before the summer begins, our CTO Eliot reviews the proposals for intern projects. He cuts the projects that don't have enough business value or won't have staff to maintain them after the interns leave.

![](tumblr_luttdnkTiT1r3ue3zo3_1280.jpg)

*Your intern projects shouldn't look like science fiction.*

***

## Teams

These days most interns join teams. They work on the same tasks as regular professionals, and they ship useful code.

Last summer I mentored two interns, Ian Boros and Fiona Rowan. They embedded with the MongoDB C Driver team with me, more or less as if they were regular hires. It was the most successful intern project I've had yet. I started each of them on a Minimum Viable Bug: the point was not to learn the code, it was to learn the workflow, and get familiar with Jira, GitHub, and our code review tool. Fiona made a little change to our integer-parsing function to ensure it detected prefixes like `0x`, and Ian fixed a potential crash in our options-parsing logic.

Once Ian and Fiona merged their first patches, I assigned them substantial tasks. Fiona optimized away some mallocs and added a more flexible API for storing binary blobs in MongoDB, and Ian wrote example code for a variety of common C Driver tasks. Finally, I set them working on their capstone features for the summer: I had Fiona expand the C Driver's API to support the big new features of MongoDB 3.4, and Ian wrote tricky cross-platform code to send usage data to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas). I wanted them each to have a major achievement to put on their r&eacute;sum&eacute; from the internship, no matter whether they ended up working here long-term.

This year, Ian and Fiona both came back to join MongoDB.

***

When an intern embeds with a team, they get a realistic experience of working for MongoDB. They experience our engineering process, and how we talk with customers, and how we hit deadlines. Just like professionals, they work on existing code bases instead of greenfield projects, and just like professionals, their priorities are set by our users' needs. We, in turn, can evaluate their performance in this realistic environment. And best of all, it maximizes the chance that the code they write will ship, be used in production, and be maintained long term. Interns have the satisfaction of contributing something valuable.

## How to Triumph as a Mentor

Mentoring interns isn't easy, and I have both succeeded and failed at it. I believe [there are four prerequisites for a successful mentorship](/mentoring); the first two are guaranteed to be present if and only if you embed your intern in your team:

1. *Expert Mentor*: You must already be an expert in the skills your intern needs to learn&mdash;it's too hard to guide a young programmer while at the same time playing catch-up. That's a danger if your intern is starting a new project with tools that are unfamiliar to you, but if your intern joins your team, then they're learning the codebase and the skillset that you already know best.

2. *Small Clear Goals*: All software development is unpredictable; internships especially so. You can manage the risk by dividing the summer into a dozen small tasks. This gives you many opportunities to check on your intern's progress and catch problems early. Interns start the summer with little experience on big jobs, so you need to ramp them slowly from small tasks to large ones. With a brand-new project there is only a vague roadmap and no backlog of bugs and features, so it's difficult to make a detailed plan. But your regular team has already planned its future work and you've grown a backlog of small tasks. It's easy to plan a summer of tasks that smoothly ramp from small to big.

(Want to know what the other two prerequisites are? Read [March To Triumph As A Mentor](/mentoring).)

***

This summer, I hope we emphasize the Team Track even more at MongoDB. If you mentor interns at your company, too, then heed: please don't give them projects. Embed them in teams. And if you're a student looking forward to an internship this summer, do everything you can to join a team and contribute to its regular work, maintaining an existing product and shipping code to customers. This is one of your few chances, before you graduate, to work like a professional. Make the most of it!

![](tumblr_luttdnkTiT1r3ue3zo2_1280.jpg)

***

<span style="color: gray">Illustrations: Nikolai Lutohin (<a href="http://yugodrom.tumblr.com/post/12943748275/ilustracije-nikolaja-lutohina-za-%C4%8Dasopis-galaksija" style="color: gray; text-decoration: underline">one</a>) (<a href="http://yugodrom.tumblr.com/post/12943734874/ilustracije-nikolaja-lutohina-za-%C4%8Dasopis-galaksija" style="color: gray; text-decoration: underline">two</a>)</span>.
