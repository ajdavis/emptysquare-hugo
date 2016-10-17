+++
type = "post"
title = "Announcing libbson and libmongoc 1.2.0 Release Candidate"
date = "2015-10-01T18:39:28"
description = "The next big release of the MongoDB C Driver is available for testing."
"blog/category" = ["C", "Mongo", "Programming"]
"blog/tag" = []
enable_lightbox = false
thumbnail = "F2Y_Sea_Dart_2@240.jpg"
draft = false
legacyid = "560db5735393742358ca1c8f"
+++

<p><img style="display:block; margin-left:auto; margin-right:auto;" src="F2Y_Sea_Dart_2.jpg" alt="Sea Dart 2" title="Sea Dart 2" /></p>
<p>We just released 1.2.0-rc0. This is a release candidate of libbson and libmongoc, the libraries that constitute the MongoDB C driver. The release includes features and bugfixes developed since 1.2.0-beta1. For an overview of what the 1.2.0 release means for you, read <a href="/blog/announcing-libmongoc-1-2-beta/">my announcement of the first 1.2.0 beta last month</a>. In short: high-performance non-blocking I/O, and standardized logic for high availability.</p>
<p>Download the release candidate release tarballs here:</p>
<ul>
<li><a href="https://github.com/mongodb/libbson/releases/tag/1.2.0-rc0">https://github.com/mongodb/libbson/releases/tag/1.2.0-rc0</a></li>
<li><a href="https://github.com/mongodb/mongo-c-driver/releases/tag/1.2.0-rc0">https://github.com/mongodb/mongo-c-driver/releases/tag/1.2.0-rc0</a></li>
</ul>
<p>Notable bugs fixed since the previous beta:</p>
<ul>
<li>Much improved reporting of network errors, unavailable servers, and authentication failure</li>
<li>Destroying an exhaust cursor must close its socket</li>
<li>Various bugs in server reconnection logic</li>
<li>mongoc_collection_aggregate returned invalid cursor after failure</li>
<li>Wrong error message after failed network write on Sparc</li>
<li>Missing JSON test files in release tarball</li>
</ul>
<p>Other changes:</p>
<ul>
<li>Enable runtime asserts in release build.</li>
<li>mongoc_client_kill_cursor is now deprecated and will be removed in version 2.0.</li>
</ul>
<p>This release candidate also includes all bugfixes from libbson and libmongoc 1.1.11.</p>
<p>Version 1.2.0 final will be a stable release with additive ABI changes and bugfixes. It is compatible with MongoDB version 2.4 and later.</p>
<p>In the last few weeks my colleague Hannes Magnusson has shouldered a large portion of the work. Kyle Suarez is also working on the C Driver for his initial six-week rotation at MongoDB&mdash;he returns for full-time work after <a href="/blog/mentoring/">a triumphant internship with me last summer</a> and he's become even more meticulous and productive in the year since we met. My great gratitude to both of them, and all who contributed to this release candidate:</p>
<ul>
<li>A. Jesse Jiryu Davis</li>
<li>Hannes Magnusson</li>
<li>Kyle Suarez</li>
<li>rubicks</li>
<li>Jose Sebastian Battig</li>
<li>Jason Carey</li>
<li>Remi Collet</li>
<li>Yuval Hager</li>
</ul>
<p>Peace,<br />
&nbsp;&nbsp;&mdash;A. Jesse Jiryu Davis</p>
<hr />
<p><a href="https://commons.wikimedia.org/wiki/File:F2Y_Sea_Dart_2.jpg"><span style="color:gray">Image: U.S. Navy</span></a></p>
    