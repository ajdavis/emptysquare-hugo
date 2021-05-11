+++
type = "post"
title = "PyMongo 2.6.3 Released"
date = "2013-10-11T14:30:32"
description = "Announcing PyMongo 2.6.3, which fixes some connection-pool bugs and hardens the BSON parser."
category = ["MongoDB", "Programming", "Python"]
tag = []
enable_lightbox = false
thumbnail = "grail-tree.jpg"
draft = false
disqus_identifier = "525842d65393740368ee2727"
disqus_url = "https://emptysqua.re/blog/525842d65393740368ee2727/"
+++

<p><a href="http://www.flickr.com/photos/emptysquare/4527549354/"><img style="display:block; margin-left:auto; margin-right:auto;" src="grail-tree.jpg" alt="Grail tree" title="Grail tree" /></a></p>
<p>Bernie Hackett and I released <a href="https://pypi.python.org/pypi/pymongo/2.6.3">PyMongo 2.6.3</a> this afternoon. It fixes some bugs introduced in 2.6.0 when we added major features to PyMongo's connection pool.</p>
<p>The headline fix is for a <a href="https://jira.mongodb.org/browse/PYTHON-580">semaphore leak during connection failure</a>: The connection pool decrements a semaphore when it creates a connection, but didn't <em>increment</em> the semaphore if the connection failed. If a long-lived Python process connected to MongoDB over a flaky network with frequent connection timeouts, the semaphore's value would reach zero and further connection attempts would hang. I fixed it with a big try/finally block that ensures we increment the semaphore if we can't connect.</p>
<p>I also fixed a sheer oversight of mine: Although you can fine-tune the pool by passing the <a href="http://api.mongodb.org/python/current/faq.html#how-does-connection-pooling-work-in-pymongo">waitQueueMultiple and waitQueueTimeoutMS</a> parameters to MongoClient, you couldn't do the same for MongoReplicaSetClient, because it <a href="https://jira.mongodb.org/browse/PYTHON-579">ignored those parameters</a>.</p>
<p>Meanwhile, Bernie tightened up our BSON parser. It now <a href="https://jira.mongodb.org/browse/PYTHON-571">raises errors instead of crashing</a> when parsing a wider range of bad inputs. This continues our effort over the last few releases to harden the parser against corrupt documents, <a href="/python-c-extensions-and-mod-wsgi/">bizarre Python interpreter states</a>, out-of-memory errors, and the like.</p>
