+++
type = "post"
title = "Testing PyMongo As A Black Pipe"
date = "2015-10-11T18:23:19"
description = "The second \"black pipe testing\" article: testing PyMongo with MockupDB."
category = ["C", "Mongo", "Programming", "Python"]
tag = ["black-pipe", "testing"]
enable_lightbox = false
thumbnail = "pipe@240.jpg"
draft = false
disqus_identifier = "55fa418c539374235671f40e"
disqus_url = "https://emptysqua.re/blog/55fa418c539374235671f40e/"
+++

<p><a href="https://www.flickr.com/photos/emptysquare/2227062653"><img style="display:block; margin-left:auto; margin-right:auto;" src="pipe.jpg" alt="Pipe" title="Pipe" /></a></p>
<p>This is the second article in <a href="/blog/black-pipe-testing-series/">my six-part series on "black pipe" testing</a>. PyMongo, the official Python client for MongoDB, is a great example of a connected application that can't be fully tested as a black box. It has <em>two</em> ends that take inputs and provide outputs: one is its public API, the methods <code>find</code> and <code>insert_one</code> and so on. But the other is its communication over the network with the MongoDB server. Only by treating it as a black pipe can we fully test its surfaces.</p>
<p>This year I implemented a tool for black pipe testing called
<a href="http://mockupdb.readthedocs.org/">MockupDB</a>. It is a <a href="http://docs.mongodb.org/meta-driver/latest/legacy/mongodb-wire-protocol/">MongoDB wire protocol</a> server written in Python, with three
sets of features to aid tests:</p>
<ul>
<li>First, it speaks the whole wire protocol,
over TCP, just like a MongoDB server. You can even connect to it with the mongo shell.</li>
<li>Second, 
it can run in the same Python process as PyMongo. A black pipe test neatly interleaves
PyMongo calls and MockupDB calls to choreograph a sequence of requests and responses.</li>
<li>Third, MockupDB has a rich API for validating the messages PyMongo sends.</li>
</ul>
<h1 id="testing-pymongo-with-mockupdb">Testing PyMongo With MockupDB</h1>
<p>Here's the sort of test for which "black box" fails, but "black pipe" is perfect.</p>
<p>Starting with version 2.6 last year, MongoDB's wire protocol for modifying data changed. To insert a document, for example, drivers no longer send an OP_INSERT message followed by a "getLastError" command. Instead, drivers send a single command, called "insert". A driver should use the new protocol if the server is modern enough to understand it.</p>
<p><em>But</em>, it is impossible to know, based on its externally-observable behavior, whether a driver is using the old or new protocol. MongoDB supports the old wire protocol to this day. Even if a driver never upgrades its protocol, it can still insert data. So a black box test would pass! How do we validate that a driver uses the new protocol?</p>
<p>First, we start a MockupDB server that speaks the new wire protocol:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #000080; font-weight: bold">&gt;&gt;&gt; </span><span style="color: #008000; font-weight: bold">from</span> <span style="color: #0000FF; font-weight: bold">mockupdb</span> <span style="color: #008000; font-weight: bold">import</span> MockupDB
<span style="color: #000080; font-weight: bold">&gt;&gt;&gt; </span>server <span style="color: #666666">=</span> MockupDB(auto_ismaster<span style="color: #666666">=</span>{<span style="color: #BA2121">&quot;maxWireVersion&quot;</span>: <span style="color: #666666">3</span>})
<span style="color: #000080; font-weight: bold">&gt;&gt;&gt; </span>server<span style="color: #666666">.</span>run()
<span style="color: #000080; font-weight: bold">&gt;&gt;&gt; </span>
<span style="color: #000080; font-weight: bold">&gt;&gt;&gt; </span><span style="color: #008000; font-weight: bold">from</span> <span style="color: #0000FF; font-weight: bold">pymongo</span> <span style="color: #008000; font-weight: bold">import</span> MongoClient
<span style="color: #000080; font-weight: bold">&gt;&gt;&gt; </span>client <span style="color: #666666">=</span> MongoClient(server<span style="color: #666666">.</span>uri)
<span style="color: #000080; font-weight: bold">&gt;&gt;&gt; </span>collection <span style="color: #666666">=</span> client<span style="color: #666666">.</span>db<span style="color: #666666">.</span>collection
</pre></div>


<p>Let us insert a document. Once the client sends its message to MockupDB, it blocks awaiting acknowledgment, so we run it on a background thread using MockupDB's <code>go</code> function:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #000080; font-weight: bold">&gt;&gt;&gt; </span><span style="color: #008000; font-weight: bold">from</span> <span style="color: #0000FF; font-weight: bold">mockupdb</span> <span style="color: #008000; font-weight: bold">import</span> go
<span style="color: #000080; font-weight: bold">&gt;&gt;&gt; </span>document <span style="color: #666666">=</span> {<span style="color: #BA2121">&quot;_id&quot;</span>: <span style="color: #666666">1</span>}
<span style="color: #000080; font-weight: bold">&gt;&gt;&gt; </span>future <span style="color: #666666">=</span> go(collection<span style="color: #666666">.</span>insert_one, document)
</pre></div>


<p>Now the client waits, and we use MockupDB to read the message it sent:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #000080; font-weight: bold">&gt;&gt;&gt; </span>request <span style="color: #666666">=</span> server<span style="color: #666666">.</span>receives()
<span style="color: #000080; font-weight: bold">&gt;&gt;&gt; </span>request
<span style="color: #888888">Command({&quot;insert&quot;: &quot;collection&quot;, &quot;documents&quot;: [{&quot;_id&quot;: 1}]})</span>
</pre></div>


<p>We see the client has correctly sent an "insert" command, part of the new wire protocol. Respond on the main thread:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #000080; font-weight: bold">&gt;&gt;&gt; </span>request<span style="color: #666666">.</span>reply({<span style="color: #BA2121">&#39;ok&#39;</span>: <span style="color: #666666">1</span>})
</pre></div>


<p>This unblocks the client, so the result of <code>go(collection.insert_one, document)</code> is ready:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #000080; font-weight: bold">&gt;&gt;&gt; </span>future()
<span style="color: #888888">&lt;pymongo.results.InsertOneResult&gt;</span>
</pre></div>


<p>Let us say the driver had a bug, and it did <em>not</em> speak the new wire protocol when talking to a modern server. A black box test could not detect this bug, but MockupDB can. We validate that the client sends the right message using MockupDB's pattern-matching:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #000080; font-weight: bold">&gt;&gt;&gt; </span><span style="color: #408080; font-style: italic"># How a test would fail if PyMongo did</span>
<span style="color: #000080; font-weight: bold">&gt;&gt;&gt; </span><span style="color: #408080; font-style: italic"># not correctly use the new protocol:</span>
<span style="color: #888888">&gt;&gt;&gt;</span>
<span style="color: #000080; font-weight: bold">&gt;&gt;&gt; </span><span style="color: #008000; font-weight: bold">from</span> <span style="color: #0000FF; font-weight: bold">mockupdb</span> <span style="color: #008000; font-weight: bold">import</span> Command
<span style="color: #000080; font-weight: bold">&gt;&gt;&gt; </span>request <span style="color: #666666">=</span> server<span style="color: #666666">.</span>receives(Command({<span style="color: #BA2121">&quot;insert&quot;</span>: <span style="color: #BA2121">&quot;collection&quot;</span>}))
<span style="color: #888888">AssertionError:</span>
<span style="color: #888888">expected Command({&quot;insert&quot;: &quot;collection&quot;}), got OpInsert({&quot;_id&quot;: 1})</span>
</pre></div>


<p>With MockupDB we catch the bug, because we test both ends of the pipe.</p>
<hr />
<p>A variety of MongoDB driver tests were difficult or impossible, until now. I'm excited to begin testing driver features that were only manually tested before, using tcpdump or the like. I look forward even more to deleting hacky old tests that access PyMongo internals or exploit odd MongoDB server behaviors. Most such tests can now be gracefully expressed as black pipe tests with MockupDB.</p>
<hr />
<p>Next:</p>
<ul>
<li><a href="/blog/mockupdb-test-libmongoc-mongodb-c-driver-python/">MockupDB: Testing The MongoDB C Driver With Python</a></li>
<li><a href="/blog/black-pipe-testing-series/">Read the whole series on black pipe testing.</a></li>
</ul>
