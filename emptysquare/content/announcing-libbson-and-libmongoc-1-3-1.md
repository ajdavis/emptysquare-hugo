+++
type = "post"
title = "Announcing libbson and libmongoc 1.3.1"
date = "2016-01-18T15:09:01"
description = "Fixes some build failures and bugs since 1.3.0."
category = ["C", "Mongo", "Programming"]
tag = []
enable_lightbox = false
thumbnail = "Deep_sea.png"
draft = false
disqus_identifier = "/blog/announcing-libbson-and-libmongoc-1-3-1"
disqus_url = "https://emptysqua.re/blog//blog/announcing-libbson-and-libmongoc-1-3-1/"
+++

<p><img alt="Deep sea" src="Deep_sea.png" /></p>
<p>I'm pleased to announce version 1.3.1 of <a href="http://mongoc.org/libbson/current/">libbson</a> and <a href="http://mongoc.org/libmongoc/current/">libmongoc</a>, the libraries constituting the MongoDB C Driver. This is a run-of-the-mill bugfix release for you, unless you use GridFS with write concern, read concern, or read preference&mdash;in that case read carefully before upgrading.</p>
<h1 id="libbson">libbson</h1>
<ul>
<li><code>bson_strnlen</code> is off by one on Windows.</li>
<li><code>BSON_HAVE_STRNLEN</code> config check used incorrectly.</li>
<li>Incompatibility with older CMake versions.</li>
<li>Wrong-sized allocation in <code>bson_json_reader_new</code>.</li>
</ul>
<h1 id="libmongoc">libmongoc</h1>
<ul>
<li><code>mongoc_client_get_gridfs</code> now copies the client's read preferences, read concern, and write concern to the newly created <code>mongoc_gridfs_t</code>. Before this fix, GridFS operations were always executed with the default config: data was read from the primary, with the read concern level "local", and written with write concern "acknowledged". Now, if you have configured any of these options on the <code>mongoc_client_t</code>, they are respected by the <code>mongoc_gridfs_t</code>.</li>
<li>CMakeLists.txt now includes and installs the pkg-config files.</li>
</ul>
<h1 id="links">Links</h1>
<ul>
<li><a href="https://github.com/mongodb/libbson/releases/download/1.3.1/libbson-1.3.1.tar.gz">libbson-1.3.1.tar.gz</a></li>
<li><a href="https://github.com/mongodb/mongo-c-driver/releases/download/1.3.1/mongo-c-driver-1.3.1.tar.gz">libmongoc-1.3.1.tar.gz</a></li>
<li><a href="https://jira.mongodb.org/issues/?jql=project%20%3D%20CDRIVER%20AND%20fixVersion%20%3D%201.3.1%20ORDER%20BY%20due%20ASC%2C%20priority%20DESC%2C%20created%20ASC">All bugs fixed in 1.3.1</a></li>
<li><a href="http://mongoc.org/libmongoc/current/">Documentation for libmongoc</a></li>
</ul>
<p>Thanks to everyone who contributed to this release.</p>
<ul>
<li>A. Jesse Jiryu Davis</li>
<li>Hannes Magnusson</li>
<li>Christopher Wang</li>
<li>Jean-Bernard Jansen</li>
<li>Jeremy Mikola</li>
<li>Jeroen Ooms</li>
<li>Alex Bishop</li>
</ul>
<p>Peace,<br />
&nbsp;&nbsp;&mdash;A. Jesse Jiryu Davis</p>
<hr />
<p><a href="https://commons.wikimedia.org/wiki/File:Deep_sea.jpg">Image: Wikipedia</a></p>
