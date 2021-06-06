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
<hr/>
<h1 id="installation">Installation</h1>
<p>CPyChecker is buried inside a general suite of extensions to GCC called the GCC Python Plugin. Its <a href="https://github.com/davidmalcolm/gcc-python-plugin">code and bug tracker are on GitHub</a> and <a href="https://gcc-python-plugin.readthedocs.org/en/latest/index.html">the docs are on ReadTheDocs</a>. David Malcolm calls CPyChecker itself a "usage example" of the GCC Python Plugin, and is forthright about its status:</p>
<blockquote>
<p><em>This code is under heavy development, and still contains bugs. It is not unusual to see Python tracebacks when running the checker. You should verify what the checker reports before acting on it: it could be wrong.</em></p>
</blockquote>
<p>I couldn't build the latest GCC Python Plugin on Ubuntu, so our first step is to set up a Fedora 18 box with <a href="http://www.vagrantup.com/">Vagrant</a>:</p>

```
$ vagrant box add fedora-18 http://puppet-vagrant-boxes.puppetlabs.com/fedora-18-x64-vbox4210-nocm.box
$ vagrant init fedora-18
```

<p>I added the following line to my Vagrantfile to share my Python virtualenv directories between the host and guest OSes:</p>

```
config.vm.synced_folder "/Users/emptysquare/.virtualenvs", "/virtualenvs"
```

<p>Now <code>vagrant up</code> and <code>vagrant ssh</code>. Once we're in Fedora, <a href="https://gcc-python-plugin.readthedocs.org/en/latest/basics.html#building-the-plugin-from-source">install the build-time dependencies according to the GCC Python Plugin instructions</a>, then get the GCC Python Plugin source and build it with <code>make</code>. (At least some of the self-tests it runs after a build always fail.)</p>
<p>I wanted to switch freely between Python 2.7 and 3.3, so I cloned the source code twice and built the plugin for both Python versions in their own checkouts.</p>
<h1 id="checks">Checks</h1>
<h2 id="refcounting-bugs">Refcounting Bugs</h2>
<p>I made <a href="https://github.com/ajdavis/modtest/blob/master/modtest.c">a little Python module in C</a> that increfs a string that shouldn't be incref'ed: </p>

{{<highlight c>}}
static PyObject* leaky(PyObject* self, PyObject* args) {
    PyObject *leaked = PyString_FromString("leak!");
    Py_XINCREF(leaked);
    return leaked;
}
{{< / highlight >}}

<p>Now I build my module, invoking CPyChecker instead of the regular compiler:</p>

```
$ CC=/usr/bin/gcc-with-cpychecker python setup.py build
```

<p>CPyChecker spits its output into the terminal, but it's barely intelligible. The good stuff is in the HTML file it places in <code>build/temp.linux-x86_64-2.7</code>:</p>
<p><img alt="CPyChecker: leaky()" src="cpychecker-leaky.png" style="display:block; margin-left:auto; margin-right:auto;" title="CPyChecker: leaky()"/></p>
<p>CPyChecker points out that "ob_refcnt of return value is 1 too high" when <code>PyString_FromString</code> succeeds.</p>
<h2 id="null-pointers">Null Pointers</h2>
<p>It can also flag null pointer dereferences. If I replaced <code>Py_XINCREF</code> with the unsafe <code>Py_INCREF</code>, CPyChecker warns, "dereferencing NULL (p->ob_refcnt) when PyString_FromString() fails." That is, if <code>PyString_FromString</code> returned <code>NULL</code>, my program would crash.</p>
<h2 id="argument-parsing">Argument Parsing</h2>
<p>The tool notices mismatches between the format string for <code>PyArg_ParseTuple</code> and its parameters. If I have two units in the format string but pass three parameters, like this:</p>

{{<highlight c>}}
int i;
const char* s;
float f;
PyArg_ParseTuple(args, "is", &i, &s, &f);
{{< / highlight >}}

<p>... CPyChecker warns in the console:</p>

{{<highlight plain>}}
warning: Too many arguments in call to PyArg_ParseTuple with format string "is"
  expected 2 extra arguments:
    "int *" (pointing to 32 bits)
    "const char * *"
  but got 3:
    "int *" (pointing to 32 bits)
    "const char * *"
    "float *" (pointing to 32 bits)
{{< / highlight >}}

<p>For some reason this warning doesn't appear in the HTML output, only in stdout, so alas you have to monitor both places to see all the warnings.</p>
<h2 id="exception-state">Exception State</h2>
<p>CPyChecker can flag a function that returns <code>NULL</code> without setting an exception. If I hand it this code:</p>

{{<highlight c>}}
static PyObject* randerr(PyObject* self, PyObject* args) {
    PyObject *p = NULL;
    if ((float)rand()/(float)RAND_MAX > 0.5)
        p = PyString_FromString("foo");

    return p;
}
{{< / highlight >}}

<p>It warns about the consequences of taking the false path:</p>
<p><img alt="CPyChecker: randerr()" src="cpychecker-randerr.png" style="display:block; margin-left:auto; margin-right:auto;" title="CPyChecker: randerr()"/></p>
<p>Indeed, this code throws a <code>SystemError</code> when it returns <code>NULL</code>:</p>

{{<highlight python3>}}
>>> import modtest
>>> modtest.randerr()
'foo'
>>> modtest.randerr()
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
SystemError: error return without exception set
{{< / highlight >}}

<p>Unfortunately this check is a big source of false positives. Let's say a function <code>maybe_error</code> sets the exception and returns 1 if it has an error, and returns 0 otherwise:</p>

{{<highlight c>}}
static int maybe_error() {
    if ((float)rand()/(float)RAND_MAX > 0.5) {
        PyErr_SetString(PyExc_Exception, "error");
        return 1;
    } else {
        return 0;
    }
}
{{< / highlight >}}

<p>Its caller knows this, so if <code>maybe_error</code> returns 1, the caller need not set the exception itself:</p>

{{<highlight c>}}
static PyObject* caller(PyObject* self, PyObject* args) {
    if (maybe_error()) {
        /* I know the error has been set. */
        return NULL;
    } else {
        return PyString_FromString("foo");
    }
}
{{< / highlight >}}

<p>This works correctly in practice:</p>

{{<highlight python3>}}
>>> modtest.caller()
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
Exception: error
>>> modtest.caller()
'foo'
{{< / highlight >}}

<p>But CPyChecker only analyzes code paths through a single function at a time, so it wrongly criticizes <code>caller</code> for omitting the exception:</p>
<p><img alt="CPyChecker: caller()" src="cpychecker-caller.png" style="display:block; margin-left:auto; margin-right:auto;" title="CPyChecker: caller()"/></p>
<p>The C extensions I help maintain—those for PyMongo—use this pattern in a few places, so we have persistent false positives. If CPyChecker grows up into an adult tool like Coverity that's used in CI systems, it will either need to do inter-function analysis, or have <a href="https://fedorahosted.org/gcc-python-plugin/ticket/17">a way of marking particular warnings as false positives</a>.</p>
<h1 id="conclusion">Conclusion</h1>
<p>These are early days for CPyChecker, but it's promising. With more complex functions CPyChecker starts to really shine. It clearly diagrams how different paths through the code can overcount or undercount references, dereference null pointers, and the like. It understands both the Python C API and the C stdlib quite well. I hope David Malcolm and others can polish it up into a real product soon.</p>
<hr/>
<p>You might also like my article on <a href="/code-coverage-python-c-extensions/">measuring test coverage of C extensions</a>, or the one on <a href="/python-c-extensions-and-mod-wsgi/">making C extensions compatible with mod_wsgi</a>.</p>
