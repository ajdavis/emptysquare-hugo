+++
type = "post"
title = "Embed Interns In Your Team, Don't Assign Them Science Fair Projects"
description = ""
category = []
tag = []
draft = true
enable_lightbox = false
+++

![](tumblr_luttq7SXGX1r3ue3zo3_1280.jpg)

It's only January, but at MongoDB we're already planning what our summer interns should work on. We have two tracks for interns:

1. **Team Track**: Interns are integrated in a team for the duration of the summer, contributing to the team's regular work. They start with smaller tasks and work up to a capstone feature that takes the final few weeks to achieve.

2. **Project Track**: Interns work on one feature or project that is not on the critical path and takes the whole summer to finish.

I've overseen interns on both tracks, and I'm certain that they're better off in Track #1: embedded in teams, working on regular bugs and features, instead of being assigned brand-new projects.

## Projects

It's tempting to invent science-fair projects for interns. For one thing, we want interns to have fun, and new projects always seem fun. Writing a MongoDB driver in an exotic programming language, or making a stylish visualization of where data is stored in a sharded cluster, or porting the MongoDB query engine to GPUs&mdash;these were all fun ways for interns to spend a summer.

But there's a big risk that these projects won't be used or maintained when the interns leave. In a survey I did a couple years ago, I found that nearly half of MongoDB interns' projects were unused 12 months later. We accomplished our main task for the summer anyway: we and our interns evaluated whether we should work together again. But there was no business case for continuing to invest more in their software.

Since intern projects are usually open source, some interns try to keep their code on life support after they go back to college in the fall. For a few months my intern Christopher Wang kept up with bug reports and pull requests on his [MongoDB Lua driver](https://github.com/mongodb-labs/mongorover), but inevitably he turned away to focus on his classes, and then moved on to his career.

What is the cost of an abandoned project? It seems like a poor use of a smart kid's time, when they could have implemented something of lasting value instead, and it must be painful if we leave their code gathering dust. It might discourage them from coming back full-time&mdash;if you had two summer internships, and one company put your code in production, but another company abandoned your code, which company would you return to?

Not all projects are abandoned, of course! When a *project* is a new feature for an existing *product*, it has better odds. Interns at MongoDB wrote the [decimal type](https://docs.mongodb.com/manual/tutorial/model-monetary-data/#numeric-decimal) for precise monetary calculations in MongoDB 3.4, which our customers now use in critical applications worldwide. They developed a Javascript fuzzer that runs continuously and has found hundreds of bugs in the MongoDB server, and they implemented network compression in the MongoDB-to-SQL translation layer of our [Business Intelligence Connector](https://www.mongodb.com/products/bi-connector).

These are success stories, but many other projects are left behind when the interns go back to school.

![](tumblr_luttdnkTiT1r3ue3zo3_1280.jpg)

*Your intern projects shouldn't look like science fiction.*

***

## Teams

Luckily, most MongoDB interns don't do new projects. They join teams, and work on regular tasks, and without exception they ship useful code.

This summer I mentored two interns, Ian Boros and Fiona Rowan. They embedded with the MongoDB C Driver team with me, more or less as if they were regular hires. It was the most successful intern project I've had yet. I started each of them on a Minimum Viable Bug: the point was not to learn the code, it was to learn the workflow, and get familiar with Jira, GitHub, and our code review tool. Fiona made a little change to our integer-parsing function to ensure it detected prefixes like `0x`, and Ian fixed a potential crash in some options-parsing logic.

Once Ian and Fiona merged their first patches, I assigned them substantial tasks. Fiona optimized away some mallocs and added a more flexible API for storing binary blobs in MongoDB, and Ian wrote example code for a variety of common C Driver tasks. Finally, I set them working on their capstone features for the summer. I wanted them each to have a major achievement to put on their resume from the internship, no matter whether they ended up working for MongoDB long-term or not. I had Fiona expand the C Driver's API to support the big new features of MongoDB 3.4, and Ian wrote tricky cross-platform code to send usage data to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas).

***

When an intern embeds with a team, they get a realistic experience of working for MongoDB full-time. They experience our engineering process, and how we talk with customers, and how we hit deadlines. Just like professionals, they work on existing code bases instead of greenfield projects, and just like professionals, their priorities are set by our users' needs. We, in turn, can evaluate their performance in this realistic environment. And best of all, it maximizes the chance that the code they write will ship, be used in production, and be maintained long term. Interns have the satisfaction of contributing something valuable.

So I hope we emphasize the Team Track even more this year. If you're mentoring interns at your company, too, then heed: please don't give them projects. Embed them in teams. And if you're a student looking forward to an internship this summer, do everything you can to join a team and contribute to its regular work, maintaining an existing product and shipping code to customers. This is one of your few chances before you graduate to work like a professional. Don't waste it!

![](tumblr_luttdnkTiT1r3ue3zo2_1280.jpg)

***

Illustrations: Nikolai Lutohin ([one](http://yugodrom.tumblr.com/post/12943748275/ilustracije-nikolaja-lutohina-za-%C4%8Dasopis-galaksija)) ([two](http://yugodrom.tumblr.com/post/12943734874/ilustracije-nikolaja-lutohina-za-%C4%8Dasopis-galaksija)).
