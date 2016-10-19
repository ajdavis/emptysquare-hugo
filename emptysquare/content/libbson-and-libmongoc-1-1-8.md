+++
type = "post"
title = "Announcing libbson and libmongoc 1.1.8"
date = "2015-06-22T11:01:33"
description = "Bugfix release of the MongoDB C library."
category = ["C", "Mongo", "Programming"]
tag = []
enable_lightbox = false
thumbnail = "deep-sea@240.jpg"
draft = false
legacyid = "5586755a5393741c764615f2"
+++

<p><img style="display:block; margin-left:auto; margin-right:auto;" src="deep-sea.jpg" alt="Deep sea fish" title="Deep sea fish" /></p>
<p>I released libbson and libmongoc 1.1.8 today. The significant change is the defeat of a stubborn crash reported weeks ago. Very rarely, when a <code>mongoc_client_t</code> is connected to a replica set while a member is added, and authentication fails, it leaves the client's data structures in an inconsistent state that makes it seg fault later in <code>mongoc_client_destroy()</code>.</p>
<p>I had already gone one round with this bug and given up: I released 1.1.7 with extra checking and logging along this code path, but without a theory about the cause of the crash, much less a fix. The customer who reported the crash could reproduce it a couple times in each of their days-long durability tests, so they sent me core dumps. My colleague Spencer Jackson devoted heroic effort to understanding the core dumps (including one with no debug symbols!), and we finally discovered the sequence that leads to the crash.</p>
<p>The bug was in <code>_mongoc_cluster_reconnect_replica_set()</code>, which has two loops. The first loop tries nodes until it finds a replica set primary. In the second loop, it iterates over the primary's peer list connecting and authenticating with each peer, including the primary itself.</p>
<p>The crash comes when we:</p>
<ol>
<li>Connect to a 2-node replica set.</li>
<li>The function enters its first loop, connects to the primary and finds two peers.</li>
<li><code>nodes_len</code> is set to 2 and the nodes list is reallocated, but the second node's struct is uninitialized.</li>
<li>The function enters its second loop.</li>
<li>Auth fails on the first node (the primary) so the driver breaks from the loop with <code>goto CLEANUP</code>.</li>
<li>Now <code>nodes_len</code> is 2 but the second node is still uninitialized!</li>
<li>Later, <code>mongoc_client_destroy</code> iterates the nodes list, destroying them.</li>
<li>Since <code>nodes_len</code> is 2, the client tries to destroy the second, uninitialized node.</li>
<li>If the <code>stream</code> field in the second node happens to be non-NULL, the client calls <code>stream-&gt;close</code> on it and segfaults.</li>
</ol>
<p>This was particularly hard for the customer's test to reproduce, because the driver has to connect while the test framework is reconfiguring auth in the replica set, <em>and</em> the buffer reallocation has to return a non-zero chunk of memory.</p>
<p>The fix is to properly manage <code>nodes_len</code>: don't increment it to N unless N nodes have actually been initialized.
Additionally, zero-out all nodes right after reallocating the nodes list to ensure all data structures are NULL.</p>
<p><a href="https://jira.mongodb.org/browse/CDRIVER-695">Details about the bug and the fix are in Jira</a>.</p>
<p>It's satisfying to nail this bug after a long chase, but also painful: that code path is long gone in the 1.2.0 branch, replaced by Samantha Ritter's implementation of the <a href="/blog/server-discovery-and-monitoring-in-pymongo-perl-and-c/">Server Discovery And Monitoring spec</a>. If I could've released 1.2.0 by now we'd have saved all the trouble of debugging the old code. It only redoubles my drive to release a beta of the new driver this quarter and get out of this bind.</p>
<hr />
<p><a href="https://en.wikipedia.org/wiki/File:PSM_V23_D086_The_deep_sea_fish_eurypharynx_pelecanoides.jpg">Image: The deep sea fish eurypharynx pelecanoides, Popular Science Monthly, 1883.</a></p>
