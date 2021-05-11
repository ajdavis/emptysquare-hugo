+++
type = "post"
title = "Announcing libbson and libmongoc 1.3.5"
date = "2016-03-30T17:14:02"
description = "Fixes a bug in mongoc_cleanup and adds a configure option to disable automatic init and cleanup."
category = ["C", "Programming", "MongoDB"]
tag = []
enable_lightbox = false
thumbnail = "ship-went-away-rawscan.jpg"
draft = false
disqus_identifier = "/blog/announcing-libbson-and-libmongoc-1-3-5"
disqus_url = "https://emptysqua.re/blog//blog/announcing-libbson-and-libmongoc-1-3-5/"
+++

<p><img alt="" src="ship-went-away-rawscan.jpg" /></p>
<p>I'm pleased to announce version 1.3.5 of <a href="http://mongoc.org/libbson/current/">libbson</a> and <a href="http://mongoc.org/libmongoc/current/">libmongoc</a>, the libraries
constituting the MongoDB C Driver.</p>
<h2 id="libbson">libbson</h2>
<p>No change since 1.3.4; released to keep pace with libmongoc's version.</p>
<h2 id="libmongoc">libmongoc</h2>
<p>This release fixes a crash
in mongoc_cleanup when an allocator had been set with <code>bson_mem_set_vtable</code>.</p>
<p>It also
introduces a configure option <code>MONGOC_NO_AUTOMATIC_GLOBALS</code> which prevents code
built with GCC from automatically calling <code>mongoc_init</code> and <code>mongoc_cleanup</code> when
your code does not. This obscure, GCC-specific behavior was a bad idea and we'll remove it entirely in version 2.0. Meanwhile, we're letting you explicitly opt-out.</p>
<h2 id="links">Links:</h2>
<ul>
<li><a href="https://github.com/mongodb/libbson/releases/download/1.3.5/libbson-1.3.5.tar.gz">libbson-1.3.5.tar.gz</a></li>
<li><a href="https://github.com/mongodb/mongo-c-driver/releases/download/1.3.5/mongo-c-driver-1.3.5.tar.gz">libmongoc-1.3.5.tar.gz</a></li>
<li><a href="https://jira.mongodb.org/issues/?jql=project%20%3D%20CDRIVER%20AND%20fixVersion%20%3D%201.3.5%20ORDER%20BY%20due%20ASC%2C%20priority%20DESC%2C%20created%20ASC">All bugs fixed in 1.3.5</a></li>
<li><a href="http://mongoc.org/libmongoc/current/">Documentation</a></li>
</ul>
<p>Thanks to Hannes Magnusson, who did the significant work on this release.</p>
<hr />
<p><a href="http://www.oldbookillustrations.com/illustrations/ship-went-away/"><span style="color: gray">Image: Henry Ford Luce, 1890.</span></a></p>
