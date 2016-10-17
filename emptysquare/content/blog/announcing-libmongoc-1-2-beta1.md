+++
type = "post"
title = "Announcing libmongoc 1.2 Beta 1"
date = "2015-09-03T17:03:54"
description = "Further improvements to the MongoDB C Driver since the first 1.2.0 beta."
"blog/category" = ["C", "Programming"]
"blog/tag" = []
enable_lightbox = false
thumbnail = "sea-clive-varley@240.jpg"
draft = false
+++

<p><img style="display:block; margin-left:auto; margin-right:auto;" src="sea-clive-varley.jpg" alt="Sea, by Clive Varley" title="Sea, by Clive Varley" /></p>
<p>It is my pleasure to announce the second beta release of the MongoDB C driver
1.2.0. It includes features and bugfixes developed since 1.2.0-beta. Get it here:</p>
<p><a href="https://github.com/mongodb/mongo-c-driver/releases/tag/1.2.0-beta1">https://github.com/mongodb/mongo-c-driver/releases/tag/1.2.0-beta1</a></p>
<p>New features:</p>
<ul>
<li>Set <a href="http://api.mongodb.org/c/1.2.0/mongoc_client_pool_t.html">mongoc_client_pool_t</a>'s size with <a href="http://api.mongodb.org/c/1.2.0/mongoc_client_pool_min_size.html">mongoc_client_pool_min_size()</a> and <a href="http://api.mongodb.org/c/1.2.0/mongoc_client_pool_max_size.html">mongoc_client_pool_max_size()</a>.</li>
<li>The write concern "w=-1" is now <a href="http://api.mongodb.org/c/1.2.0/mongoc_write_concern_t.html">documented as obsolete</a>.</li>
<li>Abundant fixes and additions to the documentation, beyond those in the
   previous beta.</li>
</ul>
<p>Notable bugs fixed:</p>
<ul>
<li>Crashes and races in several replica set scenarios.</li>
<li>The driver now uses the server's maxWireVersion to avoid an error and
   extra round-trip when executing aggregations on MongoDB 2.4 and older.</li>
<li>Fixed network error handling in multiple code paths.</li>
<li>connectTimeoutMS limits the time the driver can spend reconnecting to
   servers in single-threaded (non-pooled) mode with serverSelectionTryOnce.</li>
</ul>
<p>Version 1.2.0 final will be a stable release with additive ABI changes and
bugfixes. It is compatible with MongoDB version 2.4 and later.</p>
<p>Thanks to everyone who contributed to this version of libmongoc.</p>
<ul>
<li>A. Jesse Jiryu Davis</li>
<li>Hannes Magnusson</li>
<li>Manuel Schoenlaub</li>
<li>Kyle Suarez</li>
<li>Remi Collet</li>
</ul>
<p>I hope you'll try this beta and let me know how it goes. <a href="https://jira.mongodb.org/browse/CDRIVER/">Open a ticket in our bug tracker in the "CDRIVER" project</a> if you find an issue. If you try it and it goes well, email me! I'm jesse@mongodb.com. I'd love to hear from you, and I need to know how the beta period is going for libmongoc users.</p>
<p>Peace,</p>
<p>A. Jesse Jiryu Davis</p>
<hr />
<p><span style="color:gray"><a href="https://www.flickr.com/photos/100732098@N06/18166358058">Image: Clive Varley</a></span></p>
    