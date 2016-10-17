+++
type = "post"
title = "Save the Monkey: Reliably Writing to MongoDB"
date = "2011-12-08T14:41:20"
description = ""
"blog/category" = ["Mongo", "Programming", "Python"]
"blog/tag" = []
enable_lightbox = false
thumbnail = "3064180867_0f293b8f27@240.jpg"
draft = false
legacyid = "236 http://emptysquare.net/blog/?p=236"
+++

<p><img style="display:block; margin-left:auto; margin-right:auto;" src="3064180867_0f293b8f27.jpg" title="" /></p>
<p>Photo: <a href="http://www.flickr.com/photos/kj-an/3064180867/">Kevin Jones</a></p>
<p>MongoDB replica sets claim "automatic failover" when a primary server
goes down, and they live up to the claim, but handling failover in your
application code takes some care. I'll walk you through writing a
failover-resistant application in PyMongo.</p>
<p><strong>Update:</strong> This article is superseded by my MongoDB World 2016 talk and the accompanying article:</p>
<p><a href="https://emptysqua.re/blog/smart-strategies-for-resilient-mongodb-applications/">Writing Resilient MongoDB Applications</a></p>
<h1 id="setting-the-scene">Setting the Scene</h1>
<p><a href="http://www.catb.org/jargon/html/S/scratch-monkey.html">Mabel the Swimming Wonder
Monkey</a> is
participating in your cutting-edge research on simian scuba diving. To
keep her alive underwater, your application must measure how much oxygen
she consumes each second and pipe the same amount of oxygen to her scuba
gear. In this post, I'll describe how to write reliably to MongoDB.</p>
<h1 id="mongodb-setup">MongoDB Setup</h1>
<p>Since Mabel's life is in your hands, you want a robust Mongo deployment.
Set up a 3-node replica set. We'll do this on your local machine using
three TCP ports, but of course in production you'll have each node on a
separate machine:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #19177C">$ </span>mkdir db0 db1 db2
<span style="color: #19177C">$ </span>mongod --dbpath db0 --logpath db0/log --pidfilepath db0/pid --port <span style="color: #666666">27017</span> --replSet foo --fork
<span style="color: #19177C">$ </span>mongod --dbpath db1 --logpath db1/log --pidfilepath db1/pid --port <span style="color: #666666">27018</span> --replSet foo --fork
<span style="color: #19177C">$ </span>mongod --dbpath db2 --logpath db2/log --pidfilepath db2/pid --port <span style="color: #666666">27019</span> --replSet foo --fork
</pre></div>


<p>(Make sure you don't have any mongod processes running on those ports
first.)</p>
<p>Now connect up the nodes in your replica set. My machine's hostname is
'emptysquare.local'; replace it with yours when you run the example:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #19177C">$ </span>hostname
emptysquare.local
<span style="color: #19177C">$ </span>mongo
&gt; rs.initiate<span style="color: #666666">({</span>
  _id: <span style="color: #BA2121">&#39;foo&#39;</span>,
  members: <span style="color: #666666">[</span>
    <span style="color: #666666">{</span>_id: 0, host:<span style="color: #BA2121">&#39;emptysquare.local:27017&#39;</span><span style="color: #666666">}</span>,
    <span style="color: #666666">{</span>_id: 1, host:<span style="color: #BA2121">&#39;emptysquare.local:27018&#39;</span><span style="color: #666666">}</span>,
    <span style="color: #666666">{</span>_id: 2, host:<span style="color: #BA2121">&#39;emptysquare.local:27019&#39;</span><span style="color: #666666">}</span>
  <span style="color: #666666">]</span>
<span style="color: #666666">})</span>
</pre></div>


<p>The first _id, 'foo', must match the name you passed with --replSet on
the command line, otherwise MongoDB will complain. If everything's
correct, MongoDB replies with, "Config now saved locally. Should come
online in about a minute." Run rs.status() a few times until you see
that the replica set has come online&mdash;the first member's stateStr will be
"PRIMARY" and the other two members' stateStrs will be "SECONDARY". On
my laptop this takes about 15 seconds.</p>
<p>Voil&agrave;: a bulletproof 3-node replica set! Let's start the Mabel
experiment.</p>
<h1 id="definitely-writing">Definitely Writing</h1>
<p>Install <a href="http://pypi.python.org/pypi/pymongo/" title="PyMongo">PyMongo</a>
and create a Python script called mabel.py with the following:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">import</span> <span style="color: #0000FF; font-weight: bold">datetime</span><span style="color: #666666">,</span> <span style="color: #0000FF; font-weight: bold">random</span><span style="color: #666666">,</span> <span style="color: #0000FF; font-weight: bold">time</span>
<span style="color: #008000; font-weight: bold">import</span> <span style="color: #0000FF; font-weight: bold">pymongo</span>

mabel_db <span style="color: #666666">=</span> pymongo<span style="color: #666666">.</span>MongoReplicaSetClient(
    <span style="color: #BA2121">&#39;localhost:27017,localhost:27018,localhost:27019&#39;</span>,
    replicaSet<span style="color: #666666">=</span><span style="color: #BA2121">&#39;foo&#39;</span>
)<span style="color: #666666">.</span>mabel

<span style="color: #008000; font-weight: bold">while</span> <span style="color: #008000">True</span>:
    time<span style="color: #666666">.</span>sleep(<span style="color: #666666">1</span>)
    mabel_db<span style="color: #666666">.</span>breaths<span style="color: #666666">.</span>insert({
        <span style="color: #BA2121">&#39;time&#39;</span>: datetime<span style="color: #666666">.</span>datetime<span style="color: #666666">.</span>utcnow(),
        <span style="color: #BA2121">&#39;oxygen&#39;</span>: random<span style="color: #666666">.</span>random()
    })

    <span style="color: #008000; font-weight: bold">print</span> <span style="color: #BA2121">&#39;wrote&#39;</span>
</pre></div>


<p>mabel.py will record the amount of oxygen Mabel consumes (or, in our
test, a random amount) and insert it into MongoDB once per second. Run it:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #19177C">$ </span>python mabel.py
wrote
wrote
wrote
</pre></div>


<p>What happens when our good-for-nothing sysadmin unplugs the primary
server? Grab the primary's process id from <code>db0/pid</code> and kill it. Now,
all is not well with our Python script:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">Traceback <span style="color: #666666">(</span>most recent call last<span style="color: #666666">)</span>:
  File <span style="color: #BA2121">&quot;mabel.py&quot;</span>, line 10, in &lt;module&gt;
    <span style="color: #BA2121">&#39;oxygen&#39;</span>: random.random<span style="color: #666666">()</span>
  File <span style="color: #BA2121">&quot;/Users/emptysquare/.virtualenvs/pymongo/mongo-python-driver/pymongo/collection.py&quot;</span>, line 310, in insert
    continue_on_error, self.__uuid_subtype<span style="color: #666666">)</span>, safe<span style="color: #666666">)</span>
  File <span style="color: #BA2121">&quot;/Users/emptysquare/.virtualenvs/pymongo/mongo-python-driver/pymongo/mongo_replica_set_client.py&quot;</span>, line 738, in _send_message
    raise AutoReconnect<span style="color: #666666">(</span>str<span style="color: #666666">(</span>why<span style="color: #666666">))</span>
pymongo.errors.AutoReconnect: <span style="color: #666666">[</span>Errno 61<span style="color: #666666">]</span> Connection refused
</pre></div>


<p>This is terrible. WTF happened to "automatic failover"? And why does
PyMongo raise an AutoReconnect error rather than actually automatically
reconnecting?</p>
<p>Well, automatic failover <strong>does</strong> work, in the sense that one of the
secondaries will take over as a new primary in a few seconds. Do rs.status() in
the mongo shell to confirm that:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #19177C">$ </span>mongo --port <span style="color: #666666">27018</span> <span style="color: #408080; font-style: italic"># connect to one of the surviving mongods</span>
PRIMARY&gt; rs.status<span style="color: #666666">()</span>
// edited <span style="color: #008000; font-weight: bold">for</span> readability ...
<span style="color: #666666">{</span>
    <span style="color: #BA2121">&quot;set&quot;</span> : <span style="color: #BA2121">&quot;foo&quot;</span>,
    <span style="color: #BA2121">&quot;members&quot;</span> : <span style="color: #666666">[</span> <span style="color: #666666">{</span>
            <span style="color: #BA2121">&quot;_id&quot;</span> : 0,
            <span style="color: #BA2121">&quot;name&quot;</span> : <span style="color: #BA2121">&quot;emptysquare.local:27017&quot;</span>,
            <span style="color: #BA2121">&quot;stateStr&quot;</span> : <span style="color: #BA2121">&quot;(not reachable/healthy)&quot;</span>,
            <span style="color: #BA2121">&quot;errmsg&quot;</span> : <span style="color: #BA2121">&quot;socket exception&quot;</span>
        <span style="color: #666666">}</span>, <span style="color: #666666">{</span>
            <span style="color: #BA2121">&quot;_id&quot;</span> : 1,
            <span style="color: #BA2121">&quot;name&quot;</span> : <span style="color: #BA2121">&quot;emptysquare.local:27018&quot;</span>,
            <span style="color: #BA2121">&quot;stateStr&quot;</span> : <span style="color: #BA2121">&quot;PRIMARY&quot;</span>
        <span style="color: #666666">}</span>, <span style="color: #666666">{</span>
            <span style="color: #BA2121">&quot;_id&quot;</span> : 2,
            <span style="color: #BA2121">&quot;name&quot;</span> : <span style="color: #BA2121">&quot;emptysquare.local:27019&quot;</span>,
            <span style="color: #BA2121">&quot;stateStr&quot;</span> : <span style="color: #BA2121">&quot;SECONDARY&quot;</span>,
        <span style="color: #666666">}</span>
    <span style="color: #666666">]</span>
<span style="color: #666666">}</span>
</pre></div>


<p>Depending on which mongod took over as the primary, your output could be
a little different. Regardless, there <strong>is</strong> a new primary, so why did
our write fail? The answer is that PyMongo doesn't try repeatedly to
insert your document&mdash;it just tells you that the first attempt failed.
It's your application's job to decide what to do about that. To explain
why, let us indulge in a brief digression.</p>
<h1 id="brief-digression-monkeys-vs-kittens">Brief Digression: Monkeys vs. Kittens</h1>
<p><img style="display:block; margin-left:auto; margin-right:auto;" src="monkeys-vs-kittens.png" alt="Monkeys vs Kittens" title="monkeys-vs-kittens.png" border="0"   /></p>
<p>If what you're inserting is voluminous but no single document is very
important, like pictures of kittens or web analytics, then in the
extremely rare event of a failover you might prefer to discard a few
documents, rather than blocking your application while it waits for the
new primary. Throwing an exception if the primary dies is often the
right thing to do: You can notify your user that he should try uploading
his kitten picture again in a few seconds once a new primary has been
elected.</p>
<p>But if your updates are infrequent and tremendously valuable, like
Mabel's oxygen data, then your application should try very hard to write
them. Only you know what's best for your data, so PyMongo lets you
decide. Let's return from this digression and implement that.</p>
<h1 id="trying-hard-to-write">Trying Hard to Write</h1>
<p>Let's bring up the mongod we just killed:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #19177C">$ </span>mongod --dbpath db0 --logpath db0/log --pidfilepath db0/pid --port <span style="color: #666666">27017</span> --replSet foo --fork
</pre></div>


<p>And update mabel.py with the following armor-plated loop:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">while</span> <span style="color: #008000">True</span>:
    time<span style="color: #666666">.</span>sleep(<span style="color: #666666">1</span>)
    data <span style="color: #666666">=</span> {
        <span style="color: #BA2121">&#39;time&#39;</span>: datetime<span style="color: #666666">.</span>datetime<span style="color: #666666">.</span>utcnow(),
        <span style="color: #BA2121">&#39;oxygen&#39;</span>: random<span style="color: #666666">.</span>random()
    }

    <span style="color: #408080; font-style: italic"># Try for five minutes to recover from a failed primary</span>
    <span style="color: #008000; font-weight: bold">for</span> i <span style="color: #AA22FF; font-weight: bold">in</span> <span style="color: #008000">range</span>(<span style="color: #666666">60</span>):
        <span style="color: #008000; font-weight: bold">try</span>:
            mabel_db<span style="color: #666666">.</span>breaths<span style="color: #666666">.</span>insert(data)
            <span style="color: #008000; font-weight: bold">print</span> <span style="color: #BA2121">&#39;wrote&#39;</span>
            <span style="color: #008000; font-weight: bold">break</span> <span style="color: #408080; font-style: italic"># Exit the retry loop</span>
        <span style="color: #008000; font-weight: bold">except</span> pymongo<span style="color: #666666">.</span>errors<span style="color: #666666">.</span>AutoReconnect, e:
            <span style="color: #008000; font-weight: bold">print</span> <span style="color: #BA2121">&#39;Warning&#39;</span>, e
            time<span style="color: #666666">.</span>sleep(<span style="color: #666666">5</span>)
    <span style="color: #008000; font-weight: bold">else</span>:
        <span style="color: #008000; font-weight: bold">raise</span> <span style="color: #D2413A; font-weight: bold">Exception</span>(<span style="color: #BA2121">&quot;Couldn&#39;t write!&quot;</span>)
</pre></div>


<p>In a Python for-loop, the "else" clause executes if we exhaust the loop without executing the "break" statement. So this loop waits a full minute for a new primary, trying every 5 seconds. If there's no primary after a minute, there may never be one. Perhaps the sysadmin unplugged a majority of the members. In this case we raise an exception.</p>
<p>Now run python mabel.py, and again kill the primary. mabel.py's output
will look like:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">wrote
Warning [Errno 61] Connection refused
Warning emptysquare.local:27017: [Errno 61] Connection refused, emptysquare.local:27019: [Errno 61] Connection refused, emptysquare.local:27018: [Errno 61] Connection refused
Warning emptysquare.local:27017: not primary, emptysquare.local:27019: [Errno 61] Connection refused, emptysquare.local:27018: not primary
wrote
wrote
.
.
.
</pre></div>


<p>mabel.py goes through a few stages of grief when the primary dies, but
in a few seconds it finds a new primary, inserts its data, and continues
happily.</p>
<h1 id="what-about-duplicates">What About Duplicates?</h1>
<p>Leaving monkeys and kittens aside, another reason PyMongo doesn't
automatically retry your inserts is the risk of duplication: If the
first attempt caused an error, PyMongo can't know if the error happened
before Mongo wrote the data, or after. What if we end up writing Mabel's
oxygen data twice? Well, there's a trick you can use to prevent this:
generate the document id on the client.</p>
<p>Whenever you insert a document, Mongo checks if it has an "_id" field
and if not, it generates an ObjectId for it. But you're free to choose
the new document's id before you insert it, as long as the id is unique
within the collection. You can use an ObjectId or any other type of
data. In mabel.py you could use the timestamp as the document id, but
I'll show you the more generally applicable ObjectId approach:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">from</span> <span style="color: #0000FF; font-weight: bold">pymongo.objectid</span> <span style="color: #008000; font-weight: bold">import</span> ObjectId

<span style="color: #008000; font-weight: bold">while</span> <span style="color: #008000">True</span>:
    time<span style="color: #666666">.</span>sleep(<span style="color: #666666">1</span>)
    data <span style="color: #666666">=</span> {
        <span style="color: #BA2121">&#39;_id&#39;</span>: ObjectId(),
        <span style="color: #BA2121">&#39;time&#39;</span>: datetime<span style="color: #666666">.</span>datetime<span style="color: #666666">.</span>utcnow(),
        <span style="color: #BA2121">&#39;oxygen&#39;</span>: random<span style="color: #666666">.</span>random()
    }

    <span style="color: #408080; font-style: italic"># Try for five minutes to recover from a failed primary</span>
    <span style="color: #008000; font-weight: bold">for</span> i <span style="color: #AA22FF; font-weight: bold">in</span> <span style="color: #008000">range</span>(<span style="color: #666666">60</span>):
        <span style="color: #008000; font-weight: bold">try</span>:
            mabel_db<span style="color: #666666">.</span>breaths<span style="color: #666666">.</span>insert(data)
            <span style="color: #008000; font-weight: bold">print</span> <span style="color: #BA2121">&#39;wrote&#39;</span>
            <span style="color: #008000; font-weight: bold">break</span> <span style="color: #408080; font-style: italic"># Exit the retry loop</span>
        <span style="color: #008000; font-weight: bold">except</span> pymongo<span style="color: #666666">.</span>errors<span style="color: #666666">.</span>AutoReconnect, e:
            <span style="color: #008000; font-weight: bold">print</span> <span style="color: #BA2121">&#39;Warning&#39;</span>, e
            time<span style="color: #666666">.</span>sleep(<span style="color: #666666">5</span>)
        <span style="color: #008000; font-weight: bold">except</span> pymongo<span style="color: #666666">.</span>errors<span style="color: #666666">.</span>DuplicateKeyError:
            <span style="color: #408080; font-style: italic"># It worked the first time</span>
            <span style="color: #008000; font-weight: bold">break</span>
    <span style="color: #008000; font-weight: bold">else</span>:
        <span style="color: #008000; font-weight: bold">raise</span> <span style="color: #D2413A; font-weight: bold">Exception</span>(<span style="color: #BA2121">&quot;Couldn&#39;t write!&quot;</span>)
</pre></div>


<p>We set the document's id to a newly-generated ObjectId in our Python
code, before entering the retry loop. Then, if our insert succeeds just
before the primary dies and we catch the AutoReconnect exception, then
the next time we try to insert the document we'll catch a
DuplicateKeyError and we'll know for sure that the insert succeeded. You
can use this technique for safe, reliable writes in general.</p>
<hr />
<h2 id="bibliography">Bibliography</h2>
<p><a href="http://www.catb.org/jargon/html/S/scratch-monkey.html">Apocryphal story of Mabel, the Swimming Wonder
Monkey</a></p>
<p><a href="http://edp.org/monkey.htm">More likely true, very brutal story of 3 monkeys killed by a computer
error</a></p>
<hr />
<p><strong>History</strong>: Updated April 3, 2014 for current PyMongo syntax.</p>
    