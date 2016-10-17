+++
type = "post"
title = "Undoing Gevent's monkey-patching"
date = "2012-04-05T15:23:08"
description = ""
"blog/category" = ["Programming", "Python"]
"blog/tag" = ["gevent", "unittest"]
enable_lightbox = false
draft = false
+++

<h1 id="update">Update</h1>
<p>I'm a genius: simply executing <code>reload(socket)</code> undoes Gevent's
<code>patch_socket()</code>. Obviously, this only applies to new sockets created
after executing <code>reload</code>, but that's good enough for my unittests. The
dumb solution below is preserved for hysterical porpoises.</p>
<h1 id="prior">Prior</h1>
<p>I ran into an odd problem while testing the next release of PyMongo, the
Python driver for MongoDB which I help develop. We're improving its
support for <a href="http://www.gevent.org/">Gevent</a>, so we're of course doing
additional tests that begin with:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">from</span> <span style="color: #0000FF; font-weight: bold">gevent</span> <span style="color: #008000; font-weight: bold">import</span> monkey; monkey<span style="color: #666666">.</span>patch_socket()
</pre></div>


<p>Now, some tests rely on this patching, and some rely on <strong>not</strong> being
patched. Gevent doesn't provide an <code>unpatch_socket</code>, so I had a clever
idea: I'll fork a subprocess with
<a href="http://docs.python.org/library/multiprocessing.html">multiprocessing</a>,
do the test there, and return its result to the parent process in a
<code>multiprocessing.Value</code>. Then subsequent tests won't be affected by the
patching.</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">SUCCESS <span style="color: #666666">=</span> <span style="color: #666666">1</span>
FAILURE <span style="color: #666666">=</span> <span style="color: #666666">0</span>

<span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">my_test</span>(outcome):
    <span style="color: #008000; font-weight: bold">from</span> <span style="color: #0000FF; font-weight: bold">gevent</span> <span style="color: #008000; font-weight: bold">import</span> monkey; monkey<span style="color: #666666">.</span>patch_socket()
    <span style="color: #408080; font-style: italic"># do the test ....</span>
    outcome<span style="color: #666666">.</span>value <span style="color: #666666">=</span> SUCCESS

<span style="color: #008000; font-weight: bold">class</span> <span style="color: #0000FF; font-weight: bold">Test</span>(unittest<span style="color: #666666">.</span>TestCase):
    <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">test</span>(<span style="color: #008000">self</span>):
        outcome <span style="color: #666666">=</span> multiprocessing<span style="color: #666666">.</span>Value(<span style="color: #BA2121">&#39;i&#39;</span>, FAILURE)
        multiprocessing<span style="color: #666666">.</span>Process(
            target<span style="color: #666666">=</span>my_test,
            args<span style="color: #666666">=</span>(outcome,)
        )<span style="color: #666666">.</span>start()<span style="color: #666666">.</span>join()

        <span style="color: #008000">self</span><span style="color: #666666">.</span>assertEqual(SUCCESS, outcome<span style="color: #666666">.</span>value)
</pre></div>


<p>Nice and straightforward, right? In sane operating systems this worked
great. On Windows it broke horribly. When I did <code>python setup.py test</code>,
instead of executing <code>my_test()</code>, multiprocessing on Windows restarted
the whole test suite, which started another whole test suite, ...
Apparently, since Windows can't <code>fork()</code>, multiprocessing re-imports
your script and attempts to execute the proper function within it. If
the test suite is begun with <code>python setup.py test</code>, then everything
goes haywire. This <a href="http://mail.python.org/pipermail/python-list/2011-February/1266451.html">problem with multiprocessing and unittests on
Windows</a>
was discussed on the Python mailing list last February.</p>
<p>After some gloomy minutes, I decided to look at what <code>patch_socket()</code> is
doing. Turns out it's simple, so I wrote a version which allows
unpatching:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">patch_socket</span>(aggressive<span style="color: #666666">=</span><span style="color: #008000">True</span>):
    <span style="color: #BA2121; font-style: italic">&quot;&quot;&quot;Like gevent.monkey.patch_socket(), but stores old socket attributes</span>
<span style="color: #BA2121; font-style: italic">    for unpatching.</span>
<span style="color: #BA2121; font-style: italic">    &quot;&quot;&quot;</span>
    <span style="color: #008000; font-weight: bold">from</span> <span style="color: #0000FF; font-weight: bold">gevent</span> <span style="color: #008000; font-weight: bold">import</span> socket
    _socket <span style="color: #666666">=</span> <span style="color: #008000">__import__</span>(<span style="color: #BA2121">&#39;socket&#39;</span>)

    old_attrs <span style="color: #666666">=</span> {}
    <span style="color: #008000; font-weight: bold">for</span> attr <span style="color: #AA22FF; font-weight: bold">in</span> (
        <span style="color: #BA2121">&#39;socket&#39;</span>, <span style="color: #BA2121">&#39;SocketType&#39;</span>, <span style="color: #BA2121">&#39;create_connection&#39;</span>, <span style="color: #BA2121">&#39;socketpair&#39;</span>, <span style="color: #BA2121">&#39;fromfd&#39;</span>
    ):
        <span style="color: #008000; font-weight: bold">if</span> <span style="color: #008000">hasattr</span>(_socket, attr):
            old_attrs[attr] <span style="color: #666666">=</span> <span style="color: #008000">getattr</span>(_socket, attr)
            <span style="color: #008000">setattr</span>(_socket, attr, <span style="color: #008000">getattr</span>(socket, attr))

    <span style="color: #008000; font-weight: bold">try</span>:
        <span style="color: #008000; font-weight: bold">from</span> <span style="color: #0000FF; font-weight: bold">gevent.socket</span> <span style="color: #008000; font-weight: bold">import</span> ssl, sslerror
        old_attrs[<span style="color: #BA2121">&#39;ssl&#39;</span>] <span style="color: #666666">=</span> _socket<span style="color: #666666">.</span>ssl
        _socket<span style="color: #666666">.</span>ssl <span style="color: #666666">=</span> ssl
        old_attrs[<span style="color: #BA2121">&#39;sslerror&#39;</span>] <span style="color: #666666">=</span> _socket<span style="color: #666666">.</span>sslerror
        _socket<span style="color: #666666">.</span>sslerror <span style="color: #666666">=</span> sslerror
    <span style="color: #008000; font-weight: bold">except</span> <span style="color: #D2413A; font-weight: bold">ImportError</span>:
        <span style="color: #008000; font-weight: bold">if</span> aggressive:
            <span style="color: #008000; font-weight: bold">try</span>:
                <span style="color: #008000; font-weight: bold">del</span> _socket<span style="color: #666666">.</span>ssl
            <span style="color: #008000; font-weight: bold">except</span> <span style="color: #D2413A; font-weight: bold">AttributeError</span>:
                <span style="color: #008000; font-weight: bold">pass</span>

    <span style="color: #008000; font-weight: bold">return</span> old_attrs


<span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">unpatch_socket</span>(old_attrs):
    <span style="color: #BA2121; font-style: italic">&quot;&quot;&quot;Take output of patch_socket() and undo patching.&quot;&quot;&quot;</span>
    _socket <span style="color: #666666">=</span> <span style="color: #008000">__import__</span>(<span style="color: #BA2121">&#39;socket&#39;</span>)

    <span style="color: #008000; font-weight: bold">for</span> attr <span style="color: #AA22FF; font-weight: bold">in</span> old_attrs:
        <span style="color: #008000; font-weight: bold">if</span> <span style="color: #008000">hasattr</span>(_socket, attr):
            <span style="color: #008000">setattr</span>(_socket, attr, old_attrs[attr])


<span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">patch_dns</span>():
    <span style="color: #BA2121; font-style: italic">&quot;&quot;&quot;Like gevent.monkey.patch_dns(), but stores old socket attributes</span>
<span style="color: #BA2121; font-style: italic">    for unpatching.</span>
<span style="color: #BA2121; font-style: italic">    &quot;&quot;&quot;</span>
    <span style="color: #008000; font-weight: bold">from</span> <span style="color: #0000FF; font-weight: bold">gevent.socket</span> <span style="color: #008000; font-weight: bold">import</span> gethostbyname, getaddrinfo
    _socket <span style="color: #666666">=</span> <span style="color: #008000">__import__</span>(<span style="color: #BA2121">&#39;socket&#39;</span>)

    old_attrs <span style="color: #666666">=</span> {}
    old_attrs[<span style="color: #BA2121">&#39;getaddrinfo&#39;</span>] <span style="color: #666666">=</span> _socket<span style="color: #666666">.</span>getaddrinfo
    _socket<span style="color: #666666">.</span>getaddrinfo <span style="color: #666666">=</span> getaddrinfo
    old_attrs[<span style="color: #BA2121">&#39;gethostbyname&#39;</span>] <span style="color: #666666">=</span> _socket<span style="color: #666666">.</span>gethostbyname
    _socket<span style="color: #666666">.</span>gethostbyname <span style="color: #666666">=</span> gethostbyname

    <span style="color: #008000; font-weight: bold">return</span> old_attrs


<span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">unpatch_dns</span>(old_attrs):
    <span style="color: #BA2121; font-style: italic">&quot;&quot;&quot;Take output of patch_dns() and undo patching.&quot;&quot;&quot;</span>
    _socket <span style="color: #666666">=</span> <span style="color: #008000">__import__</span>(<span style="color: #BA2121">&#39;socket&#39;</span>)

    <span style="color: #008000; font-weight: bold">for</span> attr <span style="color: #AA22FF; font-weight: bold">in</span> old_attrs:
        <span style="color: #008000">setattr</span>(_socket, attr, old_attrs[attr])
</pre></div>


<p>In Gevent's version, calling <code>patch_socket()</code> calls <code>patch_dns()</code>
implicitly, in mine you must call both:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">class</span> <span style="color: #0000FF; font-weight: bold">Test</span>(unittest<span style="color: #666666">.</span>TestCase):
    <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">test</span>(<span style="color: #008000">self</span>):
        old_socket_attrs <span style="color: #666666">=</span> patch_socket()
        old_dns_attrs <span style="color: #666666">=</span> patch_dns()

        <span style="color: #008000; font-weight: bold">try</span>:
            <span style="color: #408080; font-style: italic"># do test ...</span>
        <span style="color: #008000; font-weight: bold">finally</span>:
            unpatch_dns(old_dns_attrs)
            unpatch_socket(old_socket_attrs)
</pre></div>


<p>Now I don't need multiprocessing at all.</p>
    