+++
type = "post"
title = "Test MongoDB Failure Scenarios With MockupDB"
date = "2015-11-04T09:46:01"
description = "Fourth in my \"black pipe testing\" series. How do you test your MongoDB application's reaction to database failures, hangs, and disconnects?"
category = ["C", "MongoDB", "Programming", "Python"]
tag = ["black-pipe", "testing"]
enable_lightbox = false
thumbnail = "york-street-pipes.jpg"
draft = false
series = ["black-pipe"]
+++

<p><a href="https://www.flickr.com/photos/emptysquare/1528243252"><img style="display:block; margin-left:auto; margin-right:auto;" src="york-street-pipes.jpg" alt="York Street pipes" title="York Street pipes" /></a></p>
<p>This is the fifth article in <a href="/black-pipe-testing-series/">my series on "black pipe" testing</a>. Traditional black box tests work well if your application takes inputs and returns output through one interface: the API. But connected applications have two interfaces: both the API and the messages they send and receive on the network. I call the validation of both ends a black pipe test.</p>
<p>In my previous article <a href="/libmongoc-black-pipe-testing-mock-server/">I described black pipe testing in pure C</a>; now we return to Python.</p>
<p>I implemented a Python tool for black pipe testing called
<a href="http://mockupdb.readthedocs.org/">MockupDB</a>. It is a <a href="http://docs.mongodb.org/meta-driver/latest/legacy/mongodb-wire-protocol/">MongoDB wire protocol</a> server, built to subject PyMongo to black pipe tests. But it's not only for testing PyMongo&mdash;if you develop a MongoDB application, you can use MockupDB too. It easily simulates network errors and server failures, or it can refuse to respond at all. Such antics are nearly impossible to test reliably using a real MongoDB server, but it's easy with MockupDB.</p>
<h1 id="testing-your-own-applications-with-mockupdb">Testing Your Own Applications With MockupDB</h1>
<p>Let us say you have a Flask application that uses MongoDB. To make testing convenient, I've wrapped it in a <code>make_app</code> function:</p>


{{< highlight py "hl_lines=" >}}
from flask import Flask, make_response
from pymongo import MongoClient

def make_app(mongodb_uri):
    app = Flask("my app")
    db = MongoClient(mongodb_uri)

    @app.route("/pages/<page_name>")
    def page(page_name):
        doc = db.content.pages.find_one({'name': page_name})
        return make_response(doc['contents'])

    return app
{{< / highlight >}}

<p>The app has one route, which returns a page by name.</p>
<p>It is simple enough to test its fairweather conduct using a real MongoDB server, provisioned with data from a test fixture. But how can we test what happens if, for example, MongoDB shuts down in the middle of the query?</p>
<p>I have cooked up for you a test class that uses MockupDB:</p>

{{< highlight py "hl_lines=" >}}
import unittest

from mockupdb import go, Command, MockupDB


class MockupDBFlaskTest(unittest.TestCase):
    def setUp(self):
        self.server = MockupDB(auto_ismaster=True)
        self.server.run()
        self.app = make_app(self.server.uri).test_client()

    def tearDown(self):
        self.server.stop()
{{< / highlight >}}

<p>(Please, Flask experts, critique me in the comments.)</p>
<p>Let me ensure this contraption works for a normal round trip:</p>

{{< highlight py "hl_lines=3 7" >}}
# Method of MockupDBFlaskTest.
def test(self):
    future = go(self.app.get, "/pages/my_page_name")
    request = self.server.receives(
        Command('find', 'pages', filter={'name': 'my_page_name'}))

    request.ok(cursor={'id': 0, 'firstBatch': [{'contents': 'foo'}]})
    http_response = future()
    self.assertEqual("foo",
                     http_response.get_data(as_text=True))
{{< / highlight >}}

<p>We use MockupDB's function <code>go</code> to run Flask on a background thread, just like <a href="/black-pipe-testing-pymongo/">we ran PyMongo operations on a background thread in an earlier article</a>. The <code>go</code> function returns a Future, which will be resolved once the background thread completes.</p>
<p>On the foreground thread, we impersonate the database server and have a conversation with the application, speaking the MongoDB wire protocol. MockupDB receives the application's query, responds with a document, and that allows Flask to finish its job and create an HTTP response. We assert the response has the expected content.</p>
<p>Now comes the payoff! We close MockupDB's connection at just the wrong instant, using its <code>hangup</code> method:</p>
{{< highlight py "hl_lines=4" >}}
def test_hangup(self):
    future = go(self.app.get, "/pages/my_page_name")
    request = self.server.receives(OpQuery, name='my_page_name')
    request.hangup()  # Close connection.
    http_response = future()
    self.assertEqual("foo",
                     http_response.get_data(as_text=True))
{{< / highlight >}}


<p>The test fails, as you guessed it would:</p>

```
FAIL: test_hangup (__main__.MockupDBFlaskTest)
---------------------------------------------------------------------
Traceback (most recent call last):
  File "test.py", line 43, in test_hangup
    self.assertEqual("foo", http_response.get_data(as_text=True))
AssertionError: 'foo' != '<html><title>500 Internal Server Error...'
```

<p>What would we rather the application do? Let's have it respond "Closed for renovations" when it can't reach the database:</p>

{{< highlight py "hl_lines=7 8" >}}
from pymongo.errors import ConnectionFailure

@app.route("/pages/<page_name>")
def page(page_name):
    try:
        doc = db.content.pages.find_one({'name': page_name})
    except ConnectionFailure:
        return make_response('Closed for renovations')
    return make_response(doc['contents'])
{{< / highlight >}}

<p>Test the new error handling by asserting that "renovations" is in the response:</p>

{{< highlight py "hl_lines=" >}}
self.assertIn("renovations",
              http_response.get_data(as_text=True))
{{< / highlight >}}

<p>(<a href="https://gist.github.com/ajdavis/96e4c64be32fce042f10">See the complete code here</a>.)</p>
<p>And how about your connection applications? Do you continuously test them with network errors? Can you imagine how difficult this would be to test without MockupDB?</p>
