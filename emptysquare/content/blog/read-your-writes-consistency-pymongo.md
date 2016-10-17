+++
type = "post"
title = "Read-Your-Writes Consistency With PyMongo"
date = "2013-11-18T16:23:03"
description = "What's the best way to get read-your-writes consistency in PyMongo?"
"blog/category" = ["Mongo", "Programming", "Python"]
"blog/tag" = []
enable_lightbox = false
thumbnail = "quill@240.jpg"
draft = false
legacyid = "528a797653937479d528989c"
+++

<p><img style="display:block; margin-left:auto; margin-right:auto;" src="quill.jpg" alt="Quill" title="Quill" />
<span style="color:gray">Photo: <a href="http://www.flickr.com/photos/appeltaart_/8645069389/">Thomas van de Vosse</a></span></p>
<p>A PyMongo user asked me a good question today: if you want read-your-writes consistency, is it better to do acknowledged writes with a connection pool (the default), or to do unacknowledged writes over a single socket?</p>
<h1 id="a-little-background">A Little Background</h1>
<p>Let's say you update a MongoDB document with PyMongo, and you want to immediately read the updated version:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">client <span style="color: #666666">=</span> pymongo<span style="color: #666666">.</span>MongoClient()
collection <span style="color: #666666">=</span> client<span style="color: #666666">.</span>my_database<span style="color: #666666">.</span>my_collection
collection<span style="color: #666666">.</span>update(
    {<span style="color: #BA2121">&#39;_id&#39;</span>: <span style="color: #666666">1</span>},
    {<span style="color: #BA2121">&#39;$inc&#39;</span>: {<span style="color: #BA2121">&#39;n&#39;</span>: <span style="color: #666666">1</span>}})

<span style="color: #008000; font-weight: bold">print</span> collection<span style="color: #666666">.</span>find_one({<span style="color: #BA2121">&#39;_id&#39;</span>: <span style="color: #666666">1</span>})
</pre></div>


<p>In a multithreaded application, PyMongo's connection pool may have multiple sockets in it, so we don't promise that you'll use the same socket for the <code>update</code> and for the <code>find_one</code>. Yet you're still guaranteed read-your-writes consistency: the change you wrote to the document is reflected in the version of the document you subsequently read with <code>find_one</code>. PyMongo accomplishes this consistency by waiting for MongoDB to acknowledge the update operation before it sends the <code>find_one</code> query. (I <a href="/blog/pymongos-new-default-safe-writes/">explained last year how acknowledgment works in PyMongo</a>.)</p>
<p>There's another way to get read-your-writes consistency: you can send both the <code>update</code> and the <code>find_one</code> over the same socket, to ensure MongoDB processes them in order. In this case, you can tell PyMongo not to request acknowledgment for the update with the <code>w=0</code> option:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #408080; font-style: italic"># Reserve one socket for this thread.</span>
<span style="background-color: #ffffcc"><span style="color: #008000; font-weight: bold">with</span> client<span style="color: #666666">.</span>start_request():
</span>    collection<span style="color: #666666">.</span>update(
        {<span style="color: #BA2121">&#39;_id&#39;</span>: <span style="color: #666666">1</span>},
        {<span style="color: #BA2121">&#39;$inc&#39;</span>: {<span style="color: #BA2121">&#39;n&#39;</span>: <span style="color: #666666">1</span>}},
<span style="background-color: #ffffcc">        w<span style="color: #666666">=0</span>)
</span>
    <span style="color: #008000; font-weight: bold">print</span> collection<span style="color: #666666">.</span>find_one({<span style="color: #BA2121">&#39;_id&#39;</span>: <span style="color: #666666">1</span>})
</pre></div>


<p>If you set PyMongo's <code>auto_start_request</code> option it will call <code>start_request</code> for you. In that case you'd better let the connection pool grow to match the number of threads by removing its <code>max_pool_size</code>:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">client <span style="color: #666666">=</span> pymongo<span style="color: #666666">.</span>MongoClient(
    auto_start_request<span style="color: #666666">=</span><span style="color: #008000">True</span>,
    max_pool_size<span style="color: #666666">=</span><span style="color: #008000">None</span>)
</pre></div>


<p>(See <a href="/blog/requests-in-python-and-mongodb/">my article on requests</a> for details.)</p>
<p>So, to answer the user's question: If there are two ways to get read-your-writes consistency, which should you use?</p>
<h1 id="the-answer">The Answer</h1>
<p>You should accept PyMongo's default settings: use acknowledged writes. Here's why:</p>
<p><strong>Number of sockets</strong>: A multithreaded Python program that uses <code>w=0</code> and <code>auto_start_request</code> needs more connections to the server than does a program that uses acknowledged writes instead. With <code>auto_start_request</code> we have to reserve a socket for every application thread, whereas without it, threads can share a pool of connections smaller than the total number of threads.</p>
<p><strong>Back pressure</strong>: If the server becomes very heavily loaded, a program that uses <code>w=0</code> won't know the server is loaded because it doesn't wait for acknowledgments. In contrast, the server can exert back pressure on a program using acknowledged writes: the program can't continue to write to the server until the server has completed and acknowledged the writes currently in progress.</p>
<p><strong>Error reporting</strong>: If you use <code>w=0</code>, your application won't know whether the writes failed due to some error on the server. For example, an insert might cause a duplicate-key violation. Or you might try to <a href="http://docs.mongodb.org/manual/reference/operator/update/inc/">increment</a> a field in a document, but the server rejects the operation because the field isn't a number. By default PyMongo raises an exception under these circumstances so your program doesn't continue blithely on, but if you use <code>w=0</code> such errors pass silently.</p>
<p><strong>Consistency</strong>: Acknowledged writes guarantee read-your-writes consistency, whether you're connected to a mongod or to a mongos in a sharded cluster.</p>
<p>Using <code>w=0</code> with <code>auto_start_request</code> also guarantees read-your-writes consistency, but only if you're connected to a mongod. If you're connected to a mongos, using <code>w=0</code> with <code>auto_start_request</code> does not guarantee any consistency, because some writes may be queued in the <a href="http://docs.mongodb.org/manual/faq/sharding/#what-does-writebacklisten-in-the-log-mean">writeback listener</a> and complete asynchronously. Waiting for acknowledgment ensures that all writes have really been completed in the cluster before your program proceeds.</p>
<p><strong>Forwards compatibility with MongoDB</strong>: The next version of the MongoDB server will offer a <a href="https://jira.mongodb.org/browse/SERVER-9038">new implementation for insert, update, and delete</a>, which will diminish the performance boost of <code>w=0</code>.</p>
<p><strong>Forwards compatibility with PyMongo</strong>: You can tell by now that we're not big fans of <code>auto_start_request</code>. We're likely to remove it from PyMongo in version 3.0, so you're better off not relying on it.</p>
<h1 id="conclusion">Conclusion</h1>
<p>In short, you should just accept PyMongo's default settings: acknowledged writes with <code>auto_start_request=False</code>. There are many disadvantages and almost no advantages to <code>w=0</code> with <code>auto_start_request</code>, and in the near future these options will be diminished or removed anyway.</p>
    