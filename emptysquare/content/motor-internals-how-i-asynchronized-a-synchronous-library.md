+++
type = "post"
title = "Motor Internals: How I Asynchronized a Synchronous Library"
date = "2012-07-09T22:07:45"
description = "How and why I wrote Motor, my asynchronous driver for MongoDB and Tornado."
category = ["MongoDB", "Motor", "Programming", "Python"]
tag = []
enable_lightbox = false
thumbnail = "motor-collection.png"
draft = false
disqus_identifier = "4ffb8e715393742d5b000000"
disqus_url = "https://emptysqua.re/blog/4ffb8e715393742d5b000000/"
+++

<p>I'm going to explain why and how I wrote <a href=https://motor.readthedocs.io/>Motor</a>, my asynchronous driver for MongoDB and Tornado. I hope I can justify my ways to you.</p>
<h1 id="the-problem">The Problem</h1>
<p>Here's how you query one document from MongoDB with <a href="http://pypi.python.org/pypi/pymongo/">PyMongo</a>, 10gen's official driver:</p>

{{<highlight python3>}}
connection = Connection()
document = connection.db.collection.find_one()
print document
{{< / highlight >}}

<p>As you can see, the official driver is blocking: you call <code>find_one</code> and your code waits for the result.</p>
<p>Deep in the bowels of PyMongo, the driver sends your query over a socket and waits for the database's response:</p>

{{<highlight python3>}}
class Connection(object):
    def send_and_receive(self, message, socket):
        socket.sendall(message)
        header = socket.recv(16) # Get 16-byte header
        length = struct.unpack("<i", header[:4])[0]
        body = socket.recv(length)
        return header + body
{{< / highlight >}}

<p>That's three blocking operations on the socket in a row. All of PyMongo relies on the assumption that it can use sockets synchronously. How the hell can I make it non-blocking so you can use it with Tornado? Specifically, how can I implement this API?:</p>

{{<highlight python3>}}
def opened(connection, error):
    connection.db.collection.find_one(callback=found)

def found(document, error):
    print document

MotorConnection().open(callback=opened)
{{< / highlight >}}

<h1 id="asyncmongos-solution">AsyncMongo's Solution</h1>
<p>bit.ly's non-blocking driver, <a href="https://github.com/bitly/asyncmongo">AsyncMongo</a>, took the straightforward approach. It copied and pasted PyMongo as it stood two years ago, and turned it inside-out to use callbacks. PyMongo's <code>send_and_receive</code> became this:</p>

{{<highlight python3>}}
class Connection(object):
    def send_and_receive(self, message, callback):
        self.callback = callback

        # self.stream is a Tornado IOStream
        self.stream.write(message)
        self.stream.read_bytes(16,
            callback=self.parse_header)

    def parse_header(self, data):
        self.header = data
        length = struct.unpack("<i", data[:4])[0]
        self.stream.read_bytes(length,
            callback=self.parse_response)

    def parse_response(self, data):
        response = self.header + data
        self.callback(response)
{{< / highlight >}}

<p>(Note that IOStream buffers the output in <code>write</code>, so only the <code>read_bytes</code> calls take callbacks.)</p>
<p>This is a solution to the problem of making PyMongo async, but now there's a new problem: how do we maintain code like this? PyMongo is extended and improved every month by 10gen's programmers (like me!). An effort comparable to that devoted to maintaining PyMongo would be required to keep AsyncMongo up to date, because every PyMongo change must be manually ported over. Who has that kind of time?</p>
<h1 id="motors-solution">Motor's Solution</h1>
<p>Since I joined 10gen in November last year, I'd been thinking there must be a better way. I wanted to somehow reuse all of PyMongo's existing code—its years of improvements and bugfixes and battle-testing—but make it non-blocking so Tornado programmers could use it. I thought that if Python had something like Scheme's <a href="http://en.wikipedia.org/wiki/Call-with-current-continuation">call-with-current-continuation</a>, I could pause PyMongo's execution whenever it would block waiting for a socket, and resume when the socket was ready. From that thought, it surely took me longer, dear reader, than it would have taken you to deduce the solution, but during a particularly distracted meditation session it somehow dawned on me: <a href="http://pypi.python.org/pypi/greenlet">greenlets</a>. I'd use a Gevent-like technique to wrap PyMongo and asynchronize it, while presenting a classic Tornado callback API to you.</p>
<p>Asynchronizing PyMongo takes two steps. First, I wrap each PyMongo method and run it on a greenlet, like this:</p>
<p><img alt="MotorCollection" border="0" src="motor-collection.png" style="display:block; margin-left:auto; margin-right:auto;" title="motor-collection.png"/></p>
<p>So when you call <code>collection.find_one(callback=found)</code>, Motor (1) grabs the callback argument and (2) starts a greenlet that (3) runs PyMongo's original <code>find_one</code>. That <code>find_one</code> sends a message to the server and calls <code>recv</code> on a socket to get the response.</p>
<p>The second step is to pause the greenlet whenever it would block. I wrote a <code>MotorSocket</code> class which seems to PyMongo like a regular socket, but in fact it wraps a Tornado IOStream:</p>
<p><img alt="MotorSocket" border="0" src="motor-socket.png" style="display:block; margin-left:auto; margin-right:auto;" title="motor-socket.png"/></p>
<p><code>MotorSocket.recv</code> (4) starts reading the requested number of bytes and (5) pauses the caller's greenlet. At this point, (6) the original call to <code>find_one</code> returns. Because Motor's API is callback-based, its <code>find_one</code> returns <code>None</code>. The actual MongoDB document will be passed into the callback asynchronously.</p>
<p>Eventually, IOStream's <code>read_bytes</code> call completes and executes the callback, which (7) resumes the paused greenlet. That greenlet then completes PyMongo's processing, parsing the server's response and so on, until PyMongo's original <code>find_one</code> returns. Motor gets a result or an exception from PyMongo's <code>find_one</code> and (8) schedules your callback on the IOLoop.</p>
<p>(The real code is a little more complicated, <a href="https://github.com/mongodb/motor/blob/0.5/motor/frameworks/tornado.py#L288">gory details here</a>.)</p>
<p>If you're a visual learner, here's the same sequence of events diagrammed:</p>
<p><img alt="Motor Internals" border="0" src="motor-internals.png" style="display:block; margin-left:auto; margin-right:auto;" title="motor-internals.png"/></p>
<p>Sorry, it's the best diagram I can think of.</p>
<h1 id="why">Why?</h1>
<p>PyMongo is three and a half years old. The core module is 3000 source lines of code. There are hundreds improvements and bugfixes, and 7000 lines of unittests. Anyone who tries to make a non-blocking version of it has a lot of work cut out, and will inevitably fall behind development of the official PyMongo. With Motor's technique, I can wrap and reuse PyMongo whole, and when we fix a bug or add a feature to PyMongo, Motor will come along for the ride, for free.</p>
