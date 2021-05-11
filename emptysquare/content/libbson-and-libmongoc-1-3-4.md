+++
type = "post"
title = "Announcing libbson and libmongoc 1.2.4 and 1.3.4"
date = "2016-03-14T23:21:32"
description = "Security vulnerability when a client reconnects with SSL."
category = ["C", "Programming", "MongoDB"]
tag = []
enable_lightbox = false
thumbnail = "still-here-rawscan.jpg"
draft = false
disqus_identifier = "/blog/libbson-and-libmongoc-1-3-4"
disqus_url = "https://emptysqua.re/blog//blog/libbson-and-libmongoc-1-3-4/"
+++

<p><img alt="" src="still-here-rawscan.jpg" /></p>
<p>I'm pleased to announce versions 1.2.4 and 1.3.4 of <a href="http://mongoc.org/libbson/current/">libbson</a> and <a href="http://mongoc.org/libmongoc/current/">libmongoc</a>, the libraries
constituting the MongoDB C Driver.</p>
<h2 id="libbson">libbson</h2>
<p>The new versions of libbson have no changes; they're released to keep pace with libmongoc.</p>
<h2 id="libmongoc">libmongoc</h2>
<p>The MongoDB C Driver releases fix a security vulnerability: when a <code>mongoc_client_t</code> uses SSL and is disconnected, it failed to re-verify the server certificate after reconnecting. This flaw affects single clients, not pooled ones.</p>
<p>Version 1.3.4 is the latest release and is recommended for all users. 1.2.4 is released only for users on the 1.2.x line who want an upgrade with minimal changes.</p>
<h2 id="links">Links:</h2>
<ul>
<li><a href="https://github.com/mongodb/libbson/releases/download/1.2.4/libbson-1.2.4.tar.gz">libbson-1.2.4.tar.gz</a></li>
<li><a href="https://github.com/mongodb/mongo-c-driver/releases/download/1.2.4/mongo-c-driver-1.2.4.tar.gz">libmongoc-1.2.4.tar.gz</a></li>
<li><a href="https://github.com/mongodb/libbson/releases/download/1.3.4/libbson-1.3.4.tar.gz">libbson-1.3.4.tar.gz</a></li>
<li><a href="https://github.com/mongodb/mongo-c-driver/releases/download/1.3.4/mongo-c-driver-1.3.4.tar.gz">libmongoc-1.3.4.tar.gz</a></li>
<li><a href="https://jira.mongodb.org/issues/?jql=project%20%3D%20CDRIVER%20AND%20fixVersion%20%3D%201.3.4%20ORDER%20BY%20due%20ASC%2C%20priority%20DESC%2C%20created%20ASC">All bugs fixed in 1.3.4</a></li>
<li><a href="http://mongoc.org/libmongoc/current/">Documentation</a></li>
</ul>
<p>Thanks to everyone who contributed to this release.</p>
<ul><li>A. Jesse Jiryu Davis<li>Hannes Magnusson<li>Remi Collet</ul>

<p>Peace,<br />
&nbsp;&nbsp;&mdash; A. Jesse Jiryu Davis</p>
<hr />
<p><a href="http://www.oldbookillustrations.com/illustrations/still-here/"><span style="color: gray">Image: Henry Justice Ford, 1890</span></a></p>
