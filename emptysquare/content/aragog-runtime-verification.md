+++
category = ["Programming"]
date = "2021-04-04T18:03:26.578838"
description = "An efficient invariant checker for network protocols."
draft = false
enable_lightbox = false
tag = ["distributedsystems"]
thumbnail = "Screen Shot 2021-04-04 at 11.31.59 AM.png"
title = "Aragog: Scalable Runtime Verification of Shardable Networked Systems"
type = "post"
+++

![](Screen Shot 2021-04-04 at 11.31.59 AM.png)

Last week in the [Distributed Systems Reading Group](http://charap.co/category/reading-group/) we read [Aragog: Scalable Runtime Verification of Shardable Networked Systems](https://www.usenix.org/conference/osdi20/presentation/yaseen). The paper describes an intriguing system from Microsoft Research and U Penn; it can analyze huge numbers of network events and find invariant violations that indicate bugs in the protocol. The invariants are expressed in a cute regular expression language, which Aragog parses and automatically decomposes into local and global verifier state machines. (But I don't know why it's called "Aragog".)

[Read Aleksey Charapko's summary](http://charap.co/reading-group-aragog-scalable-runtime-verification-of-shardable-networked-systems/) or watch my presentation.

<iframe width="560" height="315" src="https://www.youtube.com/embed/OamxMI1UEos" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
