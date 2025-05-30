+++
type = "post"
title = "Motor: Iterating Over Results, The Grand Conclusion"
date = "2012-11-17T15:50:44"
description = ""
category = ["MongoDB", "Motor", "Programming", "Python"]
tag = []
enable_lightbox = false
thumbnail = "motor-musho.png"
draft = false
+++

<p><img alt="Motor" border="0" src="motor-musho.png" title="Motor"/></p>
<p>This is another post about <a href=https://motor.readthedocs.io/>Motor, my non-blocking driver for MongoDB and Tornado</a>.</p>
<p>Last week <a href="/motor-iterating-over-results/">I asked for your help improving Motor's iteration API</a>, and I got invaluable responses here and on the <a href="https://groups.google.com/d/topic/python-tornado/zlg9XU4_E78/discussion">Tornado mailing list</a>. Today I'm pushing to GitHub some breaking changes to the API that'll greatly improve MotorCursor's ease of use.</p>
<p>(Note: I'm continuing to <strong>not</strong> make version numbers for Motor, since it's going to join PyMongo soon. Meanwhile, to protect yourself against API changes, <a href="/motor-installation-instructions/">pip install Motor with a specific git hash</a> until you're ready to upgrade.)</p>
<h1 id="next_object">next_object</h1>
<p>After getting some inspiration from Ben Darnell on the Tornado list, I added to MotorCursor a <a href="https://motor.readthedocs.io/en/stable/api-tornado/cursors.html#motor.MotorCursor.fetch_next"><code>fetch_next</code></a> attribute. You yield <code>fetch_next</code> from a Tornado coroutine, and if it sends back <code>True</code>, then <code>next_object</code> is guaranteed to have a document for you. So iterating over a MotorCursor is now quite nice:</p>

{{<highlight python3>}}
@gen.engine
def f():
    cursor = collection.find()
    while (yield cursor.fetch_next):
        document = cursor.next_object()
        print document
{{< / highlight >}}

<p>How does this work? Whenever you yield <code>fetch_next</code>, MotorCursor checks if it has another document already batched. If so, it doesn't need to contact the server, it just sends <code>True</code> back into your coroutine. Your coroutine then calls <code>next_object</code>, which simply pops a document off the list.</p>
<p>If there aren't any more documents in the current batch, but the cursor's still alive, <code>fetch_next</code> fetches another batch from the server and <strong>then</strong> sends <code>True</code> into the coroutine.</p>
<p>And finally, if the cursor is exhausted, <code>fetch_next</code> sends <code>False</code> and your coroutine exits the while-loop.</p>
<p>This new style of iteration handles all the edge cases the previous "<code>while cursor.alive</code>" style failed at: it's an especially big win for the case where <code>find()</code> found no documents at all. I like this new idiom a lot; let me know what you think.</p>
<p><strong>Migration:</strong> If you have any loops using <code>while cursor.alive</code>, you'll need to rewrite them in the style shown above. I had some special hacks in place to make <code>cursor.alive</code> useful for loops like this, but I've now removed those hacks, and you shouldn't rely on <code>cursor.alive</code> to tell you whether a cursor has more documents or not. Only rely on <code>fetch_next</code> for that. Furthermore, <code>next_object</code> is now synchronous. It doesn't take a callback, so you can no longer do this:</p>

{{<highlight python3>}}
# old syntax
document = yield motor.Op(cursor.next_object)
{{< / highlight >}}

<h1 id="to_list">to_list</h1>
<p>Shane Spencer on the Tornado list insisted I should add a <code>length</code> argument to <code>MotorCursor.to_list</code> so you could say, "Get me a certain number of documents from the result set." I finally saw he was right, so <a href="https://motor.readthedocs.io/en/stable/api-tornado/cursors.html#motor.MotorCursor.to_list">I've added the option</a>.</p>

{{<highlight python3>}}
@gen.engine
def f():
    cursor = collection.find()
    results = yield motor.Op(cursor.to_list, 10)
    while results:
        print results
        results = yield motor.Op(cursor.to_list, 10)
{{< / highlight >}}

<p>(Thanks to <a href="/motor-iterating-over-results/#comment-710590108">Andrew Downing for suggesting this loop style</a>, apparently it's called a "Yourdon loop.")</p>
<p>This is a nice addition for chunking up your documents and not holding too much in memory. Note that the actual number of documents fetched per batch is controlled by <a href="https://motor.readthedocs.io/en/stable/api-tornado/cursors.html#motor.MotorCursor.batch_size"><code>batch_size</code></a>, <strong>not</strong> by the <code>length</code> argument. But you can prevent your program from downloading all the batches at once if you pass a <code>length</code>. (I hope that makes sense.)</p>
<p><strong>Migration:</strong> If you ever called <code>to_list</code> with an explicit callback as a positional argument, like this:</p>

{{<highlight python3>}}
cursor.to_list(my_callback)
{{< / highlight >}}

<p>... then my_callback will now be interpreted as the <code>length</code> argument and you'll get an exception:</p>

{{<highlight plain>}}
TypeError: Wrong type for length, value must be an integer
{{< / highlight >}}

<p>Pass it as a keyword-argument instead:</p>

{{<highlight python3>}}
cursor.to_list(callback=my_callback)
{{< / highlight >}}

<p>Most Motor methods require you to pass the callback as a keyword argument, anyway, so you might as well use this style for all methods.</p>
<h1 id="each">each</h1>
<p><a href="https://motor.readthedocs.io/en/stable/api-tornado/cursors.html#motor.MotorCursor.each"><code>MotorCursor.each</code></a> hasn't changed. It continues to be a pretty useless method, in my opinion, but it keeps Motor close to <a href="http://mongodb.github.com/node-mongodb-native/markdown-docs/queries.html#cursors">the MongoDB Node.js Driver's API</a> so I'm not going to remove it.</p>
<h1 id="in-conclusion">In Conclusion</h1>
<p>I asked for your help and I got it; everyone's critiques helped me seriously improve Motor. I'm glad I did this before I had to freeze the API. The new API is so much better.</p>
