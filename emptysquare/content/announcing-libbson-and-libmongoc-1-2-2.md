+++
type = "post"
title = "Announcing libbson and libmongoc 1.2.2"
date = "2015-11-30T21:46:56"
description = "A fix for hidden secondaries, and an improvement to the build system."
category = ["C", "MongoDB", "Programming"]
tag = []
enable_lightbox = false
thumbnail = "Great_Sea-Dragons.jpg"
draft = false
+++

<p><img style="display:block; margin-left:auto; margin-right:auto;" src="Great_Sea-Dragons.jpg" alt="Great Sea Dragons" title="Great Sea Dragons" /></p>
<p>This morning I released version 1.2.2 of <a href="http://mongoc.org/libbson/current/">libbson</a> and <a href="http://mongoc.org/libmongoc/current/">libmongoc</a>, the libraries that compose the MongoDB C Driver.</p>
<p>This release fixes an edge case where the driver can query hidden secondaries unintentionally. The bug manifests rarely: the hidden node must be in the seed list, and your application must be reading with a non-primary read preference while no primary is available.</p>
<p>(If the hidden node is not in the seed list it is never discovered. If it is in the seed list but a primary is available, the driver trusts the primary's host list, which omits the hidden member.)</p>
<p>This release also includes fixes and improvements to the build system. I'm particularly excited about some factoring I did in our Autoconf and CMake files. Before this, I had to update the libraries' version number in a dozen places. Now the version is defined exactly once.</p>
<p>Links:</p>
<ul>
<li><a href="https://github.com/mongodb/libbson/releases/download/1.2.2/libbson-1.2.2.tar.gz">libbson-1.2.2.tar.gz</a></li>
<li><a href="https://github.com/mongodb/mongo-c-driver/releases/download/1.2.2/mongo-c-driver-1.2.2.tar.gz">mongo-c-driver-1.2.2.tar.gz</a></li>
<li><a href="https://jira.mongodb.org/issues/?jql=fixVersion%20%3D%201.2.2%20AND%20project%20%3D%20CDRIVER">Issues resolved in 1.2.2</a></li>
<li><a href="http://mongoc.org">MongoDB C Driver Documentation</a></li>
</ul>
<p>Meanwhile, <a href="/announcing-libbson-and-libmongoc-1-3-0-beta0/">I hope you're trying out the C Driver's 1.3.0 beta</a>, it brings significant features for the imminent MongoDB 3.2 release. As always, if you have an issue with the driver, please <a href="https://jira.mongodb.org/browse/CDRIVER">open a ticket in Jira in the "CDRIVER" project</a> and we'll respond promptly.</p>
<p>Peace,<br />
A. Jesse Jiryu Davis</p>
<hr />
<p><a href="https://en.wikipedia.org/wiki/Plesiosauria"><span style="color:gray">Image: Wikipedia</span></a></p>
