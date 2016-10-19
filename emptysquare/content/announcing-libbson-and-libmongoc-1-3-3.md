+++
type = "post"
title = "Announcing libbson and libmongoc 1.3.3"
date = "2016-02-05T09:11:06"
description = "One bugfix to large batched writes."
category = ["C", "Programming", "Mongo"]
tag = []
enable_lightbox = false
thumbnail = "sea-black-and-white-weather-ocean@240.jpg"
draft = false
disqus_identifier = "/blog/announcing-libbson-and-libmongoc-1-3-3"
disqus_url = "https://emptysqua.re/blog//blog/announcing-libbson-and-libmongoc-1-3-3/"
+++

<p><img alt="" src="sea-black-and-white-weather-ocean.jpg" /></p>
<p>I'm pleased to announce version 1.3.3 of libbson and libmongoc, the libraries
constituting the MongoDB C Driver.</p>
<h2 id="libbson">libbson</h2>
<p>No change since 1.3.2; released to keep pace with libmongoc's version.</p>
<h2 id="libmongoc">libmongoc</h2>
<p>Fixes a bug where
a slightly-oversized bulk write operation was not split into batches; instead,
it was sent whole to the server, which rejected it.</p>
<h2 id="links">Links:</h2>
<ul>
<li><a href="https://github.com/mongodb/libbson/releases/download/1.3.3/libbson-1.3.3.tar.gz">libbson-1.3.3.tar.gz</a></li>
<li><a href="https://github.com/mongodb/mongo-c-driver/releases/download/1.3.3/mongo-c-driver-1.3.3.tar.gz">libbson-1.3.3.tar.gz</a></li>
<li><a href="https://jira.mongodb.org/browse/CDRIVER-1082">CDRIVER-1082, "Proper bulk operation splitting at the margin"</a></li>
<li><a href="https://api.mongodb.org/c/">Documentation</a></li>
</ul>
<p>Peace,<br />
&nbsp;&nbsp;&mdash; A. Jesse Jiryu Davis</p>
<hr />
<p><a href="http://jaymantri.com/post/110848819388/download">Image: Jay Mantri</a></p>
