+++
type = "post"
title = "NYC Python Meetup recap"
date = "2011-11-15T22:14:07"
description = "I went to the NYC Python Meetup tonight at an East Village Bar. We drank, we ate pizza, we fended off recruiters (they knew they couldn't recruit at the meetup proper, but one ambushed me as I left!), and heard two quirky presentations: [ ... ]"
category = ["Programming", "Python"]
tag = []
enable_lightbox = false
draft = false
disqus_identifier = "167 http://emptysquare.net/blog/?p=167"
disqus_url = "https://emptysqua.re/blog/167 http://emptysquare.net/blog/?p=167/"
+++

<p>I went to the <a href="http://www.meetup.com/nycpython">NYC Python Meetup</a>
tonight at an East Village Bar. We drank, we ate pizza, we fended off
recruiters (they knew they couldn't recruit at the meetup proper, but
one ambushed me as I left!), and heard two quirky presentations:</p>
<p>· Roy Smith of songza.com talked about Songza's complex tech stack, and
discussed some nice techniques for dealing with the complexity. In
particular, they've hacked up their HAProxy front-end load balancer to
add an X-Unique-Id header to every incoming HTTP request. All the
software at all the tiers of their application logs the unique id along
with whatever else it's logging, so in retrospect it's easy to track the
steps it took to handle a request — or fail to handle it — as the work
bubbled from tier to tier. They've even integrated with <a href="http://getsatisfaction.com/">Get
Satisfaction</a> so they know the request id a
customer is complaining about.</p>
<p>· Aaron Watters showed us Gadfly, a Python library that implements the
SQL language for querying in-memory data or flat files. He's updated
Gadfly to talk with Cassandra (a NoSQL contender from Facebook) using
SQL. It seems to be at the clever-hack stage right now, but could lead
the way to integrating NoSQL databases with legacy systems that expect
SQL databases?</p>
