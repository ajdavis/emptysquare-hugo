+++
type = "post"
title = "Announcing PyMongo 2.8 Release Candidate"
date = "2014-11-12T17:50:15"
description = "Compatible with new MongoDB 2.8 features, and deprecates some features that will be removed in PyMongo 3.0."
category = ["MongoDB", "Programming", "Python"]
tag = ["pymongo"]
enable_lightbox = false
thumbnail = "Morelia_spilota_variegata_MNHN.jpg"
draft = false
disqus_identifier = "5463d228539374096b6aeafd"
disqus_url = "https://emptysqua.re/blog/5463d228539374096b6aeafd/"
+++

<p><a href="https://commons.wikimedia.org/wiki/File%3AMorelia_spilota_variegata_MNHN.jpg"><img alt="Morelia spilota variegata" src="Morelia_spilota_variegata_MNHN.jpg" style="display:block; margin-left:auto; margin-right:auto;" title="Morelia spilota variegata"/>
</a></p>
<p><a href="https://commons.wikimedia.org/wiki/File%3AMorelia_spilota_variegata_MNHN.jpg"><span style="color:gray">By Jebulon, via Wikimedia Commons</span></a></p>
<p>We've just tagged a release candidate of PyMongo, the standard MongoDB driver for Python. You can install it like:</p>

{{<highlight plain>}}
pip install git+git://github.com/mongodb/mongo-python-driver.git@2.8rc0
{{< / highlight >}}

<p>Most of the changes between PyMongo 2.8 and the previous release, 2.7.2, are for compatibility with the upcoming MongoDB 2.8 release. (By coincidence,  PyMongo and MongoDB are at the same version number right now.)</p>
<div class="toc">
<ul>
<li><a href="#compatibility">Compatibility</a><ul>
<li><a href="#scram-sha-1-authentication">SCRAM-SHA-1 authentication</a></li>
<li><a href="#count-with-hint">count with hint</a></li>
</ul>
</li>
<li><a href="#pymongo-improvements">PyMongo improvements</a><ul>
<li><a href="#son-performance">SON performance</a></li>
<li><a href="#socketkeepalive">socketKeepAlive</a></li>
</ul>
</li>
<li><a href="#deprecation-warnings">Deprecation warnings</a></li>
<li><a href="#bugs">Bugs</a></li>
</ul>
</div>
<hr/>
<h1 id="compatibility">Compatibility</h1>
<h2 id="scram-sha-1-authentication">SCRAM-SHA-1 authentication</h2>
<p>MongoDB 2.8 adds support for SCRAM-SHA-1 authentication and makes it the new default, replacing our inferior old protocol MONGODB-CR ("MongoDB Challenge-Response"). PyMongo's maintainer Bernie Hackett added support for the new protocol. PyMongo and MongoDB work together to make this change seamless: you can upgrade PyMongo first, then your MongoDB servers, and authentication will keep working with your existing passwords. When you choose to, you can upgrade how your passwords are hashed within the database itself—we'll document how to do that when we release MongoDB 2.8.</p>
<p>SCRAM-SHA-1 is more secure than MONGODB-CR, but it's also slower: the new protocol requires the client to do 10,000 iterations of SHA-1 by default, instead of one iteration of MD5. This has two implications for you.</p>
<p>First, you must create one MongoClient or MongoReplicaSetClient instance when your application starts up, and keep using it for your application's lifetime. For example, consider this little Flask app:</p>

{{<highlight python3>}}
from pymongo import MongoClient
from flask import Flask

# This is the right thing to do:
db = MongoClient('mongodb://user:password@host').test
app = Flask(__name__)

@app.route('/')
def home():
    doc = db.collection.find_one()
    return repr(doc)

app.run()
{{< / highlight >}}

<p>That's the right way to build your app, because it lets PyMongo reuse connections to MongoDB and maintain a connection pool.</p>
<p>But time and again and I see people write request handlers like this:</p>

{{<highlight python3>}}
@app.route('/')
def home():
    # Wrong!!
    db = MongoClient('mongodb://user:password@host').test
    doc = db.collection.find_one()
    return repr(doc)
{{< / highlight >}}

<p>When you create a new MongoClient for each request like this, it requires PyMongo to set up a new TCP connection to MongoDB for every request to your application, and then shut it down after each request. This already hurts your performance.</p>
<p>But if you're using authentication and you upgrade to PyMongo 2.8 and MongoDB 2.8, you'll also pay for SHA-1 hashing with every request. So if you aren't yet following my recommendation and reusing one client throughout your application, fix your code now.</p>
<p>Second, you should install <a href="https://pypi.python.org/pypi/backports.pbkdf2/0.1">backports.pbkdf2</a>—it speeds up the hash computation, especially on Python older than 2.7.8, or on Python 3 before Python 3.4.</p>
<p>I've updated PyMongo's <code>copy_database</code> so you can <a href="https://pymongo.readthedocs.io/en/stable/examples/copydb.html">use SCRAM-SHA-1 authentication to copy between servers</a>. More information about SCRAM-SHA-1 is in <a href="https://pymongo.readthedocs.io/en/stable/examples/authentication.html">PyMongo's latest auth documentation</a>.</p>
<h2 id="count-with-hint">count with hint</h2>
<p>Starting in MongoDB 2.6 the "count" command can <a href="https://jira.mongodb.org/browse/SERVER-2677">take a hint that tells it which index to use, by name</a>. In PyMongo 2.8 Bernie <a href="https://jira.mongodb.org/browse/PYTHON-744">added support for count with hint</a>:</p>

{{<highlight python3>}}
from pymongo import ASCENDING

collection.create_index([('field', ASCENDING)], name='my_index')

collection.find({
    'field': {'$gt': 10}
}).hint('my_index').count()
{{< / highlight >}}

<p>This will work with MongoDB 2.6, and in MongoDB 2.8 <a href="https://jira.mongodb.org/browse/SERVER-14799">count support hints by index specs</a>, not just index names:</p>

{{<highlight python3>}}
collection.find({
    'field': {'$gt': 10}
}).hint([('field', ASCENDING)]).count()
{{< / highlight >}}

<h1 id="pymongo-improvements">PyMongo improvements</h1>
<h2 id="son-performance">SON performance</h2>
<p>Don Mitchell from EdX generously offered us <a href="https://jira.mongodb.org/browse/PYTHON-703">a patch</a> that improves the performance of <a href="https://pymongo.readthedocs.io/en/stable/api/bson/son.html">SON</a>, PyMongo's implementation of an ordered dict. His patch avoids unnecessary copies of field names in many of SON's methods.</p>
<h2 id="socketkeepalive">socketKeepAlive</h2>
<p>In some network setups, users need to <a href="http://www.tldp.org/HOWTO/html_single/TCP-Keepalive-HOWTO/">set the SO_KEEPALIVE flag</a> on PyMongo's TCP connections to MongoDB, so Bernie <a href="https://jira.mongodb.org/browse/PYTHON-679">added a socketKeepAlive option to MongoClient and MongoReplicaSetClient</a>.</p>
<h1 id="deprecation-warnings">Deprecation warnings</h1>
<p>Soon we'll release a PyMongo 3.0 that removes many obsolete features from PyMongo and gives you a cleaner, safer, faster new API. But we want to make the upgrade as smooth as possible for you. To begin with, I <a href="https://pymongo.readthedocs.io/en/stable/2.8/compatibility-policy.html">documented our compatibility policy</a>. I explained how to test your code to make sure you use no deprecated features of PyMongo.</p>
<p>Second, I deprecated some features that will be removed in PyMongo 3.0:</p>
<p><code>start_request</code> is deprecated and will be removed in PyMongo 3.0, because it's <a href="/read-your-writes-consistency-pymongo/">not the right way to ensure consistency</a>, and <a href="https://jira.mongodb.org/browse/SERVER-12273">it doesn't work with sharding in MongoDB 2.8</a>. Further justifications <a href="https://jira.mongodb.org/browse/PYTHON-785">can be found here</a>.</p>
<p><code>MasterSlaveConnection</code> is deprecated and will be removed, since master-slave setups are themselves obsolete. Replica sets are superior to master-slave, especially now that <a href="https://jira.mongodb.org/browse/SERVER-15060">replica sets can have more than 12 members</a>. Anyway, even if you still have a master-slave setup, PyMongo's <code>MasterSlaveConnection</code> wasn't very useful.</p>
<p>And finally, <code>copy_database</code> is deprecated. We asked customers if they used it and the answer was no, people <a href="http://docs.mongodb.org/manual/reference/method/db.copyDatabase/">use the mongo shell for copying databases</a>, not PyMongo. For the sake of backwards compatibility I upgraded PyMongo's <code>copy_database</code> to support SCRAM-SHA-1, anyway, but in PyMongo 3.0 we plan to remove it. Let me know in the comments if you think this is the wrong decision.</p>
<h1 id="bugs">Bugs</h1>
<p>The only notable bugfix in PyMongo 2.8 is <a href="/a-normal-accident-in-python-and-mod-wsgi/">the delightfully silly mod_wsgi error I wrote about last month</a>. But if you find any <em>new</em> bugs, please let us know by <a href="https://jira.mongodb.org/browse/PYTHON">opening an issue in Jira</a>, I promise we'll handle it promptly.</p>
