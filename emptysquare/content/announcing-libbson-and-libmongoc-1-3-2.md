+++
type = "post"
title = "Announcing libbson and libmongoc 1.3.2"
date = "2016-02-01T20:53:38"
description = "Fixes a critical bug and a few minor ones."
category = ["C", "Mongo", "Programming"]
tag = []
enable_lightbox = false
thumbnail = "Deep_sea_2.jpg"
draft = false
disqus_identifier = "/blog/announcing-libbson-and-libmongoc-1-3-2"
disqus_url = "https://emptysqua.re/blog//blog/announcing-libbson-and-libmongoc-1-3-2/"
+++

<p><img alt="Deep sea" src="Deep_sea_2.jpg" /></p>
<p>I'm pleased to announce version 1.3.2 of <a href="http://mongoc.org/libbson/current/">libbson</a> and <a href="http://mongoc.org/libmongoc/current/">libmongoc</a>, the libraries constituting the MongoDB C Driver. We fixed a critical bug and a few minor ones.</p>
<h1 id="libbson">libbson</h1>
<ul>
<li>man pages couldn't be built from a distribution tarball.</li>
</ul>
<h1 id="libmongoc">libmongoc</h1>
<ul>
<li>A socket is properly discarded after a network error from a command.</li>
<li><code>mongoc_database_get_collection</code> copies the database's read preferences,
read concern, and write concern, instead of copying the client's.</li>
<li>The <code>mongoc_cursor_t</code> private struct allows a negative limit.</li>
</ul>
<h1 id="links">Links</h1>
<ul>
<li><a href="https://github.com/mongodb/libbson/releases/download/1.3.2/libbson-1.3.2.tar.gz">libbson-1.3.2.tar.gz</a></li>
<li><a href="https://github.com/mongodb/mongo-c-driver/releases/download/1.3.2/mongo-c-driver-1.3.2.tar.gz">libmongoc-1.3.2.tar.gz</a></li>
<li><a href="https://jira.mongodb.org/issues/?jql=project%20%3D%20CDRIVER%20AND%20fixVersion%20%3D%201.3.2%20ORDER%20BY%20due%20ASC%2C%20priority%20DESC%2C%20created%20ASC">All bugs fixed in 1.3.2</a></li>
<li><a href="http://api.mongodb.org/c/">Documentation for libmongoc</a></li>
</ul>
<p>Thanks to everyone who contributed to this release.</p>
<ul>
<li>A. Jesse Jiryu Davis</li>
<li>Hannes Magnusson</li>
<li>Jeremy Mikola</li>
</ul>
<p>Peace,<br />
&nbsp;&nbsp;&mdash;A. Jesse Jiryu Davis</p>
<hr />
<p><a href="https://commons.wikimedia.org/wiki/File:Deep_sea.jpg">Image: Wikipedia</a></p>
