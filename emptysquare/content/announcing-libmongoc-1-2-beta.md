+++
type = "post"
title = "Announcing libmongoc 1.2 Beta"
date = "2015-08-10T22:07:30"
description = "A rewritten mongoc_client_t with parallel server discovery, plus many features and fixes."
category = ["C", "Motor", "Programming"]
tag = []
enable_lightbox = false
thumbnail = "sea-splash.jpg"
draft = false
+++

<p><img style="display:block; margin-left:auto; margin-right:auto;" src="sea-splash.jpg" alt="Sea splash" title="Sea splash" /></p>
<p>This is the highlight of my summer: I just released 1.2.0-beta of libmongoc, the C driver for MongoDB. You can download the tarball here:</p>
<p><a href="https://github.com/mongodb/mongo-c-driver/releases/tag/1.2.0-beta">https://github.com/mongodb/mongo-c-driver/releases/tag/1.2.0-beta</a></p>
<hr />
<p>The main feature is Jason Carey and Samantha Ritter's rewrite of the <a href="http://mongoc.org/libmongoc/current/mongoc_client_t.html"><code>mongoc_client_t</code></a> internals. They overhauled it to match <a href="/server-discovery-and-monitoring-in-pymongo-perl-and-c/">the Server Discovery And Monitoring Spec</a> and <a href="https://www.mongodb.com/blog/post/server-selection-next-generation-mongodb-drivers">the
Server Selection Spec</a>. The payoff is huge:</p>
<ul>
<li>All replica set members or mongos servers are discovered and periodically
  checked in parallel. The driver's performance is dramatically better and
  more predictable with multi-server deployments, or with a flaky network,
  or when some servers are slow or down.</li>
<li>Clients from the same <a href="http://mongoc.org/libmongoc/current/mongoc_client_pool_t.html"><code>mongoc_client_pool_t</code></a> share a background thread that
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
URI; see the <a href="http://mongoc.org/libmongoc/current/mongoc_uri_t.html"><code>mongoc_uri_t</code></a> documentation for details:</p>
<ul>
<li><code>heartbeatFrequencyMS</code></li>
<li><code>serverSelectionTimeoutMS</code></li>
<li><code>serverSelectionTryOnce</code></li>
<li><code>socketCheckIntervalMS</code></li>
</ul>
<p>Other features:</p>
<ul>
<li>All timeouts that can be configured in the URI now interpret 0 to mean "use
  the default value for this timeout".</li>
<li>The client's read preference can be configured in the URI with the new
  options "readPreference" and "readPreferenceTags", see the <a href="http://mongoc.org/libmongoc/current/mongoc_uri_t.html"><code>mongoc_uri_t</code></a>
  documentation.</li>
<li>The new <a href="http://mongoc.org/libmongoc/current/mongoc_uri_get_read_prefs_t.html"><code>mongoc_uri_get_read_prefs_t</code></a> function retrieves both the read mode
  and tags from a mongoc_uri_t.</li>
<li>New accessors:<ul>
<li><a href="http://mongoc.org/libmongoc/current/mongoc_gridfs_file_get_id.html"><code>mongoc_gridfs_file_get_id</code></a></li>
<li><a href="http://mongoc.org/libmongoc/current/mongoc_client_get_database.html"><code>mongoc_client_get_default_database</code></a></li>
<li><a href="http://mongoc.org/libmongoc/current/mongoc_bulk_operation_get_write_concern.html"><code>mongoc_bulk_operation_get_write_concern</code></a></li>
</ul>
</li>
<li>Debug tracing can be controlled at runtime with <code>mongoc_log_trace_enable</code> and
  <code>mongoc_log_trace_disable</code>.</li>
</ul>
<p>Notable bugs fixed:</p>
<ul>
<li><a href="https://jira.mongodb.org/browse/CDRIVER-775">"wtimeoutms" was ignored for write concerns besides "majority".</a></li>
<li><a href="https://jira.mongodb.org/browse/CDRIVER-586">Bulk write operations might fail in mixed-version sharded clusters with
  some pre-2.6 mongos servers.</a></li>
<li><a href="https://jira.mongodb.org/browse/CDRIVER-731">Normal operations were logged during startup and could not be silenced.</a></li>
<li><a href="https://jira.mongodb.org/issues/?filter=18141&amp;jql=project%20%3D%20CDRIVER%20AND%20fixVersion%20in%20(1.2-beta%2C%201.2.0%2C%201.2-desired)%20and%20resolution%20is%20not%20empty%20and%20component%20%3D%20bulk%20ORDER%20BY%20key%20DESC">A variety of bugs and incorrect results</a> in <a href="http://mongoc.org/libmongoc/current/mongoc_bulk_operation_execute.html"><code>mongoc_bulk_operation_execute</code></a>.</li>
<li>Numerous compiler warnings and build failures on various platforms.</li>
<li>Copious refinements to the documentation.</li>
</ul>
<p>Thanks to everyone who contributed to this version of libmongoc.</p>
<ul>
<li>A. Jesse Jiryu Davis</li>
<li>Sujan Dutta</li>
<li>Jason Carey</li>
<li>Hannes Magnusson</li>
<li>Jeremy Mikola</li>
<li>Derick Rethans</li>
<li>Samantha Ritter</li>
<li>Yuchen Xie</li>
<li>Lloyd Zhou</li>
</ul>
<p>I hope you'll try this beta and let me know how it goes. <a href="https://jira.mongodb.org/browse/CDRIVER">Open a ticket in our bug tracker</a> if you find an issue. If you try it and it goes well, email me! I'm jesse@mongodb.com. I'd love to hear from you, and I need to know how the beta period is going for libmongoc users.</p>
<p>Peace,</p>
<p>&mdash; A. Jesse Jiryu Davis</p>
<hr />
<p><a href="https://www.flickr.com/photos/robertwitcher/14306767483"><span style="color:gray">Image: Robert Witcher</span></a></p>
