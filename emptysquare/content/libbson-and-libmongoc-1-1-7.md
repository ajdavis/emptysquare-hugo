+++
type = "post"
title = "Announcing libbson and libmongoc 1.1.7"
date = "2015-06-09T23:43:14"
description = "Bugfix releases for the MongoDB C libraries."
category = ["C", "Mongo", "Programming"]
tag = []
enable_lightbox = false
thumbnail = "TomCorser_Wild_Sea_Cot_Valley_Conwall_IMG_5558.JPG"
draft = false
disqus_identifier = "5577b23e5393741c64c2a441"
disqus_url = "https://emptysqua.re/blog/5577b23e5393741c64c2a441/"
+++

<p><img style="display:block; margin-left:auto; margin-right:auto;" src="TomCorser_Wild_Sea_Cot_Valley_Conwall_IMG_5558.JPG" alt="TomCorser Wild Sea Cot Valley Conwall IMG 5558" title="TomCorser Wild Sea Cot Valley Conwall IMG 5558" /></p>
<p>I released <a href="http://mongoc.org/libbson/current/">libbson</a> and <a href="http://mongoc.org/libmongoc/current/">libmongoc</a> 1.1.7 today.</p>
<p>In libbson, I fixed:</p>
<ul>
<li>Unchecked error in <code>bson_utf8_escape_for_json</code> caused unbounded memory growth and a crash.</li>
<li>Nicer floating-point formatting in <code>bson_as_json</code>.</li>
<li>Link error with CMake on Mac.</li>
</ul>
<p>In libmongoc:</p>
<ul>
<li>Thread-safe use of Cyrus SASL library.</li>
<li>Experimental support for building with CMake and SASL.</li>
<li>Faster reconnection to replica set with some hosts down.</li>
<li>Crash when iterating a cursor after reconnecting to a replica set.</li>
<li>Unchecked errors decoding invalid UTF-8 in MongoDB URIs.</li>
<li>Fix error reporting from <code>mongoc_client_get_database_names</code>.</li>
</ul>
<p><a href="https://jira.mongodb.org/secure/ReleaseNote.jspa?version=15523&amp;projectId=10030">You can read the full release notes for <a href="http://mongoc.org/libbson/current/">libbson</a> and <a href="http://mongoc.org/libmongoc/current/">libmongoc</a> 1.1.7 here</a>.</p>
<p>I continue to make small urgent bugfix releases in the 1.1.x series of the driver while I try to prepare 1.2.0 for a beta release. Unfortunately the two branches compete for my time: maintaining the current driver delays the much superior 1.2. But that's life when you have users.</p>
<p>I have a chance now to get unstuck. My experienced colleague Hannes Magnusson is going to help me with the 1.2 code for the remainder of the quarter and get me out of the bind.</p>
<hr />
<p><a href="http://commons.wikimedia.org/wiki/File:TomCorser_Wild_Sea_Cot_Valley_Conwall_IMG_5558.JPG">Image: Tom Corser / Wikimedia</a></p>
