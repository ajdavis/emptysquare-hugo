+++
type = "post"
title = "Motor: Iterating Over Results"
date = "2012-11-11T17:26:06"
description = ""
"blog/category" = ["Mongo", "Motor", "Programming", "Python"]
"blog/tag" = []
enable_lightbox = false
thumbnail = "motor-musho@240.png"
draft = false
+++

<p><img src="motor-musho.png" alt="Motor" title="Motor" border="0"   /></p>
<p>Motor (yes, that's my non-blocking MongoDB driver for <a href="http://www.tornadoweb.org/">Tornado</a>) has three methods for iterating a cursor: <a href="http://motor.readthedocs.org/en/stable/api/motor_cursor.html#motor.MotorCursor.to_list"><code>to_list</code></a>, <a href="http://motor.readthedocs.org/en/stable/api/motor_cursor.html#motor.MotorCursor.each"><code>each</code></a>, and <a href="http://motor.readthedocs.org/en/stable/api/motor_cursor.html#motor.MotorCursor.next_object"><code>next_object</code></a>. I chose these three methods to match the <a href="http://mongodb.github.com/node-mongodb-native/api-generated/cursor.html">Node.js driver's methods</a>, but in Python they all have problems.</p>
<p>I'm writing to announce an improvement I made to <code>next_object</code> and to ask you for suggestions for further improvement.</p>
<p><strong>Update:</strong> <a href="/blog/motor-iterating-over-results-the-grand-conclusion/">Here's the improvements I made to the API</a> in response to your critique.</p>
<h1 id="to_list">to_list</h1>
<p><code>MotorCursor.to_list</code> is clearly the most convenient: it buffers up all the results in memory and passes them to the callback:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #AA22FF">@gen.engine</span>
<span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">f</span>():
    results <span style="color: #666666">=</span> <span style="color: #008000; font-weight: bold">yield</span> motor<span style="color: #666666">.</span>Op(collection<span style="color: #666666">.</span>find()<span style="color: #666666">.</span>to_list)
    <span style="color: #008000; font-weight: bold">print</span> results
</pre></div>


<p>But it's dangerous, because you don't know for certain how big the results will be unless you set an explicit limit. In the docs <a href="http://motor.readthedocs.org/en/stable/api/motor_cursor.html#motor.MotorCursor.to_list">I exhort you to set a limit </a>before calling <code>to_list</code>. Should I raise an exception if you don't, or just let the user beware?</p>
<h1 id="each">each</h1>
<p>MotorCursor's <code>each</code> takes a callback which is executed once for every document. This actually <a href="http://mongodb.github.com/node-mongodb-native/api-generated/cursor.html#each">looks fairly elegant in Node.js</a>, but because Python doesn't do anonymous functions it looks like ass in Python, with control jumping forward and backward in the code:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">each</span>(document, error):
    <span style="color: #008000; font-weight: bold">if</span> error:
        <span style="color: #008000; font-weight: bold">raise</span> error
    <span style="color: #008000; font-weight: bold">elif</span> document:
        <span style="color: #008000; font-weight: bold">print</span> document
    <span style="color: #008000; font-weight: bold">else</span>:
        <span style="color: #408080; font-style: italic"># Iteration complete</span>
        <span style="color: #008000; font-weight: bold">print</span> <span style="color: #BA2121">&#39;done&#39;</span>

collection<span style="color: #666666">.</span>find()<span style="color: #666666">.</span>each(callback<span style="color: #666666">=</span>each)
</pre></div>


<p>Python's generators allow us to do <a href="http://www.tornadoweb.org/en/latest/gen.html">inline callbacks with <code>tornado.gen</code></a>, which makes up for the lack of anonymous functions. <code>each</code> doesn't work with the generator style, though, so I don't think many people will use <code>each</code>.</p>
<h1 id="next_object">next_object</h1>
<p>Since <code>tornado.gen</code> is the most straightforward way to write Tornado apps, I designed <code>next_object</code> for you to use with <code>tornado.gen</code>, like this:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #AA22FF">@gen.engine</span>
<span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">f</span>():
    cursor <span style="color: #666666">=</span> collection<span style="color: #666666">.</span>find()
    <span style="color: #008000; font-weight: bold">while</span> cursor<span style="color: #666666">.</span>alive:
        document <span style="color: #666666">=</span> <span style="color: #008000; font-weight: bold">yield</span> motor<span style="color: #666666">.</span>Op(cursor<span style="color: #666666">.</span>next_object)
        <span style="color: #008000; font-weight: bold">print</span> document

    <span style="color: #008000; font-weight: bold">print</span> <span style="color: #BA2121">&#39;done&#39;</span>
</pre></div>


<p>This loop looks pretty nice, right? The improvement I <a href="https://github.com/ajdavis/mongo-python-driver/commit/b56d476409325cb58bb619b395c35461bfb3ac32">just committed</a> is that <code>next_object</code> prefetches the next batch whenever needed to ensure that <code>alive</code> is correct&mdash;that is, <code>alive</code> is <code>True</code> if the cursor has more documents, <code>False</code> otherwise.</p>
<p>Problem is, just because <code>cursor.alive</code> is <code>True</code> doesn't truly guarantee that <code>next_object</code> will actually return a document. The first call returns <code>None</code> <em>if <code>find</code> matched no documents at all</em>, so a proper loop is more like:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #AA22FF">@gen.engine</span>
<span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">f</span>():
    cursor <span style="color: #666666">=</span> collection<span style="color: #666666">.</span>find()
    <span style="color: #008000; font-weight: bold">while</span> cursor<span style="color: #666666">.</span>alive:
        document <span style="color: #666666">=</span> <span style="color: #008000; font-weight: bold">yield</span> motor<span style="color: #666666">.</span>Op(cursor<span style="color: #666666">.</span>next_object)
        <span style="color: #008000; font-weight: bold">if</span> document:
            <span style="color: #008000; font-weight: bold">print</span> document
        <span style="color: #008000; font-weight: bold">else</span>:
            <span style="color: #408080; font-style: italic"># No results at all</span>
            <span style="color: #008000; font-weight: bold">break</span>
</pre></div>


<p>This is looking less nice. A blocking driver could have reasonable solutions like making <code>cursor.alive</code> actually fetch the first batch of results and return <code>False</code> if there are none. But a non-blocking driver needs to take a callback for every method that does I/O. I'm considering introducing a <code>MotorCursor.has_next</code> method that takes a callback:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">cursor <span style="color: #666666">=</span> collection<span style="color: #666666">.</span>find()
<span style="color: #008000; font-weight: bold">while</span> (<span style="color: #008000; font-weight: bold">yield</span> motor<span style="color: #666666">.</span>Op(cursor<span style="color: #666666">.</span>has_next)):
    <span style="color: #408080; font-style: italic"># Now we know for sure that document isn&#39;t None</span>
    document <span style="color: #666666">=</span> <span style="color: #008000; font-weight: bold">yield</span> motor<span style="color: #666666">.</span>Op(cursor<span style="color: #666666">.</span>next_object)
    <span style="color: #008000; font-weight: bold">print</span> document
</pre></div>


<p>This will be a core idiom for Motor applications; it should be as easy as possible to use.</p>
<p>What do you think?</p>
    