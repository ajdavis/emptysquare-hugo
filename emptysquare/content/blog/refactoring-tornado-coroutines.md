+++
type = "post"
title = "Refactoring Tornado Coroutines"
date = "2014-06-17T09:30:04"
description = "Asynchronous Python is more flexible than blocking code, but you need to follow a few rules."
"blog/category" = ["Mongo", "Motor", "Programming", "Python"]
"blog/tag" = ["tornado"]
enable_lightbox = false
thumbnail = "tornado-noaa@240.jpg"
draft = false
+++

<p><img style="display:block; margin-left:auto; margin-right:auto;" src="tornado-noaa.jpg" alt="Tornado" title="Tornado" />
<a href="http://es.wikipedia.org/wiki/Flujo_ciclostr%C3%B3fico#mediaviewer/Archivo:Tornado0_-_NOAA.jpg"><span style="color:gray">[Source]</span></a></p>
<p>Sometimes writing callback-style asynchronous code with <a href="http://www.tornadoweb.org/">Tornado</a> is a pain. But the real hurt comes when you want to refactor your async code into reusable subroutines. Tornado's <a href="http://www.tornadoweb.org/en/stable/gen.html#tornado.gen.coroutine">coroutines</a> make refactoring easy. I'll explain the rules.</p>
<p>(This article updates my old "Refactoring Tornado Code With gen.engine". The updated code here demonstrates the current syntax for Tornado 3 and <a href="http://motor.readthedocs.org/">Motor 0.3</a>.)</p>
<h1 id="for-example">For Example</h1>
<p>I'll use this blog to illustrate. I built it with <a href="https://github.com/ajdavis/motor-blog">Motor-Blog</a>, a trivial blog platform on top of <a href="http://motor.readthedocs.org/">Motor</a>, my asynchronous MongoDB driver for Tornado.</p>
<p>When you came here, Motor-Blog did three or four MongoDB queries to render this page.</p>
<p><strong>1</strong>: Find the blog post at this URL and show you this content.</p>
<p><strong>2 and 3</strong>: Find the next and previous posts to render the navigation links at the bottom.</p>
<p><strong>Maybe 4</strong>: If the list of categories on the left has changed since it was last cached, fetch the list.</p>
<p>Let's go through each query and see how Tornado coroutines make life easier.</p>
<h1 id="fetching-one-post">Fetching One Post</h1>
<p>In Tornado, fetching one post takes a little more work than with blocking-style code:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">db <span style="color: #666666">=</span> motor<span style="color: #666666">.</span>MotorClient()<span style="color: #666666">.</span>my_blog_db

<span style="color: #008000; font-weight: bold">class</span> <span style="color: #0000FF; font-weight: bold">PostHandler</span>(tornado<span style="color: #666666">.</span>web<span style="color: #666666">.</span>RequestHandler):
    <span style="color: #AA22FF">@tornado.asynchronous</span>
    <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">get</span>(<span style="color: #008000">self</span>, slug):
        db<span style="color: #666666">.</span>posts<span style="color: #666666">.</span>find_one({<span style="color: #BA2121">&#39;slug&#39;</span>: slug}, callback<span style="color: #666666">=</span><span style="color: #008000">self</span><span style="color: #666666">.</span>_found_post)

    <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">_found_post</span>(<span style="color: #008000">self</span>, post, error):
        <span style="color: #008000; font-weight: bold">if</span> error:
            <span style="color: #008000; font-weight: bold">raise</span> tornado<span style="color: #666666">.</span>web<span style="color: #666666">.</span>HTTPError(<span style="color: #666666">500</span>, <span style="color: #008000">str</span>(error))
        <span style="color: #008000; font-weight: bold">elif</span> <span style="color: #AA22FF; font-weight: bold">not</span> post:
            <span style="color: #008000; font-weight: bold">raise</span> tornado<span style="color: #666666">.</span>web<span style="color: #666666">.</span>HTTPError(<span style="color: #666666">404</span>)
        <span style="color: #008000; font-weight: bold">else</span>:
            <span style="color: #008000">self</span><span style="color: #666666">.</span>render(<span style="color: #BA2121">&#39;post.html&#39;</span>, post<span style="color: #666666">=</span>post)
</pre></div>


<p>Not so bad. But is it better with a coroutine?</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">class</span> <span style="color: #0000FF; font-weight: bold">PostHandler</span>(tornado<span style="color: #666666">.</span>web<span style="color: #666666">.</span>RequestHandler):
    <span style="color: #AA22FF">@gen.coroutine</span>
    <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">get</span>(<span style="color: #008000">self</span>, slug):
        post <span style="color: #666666">=</span> <span style="color: #008000; font-weight: bold">yield</span> db<span style="color: #666666">.</span>posts<span style="color: #666666">.</span>find_one({<span style="color: #BA2121">&#39;slug&#39;</span>: slug})
        <span style="color: #008000; font-weight: bold">if</span> <span style="color: #AA22FF; font-weight: bold">not</span> post:
            <span style="color: #008000; font-weight: bold">raise</span> tornado<span style="color: #666666">.</span>web<span style="color: #666666">.</span>HTTPError(<span style="color: #666666">404</span>)

        <span style="color: #008000">self</span><span style="color: #666666">.</span>render(<span style="color: #BA2121">&#39;post.html&#39;</span>, post<span style="color: #666666">=</span>post)
</pre></div>


<p>Much better. If you don't pass a callback to <code>find_one</code>, then it returns a Future instance. A Future is nothing special, it's just a little
object that represents an unresolved value. Some time hence, Motor will resolve the Future with a value or an exception. To wait for the Future
to be resolved, yield it.</p>
<p>The <code>yield</code> statement makes this function a <a href="http://www.python.org/dev/peps/pep-0342/">generator</a>.
<code>gen.coroutine</code> is a brilliant invention that runs the generator until it's complete.
Each time the generator yields a Future, <code>gen.coroutine</code> schedules the generator
to be resumed when the Future is resolved. Read the
<a href="https://github.com/tornadoweb/tornado/blob/v3.2.2/tornado/gen.py#L467">source
code of the <code>Runner</code> class</a> for details, it's exhilarating. Or just
enjoy the glow of putting all your logic in a single function again, without
defining any callbacks.</p>
<p>Even better, you get normal exception handling: if <code>find_one</code> gets a network error or some other failure, it raises an exception. Tornado knows how to turn an exception into an HTTP 500, so we no longer need special code for errors.</p>
<p>This coroutine is much more readable than a callback, but it doesn't look any nicer than multithreaded code.
It will start to shine when you need to parallelize some tasks.</p>
<h1 id="fetching-next-and-previous">Fetching Next And Previous</h1>
<p>Once Motor-Blog finds the current post, it gets the next and previous posts so it can display their titles. Since the two
queries are independent we can save a few milliseconds by doing them in parallel.
How does this look with callbacks?</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #AA22FF">@tornado.asynchronous</span>
<span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">get</span>(<span style="color: #008000">self</span>, slug):
    db<span style="color: #666666">.</span>posts<span style="color: #666666">.</span>find_one({<span style="color: #BA2121">&#39;slug&#39;</span>: slug}, callback<span style="color: #666666">=</span><span style="color: #008000">self</span><span style="color: #666666">.</span>_found_post)

<span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">_found_post</span>(<span style="color: #008000">self</span>, post, error):
    <span style="color: #008000; font-weight: bold">if</span> error:
        <span style="color: #008000; font-weight: bold">raise</span> tornado<span style="color: #666666">.</span>web<span style="color: #666666">.</span>HTTPError(<span style="color: #666666">500</span>, <span style="color: #008000">str</span>(error))
    <span style="color: #008000; font-weight: bold">elif</span> <span style="color: #AA22FF; font-weight: bold">not</span> post:
        <span style="color: #008000; font-weight: bold">raise</span> tornado<span style="color: #666666">.</span>web<span style="color: #666666">.</span>HTTPError(<span style="color: #666666">404</span>)
    <span style="color: #008000; font-weight: bold">else</span>:
        _id <span style="color: #666666">=</span> post[<span style="color: #BA2121">&#39;_id&#39;</span>]
        <span style="color: #008000">self</span><span style="color: #666666">.</span>post <span style="color: #666666">=</span> post

        <span style="color: #408080; font-style: italic"># Two queries in parallel.</span>
        <span style="color: #408080; font-style: italic"># Find the previously published post.</span>
        db<span style="color: #666666">.</span>posts<span style="color: #666666">.</span>find_one(
            {<span style="color: #BA2121">&#39;pub_date&#39;</span>: {<span style="color: #BA2121">&#39;$lt&#39;</span>: post[<span style="color: #BA2121">&#39;pub_date&#39;</span>]}}
            sort<span style="color: #666666">=</span>[(<span style="color: #BA2121">&#39;pub_date&#39;</span>, <span style="color: #666666">-1</span>)],
            callback<span style="color: #666666">=</span><span style="color: #008000">self</span><span style="color: #666666">.</span>_found_prev)

        <span style="color: #408080; font-style: italic"># Find subsequently published post.</span>
        db<span style="color: #666666">.</span>posts<span style="color: #666666">.</span>find_one(
            {<span style="color: #BA2121">&#39;pub_date&#39;</span>: {<span style="color: #BA2121">&#39;$gt&#39;</span>: post[<span style="color: #BA2121">&#39;pub_date&#39;</span>]}}
            sort<span style="color: #666666">=</span>[(<span style="color: #BA2121">&#39;pub_date&#39;</span>, <span style="color: #666666">1</span>)],
            callback<span style="color: #666666">=</span><span style="color: #008000">self</span><span style="color: #666666">.</span>_found_next)

<span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">_found_prev</span>(<span style="color: #008000">self</span>, prev_post, error):
    <span style="color: #008000; font-weight: bold">if</span> error:
        <span style="color: #008000; font-weight: bold">raise</span> tornado<span style="color: #666666">.</span>web<span style="color: #666666">.</span>HTTPError(<span style="color: #666666">500</span>, <span style="color: #008000">str</span>(error))
    <span style="color: #008000; font-weight: bold">else</span>:
        <span style="color: #008000">self</span><span style="color: #666666">.</span>prev_post <span style="color: #666666">=</span> prev_post
        <span style="color: #008000; font-weight: bold">if</span> <span style="color: #008000">self</span><span style="color: #666666">.</span>next_post:
            <span style="color: #408080; font-style: italic"># Done</span>
            <span style="color: #008000">self</span><span style="color: #666666">.</span>_render()

<span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">_found_next</span>(<span style="color: #008000">self</span>, next_post, error):
    <span style="color: #008000; font-weight: bold">if</span> error:
        <span style="color: #008000; font-weight: bold">raise</span> tornado<span style="color: #666666">.</span>web<span style="color: #666666">.</span>HTTPError(<span style="color: #666666">500</span>, <span style="color: #008000">str</span>(error))
    <span style="color: #008000; font-weight: bold">else</span>:
        <span style="color: #008000">self</span><span style="color: #666666">.</span>next_post <span style="color: #666666">=</span> next_post
        <span style="color: #008000; font-weight: bold">if</span> <span style="color: #008000">self</span><span style="color: #666666">.</span>prev_post:
            <span style="color: #408080; font-style: italic"># Done</span>
            <span style="color: #008000">self</span><span style="color: #666666">.</span>_render()

<span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">_render</span>(<span style="color: #008000">self</span>)
    <span style="color: #008000">self</span><span style="color: #666666">.</span>render(
        <span style="color: #BA2121">&#39;post.html&#39;</span>,
        post<span style="color: #666666">=</span><span style="color: #008000">self</span><span style="color: #666666">.</span>post,
        prev_post<span style="color: #666666">=</span><span style="color: #008000">self</span><span style="color: #666666">.</span>prev_post,
        next_post<span style="color: #666666">=</span><span style="color: #008000">self</span><span style="color: #666666">.</span>next_post)
</pre></div>


<p>This is completely disgusting and it makes me want to give up on async.
We need special logic in each callback to determine if the other callback has already run or not.
All that boilerplate can't be factored out. Will a coroutine help?</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #AA22FF">@gen.coroutine</span>
<span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">get</span>(<span style="color: #008000">self</span>, slug):
    post <span style="color: #666666">=</span> <span style="color: #008000; font-weight: bold">yield</span> db<span style="color: #666666">.</span>posts<span style="color: #666666">.</span>find_one({<span style="color: #BA2121">&#39;slug&#39;</span>: slug})
    <span style="color: #008000; font-weight: bold">if</span> <span style="color: #AA22FF; font-weight: bold">not</span> post:
        <span style="color: #008000; font-weight: bold">raise</span> tornado<span style="color: #666666">.</span>web<span style="color: #666666">.</span>HTTPError(<span style="color: #666666">404</span>)
    <span style="color: #008000; font-weight: bold">else</span>:
        future_0 <span style="color: #666666">=</span> db<span style="color: #666666">.</span>posts<span style="color: #666666">.</span>find_one(
            {<span style="color: #BA2121">&#39;pub_date&#39;</span>: {<span style="color: #BA2121">&#39;$lt&#39;</span>: post[<span style="color: #BA2121">&#39;pub_date&#39;</span>]}}
            sort<span style="color: #666666">=</span>[(<span style="color: #BA2121">&#39;pub_date&#39;</span>, <span style="color: #666666">-1</span>)])

        future_1 <span style="color: #666666">=</span> db<span style="color: #666666">.</span>posts<span style="color: #666666">.</span>find_one(
            {<span style="color: #BA2121">&#39;pub_date&#39;</span>: {<span style="color: #BA2121">&#39;$gt&#39;</span>: post[<span style="color: #BA2121">&#39;pub_date&#39;</span>]}}
            sort<span style="color: #666666">=</span>[(<span style="color: #BA2121">&#39;pub_date&#39;</span>, <span style="color: #666666">1</span>)])

        prev_post, next_post <span style="color: #666666">=</span> <span style="color: #008000; font-weight: bold">yield</span> [future_0, future_1]
        <span style="color: #008000">self</span><span style="color: #666666">.</span>render(
            <span style="color: #BA2121">&#39;post.html&#39;</span>,
            post<span style="color: #666666">=</span>post,
            prev_post<span style="color: #666666">=</span>prev_post,
            next_post<span style="color: #666666">=</span>next_post)
</pre></div>


<p>Yielding a list of Futures tells the coroutine to wait until they are all resolved.</p>
<p>Now our single <code>get</code> function is just as nice as it would be with blocking code.
In fact, the parallel fetch is far easier than if you were multithreading instead of using Tornado.
But what about factoring out a common subroutine that request handlers can share?</p>
<h1 id="fetching-categories">Fetching Categories</h1>
<p>Every page on my blog needs to show the category list on the left side. Each request handler could just include
this in its <code>get</code> method:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">categories <span style="color: #666666">=</span> <span style="color: #008000; font-weight: bold">yield</span> db<span style="color: #666666">.</span>categories<span style="color: #666666">.</span>find()<span style="color: #666666">.</span>sort(<span style="color: #BA2121">&#39;name&#39;</span>)<span style="color: #666666">.</span>to_list(<span style="color: #666666">10</span>)
</pre></div>


<p>But that's terrible engineering. Here's how to factor it into a coroutine:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #AA22FF">@gen.coroutine</span>
<span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">get_categories</span>(db):
    categories <span style="color: #666666">=</span> <span style="color: #008000; font-weight: bold">yield</span> db<span style="color: #666666">.</span>categories<span style="color: #666666">.</span>find()<span style="color: #666666">.</span>sort(<span style="color: #BA2121">&#39;name&#39;</span>)<span style="color: #666666">.</span>to_list(<span style="color: #666666">10</span>)
    <span style="color: #008000; font-weight: bold">raise</span> gen<span style="color: #666666">.</span>Return(categories)
</pre></div>


<p>This coroutine does <strong>not</strong> have to be part of a request handler&mdash;it stands on its own at the module scope.</p>
<p>The <code>raise gen.Return()</code> statement is the weirdest syntax in this example. It's an artifact of Python 2, in which generators aren't allowed to return values. To hack around this limitation, Tornado coroutines raise a special kind of exception called a <code>Return</code>. The coroutine catches this exception and treats it like a returned value. In Python 3, a simple <code>return categories</code> accomplishes the same result.</p>
<p>To call my new coroutine from a request handler, I do:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">class</span> <span style="color: #0000FF; font-weight: bold">PostHandler</span>(tornado<span style="color: #666666">.</span>web<span style="color: #666666">.</span>RequestHandler):
    <span style="color: #AA22FF">@gen.coroutine</span>
    <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">get</span>(<span style="color: #008000">self</span>, slug):
        categories <span style="color: #666666">=</span> <span style="color: #008000; font-weight: bold">yield</span> get_categories(db)
        <span style="color: #408080; font-style: italic"># ... get the current, previous, and</span>
        <span style="color: #408080; font-style: italic"># next posts as usual, then ...</span>
        <span style="color: #008000">self</span><span style="color: #666666">.</span>render(
            <span style="color: #BA2121">&#39;post.html&#39;</span>,
            post<span style="color: #666666">=</span>post,
            prev_post<span style="color: #666666">=</span>prev_post,
            next_post<span style="color: #666666">=</span>next_post,
            categories<span style="color: #666666">=</span>categories)
</pre></div>


<p>Since <code>get_categories</code> is a coroutine now, calling it returns a Future.
To wait for <code>get_categories</code> to complete, the caller can yield the Future.
Once <code>get_categories</code> completes, the Future it returned is resolved,
so the caller resumes.
It's almost like a regular function call!</p>
<p>Now that I've factored out <code>get_categories</code>, it's easy to add more logic to it. This is nice because I want to cache the categories between page
views. <code>get_categories</code> can be updated very simply to use a cache:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">categories <span style="color: #666666">=</span> <span style="color: #008000">None</span>

<span style="color: #AA22FF">@gen.coroutine</span>
<span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">get_categories</span>(db):
    <span style="color: #008000; font-weight: bold">global</span> categories
    <span style="color: #008000; font-weight: bold">if</span> <span style="color: #AA22FF; font-weight: bold">not</span> categories:
        categories <span style="color: #666666">=</span> <span style="color: #008000; font-weight: bold">yield</span> db<span style="color: #666666">.</span>categories<span style="color: #666666">.</span>find()<span style="color: #666666">.</span>sort(<span style="color: #BA2121">&#39;name&#39;</span>)<span style="color: #666666">.</span>to_list(<span style="color: #666666">10</span>)

    <span style="color: #008000; font-weight: bold">raise</span> gen<span style="color: #666666">.</span>Return(categories)
</pre></div>


<p>(Note for nerds: I invalidate the cache whenever a post with a new
category is added. The "new category" event is saved to a
<a href="http://www.mongodb.org/display/DOCS/Capped+Collections">capped collection</a>
in MongoDB, which all the Tornado servers are always tailing.
This is a simple way to use MongoDB as an event queue, which the multiple Tornado processes use to communicate with each other.)</p>
<h1 id="conclusion">Conclusion</h1>
<p>Tornado's <a href="http://www.tornadoweb.org/en/stable/gen.html">excellent documentation</a>
shows briefly how a method that makes a few async calls can be
simplified using <code>gen.coroutine</code>, but the power really comes when you need to
factor out a common subroutine. There are only three steps:</p>
<ol>
<li>Decorate the subroutine with <code>@gen.coroutine</code>.</li>
<li>In Python 2, the subroutine returns its result with <code>raise gen.Return(result)</code>.</li>
<li>Call the subroutine from another coroutine like <code>result = yield subroutine()</code>.</li>
</ol>
<p>That's all there is to it. Tornado's coroutines make asynchronous code efficient, clean&mdash;even beautiful.</p>
    