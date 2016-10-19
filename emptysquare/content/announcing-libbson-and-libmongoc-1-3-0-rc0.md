+++
type = "post"
title = "Announcing libbson and libmongoc 1.3.0-rc0"
date = "2015-12-02T15:13:43"
description = "A couple fixes and features since the 1.3.0 beta."
category = ["C", "Mongo", "Programming"]
tag = []
enable_lightbox = false
thumbnail = "1951336700_4295b5ebb7_o@240.jpg"
draft = false
legacyid = "565f47a11e31ec1d4936bee7"
+++

<p><a href="https://www.flickr.com/photos/emptysquare/1951336700/"><img style="display:block; margin-left:auto; margin-right:auto;" src="1951336700_4295b5ebb7_o.jpg" title="Sea, from Staten Island Ferry" />
</a></p>
<p><a href="/blog/announcing-libbson-and-libmongoc-1-3-0-beta0/">The MongoDB C Driver beta I announced two weeks ago</a> has ripened into a release candidate. Here is what's changed between 1.3.0-beta0 and today's release, 1.3.0-rc0.</p>
<h1 id="libbson">libbson</h1>
<ul>
<li>Parse DBRefs correctly from JSON.</li>
<li>CMake option to disable building tests: you can turn off ENABLE_TESTS.</li>
<li>Fix build warnings on some platforms.</li>
<li>The build system is refactored to declare the current version and latest
   release in one place.</li>
</ul>
<h1 id="libmongoc">libmongoc</h1>
<p>Features:</p>
<ul>
<li>If the driver is compiled without SSL support but a URI with "ssl=true"
   is passed to <code>mongoc_client_new</code>, <code>mongoc_client_new_from_uri</code>, or
   <code>mongoc_client_pool_new</code>, the function logs an error and returns NULL. Before,
   the driver would attempt a non-SSL connection.</li>
<li>New functions to copy database and collection handles:</li>
<li><a href="http://api.mongodb.org/c/1.3.0/mongoc_collection_copy.html"><code>mongoc_collection_copy</code></a></li>
<li><a href="http://api.mongodb.org/c/1.3.0/mongoc_database_copy.html"><code>mongoc_database_copy</code></a></li>
<li>If a GridFS chunk is missing, <code>mongoc_gridfs_file_readv</code> set the file's error to
   domain MONGOC_ERROR_GRIDFS and a new code MONGOC_ERROR_GRIDFS_CHUNK_MISSING.</li>
<li>Use electionId to detect a stale replica set primary during a network split.</li>
<li>Disconnect from replica set members whose "me" field does not match the
   connection address.</li>
<li>The client side matching feature, <code>mongoc_matcher_t</code> and related functions,
   are deprecated and scheduled for removal in version 2.0.</li>
<li>New CMake options: ENABLE_SSL, ENABLE_SASL, ENABLE_TESTS, and ENABLE_EXAMPLES.</li>
</ul>
<p>Other fixes:</p>
<ul>
<li>Memory leaks in <code>mongoc_database_has_collection</code> and <code>mongoc_cursor_next</code>.</li>
<li>Report writeConcern failures from findAndModify and from legacy writes.</li>
</ul>
<h1 id="links">Links</h1>
<ul>
<li><a href="https://github.com/mongodb/libbson/releases/download/1.3.0-rc0/libbson-1.3.0-rc0.tar.gz">libbson-1.3.0-rc0.tar.gz</a></li>
<li><a href="https://github.com/mongodb/mongo-c-driver/releases/download/1.3.0-rc0/mongo-c-driver-1.3.0-rc0.tar.gz">libmongoc-1.3.0-rc0.tar.gz</a></li>
<li><a href="https://jira.mongodb.org/issues/?jql=fixVersion%20%3D%201.3.0-rc0%20AND%20project%20%3D%20CDRIVER">All bugs fixed in 1.3.0-rc0</a></li>
<li><a href="http://api.mongodb.org/c/1.3.0/">Beta documentation for libmongoc</a></li>
</ul>
<p>Thanks to everyone who contributed to this release candidate.</p>
<ul>
<li>Hannes Magnusson</li>
<li>Matt Cotter</li>
<li>Jose Sebastian Battig</li>
<li>Claudio Canella</li>
<li>Victor Leschuk</li>
<li>Flavio Medeiros</li>
<li>Christopher Wang</li>
</ul>
<p>Peace,<br />
&mdash;A. Jesse Jiryu Davis</p>
