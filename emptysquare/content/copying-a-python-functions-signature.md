+++
type = "post"
title = "Copying A Python Function's Signature"
date = "2012-06-18T22:37:09"
description = "A supplement to functools.wraps."
category = ["Programming", "Python"]
tag = []
enable_lightbox = false
thumbnail = "john-hancock-sig@240.png"
draft = false
disqus_identifier = "644 http://emptysquare.net/blog/?p=644"
disqus_url = "https://emptysqua.re/blog/644 http://emptysquare.net/blog/?p=644/"
+++

<p><img style="display:block; margin-left:auto; margin-right:auto;" src="john-hancock-sig.png" title="John Hancock's signature" /></p>
<p>Like all Python programmers, I'm writing a minimal blogging platform. In
my particular case, I'm building my blog using Tornado, MongoDB, and an
experimental MongoDB driver I wrote, which I'll announce soon. Rather
than build an admin UI where I can create, edit, and delete blog posts,
I rely on <a href="http://www.red-sweater.com/marsedit/">MarsEdit</a>. My blog
simply implements the portion of the metaWeblog XML-RPC API that
MarsEdit uses. To implement this API I use Josh Marshall's excellent
<a href="https://github.com/joshmarshall/tornadorpc">Tornado-RPC</a> package.</p>
<p>With Tornado-RPC, I declare my particular handlers (e.g., the
<code>metaWeblog.getRecentPosts</code> handler), and Tornado-RPC introspects my
methods' signatures to check if they're receiving the right arguments at
run time:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">args, varargs, varkw, defaults <span style="color: #666666">=</span> inspect<span style="color: #666666">.</span>getargspec(func)
</pre></div>


<p>This is fantastic. But my XML-RPC handlers tend to all have similar
signatures:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">metaWeblog_newPost</span>(<span style="color: #008000">self</span>, blogid, user, password, struct, publish):
    <span style="color: #008000; font-weight: bold">pass</span>

<span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">metaWeblog_editPost</span>(<span style="color: #008000">self</span>, postid, user, password, struct, publish):
    <span style="color: #008000; font-weight: bold">pass</span>

<span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">metaWeblog_getPost</span>(<span style="color: #008000">self</span>, postid, user, password):
    <span style="color: #008000; font-weight: bold">pass</span>
</pre></div>


<p>I want to check that the user and password are correct in each handler
method, without duplicating a ton of code. The obvious approach is a
decorator:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #AA22FF">@auth</span>
<span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">metaWeblog_newPost</span>(<span style="color: #008000">self</span>, blogid, user, password, struct, publish):
    <span style="color: #008000; font-weight: bold">pass</span>

<span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">auth</span>(fn):
    argspec <span style="color: #666666">=</span> inspect<span style="color: #666666">.</span>getargspec(fn)

    <span style="color: #AA22FF">@functools.wraps</span>(fn)
    <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">_auth</span>(<span style="color: #666666">*</span>args, <span style="color: #666666">**</span>kwargs):
        <span style="color: #008000">self</span> <span style="color: #666666">=</span> args[<span style="color: #666666">0</span>]
        user <span style="color: #666666">=</span> args[argspec<span style="color: #666666">.</span>args<span style="color: #666666">.</span>index(<span style="color: #BA2121">&#39;user&#39;</span>)]
        password <span style="color: #666666">=</span> args[argspec<span style="color: #666666">.</span>args<span style="color: #666666">.</span>index(<span style="color: #BA2121">&#39;password&#39;</span>)]
        <span style="color: #008000; font-weight: bold">if</span> <span style="color: #AA22FF; font-weight: bold">not</span> check_authentication(user, password):
            <span style="color: #008000">self</span><span style="color: #666666">.</span>result(xmlrpclib<span style="color: #666666">.</span>Fault(
                <span style="color: #666666">403</span>, <span style="color: #BA2121">&#39;Bad login/pass combination.&#39;</span>))
        <span style="color: #008000; font-weight: bold">else</span>:
            <span style="color: #008000; font-weight: bold">return</span> fn(<span style="color: #666666">*</span>args, <span style="color: #666666">**</span>kwargs)

    <span style="color: #008000; font-weight: bold">return</span> _auth
</pre></div>


<p>Simple enough, right? My decorated method checks the user and password,
and either returns an authentication fault, or executes the wrapped
method.</p>
<p>Problem is, a simple <code>functools.wraps()</code> isn't enough to fool
Tornado-RPC when it inspects my handler methods' signatures using
<code>inspect.getargspec()</code>. <code>functools.wraps()</code> can change a wrapper's
module, name, docstring, and __dict__ to the wrapped function's
values, but it doesn't change the wrapper's actual method signature.</p>
<p>Inspired by <a href="http://www.voidspace.org.uk/python/mock/">Mock</a>, I found
this solution:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">auth</span>(fn):
    argspec <span style="color: #666666">=</span> inspect<span style="color: #666666">.</span>getargspec(fn)

    <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">_auth</span>(<span style="color: #666666">*</span>args, <span style="color: #666666">**</span>kwargs):
        user <span style="color: #666666">=</span> args[argspec<span style="color: #666666">.</span>args<span style="color: #666666">.</span>index(<span style="color: #BA2121">&#39;user&#39;</span>)]
        password <span style="color: #666666">=</span> args[argspec<span style="color: #666666">.</span>args<span style="color: #666666">.</span>index(<span style="color: #BA2121">&#39;password&#39;</span>)]
        <span style="color: #008000; font-weight: bold">if</span> <span style="color: #AA22FF; font-weight: bold">not</span> check_authentication(user, password):
            <span style="color: #008000">self</span><span style="color: #666666">.</span>result(xmlrpclib<span style="color: #666666">.</span>Fault(<span style="color: #666666">403</span>, <span style="color: #BA2121">&#39;Bad login/pass combination.&#39;</span>))
        <span style="color: #008000; font-weight: bold">else</span>:
            <span style="color: #008000; font-weight: bold">return</span> fn(<span style="color: #666666">*</span>args, <span style="color: #666666">**</span>kwargs)

    <span style="color: #408080; font-style: italic"># For tornadorpc to think _auth has the same arguments as fn,</span>
    <span style="color: #408080; font-style: italic"># functools.wraps() isn&#39;t enough.</span>
    formatted_args <span style="color: #666666">=</span> inspect<span style="color: #666666">.</span>formatargspec(<span style="color: #666666">*</span>argspec)
    fndef <span style="color: #666666">=</span> <span style="color: #BA2121">&#39;lambda </span><span style="color: #BB6688; font-weight: bold">%s</span><span style="color: #BA2121">: _auth</span><span style="color: #BB6688; font-weight: bold">%s</span><span style="color: #BA2121">&#39;</span> <span style="color: #666666">%</span> (
        formatted_args<span style="color: #666666">.</span>lstrip(<span style="color: #BA2121">&#39;(&#39;</span>)<span style="color: #666666">.</span>rstrip(<span style="color: #BA2121">&#39;)&#39;</span>), formatted_args)

    fake_fn <span style="color: #666666">=</span> <span style="color: #008000">eval</span>(fndef, {<span style="color: #BA2121">&#39;_auth&#39;</span>: _auth})
    <span style="color: #008000; font-weight: bold">return</span> functools<span style="color: #666666">.</span>wraps(fn)(fake_fn)
</pre></div>


<p>Yes, <code>eval</code> is evil. But for this case, it's the only way to create a
new wrapper function with the same signature as the wrapped function. My
decorator formats a string like:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">    <span style="color: #008000; font-weight: bold">lambda</span> <span style="color: #008000">self</span>, blogid, user, password, struct, publish:\
        _auth(<span style="color: #008000">self</span>, blogid, user, password, struct, publish)
</pre></div>


<p>And evals it to create a lambda. This lambda is the final wrapper. It's
what the <code>@auth</code> decorator returns in lieu of the wrapped function. Now
when Tornado-RPC does <code>inspect.getargspec()</code> on the wrapped function to
check its arguments, it thinks the wrapper has the proper method
signature.</p>
