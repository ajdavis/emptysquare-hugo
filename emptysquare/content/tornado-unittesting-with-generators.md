+++
type = "post"
title = "Tornado Unittesting With Generators"
date = "2012-03-28T17:03:27"
description = ""
category = ["MongoDB", "Programming", "Python"]
tag = []
enable_lightbox = false
draft = false
disqus_identifier = "352 http://emptysquare.net/blog/?p=352"
disqus_url = "https://emptysqua.re/blog/352 http://emptysquare.net/blog/?p=352/"
+++

<h1 id="intro">Intro</h1>
<p>This is the second installment of what is becoming an ongoing series on
unittesting in Tornado, the Python asynchronous web framework.</p>
<p>A couple months ago <a href="/tornado-unittesting-eventually-correct/">I shared some code called
assertEventuallyEqual</a>,
which tests that Tornado asynchronous processes eventually arrive at the
expected result. Today I'll talk about Tornado's generator interface and
how to write even pithier unittests.</p>
<p>Late last year Tornado gained the "gen" module, which allows you to
write async code in a synchronous-looking style by making your request
handler into a generator. <a href="http://www.tornadoweb.org/en/latest/gen.html">Go look at the Tornado documentation for the
gen module.</a></p>
<p>I've extended that idea to unittest methods by making a test decorator
called <code>async_test_engine</code>. Let's look at the classic way of testing
Tornado code first, then I'll show a unittest using my new method.</p>
<h1 id="classic-tornado-testing">Classic Tornado Testing</h1>
<p>Here's some code that tests
<a href="https://github.com/bitly/asyncmongo">AsyncMongo</a>, bit.ly's MongoDB
driver for Tornado, using a typical Tornado testing style:</p>

```python
def test_stuff(self):
    db = asyncmongo.Client(
        pool_id='test_query',
        host='127.0.0.1',
        port=27017,
        dbname='test',
        mincached=3
    )

    def cb(result, error):
        self.stop((result, error))

    db.collection.remove(safe=True, callback=cb)
    self.wait()
    db.collection.insert({"_id" : 1}, safe=True, callback=cb)
    self.wait()

    # Verify the document was inserted
    db.collection.find(callback=cb)
    result, error = self.wait()
    self.assertEqual([{'_id': 1}], result)

    # MongoDB has a unique index on _id
    db.collection.insert({"_id" : 1}, safe=True, callback=cb)
    result, error = self.wait()
    self.assertTrue(isinstance(error, asyncmongo.errors.IntegrityError))
```

<a href="https://gist.github.com/2230276">Full code in this gist</a>.&nbsp;This is the
style of testing <a href="http://www.tornadoweb.org/en/latest/testing.html">shown in the docs for Tornado's testing
module</a>.</p>
<h1 id="tornado-testing-with-generators">Tornado Testing With Generators</h1>
<p>Here's the same test, rewritten using my <code>async_test_engine</code> decorator:</p>

```python
@async_test_engine(timeout_sec=2)
def test_stuff(self):
    db = asyncmongo.Client(
        pool_id='test_query',
        host='127.0.0.1',
        port=27017,
        dbname='test',
        mincached=3
    )

    yield gen.Task(db.collection.remove, safe=True)
    yield gen.Task(db.collection.insert, {"_id" : 1}, safe=True)

    # Verify the document was inserted
    yield AssertEqual([{'_id': 1}], db.collection.find)

    # MongoDB has a unique index on _id
    yield AssertRaises(
          asyncmongo.errors.IntegrityError,
          db.collection.insert, {"_id" : 1}, safe=True)
```


<p>A few things to note about this code: First is its brevity. Most
operations and assertions about their outcomes can co&euml;xist on a single
line.</p>
<p>Next, look at the <code>@async_test_engine</code> decorator. This is my subclass of
the Tornado-provided <code>gen.engine</code>. Its main difference is that it starts
the IOLoop before running this test method, and it stops the IOLoop when
this method completes. By default it fails a test that takes more than 5
seconds, but the timeout is configurable.</p>
<p>Within the test method itself, the first two operations use <code>remove</code> to
clear the MongoDB collection, and <code>insert</code> to add one document. For both
those operations I use <code>yield gen.Task</code>, from the <code>tornado.gen</code> module,
to pause this test method (which is a generator) until the operation has
completed.</p>
<p>Next is a class I wrote, <code>AssertEqual</code>, which inherits from <code>gen.Task</code>.
The expression</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">yield</span> AssertEqual(expected_value, function, arguments, <span style="color: #666666">...</span>)
</pre></div>


<p>pauses this method until the async operation completes and calls the
implicit callback. <code>AssertEqual</code> then compares the callback's argument
to the expected value, and fails the test if they're different.</p>
<p>Finally, look at <code>AssertRaises</code>. This runs the async operation, but
instead of examining the result passed to the callback, it examines the
<strong>error</strong> passed to the callback, and checks that it's the expected
Exception.</p>
<p><a href="https://gist.github.com/2229985">Full code for <code>async_test_engine</code>, <code>AssertEqual</code>, and <code>AssertError</code> are
in this gist</a>. The code relies on
AsyncMongo's convention of passing (result, error) to each callback, so
I invite you to generalize the code for your own purposes. Let me know
what you do with it, I feel like there's a place in the world for an
elegant Tornado test framework.</p>
