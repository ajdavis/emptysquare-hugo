+++
type = "page"
title = "A Good Idea At The Time: Four Regrettable Decisions In PyMongo"
date = "2014-12-05T14:38:47"
description = "A four-part series about choices we regretted in the design of PyMongo."
category = []
tag = ["good-idea-at-the-time", "pymongo"]
enable_lightbox = false
thumbnail = "road-2@240.jpg"
draft = false
disqus_identifier = "5474062b539374096a7df69e"
disqus_url = "https://emptysqua.re/blog/5474062b539374096a7df69e/"
+++

<p><img style="display:block; margin-left:auto; margin-right:auto;" src="road-2.jpg" alt="Road" title="Road" /></p>
<p><em>The road to hell is paved with good intentions.</em></p>
<p>This is a series of articles about four regrettable decisions we made when we designed PyMongo, the standard Python driver for MongoDB. Each of these decisions made maintaining PyMongo painful for Bernie Hackett and me, and confused our users.</p>
<p>I describe the motivations behind these decisions and try to find the moral of the story: that is, some design principle that will guide you from the road to hell when you make choices for your own project.</p>
<p><strong>The Regrettable Decisions:</strong></p>
<ul>
<li><a href="/good-idea-at-the-time-pymongo-start-request/">start_request.</a></li>
<li><a href="/it-seemed-like-a-good-idea-at-the-time-pymongo-use-greenlets/">use_greenlets.</a></li>
<li><a href="/good-idea-at-the-time-pymongo-copy-database/">copy_database.</a></li>
<li><a href="/good-idea-at-the-time-pymongo-mongoreplicasetclient/">MongoReplicaSetClient.</a></li>
</ul>
