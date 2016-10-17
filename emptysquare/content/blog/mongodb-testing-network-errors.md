+++
type = "post"
title = "Testing Network Errors With MongoDB"
date = "2014-03-20T21:33:50"
description = "A little-known method for simulating a temporary outage with MongoDB."
"blog/category" = ["Mongo", "Programming"]
"blog/tag" = []
enable_lightbox = false
draft = false
legacyid = "532b9397539374726c12b367"
+++

<p>Someone asked on Twitter today for a way to trigger a connection failure between MongoDB and the client. This would be terribly useful when you're testing your application's handling of network hiccups.</p>
<p>You have options: you could use <a href="http://www.kchodorow.com/blog/2011/04/20/simulating-network-paritions-with-mongobridge/">mongobridge</a> to proxy between the client and the server, and at just the right moment, kill mongobridge.</p>
<p>Or you could use packet-filtering tools to accomplish the same: <a href="https://help.ubuntu.com/community/IptablesHowTo">iptables</a> on Linux and <a href="https://developer.apple.com/library/mac/documentation/Darwin/Reference/ManPages/man8/ipfw.8.html">ipfw</a> or <a href="https://developer.apple.com/library/mac/documentation/Darwin/Reference/ManPages/man8/pfctl.8.html">pfctl</a> on Mac and BSD. You could use one of these tools to block MongoDB's port at the proper moment, and unblock it afterward.</p>
<p>There's yet another option, not widely known, that you might find simpler: use a MongoDB "failpoint" to break your connection.</p>
<p>Failpoints are our internal mechanism for triggering faults in MongoDB so we can test their consequences. <a href="http://www.kchodorow.com/blog/2011/04/20/simulating-network-paritions-with-mongobridge/">Read about them on Kristina's blog</a>. They're not meant for public consumption, so you didn't hear about it from me.</p>
<p>The first step is to start MongoDB with the special command-line argument:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">mongod --setParameter enableTestCommands=1
</pre></div>


<p>Next, log in with the <code>mongo</code> shell and tell the server to abort the next two network operations:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">&gt; db.adminCommand({
...   configureFailPoint: &#39;throwSockExcep&#39;,
...   mode: {times: 2}
... })
2014-03-20T20:31:42.162-0400 trying reconnect to 127.0.0.1:27017 (127.0.0.1) failed
</pre></div>


<p>The server obeys you instantly, before it even replies, so the command itself appears to fail. But fear not: you've simply seen the first of the two network errors you asked for. You can trigger the next error with any operation:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">&gt; db.collection.count()
2014-03-20T20:31:48.485-0400 trying reconnect to 127.0.0.1:27017 (127.0.0.1) failed
</pre></div>


<p>The third operation succeeds:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">&gt; db.collection.count()
2014-03-20T21:07:38.742-0400 trying reconnect to 127.0.0.1:27017 (127.0.0.1) failed
2014-03-20T21:07:38.742-0400 reconnect 127.0.0.1:27017 (127.0.0.1) ok
1
</pre></div>


<p>There's a final "failed" message that I don't understand, but the shell reconnects and the command returns the answer, "1".</p>
<p>You could use this failpoint when testing a driver or an application. If you don't know exactly how many operations you need to break, you could set <code>times</code> to 50 and, at the end of your test, continue attempting to reconnect until you succeed.</p>
<p>Ugly, perhaps, but if you want a simple way to cause a network error this could be a reasonable approach.</p>
    