+++
type = "post"
title = "Motor: Iterating Over Results"
date = "2012-11-11T17:26:06"
description = ""
category = ["MongoDB", "Motor", "Programming", "Python"]
tag = []
enable_lightbox = false
thumbnail = "motor-musho.png"
draft = false
disqus_identifier = "50a025c55393741e2d1b4d0b"
disqus_url = "https://emptysqua.re/blog/50a025c55393741e2d1b4d0b/"
+++

<p><img alt="Motor" border="0" src="motor-musho.png" title="Motor"/></p>
<p>Motor (yes, that's my non-blocking MongoDB driver for <a href="http://www.tornadoweb.org/">Tornado</a>) has three methods for iterating a cursor: <a href="http://motor.readthedocs.org/en/stable/api/motor_cursor.html#motor.MotorCursor.to_list"><code>to_list</code></a>, <a href="http://motor.readthedocs.org/en/stable/api/motor_cursor.html#motor.MotorCursor.each"><code>each</code></a>, and <a href="http://motor.readthedocs.org/en/stable/api/motor_cursor.html#motor.MotorCursor.next_object"><code>next_object</code></a>. I chose these three methods to match the <a href="http://mongodb.github.com/node-mongodb-native/api-generated/cursor.html">Node.js driver's methods</a>, but in Python they all have problems.</p>
<p>I'm writing to announce an improvement I made to <code>next_object</code> and to ask you for suggestions for further improvement.</p>
<p><strong>Update:</strong> <a href="/motor-iterating-over-results-the-grand-conclusion/">Here's the improvements I made to the API</a> in response to your critique.</p>
<h1 id="to_list">to_list</h1>
<p><code>MotorCursor.to_list</code> is clearly the most convenient: it buffers up all the results in memory and passes them to the callback:</p>

{{<highlight python3>}}
@gen.engine
def f():
    results = yield motor.Op(collection.find().to_list)
    print results
{{< / highlight >}}

<p>But it's dangerous, because you don't know for certain how big the results will be unless you set an explicit limit. In the docs <a href="http://motor.readthedocs.org/en/stable/api/motor_cursor.html#motor.MotorCursor.to_list">I exhort you to set a limit </a>before calling <code>to_list</code>. Should I raise an exception if you don't, or just let the user beware?</p>
<h1 id="each">each</h1>
<p>MotorCursor's <code>each</code> takes a callback which is executed once for every document. This actually <a href="http://mongodb.github.com/node-mongodb-native/api-generated/cursor.html#each">looks fairly elegant in Node.js</a>, but because Python doesn't do anonymous functions it looks like ass in Python, with control jumping forward and backward in the code:</p>

{{<highlight python3>}}
def each(document, error):
    if error:
        raise error
    elif document:
        print document
    else:
        # Iteration complete
        print 'done'

collection.find().each(callback=each)
{{< / highlight >}}

<p>Python's generators allow us to do <a href="http://www.tornadoweb.org/en/latest/gen.html">inline callbacks with <code>tornado.gen</code></a>, which makes up for the lack of anonymous functions. <code>each</code> doesn't work with the generator style, though, so I don't think many people will use <code>each</code>.</p>
<h1 id="next_object">next_object</h1>
<p>Since <code>tornado.gen</code> is the most straightforward way to write Tornado apps, I designed <code>next_object</code> for you to use with <code>tornado.gen</code>, like this:</p>

{{<highlight python3>}}
@gen.engine
def f():
    cursor = collection.find()
    while cursor.alive:
        document = yield motor.Op(cursor.next_object)
        print document

    print 'done'
{{< / highlight >}}

<p>This loop looks pretty nice, right? The improvement I <a href="https://github.com/ajdavis/mongo-python-driver/commit/b56d476409325cb58bb619b395c35461bfb3ac32">just committed</a> is that <code>next_object</code> prefetches the next batch whenever needed to ensure that <code>alive</code> is correct—that is, <code>alive</code> is <code>True</code> if the cursor has more documents, <code>False</code> otherwise.</p>
<p>Problem is, just because <code>cursor.alive</code> is <code>True</code> doesn't truly guarantee that <code>next_object</code> will actually return a document. The first call returns <code>None</code> <em>if <code>find</code> matched no documents at all</em>, so a proper loop is more like:</p>

{{<highlight python3>}}
@gen.engine
def f():
    cursor = collection.find()
    while cursor.alive:
        document = yield motor.Op(cursor.next_object)
        if document:
            print document
        else:
            # No results at all
            break
{{< / highlight >}}

<p>This is looking less nice. A blocking driver could have reasonable solutions like making <code>cursor.alive</code> actually fetch the first batch of results and return <code>False</code> if there are none. But a non-blocking driver needs to take a callback for every method that does I/O. I'm considering introducing a <code>MotorCursor.has_next</code> method that takes a callback:</p>

{{<highlight python3>}}
cursor = collection.find()
while (yield motor.Op(cursor.has_next)):
    # Now we know for sure that document isn't None
    document = yield motor.Op(cursor.next_object)
    print document
{{< / highlight >}}

<p>This will be a core idiom for Motor applications; it should be as easy as possible to use.</p>
<p>What do you think?</p>
