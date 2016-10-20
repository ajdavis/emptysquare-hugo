+++
type = "post"
title = "Analyzing Python C Extensions With CPyChecker"
date = "2013-08-08T12:16:38"
description = "Saves you from refcount bugs and segfaults."
category = ["Programming", "Python"]
tag = ["c"]
enable_lightbox = false
thumbnail = "cpychecker-caller.png"
draft = false
disqus_identifier = "5202ece35393741a61e9f350"
disqus_url = "https://emptysqua.re/blog/5202ece35393741a61e9f350/"
+++

<p>Writing C extension modules for Python is tricky: the programmer must manually manage reference counts and the exception state, in addition to the usual dangers of coding in C. CPyChecker is a new static checker being developed by David Malcom to rescue us from our mistakes. I was introduced to it at PyCon when Malcolm gave his <a href="http://pyvideo.org/video/1698/death-by-a-thousand-leaks-what-statically-analys">Death By A Thousand Leaks</a> talk. The tool is work in progress, buggy and hard to install, but tremendously useful in detecting coding mistakes. I'll show you how to install it and what it's good for.</p>
<hr />
<h1 id="installation">Installation</h1>
<p>CPyChecker is buried inside a general suite of extensions to GCC called the GCC Python Plugin. Its <a href="https://fedorahosted.org/gcc-python-plugin/">code and bug tracker are on fedorahosted.org</a> and <a href="https://gcc-python-plugin.readthedocs.org/en/latest/index.html">the docs are on ReadTheDocs</a>. David Malcolm calls CPyChecker itself a "usage example" of the GCC Python Plugin, and is forthright about its status:</p>
<blockquote>
<p><em>This code is under heavy development, and still contains bugs. It is not unusual to see Python tracebacks when running the checker. You should verify what the checker reports before acting on it: it could be wrong.</em></p>
</blockquote>
<p>I couldn't build the latest GCC Python Plugin on Ubuntu, so our first step is to set up a Fedora 18 box with <a href="http://www.vagrantup.com/">Vagrant</a>:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #19177C">$ </span>vagrant box add fedora-18 http://puppet-vagrant-boxes.puppetlabs.com/fedora-18-x64-vbox4210-nocm.box
<span style="color: #19177C">$ </span>vagrant init fedora-18
</pre></div>


<p>I added the following line to my Vagrantfile to share my Python virtualenv directories between the host and guest OSes:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">config<span style="color: #666666">.</span>vm<span style="color: #666666">.</span>share_folder <span style="color: #BA2121">&quot;v-data&quot;</span>, <span style="color: #BA2121">&quot;/virtualenvs&quot;</span>, <span style="color: #BA2121">&quot;/Users/emptysquare/.virtualenvs&quot;</span>
</pre></div>


<p>Now <code>vagrant up</code> and <code>vagrant ssh</code>. Once we're in Fedora, <a href="https://gcc-python-plugin.readthedocs.org/en/latest/basics.html#building-the-plugin-from-source">install the build-time dependencies according to the GCC Python Plugin instructions</a>, then get the GCC Python Plugin source and build it with <code>make</code>. (At least some of the self-tests it runs after a build always fail.)</p>
<p>I wanted to switch freely between Python 2.7 and 3.3, so I cloned the source code twice and built the plugin for both Python versions in their own checkouts.</p>
<h1 id="checks">Checks</h1>
<h2 id="refcounting-bugs">Refcounting Bugs</h2>
<p>I made <a href="https://github.com/ajdavis/modtest/blob/master/modtest.c">a little Python module in C</a> that increfs a string that shouldn't be incref'ed: </p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">static</span> PyObject<span style="color: #666666">*</span> <span style="color: #0000FF">leaky</span>(PyObject<span style="color: #666666">*</span> self, PyObject<span style="color: #666666">*</span> args) {
    PyObject <span style="color: #666666">*</span>leaked <span style="color: #666666">=</span> PyString_FromString(<span style="color: #BA2121">&quot;leak!&quot;</span>);
    Py_XINCREF(leaked);
    <span style="color: #008000; font-weight: bold">return</span> leaked;
}
</pre></div>


<p>Now I build my module, invoking CPyChecker instead of the regular compiler:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #19177C">$ CC</span><span style="color: #666666">=</span>~/gcc-python-plugin/gcc-with-cpychecker python setup.py build
</pre></div>


<p>CPyChecker spits its output into the terminal, but it's barely intelligible. The good stuff is in the HTML file it places in <code>build/temp.linux-x86_64-2.7</code>:</p>
<p><img style="display:block; margin-left:auto; margin-right:auto;" src="cpychecker-leaky.png" alt="CPyChecker: leaky()" title="CPyChecker: leaky()" /></p>
<p>CPyChecker points out that "ob_refcnt of return value is 1 too high" when <code>PyString_FromString</code> succeeds.</p>
<h2 id="null-pointers">Null Pointers</h2>
<p>It can also flag null pointer dereferences. If I replaced <code>Py_XINCREF</code> with the unsafe <code>Py_INCREF</code>, CPyChecker warns, "dereferencing NULL (p-&gt;ob_refcnt) when PyString_FromString() fails." That is, if <code>PyString_FromString</code> returned <code>NULL</code>, my program would crash.</p>
<h2 id="argument-parsing">Argument Parsing</h2>
<p>The tool notices mismatches between the format string for <code>PyArg_ParseTuple</code> and its parameters. If I have two units in the format string but pass three parameters, like this:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #B00040">int</span> i;
<span style="color: #008000; font-weight: bold">const</span> <span style="color: #B00040">char</span><span style="color: #666666">*</span> s;
<span style="color: #B00040">float</span> f;
PyArg_ParseTuple(args, <span style="color: #BA2121">&quot;is&quot;</span>, <span style="color: #666666">&amp;</span>i, <span style="color: #666666">&amp;</span>s, <span style="color: #666666">&amp;</span>f);
</pre></div>


<p>... CPyChecker warns in the console:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">warning<span style="color: #666666">:</span> Too many <span style="color: #008000; font-weight: bold">arguments</span> <span style="color: #008000; font-weight: bold">in</span> call to PyArg_ParseTuple <span style="color: #008000; font-weight: bold">with</span> format string <span style="color: #BA2121">&quot;is&quot;</span>
  expected <span style="color: #666666">2</span> extra <span style="color: #008000; font-weight: bold">arguments</span><span style="color: #666666">:</span>
    <span style="color: #BA2121">&quot;int *&quot;</span> <span style="color: #666666">(</span>pointing to <span style="color: #666666">32</span> bits<span style="color: #666666">)</span>
    <span style="color: #BA2121">&quot;const char * *&quot;</span>
  but got <span style="color: #666666">3:</span>
    <span style="color: #BA2121">&quot;int *&quot;</span> <span style="color: #666666">(</span>pointing to <span style="color: #666666">32</span> bits<span style="color: #666666">)</span>
    <span style="color: #BA2121">&quot;const char * *&quot;</span>
    <span style="color: #BA2121">&quot;float *&quot;</span> <span style="color: #666666">(</span>pointing to <span style="color: #666666">32</span> bits<span style="color: #666666">)</span>
</pre></div>


<p>For some reason this warning doesn't appear in the HTML output, only in stdout, so alas you have to monitor both places to see all the warnings.</p>
<h2 id="exception-state">Exception State</h2>
<p>CPyChecker can flag a function that returns <code>NULL</code> without setting an exception. If I hand it this code:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">static</span> PyObject<span style="color: #666666">*</span> <span style="color: #0000FF">randerr</span>(PyObject<span style="color: #666666">*</span> self, PyObject<span style="color: #666666">*</span> args) {
    PyObject <span style="color: #666666">*</span>p <span style="color: #666666">=</span> <span style="color: #008000">NULL</span>;
    <span style="color: #008000; font-weight: bold">if</span> ((<span style="color: #B00040">float</span>)rand()<span style="color: #666666">/</span>(<span style="color: #B00040">float</span>)RAND_MAX <span style="color: #666666">&gt;</span> <span style="color: #666666">0.5</span>)
        p <span style="color: #666666">=</span> PyString_FromString(<span style="color: #BA2121">&quot;foo&quot;</span>);

    <span style="color: #008000; font-weight: bold">return</span> p;
}
</pre></div>


<p>It warns about the consequences of taking the false path:</p>
<p><img style="display:block; margin-left:auto; margin-right:auto;" src="cpychecker-randerr.png" alt="CPyChecker: randerr()" title="CPyChecker: randerr()" /></p>
<p>Indeed, this code throws a <code>SystemError</code> when it returns <code>NULL</code>:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #000080; font-weight: bold">&gt;&gt;&gt; </span><span style="color: #008000; font-weight: bold">import</span> <span style="color: #0000FF; font-weight: bold">modtest</span>
<span style="color: #000080; font-weight: bold">&gt;&gt;&gt; </span>modtest<span style="color: #666666">.</span>randerr()
<span style="color: #888888">&#39;foo&#39;</span>
<span style="color: #000080; font-weight: bold">&gt;&gt;&gt; </span>modtest<span style="color: #666666">.</span>randerr()
<span style="color: #0044DD">Traceback (most recent call last):</span>
  File <span style="color: #008000">&quot;&lt;stdin&gt;&quot;</span>, line <span style="color: #666666">1</span>, in &lt;module&gt;
<span style="color: #FF0000">SystemError</span>: error return without exception set
</pre></div>


<p>Unfortunately this check is a big source of false positives. Let's say a function <code>maybe_error</code> sets the exception and returns 1 if it has an error, and returns 0 otherwise:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">static</span> <span style="color: #B00040">int</span> <span style="color: #0000FF">maybe_error</span>() {
    <span style="color: #008000; font-weight: bold">if</span> ((<span style="color: #B00040">float</span>)rand()<span style="color: #666666">/</span>(<span style="color: #B00040">float</span>)RAND_MAX <span style="color: #666666">&gt;</span> <span style="color: #666666">0.5</span>) {
        PyErr_SetString(PyExc_Exception, <span style="color: #BA2121">&quot;error&quot;</span>);
        <span style="color: #008000; font-weight: bold">return</span> <span style="color: #666666">1</span>;
    } <span style="color: #008000; font-weight: bold">else</span> {
        <span style="color: #008000; font-weight: bold">return</span> <span style="color: #666666">0</span>;
    }
}
</pre></div>


<p>Its caller knows this, so if <code>maybe_error</code> returns 1, the caller need not set the exception itself:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">static</span> PyObject<span style="color: #666666">*</span> <span style="color: #0000FF">caller</span>(PyObject<span style="color: #666666">*</span> self, PyObject<span style="color: #666666">*</span> args) {
    <span style="color: #008000; font-weight: bold">if</span> (maybe_error()) {
        <span style="color: #408080; font-style: italic">/* I know the error has been set. */</span>
        <span style="color: #008000; font-weight: bold">return</span> <span style="color: #008000">NULL</span>;
    } <span style="color: #008000; font-weight: bold">else</span> {
        <span style="color: #008000; font-weight: bold">return</span> PyString_FromString(<span style="color: #BA2121">&quot;foo&quot;</span>);
    }
}
</pre></div>


<p>This works correctly in practice:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #000080; font-weight: bold">&gt;&gt;&gt; </span>modtest<span style="color: #666666">.</span>caller()
<span style="color: #0044DD">Traceback (most recent call last):</span>
  File <span style="color: #008000">&quot;&lt;stdin&gt;&quot;</span>, line <span style="color: #666666">1</span>, in &lt;module&gt;
<span style="color: #FF0000">Exception</span>: error
<span style="color: #000080; font-weight: bold">&gt;&gt;&gt; </span>modtest<span style="color: #666666">.</span>caller()
<span style="color: #888888">&#39;foo&#39;</span>
</pre></div>


<p>But CPyChecker only analyzes code paths through a single function at a time, so it wrongly criticizes <code>caller</code> for omitting the exception:</p>
<p><img style="display:block; margin-left:auto; margin-right:auto;" src="cpychecker-caller.png" alt="CPyChecker: caller()" title="CPyChecker: caller()" /></p>
<p>The C extensions I help maintain&mdash;those for PyMongo&mdash;use this pattern in a few places, so we have persistent false positives. If CPyChecker grows up into an adult tool like Coverity that's used in CI systems, it will either need to do inter-function analysis, or have <a href="https://fedorahosted.org/gcc-python-plugin/ticket/17">a way of marking particular warnings as false positives</a>.</p>
<h1 id="conclusion">Conclusion</h1>
<p>These are early days for CPyChecker, but it's promising. With more complex functions CPyChecker starts to really shine. It clearly diagrams how different paths through the code can overcount or undercount references, dereference null pointers, and the like. It understands both the Python C API and the C stdlib quite well. I hope David Malcolm and others can polish it up into a real product soon.</p>
<hr />
<p>You might also like my article on <a href="/code-coverage-python-c-extensions/">measuring test coverage of C extensions</a>, or the one on <a href="/python-c-extensions-and-mod-wsgi/">making C extensions compatible with mod_wsgi</a>.</p>
