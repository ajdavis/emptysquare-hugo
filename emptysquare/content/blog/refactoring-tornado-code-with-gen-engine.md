+++
type = "post"
title = "Refactoring Tornado Code With gen.engine"
date = "2012-07-11T02:37:35"
description = ""
categories = ["Mongo", "Motor", "Programming", "Python"]
tags = ["tornado"]
enable_lightbox = false
draft = false
+++

<p>Sometimes writing callback-style asynchronous code with <a href="http://www.tornadoweb.org/">Tornado</a> is a pain. But the real hurt comes when you want to refactor your async code into reusable subroutines. Tornado's <a href="http://www.tornadoweb.org/en/latest/gen.html">gen</a> module makes refactoring easy, but you need to learn a few tricks first.</p>
<h1 id="for-example">For Example</h1>
<p>I'll use this blog to illustrate. I built it with <a href="https://github.com/ajdavis/motor-blog">Motor-Blog</a>, a trivial blog platform on top of <a href="/motor/">Motor</a>, my new driver for Tornado and <a href="http://www.mongodb.org/">MongoDB</a>.</p>
<p>When you came here, Motor-Blog did three or four MongoDB queries to render this page.</p>
<p><strong>1</strong>: Find the blog post at this URL and show you this content.</p>
<p><strong>2 and 3</strong>: Find the next and previous posts to render the navigation links at the bottom.</p>
<p><strong>Maybe 4</strong>: If the list of categories on the left has changed since it was last cached, fetch the list.</p>
<p>Let's go through each query and see how the <code>tornado.gen</code> module makes life easier.</p>
<h1 id="fetching-one-post">Fetching One Post</h1>
<p>In Tornado, fetching one post takes a little more work than with blocking-style code:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">db <span style="color: #666666">=</span> motor<span style="color: #666666">.</span>MotorConnection()<span style="color: #666666">.</span>open_sync()<span style="color: #666666">.</span>my_blog_db

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


<p>Not so bad. But is it better with <code>gen</code>?</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">class</span> <span style="color: #0000FF; font-weight: bold">PostHandler</span>(tornado<span style="color: #666666">.</span>web<span style="color: #666666">.</span>RequestHandler):
    <span style="color: #AA22FF">@tornado.asynchronous</span>
    <span style="color: #AA22FF">@gen.engine</span>
    <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">get</span>(<span style="color: #008000">self</span>, slug):
        post, error <span style="color: #666666">=</span> <span style="color: #008000; font-weight: bold">yield</span> gen<span style="color: #666666">.</span>Task(
            db<span style="color: #666666">.</span>posts<span style="color: #666666">.</span>find_one, {<span style="color: #BA2121">&#39;slug&#39;</span>: slug})

        <span style="color: #008000; font-weight: bold">if</span> error:
            <span style="color: #008000; font-weight: bold">raise</span> tornado<span style="color: #666666">.</span>web<span style="color: #666666">.</span>HTTPError(<span style="color: #666666">500</span>, <span style="color: #008000">str</span>(error))
        <span style="color: #008000; font-weight: bold">elif</span> <span style="color: #AA22FF; font-weight: bold">not</span> post:
            <span style="color: #008000; font-weight: bold">raise</span> tornado<span style="color: #666666">.</span>web<span style="color: #666666">.</span>HTTPError(<span style="color: #666666">404</span>)
        <span style="color: #008000; font-weight: bold">else</span>:
            <span style="color: #008000">self</span><span style="color: #666666">.</span>render(<span style="color: #BA2121">&#39;post.html&#39;</span>, post<span style="color: #666666">=</span>post)
</pre></div>


<p>A little better. The <code>yield</code> statement makes this function a <a href="http://www.python.org/dev/peps/pep-0342/">generator</a>.
<code>gen.engine</code> is a brilliant hack which runs the generator until it's complete.
Each time the generator yields a <code>Task</code>, <code>gen.engine</code> schedules the generator
to be resumed when the task is complete. Read the
<a href="https://github.com/facebook/tornado/blob/master/tornado/gen.py#L304">source
code of the <code>Runner</code> class</a> for details, it's exhilarating. Or just
enjoy the glow of putting all your logic in a single function again, without
defining any callbacks.</p>
<p>Motor includes a subclass of <code>gen.Task</code> called <code>motor.Op</code>. It handles checking and raising the exception for you, so the above can be simplified further:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #AA22FF">@tornado.asynchronous</span>
<span style="color: #AA22FF">@gen.engine</span>
<span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">get</span>(<span style="color: #008000">self</span>, slug):
    post <span style="color: #666666">=</span> <span style="color: #008000; font-weight: bold">yield</span> motor<span style="color: #666666">.</span>Op(
        db<span style="color: #666666">.</span>posts<span style="color: #666666">.</span>find_one, {<span style="color: #BA2121">&#39;slug&#39;</span>: slug})  
    <span style="color: #008000; font-weight: bold">if</span> <span style="color: #AA22FF; font-weight: bold">not</span> post:
        <span style="color: #008000; font-weight: bold">raise</span> tornado<span style="color: #666666">.</span>web<span style="color: #666666">.</span>HTTPError(<span style="color: #666666">404</span>)
    <span style="color: #008000; font-weight: bold">else</span>:
        <span style="color: #008000">self</span><span style="color: #666666">.</span>render(<span style="color: #BA2121">&#39;post.html&#39;</span>, post<span style="color: #666666">=</span>post)
</pre></div>


<p>Still, no huge gains. <code>gen</code> starts to shine when you need to parallelize some tasks.</p>
<h1 id="fetching-next-and-previous">Fetching Next And Previous</h1>
<p>Once Motor-Blog finds the current post, it gets the next and previous posts. Since the two
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

        <span style="color: #408080; font-style: italic"># Two queries in parallel</span>
        db<span style="color: #666666">.</span>posts<span style="color: #666666">.</span>find_one({<span style="color: #BA2121">&#39;_id&#39;</span>: {<span style="color: #BA2121">&#39;$lt&#39;</span>: _id}},
            callback<span style="color: #666666">=</span><span style="color: #008000">self</span><span style="color: #666666">.</span>_found_prev)
        db<span style="color: #666666">.</span>posts<span style="color: #666666">.</span>find_one({<span style="color: #BA2121">&#39;_id&#39;</span>: {<span style="color: #BA2121">&#39;$gt&#39;</span>: _id}},
            callback<span style="color: #666666">=</span><span style="color: #008000">self</span><span style="color: #666666">.</span>_found_next)

<span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">_found_prev</span>(<span style="color: #008000">self</span>, prev, error):
    <span style="color: #008000; font-weight: bold">if</span> error:
        <span style="color: #008000; font-weight: bold">raise</span> tornado<span style="color: #666666">.</span>web<span style="color: #666666">.</span>HTTPError(<span style="color: #666666">500</span>, <span style="color: #008000">str</span>(error))
    <span style="color: #008000; font-weight: bold">else</span>:
        <span style="color: #008000">self</span><span style="color: #666666">.</span>prev <span style="color: #666666">=</span> prev
        <span style="color: #008000; font-weight: bold">if</span> <span style="color: #008000">self</span><span style="color: #666666">.</span>next:
            <span style="color: #408080; font-style: italic"># Done</span>
            <span style="color: #008000">self</span><span style="color: #666666">.</span>_render()

<span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">_found_next</span>(<span style="color: #008000">self</span>, <span style="color: #008000">next</span>, error):
    <span style="color: #008000; font-weight: bold">if</span> error:
        <span style="color: #008000; font-weight: bold">raise</span> tornado<span style="color: #666666">.</span>web<span style="color: #666666">.</span>HTTPError(<span style="color: #666666">500</span>, <span style="color: #008000">str</span>(error))
    <span style="color: #008000; font-weight: bold">else</span>:
        <span style="color: #008000">self</span><span style="color: #666666">.</span>next <span style="color: #666666">=</span> <span style="color: #008000">next</span>
        <span style="color: #008000; font-weight: bold">if</span> <span style="color: #008000">self</span><span style="color: #666666">.</span>prev:
            <span style="color: #408080; font-style: italic"># Done</span>
            <span style="color: #008000">self</span><span style="color: #666666">.</span>_render()

<span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">_render</span>(<span style="color: #008000">self</span>)
    <span style="color: #008000">self</span><span style="color: #666666">.</span>render(<span style="color: #BA2121">&#39;post.html&#39;</span>,
        post<span style="color: #666666">=</span><span style="color: #008000">self</span><span style="color: #666666">.</span>post, prev<span style="color: #666666">=</span><span style="color: #008000">self</span><span style="color: #666666">.</span>prev, <span style="color: #008000">next</span><span style="color: #666666">=</span><span style="color: #008000">self</span><span style="color: #666666">.</span>next)
</pre></div>


<p>This is completely disgusting and it makes me want to give up on Tornado.
All that boilerplate can't be factored out. Will <code>gen</code> help?</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #AA22FF">@tornado.asynchronous</span>
<span style="color: #AA22FF">@gen.engine</span>
<span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">get</span>(<span style="color: #008000">self</span>, slug):
    post, error <span style="color: #666666">=</span> <span style="color: #008000; font-weight: bold">yield</span> motor<span style="color: #666666">.</span>Op(
        db<span style="color: #666666">.</span>posts<span style="color: #666666">.</span>find_one, {<span style="color: #BA2121">&#39;slug&#39;</span>: slug})
    <span style="color: #008000; font-weight: bold">if</span> <span style="color: #AA22FF; font-weight: bold">not</span> post:
        <span style="color: #008000; font-weight: bold">raise</span> tornado<span style="color: #666666">.</span>web<span style="color: #666666">.</span>HTTPError(<span style="color: #666666">404</span>)
    <span style="color: #008000; font-weight: bold">else</span>:
        prev, <span style="color: #008000">next</span> <span style="color: #666666">=</span> <span style="color: #008000; font-weight: bold">yield</span> [
            motor<span style="color: #666666">.</span>Op(db<span style="color: #666666">.</span>posts<span style="color: #666666">.</span>find_one, {<span style="color: #BA2121">&#39;_id&#39;</span>: {<span style="color: #BA2121">&#39;$lt&#39;</span>: _id}}),
            motor<span style="color: #666666">.</span>Op(db<span style="color: #666666">.</span>posts<span style="color: #666666">.</span>find_one, {<span style="color: #BA2121">&#39;_id&#39;</span>: {<span style="color: #BA2121">&#39;$gt&#39;</span>: _id}})]

        <span style="color: #008000">self</span><span style="color: #666666">.</span>render(<span style="color: #BA2121">&#39;post.html&#39;</span>, post<span style="color: #666666">=</span>post, prev<span style="color: #666666">=</span>prev, <span style="color: #008000">next</span><span style="color: #666666">=</span><span style="color: #008000">next</span>)
</pre></div>


<p>Now our single <code>get</code> function is just as nice as it would be with blocking code.
In fact, the parallel fetch is far easier than if you were multithreading instead of using Tornado.
But what about factoring out a common subroutine that request handlers can share?</p>
<h1 id="fetching-categories">Fetching Categories</h1>
<p>Every page on my blog needs to show the category list on the left side. Each request handler could just include
this in its <code>get</code> method:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">categories <span style="color: #666666">=</span> <span style="color: #008000; font-weight: bold">yield</span> motor<span style="color: #666666">.</span>Op(
    db<span style="color: #666666">.</span>categories<span style="color: #666666">.</span>find()<span style="color: #666666">.</span>sort(<span style="color: #BA2121">&#39;name&#39;</span>)<span style="color: #666666">.</span>to_list)
</pre></div>


<p>But that's terrible engineering. Here's how to factor it into a subroutine with <code>gen</code>:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #AA22FF">@gen.engine</span>
<span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">get_categories</span>(db, callback):
    <span style="color: #008000; font-weight: bold">try</span>:
        categories <span style="color: #666666">=</span> <span style="color: #008000; font-weight: bold">yield</span> motor<span style="color: #666666">.</span>Op(
            db<span style="color: #666666">.</span>categories<span style="color: #666666">.</span>find()<span style="color: #666666">.</span>sort(<span style="color: #BA2121">&#39;name&#39;</span>)<span style="color: #666666">.</span>to_list)
    <span style="color: #008000; font-weight: bold">except</span> <span style="color: #D2413A; font-weight: bold">Exception</span>, e:
        callback(<span style="color: #008000">None</span>, e)
        <span style="color: #008000; font-weight: bold">return</span>

    callback(categories, <span style="color: #008000">None</span>)
</pre></div>


<p>This function does <strong>not</strong> have to be part of a request handler&mdash;it stands on its own at the module scope.
To call it from a request handler, do:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">class</span> <span style="color: #0000FF; font-weight: bold">PostHandler</span>(tornado<span style="color: #666666">.</span>web<span style="color: #666666">.</span>RequestHandler):
    <span style="color: #AA22FF">@tornado.asynchronous</span>
    <span style="color: #AA22FF">@gen.engine</span>
    <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">get</span>(<span style="color: #008000">self</span>, slug):
<span style="background-color: #ffffcc">        categories <span style="color: #666666">=</span> <span style="color: #008000; font-weight: bold">yield</span> motor<span style="color: #666666">.</span>Op(get_categories)
</span>        <span style="color: #408080; font-style: italic"># ... get the current, previous, and next posts as usual, then ...</span>
        <span style="color: #008000">self</span><span style="color: #666666">.</span>render(<span style="color: #BA2121">&#39;post.html&#39;</span>,
            post<span style="color: #666666">=</span>post, prev<span style="color: #666666">=</span>prev, <span style="color: #008000">next</span><span style="color: #666666">=</span><span style="color: #008000">next</span>, categories<span style="color: #666666">=</span>categories)
</pre></div>


<p><code>gen.engine</code> runs <code>get</code> until it yields <code>get_categories</code>, then a
separate engine runs <code>get_categories</code> until it calls the callback, which
resumes <code>get</code>. It's almost like a regular function call!</p>
<p>This is particularly nice because I want to cache the categories between page
views. <code>get_categories</code> can be updated very simply to use a cache:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">egories <span style="color: #666666">=</span> <span style="color: #008000">None</span>
<span style="color: #AA22FF">@gen.engine</span>
<span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">get_categories</span>(db, callback):
    <span style="color: #008000; font-weight: bold">global</span> categories
    <span style="color: #008000; font-weight: bold">if</span> <span style="color: #AA22FF; font-weight: bold">not</span> categories:
        <span style="color: #008000; font-weight: bold">try</span>:
            categories <span style="color: #666666">=</span> <span style="color: #008000; font-weight: bold">yield</span> motor<span style="color: #666666">.</span>Op(
                db<span style="color: #666666">.</span>categories<span style="color: #666666">.</span>find()<span style="color: #666666">.</span>sort(<span style="color: #BA2121">&#39;name&#39;</span>)<span style="color: #666666">.</span>to_list)
        <span style="color: #008000; font-weight: bold">except</span> <span style="color: #D2413A; font-weight: bold">Exception</span>, e:
            callback(<span style="color: #008000">None</span>, e)
            <span style="color: #008000; font-weight: bold">return</span>

    callback(categories, <span style="color: #008000">None</span>)
</pre></div>


<p>(Note for nerds: I invalidate the cache whenever a post with a never-before-seen
category is added. The "new category" signal is saved to a
<a href="http://www.mongodb.org/display/DOCS/Capped+Collections">capped collection</a>
in MongoDB, which all the Tornado servers are always tailing. That'll be the
subject of a future post.)</p>
<h1 id="conclusion">Conclusion</h1>
<p>The <code>gen</code> module's <a href="http://www.tornadoweb.org/en/latest/gen.html">excellent documentation</a>
shows briefly how a method that makes a few async calls can be
simplified using <code>gen.engine</code>, but the power really comes when you need to
factor out a common subroutine. It's not obvious how to do that at first, but
there are only three steps:</p>
<p><strong>1.</strong> Decorate the subroutine with <code>@gen.engine</code>.</p>
<p><strong>2.</strong> Make the subroutine take a callback argument (it <strong>must</strong> be called <code>callback</code>),
to which the subroutine will pass its results when finished.</p>
<p><strong>3.</strong> Call the subroutine within an engine-decorated function like:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">result <span style="color: #666666">=</span> <span style="color: #008000; font-weight: bold">yield</span> gen<span style="color: #666666">.</span>Task(subroutine)
</pre></div>


<p><code>result</code> contains the value or values that <code>subroutine</code> passed to the callback.</p>
<p>If you follow Motor's convention where every callback takes arguments
<code>(result, error)</code>, then you can use <code>motor.Op</code> to deal with the exception:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">result <span style="color: #666666">=</span> <span style="color: #008000; font-weight: bold">yield</span> motor<span style="color: #666666">.</span>Op(subroutine)
</pre></div>
    