+++
type = "post"
title = "PyMongo 2.4.2 Is Out"
date = "2013-01-24T09:50:46"
description = "Changes in PyMongo, the MongoDB Python driver"
category = ["Mongo", "Programming", "Python"]
tag = ["pymongo"]
enable_lightbox = false
draft = false
disqus_identifier = "5101497e5393747ddd768988"
disqus_url = "https://emptysqua.re/blog/5101497e5393747ddd768988/"
+++

<p>Yesterday we released <a href="http://pypi.python.org/pypi/pymongo/2.4.2">PyMongo 2.4.2</a>, the latest version of 10gen's Python driver for MongoDB. You can see <a href="https://jira.mongodb.org/secure/IssueNavigator.jspa?reset=true&amp;mode=hide&amp;jqlQuery=fixVersion+%3D+%222.4.2%22+AND+project+%3D+PYTHON">the whole list of nine bugs</a> fixed. Here are some highlights:</p>
<ul>
<li>
<p>I made PyMongo's <code>MongoReplicaSetClient</code> smarter about reading from replica set members in failure scenarios. Since version 2.1, PyMongo has been able to detect when a secondary becomes primary or vice versa. But it wasn't very smart about members that are neither primary <em>nor</em> secondary because they're in recovery mode. Now, PyMongo reacts as soon as it notices such a member: it stops trying to use it, and it refreshes its view of all members' states immediately.</p>
</li>
<li>
<p>We got <a href="https://github.com/mongodb/mongo-python-driver/pull/152/">an excellent pull request from Craig Hobbs</a> that lets you specify your <a href="/blog/reading-from-mongodb-replica-sets-with-pymongo/">read preference</a> in the connection string, like:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">&quot;mongodb://localhost/?readPreference=secondary&quot;
</pre></div>


</li>
<li>
<p>If you want to <a href="/blog/mongodb-full-text-search/">try MongoDB's full-text search</a>, PyMongo can now <em>create</em> a text index. (All versions let you to run the <code>text</code> command to use a text index once you've created </p>
</li>
</ul>
<p>(Down here we have to speak very quietly, because the next part is top-secret: I snuck a feature into what's supposed to be a bugfix release. PyMongo 2.4.2 has the hooks <a href="/motor/">Motor</a> needs to wrap PyMongo and make it non-blocking. This lets Motor take a new direction, which I'll blog about shortly.)</p>
