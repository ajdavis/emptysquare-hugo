+++
type = "post"
title = "Let Us Now Praise ResourceWarnings"
date = "2014-07-14T15:46:41"
description = "I used to hate Python 3's ResourceWarnings, until one saved my tuchus."
category = ["Mongo", "Motor", "Programming", "Python"]
tag = ["python3"]
enable_lightbox = false
thumbnail = "Poisonous_snake_warning_sign@240.JPG"
draft = false
disqus_identifier = "53c422a65393741fc5e7eed3"
disqus_url = "https://emptysqua.re/blog/53c422a65393741fc5e7eed3/"
+++

<p><img style="display:block; margin-left:auto; margin-right:auto;" src="Poisonous_snake_warning_sign.JPG" alt="Poisonous snake warning sign" title="Poisonous snake warning sign" /></p>
<p><a href="http://commons.wikimedia.org/wiki/File:Poisonous_snake_warning_sign.JPG"><span style="color:gray">[Source]</span></a></p>
<p>Luckily, Pythons aren't poisonous.</p>
<p>A couple years ago when I began using Python 3, <a href="/blog/against-resourcewarnings-in-python-3/">its new ResourceWarnings infuriated me and I ranted against them</a>. Python core developer Nick Coghlan patiently corrected me, and I wrote a followup, <a href="/blog/mollified-about-resourcewarnings/">"Mollified About ResourceWarnings"</a>.</p>
<p>And now, a ResourceWarning has saved my tuchus.</p>
<p>A few months ago I was fixing a bug in Motor, my asynchronous driver for MongoDB. Motor has a <code>copy_database</code> method which I'll summarize thus:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #AA22FF">@gen.coroutine</span>
<span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">copy_database</span>(<span style="color: #008000">self</span>, source, target):
    pool, socket <span style="color: #666666">=</span> <span style="color: #008000">None</span>, <span style="color: #008000">None</span>
    <span style="color: #008000; font-weight: bold">try</span>:
        pool <span style="color: #666666">=</span> <span style="color: #008000">self</span><span style="color: #666666">.</span>get_pool()
<span style="background-color: #ffffcc">        socket <span style="color: #666666">=</span> pool<span style="color: #666666">.</span>get_socket()
</span>        <span style="color: #408080; font-style: italic"># ... several operations with the socket ...</span>
    <span style="color: #008000; font-weight: bold">finally</span>:
        <span style="color: #008000; font-weight: bold">if</span> pool <span style="color: #AA22FF; font-weight: bold">and</span> socket:
            pool<span style="color: #666666">.</span>return_socket(socket)
</pre></div>


<p>The bug occurred when the source database was password-protected. The <code>get_socket</code> call didn't ensure it was authenticated before it attempted to copy the database. I fixed the bug like so:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #AA22FF">@gen.coroutine</span>
<span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">copy_database</span>(<span style="color: #008000">self</span>, source, target):
    pool, socket <span style="color: #666666">=</span> <span style="color: #008000">None</span>, <span style="color: #008000">None</span>
    <span style="color: #008000; font-weight: bold">try</span>:
        member <span style="color: #666666">=</span> <span style="color: #008000">self</span><span style="color: #666666">.</span>get_cluster_member()
<span style="background-color: #ffffcc">        socket <span style="color: #666666">=</span> <span style="color: #008000">self</span><span style="color: #666666">.</span>get_authenticated_socket_from_member(member)
</span>        <span style="color: #408080; font-style: italic"># ... several operations with the socket ...</span>
    <span style="color: #008000; font-weight: bold">finally</span>:
        <span style="color: #008000; font-weight: bold">if</span> pool <span style="color: #AA22FF; font-weight: bold">and</span> socket:
            pool<span style="color: #666666">.</span>return_socket(socket)
</pre></div>


<p>Whoops. I fixed the authentication bug, but introduced a socket leak. Since <code>pool</code> is now always <code>None</code>, the code in the <code>finally</code> clause never runs. In this example the bug is obvious, but the real method is 60 lines long&mdash;just long enough for me not to see the mismatch between its first and final lines.</p>
<p>I blithely released the bug in Motor 0.2.</p>
<p>Apparently my users don't call <code>copy_database</code> much, since no one reported the socket leak. I'm not surprised: Motor is optimized for high-concurrency web applications, not for administrative scripts that copy databases around. If you want to copy a database you'd use the regular driver, PyMongo, instead. And so the bug lurked for three months.</p>
<p>This weekend I teased Motor apart, into two modules: a "core" module that talks to MongoDB, and a "framework" module that uses <a href="http://www.tornadoweb.org/">Tornado</a> for asynchronous I/O. Once I had separated the two aspects of Motor, I made a second "framework" module that uses <a href="https://docs.python.org/3/library/asyncio.html">Python 3.4's new asyncio framework</a> instead of Tornado. <code>copy_database</code> was among the first methods I tested in the new Motor-on-asyncio. It's relatively complex so I used it to give my new code a workout.</p>
<p><code>copy_database</code> worked with asyncio! But I wasn't ready to celebrate yet:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">ResourceWarning<span style="color: #666666">:</span> unclosed <span style="color: #666666">&lt;</span>socket<span style="color: #666666">.</span><span style="color: #7D9029">socket</span> fd<span style="color: #666666">=9,</span> laddr<span style="color: #666666">=(</span><span style="color: #BA2121">&#39;127.0.0.1&#39;</span><span style="color: #666666">,</span> <span style="color: #666666">54065),</span> raddr<span style="color: #666666">=(</span><span style="color: #BA2121">&#39;127.0.0.1&#39;</span><span style="color: #666666">,</span> <span style="color: #666666">27017)&gt;</span>
</pre></div>


<p>That damn ResourceWarning. I did a bit of binary-searching through my test code until I found it: I wasn't returning the socket in <code>copy_database</code>. The fix is obvious:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #AA22FF">@gen.coroutine</span>
<span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">copy_database</span>(<span style="color: #008000">self</span>, source, target):
<span style="background-color: #ffffcc">    member, socket <span style="color: #666666">=</span> <span style="color: #008000">None</span>, <span style="color: #008000">None</span>
</span>    <span style="color: #008000; font-weight: bold">try</span>:
        member <span style="color: #666666">=</span> <span style="color: #008000">self</span><span style="color: #666666">.</span>get_cluster_member()
        socket <span style="color: #666666">=</span> <span style="color: #008000">self</span><span style="color: #666666">.</span>get_authenticated_socket_from_member(member)
        <span style="color: #408080; font-style: italic"># ... several operations with the socket ...</span>
    <span style="color: #008000; font-weight: bold">finally</span>:
        <span style="color: #008000; font-weight: bold">if</span> socket:
<span style="background-color: #ffffcc">            member<span style="color: #666666">.</span>pool<span style="color: #666666">.</span>return_socket(socket)
</span></pre></div>


<p><a href="/blog/motor-0-3-2-released/">I've released this fix today in Motor 0.3.2</a>.</p>
<p>One lesson learned is: I was foolish when I made my code "robust" against unexpected conditions. The earlier code had returned the socket <code>if pool and socket</code>. But if <code>socket</code> isn't null, <code>pool</code> shouldn't be, either. So <code>if socket</code> alone should be sufficient. This simpler code, that only handles the case I expect to arise, would have failed immediately when I introduced the bug. The misguided robustness of my earlier code masked my bug for months.</p>
<p>Another lesson is: I finally understand the value of ResourceWarnings. They force me to decide when costly objects are deallocated, and they warn me if I mess it up. I'm reviewing my test procedures to ensure that ResourceWarnings are displayed. Ideally, a ResourceWarning should be converted to an exception that causes my unittests to fail. Do you know how to make that happen?</p>
