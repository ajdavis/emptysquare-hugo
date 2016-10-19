+++
type = "post"
title = "This Blog Runs MongoDB 3.2 rc2"
date = "2015-11-08T22:11:02"
description = "I'm dogfooding the latest release candidate."
category = ["Mongo", "Programming", "Python"]
tag = []
enable_lightbox = false
thumbnail = "amx@240.jpg"
draft = false
disqus_identifier = "56400e2f1e31ec2550da976e"
disqus_url = "https://emptysqua.re/blog/56400e2f1e31ec2550da976e/"
+++

<p><img style="display:block; margin-left:auto; margin-right:auto;" src="amx.jpg" alt="1968 AMC AMX GT Concept Car" title="1968 AMC AMX GT Concept Car" /></p>
<hr />
<p>This blog is my equivalent of the hotrod an auto-mechanic has sitting in the garage: very custom, chopped down, and jagged at the edges. <a href="https://github.com/ajdavis/motor-blog">I've built it in Python</a>, of course, with Tornado and <a href="http://motor.readthedocs.org/">Motor</a>, my async driver for MongoDB. The original intent of the blog was to <a href="/eating-your-own-hamster-food/">eat my own hamster food</a> by building substantial software on top of Motor. Nowadays it's just the roadster I tinker with on the weekend.</p>
<p>This weekend, in particular, I switched the server to a more recent Rackspace Ubuntu instance (I was still on Ubuntu 9, somehow; now it's 14.04) and upgraded all the Python packages, including Motor itself.</p>
<p>Most exciting of all, this blog is now running on <a href="https://www.mongodb.com/blog/post/announcing-mongodb-3-2">MongoDB 3.2 rc2</a> with WiredTiger. I upgraded all the way from 2.5.1 to 3.2 in one shot, by mongodumping the old blog content and loading it into the new database with mongorestore. I'm so impressed with our server team's commitment to backwards compatibility over the last few years. The sole change I had to make was switching from the short-lived, experimental "text" command to the <a href="https://docs.mongodb.org/manual/reference/operator/query/text/">"$text" query syntax</a> introduced back in MongoDB 2.6.</p>
