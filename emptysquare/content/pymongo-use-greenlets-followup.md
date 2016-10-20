+++
type = "post"
title = "PyMongo's \"use_greenlets\" Followup"
date = "2015-03-15T22:29:53"
description = "I wrote in December that we were removing a quirky feature from PyMongo. Here's how my conversation went with a critic."
category = ["Mongo", "Programming", "Python"]
tag = ["gevent", "pymongo"]
enable_lightbox = false
thumbnail = "fern.jpg"
draft = false
disqus_identifier = "550634af539374097d8896b1"
disqus_url = "https://emptysqua.re/blog/550634af539374097d8896b1/"
+++

<p><img style="display:block; margin-left:auto; margin-right:auto;" src="fern.jpg" alt="Fern - (cc) Wingchi Poon" title="Fern - (cc) Wingchi Poon" /></p>
<p>In December, I wrote that <a href="/it-seemed-like-a-good-idea-at-the-time-pymongo-use-greenlets/">we are removing the idiosyncratic <code>use_greenlets</code> option from PyMongo</a> when we release <a href="/pymongo-3-beta/">PyMongo 3</a>.</p>
<p>In PyMongo 2 you have two options for using Gevent. First, you can do:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">from</span> <span style="color: #0000FF; font-weight: bold">gevent</span> <span style="color: #008000; font-weight: bold">import</span> monkey; monkey<span style="color: #666666">.</span>patch_all()
<span style="color: #008000; font-weight: bold">from</span> <span style="color: #0000FF; font-weight: bold">pymongo</span> <span style="color: #008000; font-weight: bold">import</span> MongoClient

client <span style="color: #666666">=</span> MongoClient()
</pre></div>


<p>Or:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">from</span> <span style="color: #0000FF; font-weight: bold">gevent</span> <span style="color: #008000; font-weight: bold">import</span> monkey; monkey<span style="color: #666666">.</span>patch_socket()
<span style="color: #008000; font-weight: bold">from</span> <span style="color: #0000FF; font-weight: bold">pymongo</span> <span style="color: #008000; font-weight: bold">import</span> MongoClient

client <span style="color: #666666">=</span> MongoClient(use_greenlets<span style="color: #666666">=</span><span style="color: #008000">True</span>)
</pre></div>


<p>In the latter case, I wrote, "you could use PyMongo after calling Gevent's <code>patch_socket</code> without having to call <code>patch_thread</code>. But who would do that? What conceivable use case had I enabled?" So I removed <code>use_greenlets</code> in PyMongo 3; the first example code continues to work but the second will not.</p>
<p>In the comments, PyMongo user Peter Hansen replied,</p>
<blockquote>
<p>I hope you're not saying that the only way this will work is if one uses <code>monkey.patch_all</code>, because, although this is a very common way to use Gevent, it's absolutely not the only way. (If it were, it would just be done automatically!) We have a large Gevent application here which cannot do that, because threads must be allowed to continue working as regular threads, but we monkey patch only what we need which happens to be everything else (with <code>monkey.patch_all(thread=False)</code>).</p>
</blockquote>
<p>So Peter, Bernie, and I met online and he told us about his <em>very</em> interesting application. It needs to interface with some C code that talks an obscure network protocol; to get the best of both worlds his Python code uses asynchronous Gevent in the main thread, and it avoids blocking the event loop by launching Python threads to talk with the C extension. Peter had, in fact, perfectly understood PyMongo 2's design and was using it as intended. It was I who hadn't understood the feature's use case before I diked it out.</p>
<p>So what now? I would be sad to lose the great simplifications I achieved in PyMongo by removing its Gevent-specific code. Besides, occasional complaints from Eventlet and other communities motivated us to support all frameworks equally.</p>
<p>Luckily, Gevent 1.0 provides a workaround for the loss of <code>use_greenlets</code> in PyMongo. Beginning the same as the first example above:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">from</span> <span style="color: #0000FF; font-weight: bold">gevent</span> <span style="color: #008000; font-weight: bold">import</span> monkey; monkey<span style="color: #666666">.</span>patch_all()
<span style="color: #008000; font-weight: bold">from</span> <span style="color: #0000FF; font-weight: bold">pymongo</span> <span style="color: #008000; font-weight: bold">import</span> MongoClient

client <span style="color: #666666">=</span> MongoClient()


<span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">my_function</span>():
    <span style="color: #408080; font-style: italic"># Call some C code that drops the GIL and does</span>
    <span style="color: #408080; font-style: italic"># blocking I/O from C directly.</span>
    <span style="color: #008000; font-weight: bold">pass</span>

start_new_thread <span style="color: #666666">=</span> monkey<span style="color: #666666">.</span>saved[<span style="color: #BA2121">&#39;thread&#39;</span>][<span style="color: #BA2121">&#39;start_new_thread&#39;</span>]
real_thread <span style="color: #666666">=</span> start_new_thread(my_function, ())
</pre></div>


<p>I <a href="https://groups.google.com/d/topic/gevent/pTT_89I3B08/discussion">checked with Gevent's author Denis Bilenko</a> whether <code>monkey.saved</code> was a stable API and he confirmed it is. If you use Gevent and PyMongo as Peter does, port your code to this technique when you upgrade to PyMongo 3.</p>
<p><a href="http://commons.wikimedia.org/wiki/File:Unfurling_Spiral_Fiddlehead_Fern_Frond.JPG#/media/File:Unfurling_Spiral_Fiddlehead_Fern_Frond.JPG"><span style="color:gray">Image: Wingchi Poon, CC BY-SA 3.0</span></a></p>
