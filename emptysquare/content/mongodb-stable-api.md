+++
category = ["MongoDB"]
date = "2021-07-15T14:18:26.145653"
description = "For MongoDB 5.0, I designed a new Stable API that permits you to upgrade without code changes."
draft = false
enable_lightbox = false
tag = ["mongodbworld", "best"]
thumbnail = "stable-api.png"
title = "The MongoDB Stable API"
type = "post"
+++

MongoDB has released new database versions annually for the whole decade I've worked here. But starting now we're increasing our pace to quarterly, and eventually we'll release even more often. This means we deliver new features to you sooner, but it also presents you with a problem: you can't upgrade your database constantly if you can't trust that your existing code is compatible with the new version of MongoDB.

The MongoDB Stable API, which I designed for MongoDB 5.0, solves this problem. We announced it this week at our MongoDB.live conference. (It was called the "Versioned API" then, we renamed it the "Stable API" a while after that.) Here's a 10-minute explanation of the Stable API:

<iframe width="560" height="315" src="https://www.youtube.com/embed/RvJPG3ChAho" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen style="margin-bottom: 2em"></iframe>

I demonstrated how to use the Stable API in Python with PyMongo:

<iframe width="560" height="315" src="https://www.youtube.com/embed/3cs670Mtk7Q" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen style="margin-bottom: 2em"></iframe>

[You can read more about the Stable API in my MongoDB Developer Hub article](https://www.mongodb.com/developer/how-to/upgrade-fearlessly-stable-api/), and the [MongoDB Reference Manual](https://www.mongodb.com/docs/manual/reference/stable-api/).

***

My presentation and article focus on user experience, so I didn't get to talk about my favorite part of the Stable API project: how we prevent ourselves from making incompatible changes by mistake.

The Stable API permits **compatible** changes, e.g., we can add an optional parameter to a command, or a new field to the command's reply, or we can add a whole new command. None of these changes would cause errors in your existing code when you upgrade MongoDB. But **incompatible** changes are banned: we can't remove a parameter from a command, or remove a reply field, or remove a command entirely. So, how do we continuously test that we don't make incompatible changes?

We chose static analysis, which worked better than I expected. Before the Stable API, some MongoDB commands' inputs and outputs were [defined in YAML files](https://github.com/mongodb/mongo/blob/master/src/mongo/db/query/find_command.idl). This is an example of an [interface definition language](https://en.wikipedia.org/wiki/Interface_description_language) ("IDL"). We use the IDL to generate C++ code to parse command inputs and generate command replies. This was a nice start for compatibility testing, so we extended it: now **all** commands in the Stable API are defined in IDL.

Next, [we wrote a compatibility checker in Python](https://github.com/mongodb/mongo/blob/master/buildscripts/idl/idl_check_compatibility.py). It runs on each git commit. For all commands in the Stable API, the checker compares their latest IDL definitions with their definitions in all previous MongoDB releases. (Right now there's only MongoDB 5.0, since we just started using this system. In the future, we'll compare the latest commit to all major and minor releases from 5.0 forward.) The compatibility checker verifies that all differences among IDL versions are compatible. That is, if there's a new command parameter it must be optional, if a parameter's type changed the new type must be a superset of the old one, and so on.

There are a couple dozen rules for which IDL differences are permitted or banned, and we have meta-tests that check the compatibility checker catches incompatible changes of each kind. The checker is sound&mdash;every reported incompatibility is real&mdash;though not complete. There are plenty of ways we could mistakenly change MongoDB's behavior that a static checker won't catch. We already have some runtime tests that should catch most of those; for example, a "multi-version aggregation fuzzer" that checks that random [aggregation pipelines](https://docs.mongodb.com/manual/core/aggregation-pipeline/) have the same results in all MongoDB versions.

Of course, our testing isn't perfect and some bugs are bound to slip through. But I'm very happy with how simple and comprehensive the static checker turned out to be.
