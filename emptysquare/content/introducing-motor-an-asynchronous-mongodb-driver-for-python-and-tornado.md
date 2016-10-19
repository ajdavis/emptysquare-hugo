+++
type = "post"
title = "Introducing Motor, an asynchronous MongoDB driver for Python and Tornado"
date = "2012-07-06T14:37:29"
description = ""
category = ["Mongo", "Motor", "Programming", "Python"]
tag = []
enable_lightbox = false
thumbnail = "dampfmaschinen2-brockhaus@240.jpg"
draft = false
legacyid = "4ff730695393742d65000000"
+++

<p><img style="display:block; margin-left:auto; margin-right:auto;" src="dampfmaschinen2-brockhaus.jpg" alt="Dampfmaschinen2 brockhaus" title="Dampfmaschinen2_brockhaus.jpg" border="0"   /></p>
<p>Tornado is a popular asynchronous Python web server, and MongoDB a widely used non-relational database. Alas, to connect to MongoDB from a Tornado app requires a tradeoff: You can either use <a href="http://pypi.python.org/pypi/pymongo/">PyMongo</a> and give up the advantages of an async web server, or use <a href="http://pypi.python.org/pypi/asyncmongo/1.2.1">AsyncMongo</a>, which is non-blocking but lacks key features.</p>
<p>I decided to fill the gap by writing a new async driver called Motor (for "MOngo + TORnado"), and it's reached the public alpha stage. Please try it out and tell me what you think. I'll maintain a homepage for it <a href="http://motor.readthedocs.org/">here</a>.</p>
<h1 id="status">Status</h1>
<p><strong>Update</strong>: <a href="/blog/motor-progress-report/">Latest Motor progress report</a>.</p>
<p>Motor is alpha. It is certainly buggy. Its implementation and possibly its API will change in the coming months. I hope you'll help me by reporting bugs, requesting features, and pointing out how it could be better.</p>
<h1 id="advantages">Advantages</h1>
<p>Two good projects, AsyncMongo and <a href="https://github.com/yamins81/apymongo/">APyMongo</a>, took the straightforward approach to implementing an async MongoDB driver: they forked PyMongo and rewrote it to use callbacks. But this approach creates a maintenance headache: now every improvement to PyMongo must be manually ported over. Motor sidesteps the problem. It uses a Gevent-like technique to wrap PyMongo and run it asynchronously, while presenting a classic callback interface to Tornado applications. This wrapping means Motor reuses all of PyMongo's code and, aside from GridFS support, Motor is already feature-complete. Motor can easily keep up with PyMongo development in the future.</p>
<h1 id="installation">Installation</h1>
<p>Motor depends on <a href="http://pypi.python.org/pypi/greenlet">greenlet</a> and, of course, Tornado. It's been tested only with Python 2.7. You can get the code from my fork of the PyMongo repo, on the <code>motor</code> branch:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">pip install tornado greenlet    
pip install git+https://github.com/ajdavis/mongo-python-driver.git@motor
</pre></div>


<p>To keep up with development, <a href="https://github.com/ajdavis/mongo-python-driver/tree/motor">watch my repo</a> and do </p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">pip install -U git+https://github.com/ajdavis/mongo-python-driver.git@motor
</pre></div>


<p>when you want to upgrade.</p>
<p><strong>Note</strong>: Do not install the official PyMongo. If you have it installed, uninstall it before installing my fork.</p>
<h1 id="example">Example</h1>
<p>Here's an example of an application that can create and display short messages.</p>
<p><strong>Updated Jan 11, 2013</strong>: <a href="/blog/motorconnection-has-been-renamed-motorclient/">MotorConnection has been renamed MotorClient</a>.</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">import</span> <span style="color: #0000FF; font-weight: bold">tornado.web</span><span style="color: #666666">,</span> <span style="color: #0000FF; font-weight: bold">tornado.ioloop</span>
<span style="color: #008000; font-weight: bold">import</span> <span style="color: #0000FF; font-weight: bold">motor</span>

<span style="color: #008000; font-weight: bold">class</span> <span style="color: #0000FF; font-weight: bold">NewMessageHandler</span>(tornado<span style="color: #666666">.</span>web<span style="color: #666666">.</span>RequestHandler):
    <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">get</span>(<span style="color: #008000">self</span>):
        <span style="color: #BA2121; font-style: italic">&quot;&quot;&quot;Show a &#39;compose message&#39; form&quot;&quot;&quot;</span>
        <span style="color: #008000">self</span><span style="color: #666666">.</span>write(<span style="color: #BA2121">&#39;&#39;&#39;</span>
<span style="color: #BA2121">        &lt;form method=&quot;post&quot;&gt;</span>
<span style="color: #BA2121">            &lt;input type=&quot;text&quot; name=&quot;msg&quot;&gt;</span>
<span style="color: #BA2121">            &lt;input type=&quot;submit&quot;&gt;</span>
<span style="color: #BA2121">        &lt;/form&gt;&#39;&#39;&#39;</span>)

    <span style="color: #408080; font-style: italic"># Method exits before the HTTP request completes, thus &quot;asynchronous&quot;</span>
    <span style="color: #AA22FF">@tornado.web.asynchronous</span>
    <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">post</span>(<span style="color: #008000">self</span>):
        <span style="color: #BA2121; font-style: italic">&quot;&quot;&quot;Insert a message</span>
<span style="color: #BA2121; font-style: italic">        &quot;&quot;&quot;</span>
        msg <span style="color: #666666">=</span> <span style="color: #008000">self</span><span style="color: #666666">.</span>get_argument(<span style="color: #BA2121">&#39;msg&#39;</span>)

        <span style="color: #408080; font-style: italic"># Async insert; callback is executed when insert completes</span>
        <span style="color: #008000">self</span><span style="color: #666666">.</span>settings[<span style="color: #BA2121">&#39;db&#39;</span>]<span style="color: #666666">.</span>messages<span style="color: #666666">.</span>insert(
            {<span style="color: #BA2121">&#39;msg&#39;</span>: msg},
            callback<span style="color: #666666">=</span><span style="color: #008000">self</span><span style="color: #666666">.</span>_on_response)

    <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">_on_response</span>(<span style="color: #008000">self</span>, result, error):
        <span style="color: #008000; font-weight: bold">if</span> error:
            <span style="color: #008000; font-weight: bold">raise</span> tornado<span style="color: #666666">.</span>web<span style="color: #666666">.</span>HTTPError(<span style="color: #666666">500</span>, error)
        <span style="color: #008000; font-weight: bold">else</span>:
            <span style="color: #008000">self</span><span style="color: #666666">.</span>redirect(<span style="color: #BA2121">&#39;/&#39;</span>)

<span style="color: #008000; font-weight: bold">class</span> <span style="color: #0000FF; font-weight: bold">MessagesHandler</span>(tornado<span style="color: #666666">.</span>web<span style="color: #666666">.</span>RequestHandler):
    <span style="color: #AA22FF">@tornado.web.asynchronous</span>
    <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">get</span>(<span style="color: #008000">self</span>):
        <span style="color: #BA2121; font-style: italic">&quot;&quot;&quot;Display all messages</span>
<span style="color: #BA2121; font-style: italic">        &quot;&quot;&quot;</span>
        <span style="color: #008000">self</span><span style="color: #666666">.</span>write(<span style="color: #BA2121">&#39;&lt;a href=&quot;/compose&quot;&gt;Compose a message&lt;/a&gt;&lt;br&gt;&#39;</span>)
        <span style="color: #008000">self</span><span style="color: #666666">.</span>write(<span style="color: #BA2121">&#39;&lt;ul&gt;&#39;</span>)
        db <span style="color: #666666">=</span> <span style="color: #008000">self</span><span style="color: #666666">.</span>settings[<span style="color: #BA2121">&#39;db&#39;</span>]
        db<span style="color: #666666">.</span>messages<span style="color: #666666">.</span>find()<span style="color: #666666">.</span>sort([(<span style="color: #BA2121">&#39;_id&#39;</span>, <span style="color: #666666">-1</span>)])<span style="color: #666666">.</span>each(<span style="color: #008000">self</span><span style="color: #666666">.</span>_got_message)

    <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">_got_message</span>(<span style="color: #008000">self</span>, message, error):
        <span style="color: #008000; font-weight: bold">if</span> error:
            <span style="color: #008000; font-weight: bold">raise</span> tornado<span style="color: #666666">.</span>web<span style="color: #666666">.</span>HTTPError(<span style="color: #666666">500</span>, error)
        <span style="color: #008000; font-weight: bold">elif</span> message:
            <span style="color: #008000">self</span><span style="color: #666666">.</span>write(<span style="color: #BA2121">&#39;&lt;li&gt;</span><span style="color: #BB6688; font-weight: bold">%s</span><span style="color: #BA2121">&lt;/li&gt;&#39;</span> <span style="color: #666666">%</span> message[<span style="color: #BA2121">&#39;msg&#39;</span>])
        <span style="color: #008000; font-weight: bold">else</span>:
            <span style="color: #408080; font-style: italic"># Iteration complete</span>
            <span style="color: #008000">self</span><span style="color: #666666">.</span>write(<span style="color: #BA2121">&#39;&lt;/ul&gt;&#39;</span>)
            <span style="color: #008000">self</span><span style="color: #666666">.</span>finish()

db <span style="color: #666666">=</span> motor<span style="color: #666666">.</span>MotorClient()<span style="color: #666666">.</span>open_sync()<span style="color: #666666">.</span>test

application <span style="color: #666666">=</span> tornado<span style="color: #666666">.</span>web<span style="color: #666666">.</span>Application([
        (<span style="color: #BA2121">r&#39;/compose&#39;</span>, NewMessageHandler),
        (<span style="color: #BA2121">r&#39;/&#39;</span>, MessagesHandler)
    ], db<span style="color: #666666">=</span>db
)

<span style="color: #008000; font-weight: bold">print</span> <span style="color: #BA2121">&#39;Listening on http://localhost:8888&#39;</span>
application<span style="color: #666666">.</span>listen(<span style="color: #666666">8888</span>)
tornado<span style="color: #666666">.</span>ioloop<span style="color: #666666">.</span>IOLoop<span style="color: #666666">.</span>instance()<span style="color: #666666">.</span>start()
</pre></div>


<p>A full example is <a href="https://github.com/ajdavis/motor-blog">Motor-Blog</a>, a basic blog engine.</p>
<h1 id="support">Support</h1>
<p>For now, you can ask for help in the comments, or email me directly at <a href="mailto:jesse@10gen.com">jesse@10gen.com</a> if you have any questions or feedback. I'm going on Zencation July 25th through August 13; aside from that time I'll do my best to respond immediately.</p>
<h1 id="roadmap">Roadmap</h1>
<p>In the next few months I'll implement the PyMongo feature I'm missing, <a href="http://api.mongodb.org/python/current/api/gridfs/index.html">GridFS</a>, and make Motor work with all the Python versions Tornado does: Python 2.5, 2.6, 2.7, 3.2, and PyPy. (Only Python 2.7 is tested now.) Once the public alpha and beta stages have shaken out the bugs and revealed missing features, I hope Motor will be included as a module in the official PyMongo distribution.</p>
