+++
type = "post"
title = "A Normal Accident In Python and mod_wsgi"
date = "2014-10-13T14:17:45"
description = "Cascading failures lead to a tricky bug in PyMongo."
category = ["MongoDB", "Programming", "Python"]
tag = []
enable_lightbox = false
thumbnail = "class-reference-cycle.png"
draft = false
+++

<p><img alt="Three Mile Island nuclear power plant" src="Three_Mile_Island_nuclear_power_plant.jpg" style="display:block; margin-left:auto; margin-right:auto;" title="Three Mile Island nuclear power plant"/></p>
<p>I fixed a glitch in PyMongo last week, the result of a slapstick series of mishaps. It reminds me of the Three Mile Island nuclear accident, which inspired the <a href="http://en.wikipedia.org/wiki/Normal_Accidents">"Normal Accidents"</a> theory of failure in complex systems: one surprise leads to the next, to the next, to an outcome no one anticipated.</p>
<p>It started a couple months ago, when <a href="https://jira.mongodb.org/browse/PYTHON-747">we got a minor bug report about PyMongo</a>. The reporter was using PyMongo with Python 3.2, mod_wsgi, and Apache. Whenever he restarted his application, he saw this error message in his log:</p>

{{<highlight plain>}}
Exception TypeError:
  "'NoneType' object is not callable"
  in <bound method Pool.__del__> ignored
{{< / highlight >}}

<p>The exception was ignored because it was raised from a "__del__" method, so it didn't affect his application. Still, I needed to understand what was going on. So I made a test environment, and I used Apache to run a Python script like the one in the bug report:</p>

{{<highlight python3>}}
import pymongo

class C:
    pass

C.client = pymongo.MongoClient()
{{< / highlight >}}

<p>I could reproduce the bug: Whenever I restarted Apache, the PyMongo connection pool's destructor logged "TypeError: NoneType object is not callable."</p>
<p>The pool's destructor makes two method calls, and no function calls:</p>

{{<highlight python3>}}
def __del__(self):
    # _thread_id_to_sock is a dict of sockets.
    for sock in self._thread_id_to_sock.values():
        sock.close()
{{< / highlight >}}

<p>During interpreter shutdown, None is somehow being called as a function. I'm no expert on Python's shutdown sequence, but I've never heard of a method being set to None. And yet, the only calls in this code are the "values" method and the "close" method. What gives?</p>
<p>I put a "return" statement at the beginning of "__del__" and restarted Apache: the error disappeared. So I moved the "return" statement down a line, before "sock.close()". The next time I restarted Apache, I saw the error again.</p>
<p>While I was hacking directly on the installed PyMongo package, I noticed something funny. The installed code looked like:</p>

{{<highlight python3>}}
def __del__(self):
    # _thread_id_to_sock is a dict of sockets.
    for sock in list(self._thread_id_to_sock.values()):
        sock.close()
{{< / highlight >}}

<p>Notice the call to "list"? When I installed PyMongo with Python 3.2, the installer ran 2to3 on PyMongo's code, which automatically translates Python 2 syntax to Python 3.</p>
<p>Why did 2to3 decide to wrap the "values" call in "list"? Well, in Python 2, "values" returns a copy, but in Python 3 it returns a <a href="http://python3porting.com/preparing.html#optional-use-the-iterator-methods-on-dictionaries">dictionary view</a> that's tied to the dict's underlying data. 2to3 worries that I might rely on the old, copying behavior, so in Python 3 it makes a copy of the values by calling "list".</p>
<p>So it must be the call to "list" that raises the TypeError. Sure enough, when I deleted the "list" call from the installed PyMongo code, the exception disappears. Fantastic!</p>
<p>Why don't we see this error all the time, though? Perhaps it has to do with the shutdown sequence. Normally, a pool is referred to by other objects, but not by a class. I hypothesized that the reporter saw the error because he'd made a reference from a class to the MongoClient to the pool, which delayed the pool's destruction until after the "list" builtin had been set to None:</p>
<p><img alt="Class refers to pool" src="class-refers-to-pool.png" style="display:block; margin-left:auto; margin-right:auto;" title="Class refers to pool"/></p>
<p>To test this theory, I replaced this line:</p>

{{<highlight python3>}}
C.client = pymongo.MongoClient()
{{< / highlight >}}

<p>...with this:</p>

{{<highlight python3>}}
client = pymongo.MongoClient()
{{< / highlight >}}

<p>Now the pool is no longer referred to by a class, it's only referred to by a global variable in the module named "mod":</p>
<p><img alt="Variable refers to pool" src="variable-refers-to-pool.png" style="display:block; margin-left:auto; margin-right:auto;" title="Variable refers to pool"/></p>
<p>Sure enough the error disappeared.</p>
<p>So far, I understood that the connection pool's destructor ran too late, because it was being kept alive by a reference from a class, <strong>and</strong> it relied on the "list" builtin, because 2to3 had added a call to "list", so it raised a TypeError. Now, did it only happen with mod_wsgi? I wrote the simplest Python example I could, and I tried to reproduce the TypeError:</p>

{{<highlight python3>}}
# mod.py
class C(object):
    pass

class Pool(object):
    def __del__(self):
        print('del')
        list()

C.pool = Pool()
{{< / highlight >}}

<p>I could import this module into the Python shell, then quit, and I got no TypeError. Actually I didn't see it print "del" either—the pool's destructor never runs at all. Why not?</p>
<p>A class definition like "C" creates a reference cycle. It refers to itself as the first element in its method resolution order. You can see how "C" refers to itself by printing its method resolution order in the Python shell:</p>

{{<highlight python3>}}
>>> import mod
>>> mod.C.__mro__
(<class 'mod.C'>, <type 'object'>)
{{< / highlight >}}

<p>When the interpreter shuts down it runs <a href="https://hg.python.org/cpython/file/eac54f7a8018/Python/pythonrun.c#l396">the C function "Py_Finalize"</a>, which first does a round of garbage collection to destroy reference cycles, then destroys all modules:</p>

{{<highlight c>}}
void Py_Finalize(void) {
    /* Collect garbage.  This may call finalizers; it's nice to call these
     * before all modules are destroyed.
     */
    PyGC_Collect();

    /* Destroy all modules */
    PyImport_Cleanup();
}
{{< / highlight >}}

<p>When "PyGC_Collect" runs, the "mod" module still refers to class C, so the class isn't destroyed and neither is the Pool it refers to:</p>
<p><img alt="Class reference cycle" src="class-reference-cycle.png" style="display:block; margin-left:auto; margin-right:auto;" title="Class reference cycle"/></p>
<p>Next, "PyImport_Cleanup" sets all modules' global variables to None. Now class C is garbage: it's in a reference cycle and nothing else refers to it:</p>
<p><img alt="Cyclic garbage" src="cyclic-garbage.png" style="display:block; margin-left:auto; margin-right:auto;" title="Cyclic garbage"/></p>
<p>But the interpreter is dying and it will never call "PyGC_Collect" again, so class C is never destroyed and neither is the pool.</p>
<p>Great, I understand everything up to this point. But, if the pool is never destroyed when a regular Python interpreter shuts down, why is it destroyed when a mod_wsgi application restarts? I dove into mod_wsgi's source code to see how it manages Python interpreters. (This isn't my first rodeo: I examined mod_wsgi closely for my <a href="/python-c-extensions-and-mod-wsgi/">"Python C Extensions And mod_wsgi"</a> article last year.) I wrote <a href="https://github.com/ajdavis/python-sub-interpreter-demo">a little C program that runs Python in a sub interpreter</a>, the same as mod_wsgi does:</p>

{{<highlight c>}}
int main()
{
    Py_Initialize();
    PyThreadState *tstate_enter = PyThreadState_Get();
    PyThreadState *tstate = Py_NewInterpreter();

    PyRun_SimpleString("import mod\n");
    if (PyErr_Occurred()) {
        PyErr_Print();
    }
    Py_EndInterpreter(tstate);
    PyThreadState_Swap(tstate_enter);
    printf("about to finalize\n");
    Py_Finalize();
    printf("done\n");

    return 0;
}
{{< / highlight >}}

<p>Just like mod_wsgi, my program creates a new Python sub interpreter and tells it to import my module, then it swaps out the sub interpreter and shuts it down with "Py_EndInterpreter". Its last act is "Py_Finalize". And behold! The script quoth:</p>

{{<highlight plain>}}
about to finalize

Exception TypeError:
  "'NoneType' object is not callable"
  in <bound method Pool.__del__> ignored

done
{{< / highlight >}}

<p>My little C program acts just like the application in the bug report! What is it about this code that makes it throw the TypeError during shutdown, when a regular Python interpreter does not?</p>
<p>I stepped through my program in the debugger and solved the final mystery. What makes this code special is, it calls "Py_EndInterpreter". "Py_EndInterpreter" calls "PyImport_Cleanup", which sets all modules' global variables to None, thus turning class C into cyclic garbage:</p>
<p><img alt="Cyclic garbage" src="cyclic-garbage.png" style="display:block; margin-left:auto; margin-right:auto;" title="Cyclic garbage"/></p>
<p>"PyImport_Cleanup" even clears the "builtins" module, which includes functions like "list". Any code that tries to call "list" afterward is actually calling None.</p>
<p>Now "Py_Finalize" calls "PyGC_Collect". (It will then run "PyImport_Cleanup" for the second time, but that's not relevant now.) This is the difference between the regular interpreter's shutdown sequence and mod_wsgi's: In the mod_wsgi case, modules have been cleared before the final garbage collection, so class C is destroyed along with the pool. However, since the pool's destructor runs after "PyImport_Cleanup", its reference to "list" is now None, and it throws "TypeError: 'NoneType' object is not callable".</p>
<p>Success! I had traced the cause of the bug from start to finish. To recap: in the bug-reporter's code, he had made a reference from a class to a pool, which made the pool's destructor run very late. And he ran the code in mod_wsgi, which clears modules before the final garbage collection, otherwise the pool's destructor wouldn't have run at all. He was using Python 3, so 2to3 had inserted a call to "list" in the pool's destructor, and since the destructor ran after all modules were cleared, the call to "list" failed.</p>
<p>Luckily, this cascade of failures leads merely to an occasional log message, not to a Three Mile Island meltdown. My boss Bernie came up with an incredibly simple fix. I replace the call to "values":</p>

{{<highlight python3>}}
def __del__(self):
    for sock in self._thread_id_to_sock.values():
        sock.close()
{{< / highlight >}}

<p>... with a call to "itervalues":</p>

{{<highlight python3>}}
def __del__(self):
    for sock in self._thread_id_to_sock.itervalues():
        sock.close()
{{< / highlight >}}

<p>(You can <a href="https://github.com/mongodb/mongo-python-driver/commit/2ef85956b8b3d8a1918460f3b9e7f47a3112751f">view the whole commit here</a>.)</p>
<p>Now that I'm using "itervalues", 2to3 now replaces it with "values" in Python 3 instead of "list(values)". Since I'm no longer relying on the "list" builtin to be available in the destructor, no TypeError is raised.</p>
