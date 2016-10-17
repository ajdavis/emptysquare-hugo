+++
type = "post"
title = "Announcing libbson and libmongoc 1.4.2"
date = "2016-09-30T17:26:03"
description = "Fixes two bugs in \"minPoolSize\" logic."
"blog/category" = ["C", "Mongo", "Programming"]
"blog/tag" = []
enable_lightbox = false
thumbnail = "ss-princess-may@240.jpg"
draft = false
+++

<p><a href="https://en.wikipedia.org/wiki/Princess_May_(steamship)"><img alt="Black and white photo. The steamship Princess May ran aground in 1910 on rocks near the north end of Sentinel Island. It was high tide and the momentum of the ship forced it well up onto the rocks, with the bow jutting upward at an angle of 23 degrees." src="ss-princess-may.jpg" /></a></p>
<p>I'm pleased to announce version 1.4.2 of libbson and libmongoc,
the libraries constituting the MongoDB C Driver.</p>
<h2 id="libbson">libbson</h2>
<p>No change since 1.4.1; released to keep pace with libmongoc's version.</p>
<h2 id="libmongoc">libmongoc</h2>
<p>This release fixes two bugs in
"minPoolSize" logic:</p>
<ul>
<li>minPoolSize should mean "the number of inactive clients to keep cached in the pool", so when a client is pushed, if there are already minPoolSize clients in the pool, the oldest should be freed. Instead, minPoolSize is compared to pool-&gt;size, which is the total number of active or inactive clients. So if there are 10 clients total and minPoolSize is 3, all pushed clients are freed, not just clients in excess of the first 3.</li>
<li>The pool is <a href="https://jira.mongodb.org/browse/CDRIVER-1196">supposed to be a LIFO for memory coherence</a> but it destroys the most-recently used client, not the least-recently used.</li>
</ul>
<p>See <a href="https://jira.mongodb.org/browse/CDRIVER-1558">CDRIVER-1558</a> for details.</p>
<h2 id="links">Links:</h2>
<ul>
<li><a href="https://github.com/mongodb/libbson/releases/download/1.4.2/libbson-1.4.2.tar.gz">libbson-1.4.2.tar.gz</a></li>
<li><a href="https://github.com/mongodb/mongo-c-driver/releases/download/1.4.2/mongo-c-driver-1.4.2.tar.gz">libmongoc-1.4.2.tar.gz</a></li>
<li><a href="https://jira.mongodb.org/issues/?jql=project%20%3D%20CDRIVER%20AND%20fixVersion%20%3D%201.4.2%20ORDER%20BY%20due%20ASC%2C%20priority%20DESC%2C%20created%20ASC">All bugs fixed in 1.4.2</a></li>
<li><a href="http://mongoc.org/">Documentation</a></li>
</ul>
<p>Peace,<br />
&nbsp;&nbsp;&mdash; A. Jesse Jiryu Davis</p>
    