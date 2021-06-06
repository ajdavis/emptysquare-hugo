+++
type = "post"
title = "Python C Extensions And mod_wsgi"
date = "2013-09-26T11:39:38"
description = "If you use mod_wsgi, or you're the author of a Python C extension, it's time for you to learn how they interact."
category = ["MongoDB", "Programming", "Python"]
tag = ["best", "mod_wsgi"]
enable_lightbox = false
draft = false
disqus_identifier = "523cefc75393741a66f71344"
disqus_url = "https://emptysqua.re/blog/523cefc75393741a66f71344/"
+++

<p>For the next release of PyMongo, Bernie Hackett and I have updated PyMongo's C extensions to be more compatible with <code>mod_wsgi</code>, and improved PyMongo's docs about <code>mod_wsgi</code>. In the process I had to buckle down and finally grasp the relationship between <code>mod_wsgi</code> and C extensions. The only way I could master it was to experiment. Enjoy the fruits of my research.</p>
<p><strong>Summary</strong>: Python scripts in a <code>mod_wsgi</code> daemon process are isolated from each other in separate Python sub interpreters, but the state of their C extensions is <em>not</em> isolated. If a C extension tries to import and use Python classes, it creates an unholy mix of classes from different interpreters. PyMongo fell victim to this issue when encoding and decoding BSON. We used to have a hack for this, and now we have a nice workaround. When you deploy WSGI scripts, configure <code>mod_wsgi</code> to isolate your scripts from each other completely, by running them in separate daemon processes. If you maintain a Python extension, our latest strategies can help you make your script compatible with <code>mod_wsgi</code>.</p>
<div class="toc">
<ul>
<li><a href="#python-runs-in-a-daemon-process">Python Runs In A Daemon Process</a></li>
<li><a href="#python-variables-are-isolated-in-sub-interpreters">Python Variables Are Isolated In Sub Interpreters</a></li>
<li><a href="#but-c-extensions-are-not-isolated">But C Extensions Are Not Isolated</a><ul>
<li><a href="#static-variables-are-shared">Static Variables Are Shared</a></li>
<li><a href="#python-classes-only-work-in-the-first-interpreter">Python Classes Only Work In The First Interpreter</a></li>
</ul>
</li>
<li><a href="#pymongo-and-mod_wsgi">PyMongo and mod_wsgi</a><ul>
<li><a href="#encoding">Encoding</a></li>
<li><a href="#decoding">Decoding</a></li>
</ul>
</li>
<li><a href="#you-can-isolate-c-extensions-in-separate-daemons">You Can Isolate C Extensions In Separate Daemons</a></li>
<li><a href="#how-should-c-extensions-handle-multiple-sub-interpreters">How Should C Extensions Handle Multiple Sub Interpreters?</a><ul>
<li><a href="#pymongos-crummy-old-hack">PyMongo's Crummy Old Hack</a></li>
<li><a href="#pymongos-pretty-good-new-workaround">PyMongo's Pretty Good New Workaround</a></li>
</ul>
</li>
<li><a href="#recommendations">Recommendations</a><ul>
<li><a href="#deployment">Deployment</a></li>
<li><a href="#writing-c-extensions">Writing C Extensions</a></li>
</ul>
</li>
</ul>
</div>
<h2 id="python-runs-in-a-daemon-process">Python Runs In A Daemon Process</h2>
<p>Graham Dumpleton, <code>mod_wsgi</code>'s author, <a href="http://blog.dscpl.com.au/2012/10/why-are-you-using-embedded-mode-of.html">recommends we use daemon mode under most circumstances</a>. So the first step in configuring <code>mod_wsgi</code> is to fork a daemon process with <a href="https://code.google.com/p/modwsgi/wiki/ConfigurationDirectives#WSGIDaemonProcess">WSGIDaemonProcess</a>:</p>

{{<highlight plain>}}
<VirtualHost *>
    WSGIDaemonProcess my_process
</VirtualHost>
{{< / highlight >}}

<p>Now, I'll use <a href="https://code.google.com/p/modwsgi/wiki/ConfigurationDirectives#WSGIScriptAlias">WSGIScriptAlias</a> to tell <code>mod_wsgi</code> where my script is, and use <a href="https://code.google.com/p/modwsgi/wiki/ConfigurationDirectives#WSGIProcessGroup">WSGIProcessGroup</a> to assign the script to the daemon:</p>

{{<highlight plain>}}
<VirtualHost *>
    WSGIDaemonProcess my_process
    WSGIScriptAlias /my_app /path/to/app.wsgi
    WSGIProcessGroup my_process
</VirtualHost>
{{< / highlight >}}

<h2 id="python-variables-are-isolated-in-sub-interpreters">Python Variables Are Isolated In Sub Interpreters</h2>
<p>When the daemon runs my script, it needs a Python interpreter. By default, the daemon uses a different Python interpreter for each "resource" on my web server. A resource is the concatenation of the server name, port number, and script name, so requests to my application over port 8080 might use an interpreter named "example.com:8080|/my_app". Each distinct combination of domain name, port number, and script name is mapped to a separate interpreter, so that multiple scripts don't affect each other's state.</p>
<p>When an HTTP request arrives, the daemon checks if it's created an interpreter for this resource. If not, it calls the Python C API function <code>Py_NewInterpreter</code>. <a href="http://docs.python.org/2/c-api/init.html#Py_NewInterpreter">The Python docs say</a>:</p>
<blockquote>
<p>This is an (almost) totally separate environment for the execution of Python code. In particular, the new interpreter has separate, independent versions of all imported modules, including the fundamental modules <code>builtins</code>, <code>__main__</code> and <code>sys</code>. The table of loaded modules (<code>sys.modules</code>) and the module search path (<code>sys.path</code>) are also separate.</p>
</blockquote>
<p>Let's see this separation in action. I'll make a module with a variable:</p>

{{<highlight python3>}}
# module.py

var = 0
{{< / highlight >}}

<p>My WSGI script increments the variable with each request and responds with the new value:</p>

{{<highlight python3>}}
# app.wsgi

import module

def application(environ, start_response):
    module.var += 1

    output = 'var = %d\n' % module.var
    response_headers = [('Content-Length', str(len(output)))]
    start_response('200 OK', response_headers)
    return [output]
{{< / highlight >}}

<p>(<a href="/python-increment-is-weird/">Incrementing an integer is not thread-safe</a>, but I'm ignoring thread-safety here.)</p>
<p>I'll map two URLs, "foo" and "bar", to the same script:</p>

{{<highlight plain>}}
<VirtualHost *>
    WSGIDaemonProcess my_process
    WSGIProcessGroup my_process
    WSGIScriptAlias /foo /path/to/app.wsgi
    WSGIScriptAlias /bar /path/to/app.wsgi
</VirtualHost>
{{< / highlight >}}

<p><code>mod_wsgi</code> uses different sub interpreters for the two URLs, so they have different copies of <code>var</code>. When I request "foo" it increments one copy, and when I request "bar" it increments the other copy:</p>

{{<highlight plain>}}
$ curl localhost/foo
var = 1
$ curl localhost/foo
var = 2
$ curl localhost/bar
var = 1
$ curl localhost/bar
var = 2
{{< / highlight >}}

<p>I can use <a href="https://code.google.com/p/modwsgi/wiki/ConfigurationDirectives#WSGIApplicationGroup">WSGIApplicationGroup</a> to change the relationship between URLs and sub interpreters. I'll put both URLs in the same "application group," meaning the same Python sub interpreter:</p>

{{<highlight plain>}}
<VirtualHost *>
    WSGIDaemonProcess my_process
    WSGIProcessGroup my_process
    WSGIScriptAlias /foo /path/to/app.wsgi
    WSGIScriptAlias /bar /path/to/app.wsgi
    WSGIApplicationGroup my_application_group
</VirtualHost>
{{< / highlight >}}

<p>Now requests to "foo" and "bar" run in the same interpreter and increment the same copy of <code>var</code>:</p>

{{<highlight plain>}}
$ curl localhost/foo
var = 1
$ curl localhost/foo
var = 2
$ curl localhost/bar
var = 3
$ curl localhost/bar
var = 4
{{< / highlight >}}

<p>If I set the application group to <code>%{GLOBAL}</code>, "foo" and "bar" will run in the daemon's main interpreter, not any sub interpreter at all. We'll see momentarily why this is useful.</p>
<h2 id="but-c-extensions-are-not-isolated">But C Extensions Are Not Isolated</h2>
<p>Remember when the Python docs said that <code>Py_NewInterpreter</code> creates "an (almost) totally separate environment"? One reason it's not completely separate is that C extensions are shared:</p>
<blockquote>
<p>Extension modules are shared between (sub-)interpreters as follows: the first time a particular extension is imported, it is initialized normally, and a (shallow) copy of its module’s dictionary is squirreled away. When the same extension is imported by another (sub-)interpreter, a new module is initialized and filled with the contents of this copy; the extension’s init function is <strong>not</strong> called.</p>
</blockquote>
<h3 id="static-variables-are-shared">Static Variables Are Shared</h3>
<p>I wrote an example C extension called <code>demo</code> to demonstrate the issues. <a href="https://github.com/ajdavis/demo-c-extension">The code is on GitHub.</a> Instead of declaring a global variable in a Python module, let's make one in C:</p>

{{<highlight c>}}
/* A global variable. */
static long var = 0;

static PyObject* inc_and_get_var(PyObject* self, PyObject* args)
{
    var++;
    return PyInt_FromLong(var);
}
{{< / highlight >}}

<p>I call <code>inc_and_get_var()</code> in my WSGI script:</p>

{{<highlight python3>}}
output = 'var: %s\n' % demo.inc_and_get_var()
{{< / highlight >}}

<p>Now, I'll change my Apache configuration back, so it uses the default application groups:</p>

{{<highlight plain>}}
<VirtualHost *>
    WSGIDaemonProcess my_process
    WSGIProcessGroup my_process
    WSGIScriptAlias /foo /path/to/app.wsgi
    WSGIScriptAlias /bar /path/to/app.wsgi
</VirtualHost>
{{< / highlight >}}

<p>Once again <code>mod_wsgi</code> uses a different interpreter for each URL. So if I were using the <code>var</code> declared in Python, "foo" and "bar" would increment different copies of it. But of course a static variable declared in C is shared among all interpreters in a daemon:</p>

{{<highlight plain>}}
$ curl localhost/foo
var: 1
$ curl localhost/bar
var: 2
{{< / highlight >}}

<p>Instead of using a static variable, I could have put the variable in the module's dict. But as the Python doc said, that dict is copied into the new interpreter, so the interpreters still wouldn't be completely isolated.</p>
<h3 id="python-classes-only-work-in-the-first-interpreter">Python Classes Only Work In The First Interpreter</h3>
<p>The shared-state problem becomes worse if the C extension uses a class implemented in Python. What if an extension imports a Python class and later calls <code>PyObject_IsInstance()</code> on it? Here's some C code for a function called <code>is_myclass()</code>:</p>

{{<highlight c>}}
static PyObject* MyClass;

static PyObject* is_myclass(PyObject* self, PyObject* args)
{
    int outcome;
    PyObject* obj;
    if (!PyArg_ParseTuple(args, "O", &obj)) return NULL;

    outcome = PyObject_IsInstance(obj, MyClass);
    if (outcome) { Py_RETURN_TRUE; }
    else { Py_RETURN_FALSE; }
}

PyMODINIT_FUNC
initdemo(void)
{
    PyObject* mymodule = PyImport_ImportModule("mymodule");
    MyClass = PyObject_GetAttrString(mymodule, "MyClass");
    Py_DECREF(mymodule);
    Py_InitModule("demo", Methods);
}
{{< / highlight >}}

<p>(Error-checking is omitted. See GitHub for the real code.)</p>
<p><code>is_myclass()</code> works just fine in the shell:</p>

{{<highlight python3>}}
>>> import demo, mymodule
>>> obj = mymodule.MyClass()
>>> demo.is_myclass(obj)
True
{{< / highlight >}}

<p>How about in <code>mod_wsgi</code>? I'll make my WSGI script output the result of <code>is_myclass()</code>:</p>

{{<highlight python3>}}
import demo
import mymodule

def application(environ, start_response):
    obj = mymodule.MyClass()
    outcome = demo.is_myclass(obj)

    output = 'outcome = %s\n' % outcome
    response_headers = [('Content-Length', str(len(output)))]
    start_response('200 OK', response_headers)
    return [output]
{{< / highlight >}}

<p>Then I map two URLs to this script:</p>

{{<highlight plain>}}
<VirtualHost *>
    WSGIDaemonProcess my_process
    WSGIProcessGroup my_process
    WSGIScriptAlias /foo demo.wsgi
    WSGIScriptAlias /bar demo.wsgi
</VirtualHost>
{{< / highlight >}}

<p>If I request the URL "foo", everything's peachy: my script thinks <code>obj</code> is an instance of <code>MyClass</code>. But when I request "bar" it thinks the opposite:</p>

{{<highlight plain>}}
$ curl localhost/foo
outcome = True
$ curl localhost/bar
outcome = False
{{< / highlight >}}

<p>From now on, "foo" returns True and "bar" returns False. But if I restart Apache and request "bar" first, followed by "foo", the outcome is reversed:</p>

{{<highlight plain>}}
$ sudo service apache2 restart
 * Restarting web server apache2
$ curl localhost/bar
outcome = True
$ curl localhost/foo
outcome = False
{{< / highlight >}}

<p>Do you see why? Only the first interpreter that imports my extension runs <code>initdemo()</code>, imports <code>MyClass</code>, and assigns it to a static variable. From then on, calls to <code>is_myclass</code> work in the first interpreter, because the object is compared to the Python class created in the same interpreter. Calls in the other interpreter always return false.</p>
<p>The inverse problem happens when I instantiate a <code>MyClass</code> object in C:</p>

{{<highlight c>}}
static PyObject* create_myclass(PyObject* self, PyObject* args)
{
    return PyObject_CallObject(MyClass, NULL);
}
{{< / highlight >}}

<p>I'll update my Python script to check if <code>create_myclass()</code> returns an instance of <code>MyClass</code>:</p>

{{<highlight python3>}}
outcome = isinstance(
    demo.create_myclass(),
    mymodule.MyClass)

output = 'isinstance: %s' % outcome
{{< / highlight >}}

<p>Again, if I request "foo" first, it returns True and "bar" returns False:</p>

{{<highlight plain>}}
$ curl localhost/foo
isinstance: True
$ curl localhost/bar
isinstance: False
{{< / highlight >}}

<p>If I restart Apache and request "bar" first, it returns True from then on, and "foo" returns False.</p>
<p>What's going on? <code>initdemo()</code> caches <code>MyClass</code> from the interpreter that calls it, so the instances it creates act normally in that interpreter. The second Python interpreter that imports <code>demo</code> does <strong>not</strong> call <code>initdemo()</code>, so the module has no opportunity to discover that it's being used from a different interpreter. It continues making objects that only work in the first interpreter. <a href="https://code.google.com/p/modwsgi/wiki/ApplicationIssues#Multiple_Python_Sub_Interpreters">The <code>mod_wsgi</code> docs call this</a> "an unholy mixing of code and data from multiple sub interpreters."</p>
<p>Note that types defined in C don't suffer these ills: they're static. For example, the datetime type is defined as:</p>

{{<highlight c>}}
static PyTypeObject PyDateTime_DateTimeType;
{{< / highlight >}}

<p>Every interpreter in the daemon process agrees on the memory address of this type, so both <code>PyObject_IsInstance</code> and <code>isinstance</code> work on datetimes across interpreters.</p>
<h2 id="pymongo-and-mod_wsgi">PyMongo and <code>mod_wsgi</code></h2>
<p>PyMongo's BSON encoder and decoder are written in C, in an extension called <code>_cbson</code>. <code>_cbson</code> caches Python classes, so it's vexed by problems with <code>PyObject_IsInstance</code> and <code>isinstance</code> when running in multiple sub interpreters. Bear with me, I'm going into some detail about why PyMongo had trouble in each case.</p>
<h3 id="encoding">Encoding</h3>
<p>In PyMongo we have a class representing MongoDB ObjectIds:</p>

{{<highlight python3>}}
class ObjectId(object):
    # Etcetera.
    pass
{{< / highlight >}}

<p><code>_cbson</code> needs both to recognize ObjectIds and to create them, so it caches the ObjectId class when it initializes:</p>

{{<highlight c>}}
static PyObject* ObjectId;

PyMODINIT_FUNC
init_cbson(void)
    PyObject* module = PyImport_ImportModule("bson.objectid");
    ObjectId = PyObject_GetAttrString(module, "ObjectId");
    Py_DECREF(module);

    /** More module setup .... */
}
{{< / highlight >}}

<p>Let's say I'm turning a dict into BSON. I execute this Python code:</p>

{{<highlight python3>}}
bson_document = BSON.encode({"_id": ObjectId()})
{{< / highlight >}}

<p>PyMongo iterates the dict, checking each value's type to decide how to encode it. Is the value an int, a string, an ObjectId, something else?</p>

{{<highlight c>}}
PyObject* iter = PyObject_GetIter(dict);
while ((key = PyIter_Next(iter)) != NULL) {
    PyObject* value = PyDict_GetItem(dict, key);
    if (PyObject_IsInstance(value, ObjectId)) {
        /* Encode the ObjectId as BSON .... */
    }

    /* Check for other possible types .... */

    Py_DECREF(key);
}
Py_DECREF(iter);
{{< / highlight >}}

<p>By now you know what's going to happen: the first interpreter that imports <code>_cbson</code> is the one that caches the ObjectId class, and <code>PyObject_IsInstance</code> works there. In other interpreters, <code>PyObject_IsInstance</code> can't recognize ObjectIds.</p>
<h3 id="decoding">Decoding</h3>
<p>The <code>PyObject_IsInstance</code> problem manifested when turning Python objects into BSON. The inverse happens when decoding BSON: <code>_cbson</code> churns through a BSON document reading the type code for each field:</p>

{{<highlight c>}}
switch (type) {
case 7:
    value = PyObject_CallFunction(state->ObjectId,
                                  "s#", buffer, 12);
    break;
{{< / highlight >}}

<p>The value so constructed is an ObjectId, but <code>isinstance(value, ObjectId)</code> is False in any interpreters besides the first one. Our users don't call <code>isinstance</code>, it seems, because this bug was never reported.</p>
<h2 id="you-can-isolate-c-extensions-in-separate-daemons">You Can Isolate C Extensions In Separate Daemons</h2>
<p>The <code>mod_wsgi</code> docs provide no guidance for writing C extensions, they just say:</p>
<blockquote>
<p>Because of the possibility that extension module writers have not written their code to take into consideration it being used from multiple sub interpreters, the safest approach is to force all WSGI applications to run within the same application group, with that preferably being the first interpreter instance created by Python.</p>
</blockquote>
<p>Following Dumpleton's advice, we tell PyMongo users to always use <code>WSGIApplicationGroup %{GLOBAL}</code> to put their applications in the main interpreter. Since that risks interference if you run multiple applications in the same daemon process, you should run each application in a separate daemon, like this:</p>

{{<highlight plain>}}
<VirtualHost *>
    WSGIDaemonProcess my_process
    WSGIScriptAlias /foo /path/to/app.wsgi
    <Location /foo>
        WSGIProcessGroup my_process
    </Location>

    WSGIDaemonProcess my_other_process
    WSGIScriptAlias /bar /path/to/app.wsgi
    <Location /bar>
        WSGIProcessGroup my_other_process
    </Location>

    WSGIApplicationGroup %{GLOBAL}
</VirtualHost>
{{< / highlight >}}

<p>I've <a href="https://github.com/mongodb/mongo-python-driver/blob/master/doc/examples/mod_wsgi.rst">added an example like this</a> to PyMongo's docs.</p>
<h2 id="how-should-c-extensions-handle-multiple-sub-interpreters">How Should C Extensions Handle Multiple Sub Interpreters?</h2>
<p>But some users don't read the manual, and some aren't allowed to change their Apache config. How can we write a C extension that handles multiple sub interpreters gracefully?</p>
<h3 id="pymongos-crummy-old-hack">PyMongo's Crummy Old Hack</h3>
<p>Through version 2.6, our BSON encoder used the following algorithm to deal with multiple sub interpreters:</p>
<ul>
<li>For each value, use <code>PyObject_IsInstance</code> to check if it is any BSON-encodable Python type.</li>
<li>If all checks fail, log a RuntimeWarning saying, "couldn't encode—reloading python modules and trying again."</li>
<li>Re-import and re-cache all Python classes, such as ObjectId. This ensures <code>_cbson</code>'s references to Python classes come from the current interpreter.</li>
<li>Again check if the value is encodable.</li>
<li>If not, raise InvalidBSON because this isn't a <code>mod_wsgi</code> problem: the application is actually trying to encode something that isn't BSON-encodable.</li>
</ul>
<p>There were a few problems with this. First, it wrote a warning to the Apache error log whenever an application encoded BSON in a different interpreter from the last one in which it had encoded BSON. Second, it only fixed <code>PyObject_IsInstance</code>, not <code>isinstance</code>.</p>
<h3 id="pymongos-pretty-good-new-workaround">PyMongo's Pretty Good New Workaround</h3>
<p>Bernie Hackett's elegant solution avoids <code>PyObject_IsInstance</code> entirely when encoding. He added a <code>_type_marker</code> field to our Python classes:</p>

{{<highlight python3>}}
class ObjectId(object):
    _type_marker = 7
{{< / highlight >}}

<p><code>_cbson</code> uses the type marker to decide how to encode each value:</p>

{{<highlight c>}}
if (PyObject_HasAttrString(value, "_type_marker")) {
    long type;
    PyObject* type_marker = PyObject_GetAttrString(
        value, "_type_marker");

    type = PyInt_AsLong(type_marker);
    Py_DECREF(type_marker);
    switch (type) {
    case 7:
        /* Encode an ObjectId .... */
{{< / highlight >}}

<p>Not only is the type marker robust against sub interpreter issues, but it's faster than <code>PyObject_IsInstance</code>. If a value has no type marker, then we check for builtin types like strings and ints.</p>
<p>The only BSON-encodable Python type we don't control is UUID. It's implemented in Python, but it's provided by the standard library so we can't add a type marker. Here, Bernie took two approaches. First, he checked whether we're in a sub interpreter or the main one:</p>

{{<highlight c>}}
/*
 * Are we in the main interpreter or a sub-interpreter?
 * Useful for deciding if we can use cached pure python
 * types in mod_wsgi.
 */
static int
_in_main_interpreter(void) {
    static PyInterpreterState* main_interpreter = NULL;
    PyInterpreterState* interpreter;

    if (main_interpreter == NULL) {
        interpreter = PyInterpreterState_Head();
        while (PyInterpreterState_Next(interpreter))
            interpreter = PyInterpreterState_Next(interpreter);

        main_interpreter = interpreter;
    }

    return (main_interpreter == PyThreadState_Get()->interp);
}
{{< / highlight >}}

<p>The first time <code>_in_main_interpreter()</code> is called, it stashes a reference to the main interpreter. From then on, it can detect if we're in a sub interpreter by comparing the current interpreter's address to the main one's.</p>
<p>If we're in the main interpreter, we can use our cached copy of the UUID class with <code>PyObject_IsInstance</code> as normal. (We're either in the global application group, or not in <code>mod_wsgi</code> at all.) If we're in a sub interpreter, we have to re-import UUID each time, before we pass it to <code>PyObject_IsInstance</code>. The performance penalty is minimal: for one thing, we only check if a value is a UUID if it's failed all other checks. Second, the speedup from <code>_type_marker</code> compensates for the cost of re-importing UUID.</p>
<p>What about decoding? How does <code>_cbson</code> avoid returning instances of one interpreter's classes to another interpreter? Again, if <code>_in_main_interpreter()</code> is true, <code>_cbson</code> can safely use its cached classes. If not, it re-imports ObjectId each time it needs it—same for UUID and so forth. This is cheap: my benchmark only showed it costing a few microseconds per value. After all, re-importing a module is essentially a lookup in <code>sys.modules</code>. Real applications are I/O bound anyway and won't notice the hit. But if you're concerned, use <code>WSGIApplicationGroup %{GLOBAL}</code> to run your script in the main interpreter.</p>
<h2 id="recommendations">Recommendations</h2>
<p>After all the intricacies I learned, I've arrived at simple recommendations.</p>
<h3 id="deployment">Deployment</h3>
<p>Multiple sub interpreters are only an issue if you have multiple scripts using the same C extension. If so, run the scripts in separate daemon processes using <code>WSGIDaemonProcess</code> and <code>WSGIProcessGroup</code>, and assign them to the main interpreter with <code>WSGIApplicationGroup %{GLOBAL}</code>.</p>
<h3 id="writing-c-extensions">Writing C Extensions</h3>
<p>Extension authors can't rely on users to deploy this way, so C extensions should be written to support multiple sub interpreters.</p>
<ul>
<li>If your extension imports <em>your</em> Python classes, add type markers to them as PyMongo did and use the type markers instead of <code>PyObject_IsInstance</code>.</li>
<li>Alternatively, implement the classes you need in C instead of Python, so they're safe to use across interpreters, the same as datetimes are.</li>
<li>If you import third-party or standard-library Python classes, check if you're running in a sub interpreter. If so, re-import these classes on demand. It's cheaper than you think.</li>
</ul>
<hr/>
<p>You might also like my article on <a href="/code-coverage-python-c-extensions/">measuring test coverage of C extensions</a>, or the one on <a href="/analyzing-python-c-extensions-with-cpychecker/">automatically detecting refcount errors in C extensions</a>.</p>
