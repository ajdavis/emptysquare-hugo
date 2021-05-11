+++
type = "post"
title = "How To Hobble Your Python Web-Scraper With getaddrinfo()"
date = "2016-01-31T22:54:39"
description = "I discover that contention for the getaddrinfo lock on Mac makes it appear that connecting to localhost times out."
category = ["Python", "MongoDB", "Programming", "Motor"]
tag = ["getaddrinfo"]
enable_lightbox = false
thumbnail = "lunardo-fero-1.jpg"
draft = false
disqus_identifier = "/blog/mac-python-getaddrinfo-queueing"
disqus_url = "https://emptysqua.re/blog//blog/mac-python-getaddrinfo-queueing/"
+++

<p><img alt="" src="medieval.jpg" /></p>
<p>This is the second article in what seems destined to be <a href="/getaddrinfo-on-macosx">a four-part series about Python's <code>getaddrinfo</code> on Mac</a>. Here, I discover that contention for the <code>getaddrinfo</code> lock makes connecting to localhost appear to time out.</p>
<h1 id="network-timeouts-from-asyncio">Network Timeouts From asyncio</h1>
<p>A Washington Post data scientist named <a href="https://twitter.com/aljohri">Al Johri</a> posted to the MongoDB User Group list, asking for help with a Python script. His script downloaded feeds from 500 sites concurrently and stored the feeds' links in MongoDB. Since this is the sort of problem async is good for, he used my async driver Motor. He'd chosen to implement his feed-fetcher on <code>asyncio</code>, with Motor's new <code>asyncio</code> integration and <a href="https://twitter.com/andrew_svetlov">Andrew Svetlov</a>'s <code>aiohttp</code> library.</p>
<p>Al wrote:</p>
<blockquote>
<p>Each feed has a variable number of articles (average 10?). So it should launch around 5000+ "concurrent" requests to insert into the database. I put concurrent in quotes because it's sending the insert requests as the downloads come in so it really shouldn't be that many requests per second. I understand PyMongo should be able to do at least 20k-30k plus?</p>
</blockquote>
<p>He's right. And yet, <strong>Motor threw connection timeouts</strong> every time he ran his script. What was going wrong with Motor?</p>
<h1 id="three-clues">Three Clues</h1>
<p>It was a Saturday afternoon when I saw Al's message to the mailing list; I wanted to leave it until Monday, but I couldn't stand the anxiety. What if my driver was buggy?</p>
<p>In Al's message I saw three clues. The first clue was, Motor made its initial connection to MongoDB without trouble, but while the script downloaded feeds and inserted links into the database, Motor began throwing timeouts. Since Motor was already connected to MongoDB, and since MongoDB was running on the same machine as his code, it seemed it must be a Motor bug.</p>
<blockquote>
<p>I feel like what I'm trying to accomplish really shouldn't be this hard.</p>
</blockquote>
<p>Al's code also threw connection errors from <code>aiohttp</code>, but this was less surprising than Motor's errors, since it was fetching from remote servers. Still, I noted this as a possible second clue.</p>
<p>The third clue was this: If Al turned his script's concurrency down from 500 feeds to 150 or less, Motor stopped timing out. Why?</p>
<p><img alt="" src="lunardo-fero-1.jpg" /></p>
<h1 id="investigation">Investigation</h1>
<p>On Sunday, I ran Al's script on my Mac and reproduced the Motor errors. This was a relief, of course. A reproducible bug is a tractable one.</p>
<p>With some print statements and PyCharm, I determined that Motor occasionally expands its connection pool in order to increase its "insert" concurrency. That's when the errors happen.</p>
<p>I reviewed my connection-pool tests and verified that Motor can expand its connection pool under normal circumstances. So <code>aiohttp</code> must be fighting with Motor somehow.</p>
<p>I tracked down the location of the timeout to this line in the <code>asyncio</code> event loop, where it begins a DNS lookup on its thread pool:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">create_connection</span>(<span style="color: #008000">self</span>):
    executor <span style="color: #666666">=</span> <span style="color: #008000">self</span><span style="color: #666666">.</span>thread_pool_executor

    <span style="color: #008000; font-weight: bold">yield from</span> executor<span style="color: #666666">.</span>submit(
        socket<span style="color: #666666">.</span>getaddrinfo, 
        host, port, family, <span style="color: #008000">type</span>, proto, flags)
</pre></div>


<p>Motor's first <code>create_connection</code> call always succeeded, but later calls sometimes timed out.</p>
<p>I wondered what the holdup was in the thread pool. So I printed its queue size before the <code>getaddrinfo</code> call:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #408080; font-style: italic"># Ensure it&#39;s initialized.</span>
<span style="color: #008000; font-weight: bold">if</span> <span style="color: #008000">self</span><span style="color: #666666">.</span>_default_executor:
    q <span style="color: #666666">=</span> <span style="color: #008000">self</span><span style="color: #666666">.</span>_default_executor<span style="color: #666666">.</span>_work_queue

    <span style="color: #008000">print</span>(<span style="color: #BA2121">&quot;unfinished tasks: %d&quot;</span> <span style="color: #666666">%</span> 
          q<span style="color: #666666">.</span>unfinished_tasks)
</pre></div>


<p>There were hundreds of unfinished tasks! Why were these lookups getting clogged? I tried increasing the thread pool size, from the <code>asyncio</code> default of 5, to 50, to 500....but the timeouts happened just the same.</p>
<p><img alt="" src="lunardo-fero-3.jpg" /></p>
<h1 id="eureka">Eureka</h1>
<p>I thought about the problem as I made dinner, I thought about it as I fell asleep, I thought about it while I was walking to the subway Monday morning in December's unseasonable warmth.</p>
<p>I recalled a PyMongo investigation where <a href="/getaddrinfo-deadlock/">Anna Herlihy and I had explored CPython's getaddrinfo lock</a>: On Mac, Python only allows one <code>getaddrinfo</code> call at a time. I was climbing the stairs out of the Times Square station near the office when I figured it out: Al's script was queueing on that <code>getaddrinfo</code> lock!</p>
<h1 id="diagnosis">Diagnosis</h1>
<p>When Motor opens a new connection to the MongoDB server, it starts a 20-second timer, then calls <code>create_connection</code> with the server address. If hundreds of other <code>getaddrinfo</code> calls are already enqueued, then Motor's call can spend more than 20 seconds waiting in line for the <code>getaddrinfo</code> lock. It doesn't matter that looking up "localhost" is near-instant: we need the lock first. It appears as if Motor can't connect to MongoDB, when in fact it simply couldn't get the <code>getaddrinfo</code> lock in time.</p>
<p>My theory explains the first clue: that Motor's initial connection succeeds. 
In the case of Al's script, specifically, Motor opens its first connection before <code>aiohttp</code> begins its hundreds of lookups, so there's no queue on the lock yet.</p>
<p>Then <code>aiohttp</code> starts 500 calls to <code>getaddrinfo</code> for the 500 feeds' domains. As feeds are fetched it inserts them into MongoDB.</p>
<p>There comes a moment when the script begins an insert while another insert is in progress. When this happens, Motor tries to open a new MongoDB connection to start the second insert concurrently. That's when things go wrong: since <code>aiohttp</code> has hundreds of <code>getaddrinfo</code> calls still in progress, Motor's new connection gets enqueued, waiting for the lock so it can resolve "localhost" again. After 20 seconds it gives up. Meanwhile, dozens of other Motor connections have piled up behind this one, and as they reach their 20-second timeouts they fail too.</p>
<p>Motor's not the only one suffering, of course. The <code>aiohttp</code> coroutines are all waiting in line, too. So my theory explained the second clue: the <code>aiohttp</code> errors were also caused by queueing on the <code>getaddrinfo</code> lock.</p>
<p>What about the third clue? Why does turning concurrency down to 150 fix the problem? My theory explains that, too. The first 150 hostnames in Al's list of feeds can all be resolved in under 20 seconds total. When Motor opens a connection it is certainly slow, but it doesn't time out.</p>
<p style="text-align: center"><img src="lunardo-fero-5.jpg" style="max-width: 300px; margin:auto"></p>

<h1 id="verification">Verification</h1>
<p>An explanatory theory is good, but experimental evidence is even better. I designed three tests for my hypothesis.</p>
<p>First, I tried Al's script on Linux. The Python interpreter doesn't lock around <code>getaddrinfo</code> calls on Linux, so a large number of in-flight lookups shouldn't slow down Motor very much when it needs to resolve "localhost". Indeed, on Linux the script worked fine, and Motor could expand its connection pool easily.</p>
<p>Second, on my Mac, I tried setting Motor's maximum pool size to 1. This prevented Motor from trying to open more connections after the script began the feed-fetcher, so Motor never got stuck in line behind the fetcher. Capping the pool size at 1 didn't cost any performance in this application, since the script spent so little time writing to MongoDB compared to the time it spent fetching and parsing feeds.</p>
<p>For my third experiment, I patched the <code>asyncio</code> event loop to always resolve "localhost" to "127.0.0.1", skipping the <code>getaddrinfo</code> call. This also worked as I expected.</p>
<p><img alt="" src="lunardo-fero-2.jpg" /></p>
<h1 id="solution">Solution</h1>
<p>I wrote back to Al Johri with my findings. His response made my day:</p>
<blockquote>
<p>Holy crap, thank you so much. This is amazing!</p>
</blockquote>
<p>I wish bug investigations always turned out this well.</p>
<p>But still&mdash;all I'd done was diagnose the problem. How should I solve it? 
Motor could cache lookups, or treat "localhost" specially. Or <code>asyncio</code> could make one of those changes instead of Motor. Or perhaps the <code>asyncio</code> method <code>create_connection</code> should take a connection timeout argument, since <code>asyncio</code> can tell the difference between a slow call to <code>getaddrinfo</code> and a genuine connection timeout.</p>
<p>Which solution did I choose? Stay tuned for the next installment!</p>
<hr />
<p><strong>Links:</strong></p>
<ol>
<li><a href="https://groups.google.com/d/topic/mongodb-user/2oK6C3BrVKI/discussion">The original bug report on the MongoDB User Group list.</a></li>
<li><a href="https://hg.python.org/cpython/file/d2b8354e87f5/Modules/socketmodule.c#l185">Python's getaddrinfo lock.</a></li>
<li><a href="/getaddrinfo-on-macosx/">The full series on getaddrinfo on Mac</a></li>
</ol>
<hr />
<p>Images: Lunardo Fero, embroidery designs, Italy circa 1559. From <em>Fashion and Virtue: Textile Patterns and the Print Revolution 1520&ndash;1620</em>, by Femke Speelberg.</p>
<p style="text-align: center"><img src="lunardo-fero-4.jpg" style="max-width: 300px; margin:auto"></p>
