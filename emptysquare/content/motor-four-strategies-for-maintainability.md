+++
type = "post"
title = "Motor: Four Strategies For Maintainability"
date = "2012-07-13T00:21:59"
description = ""
category = ["MongoDB", "Motor", "Programming", "Python"]
tag = []
enable_lightbox = false
draft = false
disqus_identifier = "4fffa26753937451f6000000"
disqus_url = "https://emptysqua.re/blog/4fffa26753937451f6000000/"
+++

<p>When I started writing <a href=https://motor.readthedocs.io/>Motor</a>, my async driver for Tornado and MongoDB, my main concern was maintainability. I want 100% feature-parity with the official driver, PyMongo. And I don't just want it now: I want to easily maintain that completeness in the future, forever.</p>
<p>Maintainability is a struggle for the Tornado version of any Python library. There's always the gold-standard implementation of some library written in the standard blocking fashion, and then there's a midget cousin written for Tornado, which starts small and never seems to grow up. For example, Python ships with a <a href="http://docs.python.org/library/simplexmlrpcserver.html">SimpleXMLRPCServer</a> which is fairly complete. If you're using Tornado, however, you have to use <a href="https://github.com/joshmarshall/tornadorpc/">Tornado-RPC</a>. It hasn't been touched in two years, and it has severe deficiencies, e.g. it doesn't work with <a href="http://www.tornadoweb.org/en/latest/gen.html">tornado.gen</a>.</p>
<p>Gevent solves the maintainability problem by monkey-patching existing libraries to make them async. When the library code changes, the monkey-patching still works with the new version. Node.js, on the other hand, is a space where no synchronous libraries exist. The best implementation of any library for Node is <strong>already</strong> the async version.</p>
<p>But Tornado libraries are always playing catch-up with a more complete synchronous library, and usually not playing it very well.</p>
<p>With Motor, I've done the best job I can think of to get caught up with PyMongo and stay caught up. I have 4 strategies:</p>
<p><strong>1</strong>. Reuse PyMongo. I use a cute technique with greenlets to reuse most of PyMongo's code and make it async. <a href="/motor-internals-how-i-asynchronized-a-synchronous-library/">I've written up this method previously.</a></p>
<p><strong>2</strong>. Directly test Motor. As with any library, thorough tests catch regressions, and it's particularly important with Motor because it could break when PyMongo changes. Testing async code is a bit painful; I've written both callback-style tests using my <a href="/tornado-unittesting-eventually-correct/">assertEventuallyEqual</a> method, and generator-style tests using my <a href="/tornado-unittesting-with-generators/">async_test_engine decorator</a>. If the underlying PyMongo code changes and breaks Motor, I'll know immediately.</p>
<p><strong>3</strong>. Reuse PyMongo's tests. Just as Motor wraps PyMongo and makes it async, I've written another wrapper that makes Motor synchronous again, so Motor looks just like PyMongo. This wrapper is called Synchro. For each async Motor method, Synchro wraps it like:</p>

{{<highlight python3>}}
class Collection(object):
    """Synchro's fake Collection, which wraps MotorCollection, which
       wraps the real PyMongo Collection.
    """
    def find_one(self, *args, **kwargs):
        loop = tornado.ioloop.IOLoop.instance()
        outcome = {}

        def callback(result, error):
            loop.stop()
            outcome['result'] = result
            outcome['error'] = error

        kwargs['callback'] = callback
        self.motor_collection.find_one(*args, **kwargs)
        loop.start()

        # Now the callback has been run and has stopped the loop
        if outcome['error']:
            raise outcome['error']
        else:
            return outcome['result']
{{< / highlight >}}

<p>(In <a href="https://github.com/mongodb/motor/blob/master/synchro/__init__.py">the actual code</a> I also add a timeout to the loop so an error doesn't risk hanging my tests.)</p>
<p>What does this craziness buy me? I can run most of PyMongo's tests, about 350 of them, against Synchro. Since Synchro passes these tests, I'm confident Motor isn't missing any features without my knowledge. So, for example, we're adding an <code>aggregate</code> method to PyMongo in its next release, and we'll add a test to PyMongo's suite that exercises <code>aggregate</code>. That test will fail against Synchro, since Synchro uses Motor and Motor doesn't have <code>aggregate</code> yet. The Synchro tests fail promptly, and I can simply add a line to Motor saying, "asynchronize <code>aggregate</code>, too."</p>
<p><strong>4</strong>. Reuse PyMongo's documentation. Every Motor method takes the same parameters and has the same behavior as the PyMongo method it wraps, except it's async and takes a callback. I could just copy and paste PyMongo's docs and add the callback parameter to each method, but then when PyMongo's docs change Motor will fall behind. Instead, I wrote a <a href="https://github.com/mongodb/motor/blob/master/doc/motor_extensions.py">Sphinx extension</a>. For each method in Motor, the extension finds the analogous PyMongo documentation and adds the <code>callback</code> parameter. For example, the <a href="https://motor.readthedocs.io/en/stable/api-tornado/motor_collection.html">MotorCollection</a> API docs are largely generated from PyMongo's Collection docs.</p>
