+++
type = "post"
title = "Announcing libbson and libmongoc 1.1.9"
date = "2015-06-29T00:33:57"
description = "Urgent bugfix release of the MongoDB C library."
category = ["C", "Mongo", "Programming"]
tag = []
enable_lightbox = false
thumbnail = "sea-black-and-white-flight-sky@240.jpg"
draft = false
disqus_identifier = "5590ca145393741c70667e2c"
disqus_url = "https://emptysqua.re/blog/5590ca145393741c70667e2c/"
+++

<p><img style="display:block; margin-left:auto; margin-right:auto;" src="sea-black-and-white-flight-sky.jpg" alt="Sea black and white flight sky" title="Sea black and white flight sky" /></p>
<p>I'm releasing libmongoc with an urgent bugfix for a common crash in 1.1.8, which itself was introduced while I was fixing a rare crash in 1.1.7. For further details:</p>
<ul>
<li><a href="https://jira.mongodb.org/browse/CDRIVER-721">CDRIVER-721</a></li>
<li><a href="https://jira.mongodb.org/browse/CDRIVER-695">CDRIVER-695</a></li>
</ul>
<p>In the process of validating my latest fix I expanded test coverage, and noticed that <code>./configure --enable-coverage</code> didn't work. That is now fixed in libbson and libmongoc.</p>
<p>libbson 1.1.9 can be downloaded here:</p>
<ul>
<li><a href="https://github.com/mongodb/libbson/releases/download/1.1.9/libbson-1.1.9.tar.gz">https://github.com/mongodb/libbson/releases/download/1.1.9/libbson-1.1.9.tar.gz</a></li>
</ul>
<p>libmongoc 1.1.9 can be downloaded here:</p>
<ul>
<li><a href="https://github.com/mongodb/mongo-c-driver/releases/download/1.1.9/mongo-c-driver-1.1.9.tar.gz">https://github.com/mongodb/mongo-c-driver/releases/download/1.1.9/mongo-c-driver-1.1.9.tar.gz</a></li>
</ul>
