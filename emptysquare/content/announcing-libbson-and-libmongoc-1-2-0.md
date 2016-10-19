+++
type = "post"
title = "Announcing libbson and libmongoc 1.2.0"
date = "2015-10-13T16:16:42"
description = "A rewritten mongoc_client_t with parallel server discovery, plus many features and fixes."
category = ["C", "Programming"]
tag = []
enable_lightbox = false
thumbnail = "sea@240.jpg"
draft = false
disqus_identifier = "561d637b539374099687eea2"
disqus_url = "https://emptysqua.re/blog/561d637b539374099687eea2/"
+++

<p><img style="display:block; margin-left:auto; margin-right:auto;" src="sea.jpg" alt="Sea" title="Sea" /></p>
<p>It is my pleasure to announce the 1.2.0 release of libbson and libmongoc, the C libraries that compose the MongoDB C Driver. This is the most significant C Driver release of the year. It includes rewritten client code with parallel server discovery, plus many features and fixes.</p>
<p>These notes summarize changes since the previous stable release, 1.1.11, including changes in the 1.2.0 betas and release candidate.</p>
<h1 id="libbson">libbson</h1>
<p>libbson 1.2.0 can be downloaded here:</p>
<ul>
<li><a href="https://github.com/mongodb/libbson/releases/download/1.2.0/libbson-1.2.0.tar.gz">libbson-1.2.0.tar.gz</a></li>
</ul>
<p>libbson is a C library for creating, parsing, and manipulating BSON documents. It also serves as a portability base for libmongoc.</p>
<p>Changes since 1.1.11:</p>
<ul>
<li>Add <a href="https://api.mongodb.org/libbson/current/bson_mem_restore_vtable.html"><code>bson_mem_restore_vtable()</code></a>, inverse of <a href="https://api.mongodb.org/libbson/current/bson_mem_set_vtable.html"><code>bson_mem_set_vtable()</code></a></li>
<li>Enable runtime asserts in release build.</li>
<li>Fixed compiler warnings and build failures on various platforms.</li>
<li>Improvements to the formatting and contents of the documentation.</li>
</ul>
<p>The libbson documentation is here:</p>
<ul>
<li><a href="https://api.mongodb.org/libbson">libbson reference manual</a></li>
</ul>
<h1 id="libmongoc">libmongoc</h1>
<p>libmongoc 1.2.0 can be downloaded here:</p>
<ul>
<li><a href="https://github.com/mongodb/mongo-c-driver/releases/download/1.2.0/mongo-c-driver-1.2.0.tar.gz">mongo-c-driver-1.2.0.tar.gz</a></li>
</ul>
<p>libmongoc is the C Driver for MongoDB, a library for building high-performance applications that communicate with MongoDB in the C language. It can also serve as the base for drivers in higher-level languages.</p>
<h2 id="internal-rewrite">Internal rewrite</h2>
<p>The main feature is Jason Carey and Samantha Ritter's rewrite of the <a href="http://api.mongodb.org/c/current/mongoc_client_t.html"><code>mongoc_client_t</code></a> internals. They overhauled it to match <a href="/blog/server-discovery-and-monitoring-in-pymongo-perl-and-c/">the Server Discovery And Monitoring Spec</a> and <a href="https://www.mongodb.com/blog/post/server-selection-next-generation-mongodb-drivers">the
Server Selection Spec</a>. The payoff is huge:</p>
<ul>
<li>All replica set members or mongos servers are discovered and periodically
  checked in parallel. The driver's performance is dramatically better and
  more predictable with multi-server deployments, or with a flaky network,
  or when some servers are slow or down.</li>
<li>Clients from the same <a href="http://api.mongodb.org/c/current/mongoc_client_pool_t.html"><code>mongoc_client_pool_t</code></a> share a background thread that
  discovers and monitors all servers in parallel.</li>
<li>Unnecessary round trips for server checks and pings are eliminated.</li>
<li>Behavior is documented in the specs, and consistent with other drivers, even
  in complex or unusual scenarios.</li>
<li>The URI's "replicaSet" option is enforced: the driver now refuses to connect
  to a server unless it is a member of a replica set with the right setName.</li>
<li>Many race conditions related to changing deployment conditions are fixed.</li>
</ul>
<p>The worst code in the old driver, the cause of most of the bugfix releases in the 1.1.x series, has been completely replaced with a well-designed architecture.</p>
<p>To conform to the new specs, the client accepts these options in the MongoDB
URI; see the <a href="http://api.mongodb.org/c/current/mongoc_uri_t.html"><code>mongoc_uri_t</code></a> documentation for details:</p>
<ul>
<li><code>heartbeatFrequencyMS</code></li>
<li><code>serverSelectionTimeoutMS</code></li>
<li><code>serverSelectionTryOnce</code></li>
<li><code>socketCheckIntervalMS</code></li>
</ul>
<h2 id="other-features">Other features:</h2>
<ul>
<li>All timeouts that <a href="http://api.mongodb.org/c/current/mongoc_uri_t.html">can be configured in the URI</a> now interpret 0 to mean "use
  the default value for this timeout".</li>
<li>The client's read preference can be configured in the URI with the new
  options "readPreference" and "readPreferenceTags", see the <a href="http://api.mongodb.org/c/current/mongoc_uri_t.html"><code>mongoc_uri_t</code></a>
  documentation.</li>
<li>The new <a href="http://api.mongodb.org/c/current/mongoc_uri_get_read_prefs_t.html"><code>mongoc_uri_get_read_prefs_t</code></a> function retrieves both the read mode
  and tags from a mongoc_uri_t.</li>
<li>New accessors:<ul>
<li><a href="http://api.mongodb.org/c/current/mongoc_gridfs_file_get_id.html"><code>mongoc_gridfs_file_get_id</code></a></li>
<li><a href="http://api.mongodb.org/c/current/mongoc_client_get_database.html"><code>mongoc_client_get_default_database</code></a></li>
<li><a href="http://api.mongodb.org/c/current/mongoc_bulk_operation_get_write_concern.html"><code>mongoc_bulk_operation_get_write_concern</code></a></li>
</ul>
</li>
<li><a href="https://api.mongodb.org/c/current/logging.html">Debug tracing can be controlled at runtime</a> with <code>mongoc_log_trace_enable</code> and
  <code>mongoc_log_trace_disable</code>.</li>
<li>Set <a href="https://api.mongodb.org/c/current/mongoc_client_pool_t.html"><code>mongoc_client_pool_t</code></a> size with <a href="https://api.mongodb.org/c/current/mongoc_client_pool_min_size.html"><code>mongoc_client_pool_min_size()</code></a> and <a href="https://api.mongodb.org/c/current/mongoc_client_pool_max_size.html"><code>mongoc_client_pool_max_size()</code></a>.</li>
</ul>
<h2 id="other-changes">Other changes:</h2>
<ul>
<li>Enable runtime asserts in release build.</li>
<li>The libbson submodule's URL now uses the recommended <code>https://</code>, not <code>git://</code></li>
<li><code>mongoc_client_kill_cursor()</code> is now deprecated and will be removed in 2.0.</li>
<li>The write concern "w=-1" is documented as obsolete.</li>
</ul>
<h2 id="bugfixes">Bugfixes</h2>
<p>These notable bugs have been fixed since 1.1.11:</p>
<ul>
<li>The driver now uses the server's maxWireVersion to avoid an error and extra round-trip when executing aggregations on MongoDB 2.4 and older.</li>
<li>Much improved reporting of network errors, unavailable servers, and authentication failure</li>
<li>Off-by-one error in <a href="https://api.mongodb.org/c/current/mongoc_gridfs_file_seek.html">mongoc_gridfs_file_seek</a> with mode SEEK_END</li>
<li>The writeConcernErrors field of bulk results is properly formatted.</li>
<li>A cursor with a server "hint" sets slaveOkay and / or $readPreference.</li>
<li>Destroying an exhaust cursor must close its socket</li>
<li>"wtimeoutms" was ignored for write concerns besides "majority".</li>
<li>Bulk write operations might fail in mixed-version sharded clusters with some pre-2.6 mongos servers.</li>
<li>A variety of bugs and incorrect results in <a href="https://api.mongodb.org/c/current/mongoc_bulk_operation_execute.html">mongoc_bulk_operation_execute</a>.</li>
<li>Numerous compiler warnings and build failures on various platforms.</li>
<li>Copious refinements to the documentation.</li>
</ul>
<p>The documentation is here:</p>
<ul>
<li><a href="http://docs.mongodb.org/ecosystem/drivers/c/">MongoDB C Driver Documentation</a></li>
</ul>
<p>Thanks to everyone who contributed to this version of libbson and libmongoc.</p>
<ul>
<li>Jason Carey</li>
<li>Samantha Ritter</li>
<li>A. Jesse Jiryu Davis</li>
<li>Hannes Magnusson</li>
<li>Kyle Suarez</li>
<li>Jeremy Mikola</li>
<li>Remi Collet</li>
<li>Jose Sebastian Battig</li>
<li>Derick Rethans</li>
<li>David Hatch</li>
<li>Yuchen Xie</li>
<li>Manuel Schoenlaub</li>
<li>Sujan Dutta</li>
<li>Lloyd Zhou</li>
<li>rubicks</li>
<li>Pawel Szczurko</li>
<li>Yuval Hager</li>
</ul>
<p>Peace,<br />
&nbsp;&nbsp;&nbsp;&mdash;A. Jesse Jiryu Davis</p>
<hr />
<p><span style="color:gray"><a href="https://www.flickr.com/photos/mizzmurray/2276790171">Image: Lisa Murray.</a></span></p>
