+++
type = "post"
title = "Mongo Conduction: Or, What I Did For Spring SkunkWorks"
date = "2015-03-13T06:44:53"
description = "A demo of Mongo Conduction, a server I made that looks like MongoDB and deploys topologies of MongoDB servers for testing."
"blog/category" = ["Mongo", "Programming", "Python", "C"]
"blog/tag" = []
enable_lightbox = false
draft = false
+++

<p>MongoDB, Inc. holds quarterly skunkworks sessions&mdash;basically a hackathon, but more relaxed. We set aside three days to work on neat hacks, or to start deep projects that need uninterrupted concentration, or to do something new outside our regular duties.</p>
<iframe width="560" height="315" src="https://www.youtube.com/embed/BDBvBYHxDzM?rel=0" frameborder="0" allowfullscreen></iframe>

<p>For SkunkWorks last week I did three related projects:</p>
<p><a href="http://mockupdb.readthedocs.org/en/latest/tutorial.html">MockupDB, a MongoDB Wire Protocol server written in Python.</a></p>
<p><a href="http://mongo-conduction.readthedocs.org/">Mongo Conduction, a server that receives Wire Protocol messages and creates test deployments of MongoDB servers.</a> It looks sort of like a JSON-over-HTTP RESTful API, but what it actually does is a BSON-over-Wire-Protocol RESTful API.</p>
<p><a href="https://github.com/ajdavis/mongo-c-orchestration-demo/blob/master/mongo-c-orchestration-demo.c">A test-suite runner written in C</a>. It reads our standard driver test specifications from YAML files, sends commands to Mongo Conduction to create the cluster, and connects the C Driver, <a href="https://github.com/mongodb/mongo-c-driver">libmongoc</a>, to the cluster. It does operations with the driver, and sends more commands to Mongo Conduction to alter the cluster while the driver is connected to it, and asserts that the outcomes of the driver operations match the expected outcomes from the standard test.</p>
<p>In the demo I'm using <a href="https://www.jetbrains.com/clion/">CLion</a>, a new C/C++ IDE.</p>
<p>If you use the closed captions I added, let me know if I did an ok job, it's my first time captioning a video.</p>
    