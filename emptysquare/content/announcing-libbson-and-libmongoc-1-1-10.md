+++
type = "post"
title = "Announcing libbson and libmongoc 1.1.10"
date = "2015-07-22T06:28:26"
description = "Three bugfixes in the MongoDB C library."
category = ["C", "Mongo", "Programming"]
tag = []
enable_lightbox = false
thumbnail = "coastline.jpg"
draft = false
disqus_identifier = "55af704a5393741c7066d53d"
disqus_url = "https://emptysqua.re/blog/55af704a5393741c7066d53d/"
+++

<p><img style="display:block; margin-left:auto; margin-right:auto;" src="coastline.jpg" alt="Coastline" title="Coastline" /></p>
<p>I released libbson and libmongoc 1.1.10 last night. (That's version "one one ten".) There are no changes in libbson, but in libmongoc I fixed:</p>
<ul>
<li><a href="https://jira.mongodb.org/browse/CDRIVER-745">Occasional crash reconnecting to replica set.</a></li>
<li><a href="https://jira.mongodb.org/browse/CDRIVER-750">Queries sent to recovering replica set members.</a></li>
<li><a href="https://jira.mongodb.org/browse/CDRIVER-755">Memory leak when calling ismaster on replica set members.</a></li>
</ul>
<p>Tarballs:</p>
<ul>
<li><a href="https://github.com/mongodb/libbson/releases/tag/1.1.10">libbson-1.1.10.tar.gz</a></li>
<li><a href="https://github.com/mongodb/mongo-c-driver/releases/tag/1.1.10">mongo-c-driver-1.1.10.tar.gz</a></li>
</ul>
<p>Thanks to Jason Carey, Jeremy Mikola, and Daniil Zaitsev for contributing to this release.</p>
<p>I leave for <a href="http://villagezendo.org/2015/03/grail2015/">an eight-day meditation retreat with the Village Zendo</a> this morning and I'm not taking my damn laptop with me. Shortly after I return, I intend to do a beta release of the sparkly C Driver 1.2.0; stay tuned.</p>
<hr />
<p><a href="https://commons.wikimedia.org/wiki/File:Coastline_old_vintage_photography_nature_landscape.jpg">Image: Halter Leo / U.S. Fish and Wildlife Service</a></p>
