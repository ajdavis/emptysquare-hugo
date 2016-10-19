+++
type = "post"
title = "Announcing The Server Discovery And Monitoring Spec"
date = "2014-09-17T22:45:36"
description = "The new spec defines how MongoDB drivers connect to replica sets and other server topologies."
category = ["Mongo", "Programming", "Python"]
tag = ["pymongo"]
enable_lightbox = false
thumbnail = "discovery-2001@240.jpg"
draft = false
disqus_identifier = "541a452953937409602a1e70"
disqus_url = "https://emptysqua.re/blog/541a452953937409602a1e70/"
+++

<p><img style="display:block; margin-left:auto; margin-right:auto;" src="discovery-2001.jpg" alt="Spacecraft Discovery from 2001: A Space Odyssey" title="Spacecraft Discovery from 2001: A Space Odyssey" /></p>
<p>Today I published a draft of the Server Discovery And Monitoring Spec for MongoDB drivers. This spec defines how a MongoDB client discovers and monitors a single server, a set of mongoses, or a replica set. How does the client determine what types of servers they are? How does it keep this information up to date? How does the client find an entire replica set from a seed list, and how does it respond to a stepdown, election, reconfiguration, or network error?</p>
<p>In the past each MongoDB driver answered these questions a little differently, and mongos differed a little from the drivers. We couldn't answer questions like, "Once I add a secondary to my replica set, how long does it take for the driver to discover it?" Or, "How does a driver detect when the primary steps down, and how does it react?"</p>
<p>From now on, all drivers answer these questions the same. Or, where there's a legitimate reason for them to differ, there are as few differences as possible and each is clearly explained in the spec. Even in cases where several answers seem equally good, drivers agree on one way to do it.</p>
<p>The server discovery and monitoring method is specified in five sections. First, a client is constructed. Second, it begins monitoring the server topology by calling the <a href="http://docs.mongodb.org/manual/reference/command/isMaster/">ismaster command</a> on all servers. (The algorithm for multi-threaded and asynchronous clients is described separately from single-threaded clients.) Third, as ismaster responses are received the client parses them, and fourth, it updates its view of the topology. Finally, the spec describes how drivers update their topology view in response to errors.</p>
<p>I'm particularly excited about the unittests that accompany the spec. We have 37 tests that are specified formally in YAML files, with inputs and expected outcomes for a variety of scenarios. For each driver we'll write a test runner that feeds the inputs to the driver and verifies the outcome. This ends confusion about what the spec means, or whether all drivers conform to it.</p>
<p>The Java driver 2.12.1 is the spec's reference implementation for multi-threaded drivers, and I'm making the upcoming PyMongo 3.0 release conform to the spec as well. Mongos 2.6's replica set monitor is the reference implementation for single-threaded drivers, with a few differences. The upcoming Perl driver 1.0 implements the spec orthodoxly.</p>
<p>Once we have multiple reference implementations and the dust has settled, the draft spec will be final. We'll bring the rest of our drivers up to spec over the next year.</p>
<p>You can read more about the Server Discovery And Monitoring Spec at these links:</p>
<ul>
<li><a href="/server-discovery-and-monitoring-summary.html">A summary of the spec.</a></li>
<li><a href="/server-discovery-and-monitoring.html">The Server Discovery And Monitoring Spec.</a></li>
<li><a href="https://github.com/mongodb/specifications/tree/master/source/server-discovery-and-monitoring">The spec source, including the YAML test files.</a></li>
<li><a href="https://github.com/mongodb/mongo-python-driver/blob/3.0/test/test_discovery_and_monitoring.py">PyMongo's test runner.</a></li>
<li><a href="https://github.com/mongodb/mongo-python-driver/blob/3.0/pymongo/topology_description.py">PyMongo's core implementation of the spec.</a></li>
</ul>
<p>We have more work to do. For one thing, the Server Discovery And Monitoring Spec only describes how the client gathers information about your server topology&mdash;it does not describe which servers the client uses for operations. <a href="/blog/reading-from-mongodb-replica-sets-with-pymongo/">My Read Preferences Spec</a> only partly answers this second question. My colleague David Golden is writing an improved and expanded version of Read Preferences, which will be called the Server Selection Spec. Once that spec is complete, we'll have a standard algorithm for all drivers that answers questions like, "Which replica set member does the driver use for a query? What about an aggregation? Which mongos does it use for an insert?" It'll include tests of the same formality and rigor as the Server Discovery And Monitoring Spec does.</p>
<p>Looking farther ahead, we plan to standardize the drivers' APIs so we all do basic CRUD operations the same. And since <a href="https://jira.mongodb.org/browse/SERVER-15060">we'll allow much larger replica sets soon</a>, both the server-discovery and the server-selection specs will need amendments to handle large replica sets. In all cases, we'll provide a higher level of rigor, clarity, and formality in our specs than we have before.</p>
<p><img style="display:block; margin-left:auto; margin-right:auto;" src="shuttle-discovery.jpg" alt="Space Shuttle Discovery" title="Space Shuttle Discovery" /></p>
<p><span style="color: gray; font-style: italic"><a href="http://en.wikipedia.org/wiki/Space_Shuttle_Discovery">[Space Shuttle Discovery]</a></span></p>
