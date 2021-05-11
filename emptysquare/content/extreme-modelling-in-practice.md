+++
category = ["Research"]
date = "2020-08-30T16:19:06.735073"
description = "At MongoDB we tried two methods to test that a spec matches the code: one worked, one didn't. We explain our results in a VLDB 2020 paper."
draft = false
enable_lightbox = false
tag = ["tla+", "distributedsystems"]
thumbnail = "honeycomb-thumbnail.jpg"
title = "Two attempts to compare a TLA+ spec with a C++ implementation"
type = "post"
+++

![](honeycomb.jpg)

At MongoDB, we use [TLA+](https://lamport.azurewebsites.net/tla/tla.html) to specify some of the protocols we use in both the MongoDB server and MongoDB Realm Sync. Formal specification has made us more confident that our protocols are correct, but it leads to a new uncertainty: what if our C++ implementations don't conform to our specs? Since we change both our specs and our implementations over time, we worry they might diverge, even if they conformed at first.

With my colleagues Max Hirschhorn and Judah Schvimer, I sought a way to continuously test conformance. We found a 2011 paper, [Concurrent Development of Model and Implementation](https://arxiv.org/abs/1111.2826), that proposed several testing methods as part of a software development process the authors called "eXtreme Modelling." We performed two case studies to experiment with two of these testing methods. We described our results in a paper titled [eXtreme Modelling in Practice](http://www.vldb.org/pvldb/vol13/p1346-davis.pdf), for the [Very Large Databases conference](https://vldb2020.org/program.html) (VLDB).

In our first case study, we tried to test the conformance of the MongoDB Server to its specs, using "model-based trace-checking." We captured execution traces from the server as we fuzz-tested it, and checked that these traces were permitted by the spec. This case study ended in failure: the project grew to cost more effort than it was worth, so we cancelled it. Our paper describes three factors that led to our failure and what we would do differently if we tried again.

In the second case study, we tested the conformance of MongoDB Realm Sync to its spec using "model-based test-case generation." We enumerated all behaviors of the spec, and generated C++ unit tests to check that the implementation conforms to each. This project was successful and achieved 100% branch coverage of the specified algorithm. Our paper compares this case study to the model-based trace-checking case study, and explains why this project was successful.

Please join us for a presentation and discussion of this paper at [VLDB 2020](https://vldb2020.org). It'll be useful to all engineers who specify industrial software systems. You'll learn about two useful testing techniques, and our story will help you repeat our success and avoid repeating our mistakes.

***

<a href="https://www.flickr.com/photos/internetarchivebookimages/14782709114"><span style="color:gray">Image: The honey bee; its natural history, physiology, and management (1827).</span></a>
