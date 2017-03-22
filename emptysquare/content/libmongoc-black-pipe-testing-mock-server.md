+++
type = "post"
title = "Black Pipe Testing A Connected Application In C"
date = "2015-10-26T23:20:08"
description = "The fourth \"black pipe testing\" article: testing the MongoDB C Driver with mock_server_t."
category = ["C", "Mongo", "Programming", "Python"]
tag = ["black-pipe", "testing"]
enable_lightbox = false
thumbnail = "coney-island.jpg"
draft = false
disqus_identifier = "55fa4e285393742358c9c260"
disqus_url = "https://emptysqua.re/blog/55fa4e285393742358c9c260/"
series = ["black-pipe"]
+++

<p><a href="https://www.flickr.com/photos/emptysquare/404160108"><img style="display:block; margin-left:auto; margin-right:auto;" src="f-train.jpg" alt="The F Train" title="The F Train" /></a></p>
<p>This is the fourth article in <a href="/black-pipe-testing-series/">my series on "black pipe" testing</a>. Here I describe testing libmongoc (the MongoDB C Driver) as a black pipe.</p>
<p>Like any network client library, libmongoc cannot be fully tested as a black box. Traditional black box tests enter some input and check the output&mdash;this only validates one side of the system at a time. But libmongoc has two sides, working in concert. One side is its public API, its structs and functions and so on. The other is its communication over the network with the MongoDB server. Only by treating it as a black pipe can we fully test its two sides.</p>
<div class="toc">
<ul>
<li><a href="#origin">Origin</a></li>
<li><a href="#evolution-from-c-to-python">Evolution: from C to Python</a></li>
<li><a href="#more-evolution-from-python-back-to-c">More evolution: from Python back to C</a></li>
<li><a href="#conclusion">Conclusion</a></li>
</ul>
</div>
<hr />
<h1 id="origin">Origin</h1>
<p>I began thinking about black pipe testing early this year. I was reading the libmongoc test suite in preparation for taking over the project from Christian Hergert and Jason Carey, and I came across Christian's <code>mock_server_t</code> struct. Test code in C does not ordinarily make lively reading, but I woke up when I saw this. Had he really written a MongoDB wire protocol server in order to test the client library?</p>
<p>If you know Christian Hergert's work, you know the answer. Of course he had. His mock server listened on a random TCP port, parsed the client's network messages, and sent MongoDB responses. At the time, <code>mock_server_t</code> used callbacks: you created a mock server with a pointer to a function that handled requests and chose how to reply. And if you think callbacks are ungainly in Javascript or Python, try them in C.</p>
<p>Despite its awkward API, the mock server was indispensable for certain tests. For example, Christian had a mock server that reported it only spoke wire protocol versions 10 and 11. Since the latest MongoDB protocol version is only 3, the driver does not know how to talk to such a futuristic server and should refuse to, but the only way to test that behavior is by simulating the server.</p>
<p>Besides the protocol-version test, Christian also used the mock server to validate the client's handling of "read preferences". That is, how the client expresses whether it wants to read from a primary server, a secondary, or some subtler criterion. A mock server is required here because a correct client and a buggy one appear the same at the API level: it is only when we test its behavior at the network layer that bugs are caught.</p>
<p>In these two tests I saw the two use cases for "black pipe" testing. First, black pipe tests simulate unusual server behavior and network events. Second, in cases where the client's API behavior can appear correct even when there are bugs at the network layer, black pipe tests validate the network-level logic too.</p>
<p><a href="https://www.flickr.com/photos/emptysquare/352837037/"><img style="display:block; margin-left:auto; margin-right:auto;" src="f-train-2.jpg" alt="F Train" title="F Train" /></a></p>
<h1 id="evolution-from-c-to-python">Evolution: from C to Python</h1>
<p>I had not yet taken leadership of libmongoc&mdash;I was finishing up some Python work. So, inspired by Christian's idea, I wrote a mock server in Python, called <a href="http://mockupdb.readthedocs.org/">MockupDB</a>. MockupDB is the subject of my earlier article in this series: <a href="/black-pipe-testing-pymongo/">"Testing PyMongo As A Black Pipe."</a></p>
<p>Since I was working in my native tongue Python, I could afford to be finicky about MockupDB's interface. I didn't want callbacks, dammit, I wanted to make something nice! As I wrote in the MockupDB article, I came up with a future-based programming interface that let me neatly interleave client and server operations in a single test function:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">from</span> <span style="color: #0000FF; font-weight: bold">mockupdb</span> <span style="color: #008000; font-weight: bold">import</span> MockupDB, Command, go
<span style="color: #008000; font-weight: bold">from</span> <span style="color: #0000FF; font-weight: bold">pymongo</span> <span style="color: #008000; font-weight: bold">import</span> MongoClient

<span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">test</span>():
   server <span style="color: #666666">=</span> MockupDB(auto_ismaster<span style="color: #666666">=</span>{<span style="color: #BA2121">&quot;maxWireVersion&quot;</span>: <span style="color: #666666">3</span>})
   server<span style="color: #666666">.</span>run()

   client <span style="color: #666666">=</span> MongoClient(server<span style="color: #666666">.</span>uri)
   collection <span style="color: #666666">=</span> client<span style="color: #666666">.</span>db<span style="color: #666666">.</span>collection

   future <span style="color: #666666">=</span> go(collection<span style="color: #666666">.</span>insert_one, {<span style="color: #BA2121">&quot;_id&quot;</span>: <span style="color: #666666">1</span>})
   request <span style="color: #666666">=</span> server<span style="color: #666666">.</span>receives(Command({<span style="color: #BA2121">&quot;insert&quot;</span>: <span style="color: #BA2121">&quot;collection&quot;</span>}))
   request<span style="color: #666666">.</span>reply({<span style="color: #BA2121">&#39;ok&#39;</span>: <span style="color: #666666">1</span>})
   <span style="color: #008000; font-weight: bold">assert</span>(future()<span style="color: #666666">.</span>inserted_id <span style="color: #666666">==</span> <span style="color: #666666">1</span>)
</pre></div>


<p>Let's break this down. I use MockupDB's <a href="http://mockupdb.readthedocs.org/reference.html#mockupdb.go"><code>go</code></a> function to start a PyMongo operation on a background thread, obtaining a handle to its future result:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">future <span style="color: #666666">=</span> go(collection<span style="color: #666666">.</span>insert_one, {<span style="color: #BA2121">&quot;_id&quot;</span>: <span style="color: #666666">1</span>})
</pre></div>


<p>The driver sends an "insert" command to the mock server and blocks waiting for the server response. I retrieve that command from the server and validate that it has the expected format:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">request <span style="color: #666666">=</span> server<span style="color: #666666">.</span>receives(Command({<span style="color: #BA2121">&quot;insert&quot;</span>: <span style="color: #BA2121">&quot;collection&quot;</span>}))
</pre></div>


<p>MockupDB asserts that the command arrives promptly and has the right format before it returns the command to me. I reply to the client, which unblocks it and lets me retrieve the future value:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">request<span style="color: #666666">.</span>reply({<span style="color: #BA2121">&#39;ok&#39;</span>: <span style="color: #666666">1</span>})
<span style="color: #008000; font-weight: bold">assert</span>(future()<span style="color: #666666">.</span>inserted_id <span style="color: #666666">==</span> <span style="color: #666666">1</span>)
</pre></div>


<h1 id="more-evolution-from-python-back-to-c">More evolution: from Python back to C</h1>
<p>Once Bernie Hackett and I <a href="/announcing-pymongo-3/">released PyMongo 3.0</a>, I devoted myself to libmongoc full-time. I set to work updating its <code>mock_server_t</code> with the ideas I had developed in Python. I wrote an example with the API I wanted:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #B00040">mock_server_t</span> <span style="color: #666666">*</span>server;
<span style="color: #B00040">mongoc_client_t</span> <span style="color: #666666">*</span>client;
<span style="color: #B00040">mongoc_collection_t</span> <span style="color: #666666">*</span>collection;
<span style="color: #B00040">bson_t</span> <span style="color: #666666">*</span>document;
<span style="color: #B00040">bson_error_t</span> error;
<span style="color: #B00040">future_t</span> <span style="color: #666666">*</span>future;
<span style="color: #B00040">request_t</span> <span style="color: #666666">*</span>request;

<span style="color: #408080; font-style: italic">/* protocol version 3 includes the new &quot;insert&quot; command */</span>
server <span style="color: #666666">=</span> mock_server_with_autoismaster (<span style="color: #666666">3</span>);
mock_server_run (server);

client <span style="color: #666666">=</span> mongoc_client_new_from_uri (mock_server_get_uri (server));
collection <span style="color: #666666">=</span> mongoc_client_get_collection (client, <span style="color: #BA2121">&quot;test&quot;</span>, <span style="color: #BA2121">&quot;collection&quot;</span>);
document <span style="color: #666666">=</span> BCON_NEW (<span style="color: #BA2121">&quot;_id&quot;</span>, BCON_INT64 (<span style="color: #666666">1</span>));
future <span style="color: #666666">=</span> future_collection_insert (collection,
                                   MONGOC_INSERT_NONE,<span style="color: #408080; font-style: italic">/* flags */</span>
                                   document,
                                   <span style="color: #008000">NULL</span>,              <span style="color: #408080; font-style: italic">/* writeConcern */</span>
                                   <span style="color: #666666">&amp;</span>error);

request <span style="color: #666666">=</span> mock_server_receives_command (server, <span style="color: #BA2121">&quot;test&quot;</span>, MONGOC_QUERY_NONE,
                                        <span style="color: #BA2121">&quot;{&#39;insert&#39;: &#39;collection&#39;}&quot;</span>);

mock_server_replies_simple (request, <span style="color: #BA2121">&quot;{&#39;ok&#39;: 1}&quot;</span>);
assert (future_get_bool (future));

future_destroy (future);
request_destroy (request);
bson_destroy (document);
mongoc_collection_destroy(collection);
mongoc_client_destroy(client);
mock_server_destroy (server);
</pre></div>


<p>Alas, C is prolix; this was as lean as I could make it. I doubt that you read that block of code. Let's focus on some key lines.</p>
<p>First, the mock server starts up and binds an unused port. Just like in Python, I connect a real client object to the mock server's URI:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">client <span style="color: #666666">=</span> mongoc_client_new_from_uri (mock_server_get_uri (server));
</pre></div>


<p>Now I insert a document. The client sends an "insert" command to the mock server, and blocks waiting for the response:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">future <span style="color: #666666">=</span> future_collection_insert (collection,
                                   MONGOC_INSERT_NONE,<span style="color: #408080; font-style: italic">/* flags */</span>
                                   document,
                                   <span style="color: #008000">NULL</span>,              <span style="color: #408080; font-style: italic">/* writeConcern */</span>
                                   <span style="color: #666666">&amp;</span>error);
</pre></div>


<p>The <code>future_collection_insert</code> function starts a background thread and runs the libmongoc function <a href="http://mongoc.org/libmongoc/current/mongoc_collection_insert.html"><code>mongoc_collection_insert</code></a>. It returns a future value, which will be resolved once the background thread completes.</p>
<p>Meanwhile, the mock server receives the client's "insert" command:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">request <span style="color: #666666">=</span> mock_server_receives_command (server,
                                        <span style="color: #BA2121">&quot;test&quot;</span>,            <span style="color: #408080; font-style: italic">/* DB name */</span>
                                        MONGOC_QUERY_NONE, <span style="color: #408080; font-style: italic">/* no flags */</span>
                                        <span style="color: #BA2121">&quot;{&#39;insert&#39;: &#39;collection&#39;}&quot;</span>);
</pre></div>


<p>This statement accomplishes several goals. First, it waits (using a condition variable) for the background thread to send the "insert" command. Second, it validates that the command has the proper format: its database name is "test", its flags are unset, the command itself is named "insert", and the target collection is named "collection".</p>
<p>The test completes when I reply to the client:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">mock_server_replies_simple (request, <span style="color: #BA2121">&quot;{&#39;ok&#39;: 1}&quot;</span>);
assert (future_get_bool (future));
</pre></div>


<p>This unblocks the background thread. The future is resolved with the return value of <code>mongoc_collection_insert</code>. I assert that its return value was <code>true</code>, meaning it succeeded. My test framework detects if <code>future_get_bool</code> stays blocked: this means <code>mongoc_collection_insert</code> is not finishing for some reason, and this too will cause my test to fail.</p>
<h1 id="conclusion">Conclusion</h1>
<p>When I first saw Christian Hergert's <code>mock_server_t</code> its brilliance inspired me: To test a MongoDB client, impersonate a MongoDB server!</p>
<p>I wrote the MockupDB package in Python, and then I overhauled Christian's mock server in C. As I developed and used this idea over the last year, I generalized it beyond the problem of testing MongoDB drivers. What I call a "black pipe test" applies to any networked application whose API behavior and network protocol must be validated simultaneously.</p>
<hr />
<p><a href="https://www.flickr.com/photos/emptysquare/855064419"><img style="display:block; margin-left:auto; margin-right:auto;" src="coney-island.jpg" alt="Coney Island / Stillwell Avenue" title="Coney Island / Stillwell Avenue" /></a></p>
