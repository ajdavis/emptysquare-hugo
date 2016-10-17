+++
type = "post"
title = "Announcing libbson and libmongoc 1.4.1"
date = "2016-09-20T16:16:32"
description = "Three minor bugfixes."
"blog/category" = ["C", "Mongo", "Programming"]
"blog/tag" = []
enable_lightbox = false
thumbnail = "steam-ships@240.jpg"
draft = false
+++

<p><img alt="Description: 19th-Century color print, hand drawing of two elegant white steam ships, with black smoke pouring from each ship's twin chimneys and large paddle wheels. The ship on the left is triple-decked flying an American flag and a flag with the ship's name, &quot;St. John&quot;. The other is double-decked, with an American flag and a flag with its name, &quot;Drew&quot;." src="steam-ships.jpg" /></p>
<p>Hannes Magnusson and I are pleased to announce version 1.4.1 of libbson and libmongoc, the libraries
constituting the MongoDB C Driver.</p>
<h2 id="libbson">libbson</h2>
<p>This release improves the HTML documentation's Makefile.</p>
<h2 id="libmongoc">libmongoc</h2>
<p>This is a bugfix release:</p>
<ul>
<li>mongoc_client_get_server_descriptions could return a list including NULLs</li>
<li>Tailable cursors on MongoDB 3.2 only worked with MONGOC_QUERY_AWAIT_DATA</li>
<li>Spurious warnings with MONGOC_DISABLE_SHM</li>
</ul>
<h2 id="links">Links:</h2>
<ul>
<li><a href="https://github.com/mongodb/libbson/releases/download/1.4.1/libbson-1.4.1.tar.gz">libbson-1.4.1.tar.gz</a></li>
<li><a href="https://github.com/mongodb/mongo-c-driver/releases/download/1.4.1/mongo-c-driver-1.4.1.tar.gz">libmongoc-1.4.1.tar.gz</a></li>
<li><a href="https://jira.mongodb.org/issues/?jql=project%20%3D%20CDRIVER%20AND%20fixVersion%20%3D%201.4.1%20ORDER%20BY%20due%20ASC%2C%20priority%20DESC%2C%20created%20ASC">All bugs fixed in 1.4.1</a></li>
<li><a href="http://mongoc.org/">Documentation</a></li>
</ul>
<hr />
<p><a style="color: gray" href="http://www.albanyinstitute.org/details/items/the-grandest-palace-drawing-room-steamers-in-the-world-dre.html">Image: Currier &amp; Ives, Steamers on the Hudson River.</a></p>
    