+++
type = "post"
title = "Test MongoDB Failure Scenarios With MockupDB"
date = "2015-11-04T09:46:01"
description = "Fourth in my \"black pipe testing\" series. How do you test your MongoDB application's reaction to database failures, hangs, and disconnects?"
category = ["C", "Mongo", "Programming", "Python"]
tag = ["black-pipe", "testing"]
enable_lightbox = false
thumbnail = "york-street-pipes@240.jpg"
draft = false
disqus_identifier = "55fa49075393742358c9c237"
disqus_url = "https://emptysqua.re/blog/55fa49075393742358c9c237/"
+++

<p><a href="https://www.flickr.com/photos/emptysquare/1528243252"><img style="display:block; margin-left:auto; margin-right:auto;" src="york-street-pipes.jpg" alt="York Street pipes" title="York Street pipes" /></a></p>
<p>This is the fifth article in <a href="/blog/black-pipe-testing-series/">my series on "black pipe" testing</a>. Traditional black box tests work well if your application takes inputs and returns output through one interface: the API. But connected applications have two interfaces: both the API and the messages they send and receive on the network. I call the validation of both ends a black pipe test.</p>
<p>In my previous article <a href="/blog/libmongoc-black-pipe-testing-mock-server/">I described black pipe testing in pure C</a>; now we return to Python.</p>
<p>I implemented a Python tool for black pipe testing called
<a href="http://mockupdb.readthedocs.org/">MockupDB</a>. It is a <a href="http://docs.mongodb.org/meta-driver/latest/legacy/mongodb-wire-protocol/">MongoDB wire protocol</a> server, built to subject PyMongo to black pipe tests. But it's not only for testing PyMongo&mdash;if you develop a MongoDB application, you can use MockupDB too. It easily simulates network errors and server failures, or it can refuse to respond at all. Such antics are nearly impossible to test reliably using a real MongoDB server, but it's easy with MockupDB.</p>
<h1 id="testing-your-own-applications-with-mockupdb">Testing Your Own Applications With MockupDB</h1>
<p>Let us say you have a Flask application that uses MongoDB. To make testing convenient, I've wrapped it in a <code>make_app</code> function:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">from</span> <span style="color: #0000FF; font-weight: bold">flask</span> <span style="color: #008000; font-weight: bold">import</span> Flask, make_response
<span style="color: #008000; font-weight: bold">from</span> <span style="color: #0000FF; font-weight: bold">pymongo</span> <span style="color: #008000; font-weight: bold">import</span> MongoClient

<span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">make_app</span>(mongodb_uri):
    app <span style="color: #666666">=</span> Flask(<span style="color: #BA2121">&quot;my app&quot;</span>)
    db <span style="color: #666666">=</span> MongoClient(mongodb_uri)

    <span style="color: #AA22FF">@app.route</span>(<span style="color: #BA2121">&quot;/pages/&lt;page_name&gt;&quot;</span>)
    <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">page</span>(page_name):
        doc <span style="color: #666666">=</span> db<span style="color: #666666">.</span>content<span style="color: #666666">.</span>pages<span style="color: #666666">.</span>find_one({<span style="color: #BA2121">&#39;name&#39;</span>: page_name})
        <span style="color: #008000; font-weight: bold">return</span> make_response(doc[<span style="color: #BA2121">&#39;contents&#39;</span>])

    <span style="color: #008000; font-weight: bold">return</span> app
</pre></div>


<p>The app has one route, which returns a page by name.</p>
<p>It is simple enough to test its fairweather conduct using a real MongoDB server, provisioned with data from a test fixture. But how can we test what happens if, for example, MongoDB shuts down in the middle of the query?</p>
<p>I have cooked up for you a test class that uses MockupDB:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">import</span> <span style="color: #0000FF; font-weight: bold">unittest</span>

<span style="color: #008000; font-weight: bold">from</span> <span style="color: #0000FF; font-weight: bold">mockupdb</span> <span style="color: #008000; font-weight: bold">import</span> go, OpQuery, MockupDB


<span style="color: #008000; font-weight: bold">class</span> <span style="color: #0000FF; font-weight: bold">MockupDBFlaskTest</span>(unittest<span style="color: #666666">.</span>TestCase):
    <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">setUp</span>(<span style="color: #008000">self</span>):
        <span style="color: #008000">self</span><span style="color: #666666">.</span>server <span style="color: #666666">=</span> MockupDB(auto_ismaster<span style="color: #666666">=</span><span style="color: #008000">True</span>)
        <span style="color: #008000">self</span><span style="color: #666666">.</span>server<span style="color: #666666">.</span>run()
        <span style="color: #008000">self</span><span style="color: #666666">.</span>app <span style="color: #666666">=</span> make_app(<span style="color: #008000">self</span><span style="color: #666666">.</span>server<span style="color: #666666">.</span>uri)<span style="color: #666666">.</span>test_client()

    <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">tearDown</span>(<span style="color: #008000">self</span>):
        <span style="color: #008000">self</span><span style="color: #666666">.</span>server<span style="color: #666666">.</span>stop()
</pre></div>


<p>(Please, Flask experts, critique me in the comments.)</p>
<p>Let me ensure this contraption works for a normal round trip:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #408080; font-style: italic"># Method of MockupDBFlaskTest.</span>
<span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">test</span>(<span style="color: #008000">self</span>):
<span style="background-color: #ffffcc">    future <span style="color: #666666">=</span> go(<span style="color: #008000">self</span><span style="color: #666666">.</span>app<span style="color: #666666">.</span>get, <span style="color: #BA2121">&quot;/pages/my_page_name&quot;</span>)
</span>    request <span style="color: #666666">=</span> <span style="color: #008000">self</span><span style="color: #666666">.</span>server<span style="color: #666666">.</span>receives(OpQuery, name<span style="color: #666666">=</span><span style="color: #BA2121">&#39;my_page_name&#39;</span>)
    request<span style="color: #666666">.</span>reply({<span style="color: #BA2121">&quot;contents&quot;</span>: <span style="color: #BA2121">&quot;foo&quot;</span>})
<span style="background-color: #ffffcc">    http_response <span style="color: #666666">=</span> future()
</span>    <span style="color: #008000">self</span><span style="color: #666666">.</span>assertEqual(<span style="color: #BA2121">&quot;foo&quot;</span>,
                     http_response<span style="color: #666666">.</span>get_data(as_text<span style="color: #666666">=</span><span style="color: #008000">True</span>))
</pre></div>


<p>We use MockupDB's function <code>go</code> to run Flask on a background thread, just like <a href="/blog/black-pipe-testing-pymongo/">we ran PyMongo operations on a background thread in an earlier article</a>. The <code>go</code> function returns a Future, which will be resolved once the background thread completes.</p>
<p>On the foreground thread, we impersonate the database server and have a conversation with the application, speaking the MongoDB wire protocol. MockupDB receives the application's query, responds with a document, and that allows Flask to finish its job and create an HTTP response. We assert the response has the expected content.</p>
<p>Now comes the payoff! We close MockupDB's connection at just the wrong instant, using its <code>hangup</code> method:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">test_hangup</span>(<span style="color: #008000">self</span>):
    future <span style="color: #666666">=</span> go(<span style="color: #008000">self</span><span style="color: #666666">.</span>app<span style="color: #666666">.</span>get, <span style="color: #BA2121">&quot;/pages/my_page_name&quot;</span>)
    request <span style="color: #666666">=</span> <span style="color: #008000">self</span><span style="color: #666666">.</span>server<span style="color: #666666">.</span>receives(OpQuery, name<span style="color: #666666">=</span><span style="color: #BA2121">&#39;my_page_name&#39;</span>)
<span style="background-color: #ffffcc">    request<span style="color: #666666">.</span>hangup()  <span style="color: #408080; font-style: italic"># Close connection.</span>
</span>    http_response <span style="color: #666666">=</span> future()
    <span style="color: #008000">self</span><span style="color: #666666">.</span>assertEqual(<span style="color: #BA2121">&quot;foo&quot;</span>,
                     http_response<span style="color: #666666">.</span>get_data(as_text<span style="color: #666666">=</span><span style="color: #008000">True</span>))
</pre></div>


<p>The test fails, as you guessed it would:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">FAIL<span style="color: #666666">:</span> test_hangup <span style="color: #666666">(</span>__main__<span style="color: #666666">.</span><span style="color: #7D9029">MockupDBFlaskTest</span><span style="color: #666666">)</span>
<span style="color: #666666">---------------------------------------------------------------------</span>
Traceback <span style="color: #666666">(</span>most recent call last<span style="color: #666666">):</span>
  File <span style="color: #BA2121">&quot;test.py&quot;</span><span style="color: #666666">,</span> line <span style="color: #666666">43,</span> <span style="color: #008000; font-weight: bold">in</span> test_hangup
    self<span style="color: #666666">.</span><span style="color: #7D9029">assertEqual</span><span style="color: #666666">(</span><span style="color: #BA2121">&quot;foo&quot;</span><span style="color: #666666">,</span> http_response<span style="color: #666666">.</span><span style="color: #7D9029">get_data</span><span style="color: #666666">(</span>as_text<span style="color: #666666">=</span>True<span style="color: #666666">))</span>
AssertionError<span style="color: #666666">:</span> <span style="color: #BA2121">&#39;foo&#39;</span> <span style="color: #666666">!=</span> <span style="color: #BA2121">&#39;&lt;html&gt;&lt;title&gt;500 Internal Server Error...&#39;</span>
</pre></div>


<p>What would we rather the application do? Let's have it respond "Closed for renovations" when it can't reach the database:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">from</span> <span style="color: #0000FF; font-weight: bold">pymongo.errors</span> <span style="color: #008000; font-weight: bold">import</span> ConnectionFailure

<span style="color: #AA22FF">@app.route</span>(<span style="color: #BA2121">&quot;/pages/&lt;page_name&gt;&quot;</span>)
<span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">page</span>(page_name):
    <span style="color: #008000; font-weight: bold">try</span>:
        doc <span style="color: #666666">=</span> db<span style="color: #666666">.</span>content<span style="color: #666666">.</span>pages<span style="color: #666666">.</span>find_one({<span style="color: #BA2121">&#39;name&#39;</span>: page_name})
<span style="background-color: #ffffcc">    <span style="color: #008000; font-weight: bold">except</span> ConnectionFailure:
</span><span style="background-color: #ffffcc">        <span style="color: #008000; font-weight: bold">return</span> make_response(<span style="color: #BA2121">&#39;Closed for renovations&#39;</span>)
</span>    <span style="color: #008000; font-weight: bold">return</span> make_response(doc[<span style="color: #BA2121">&#39;contents&#39;</span>])
</pre></div>


<p>Test the new error handling by asserting that "renovations" is in the response:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000">self</span><span style="color: #666666">.</span>assertIn(<span style="color: #BA2121">&quot;renovations&quot;</span>,
              http_response<span style="color: #666666">.</span>get_data(as_text<span style="color: #666666">=</span><span style="color: #008000">True</span>))
</pre></div>


<p>(<a href="https://gist.github.com/ajdavis/96e4c64be32fce042f10">See the complete code here</a>.)</p>
<p>And how about your connection applications? Do you continuously test them with network errors? Can you imagine how difficult this would be to test without MockupDB?</p>
<hr />
<p>Next is the thrilling conclusion: <a href="/blog/black-pipe-testing-in-summary/">generalizing black pipe testing to other applications</a>, or <a href="/blog/black-pipe-testing-series/">read the complete "black pipe" series here</a>.</p>
