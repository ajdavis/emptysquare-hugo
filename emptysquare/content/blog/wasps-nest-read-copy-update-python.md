+++
type = "post"
title = "Wasp's Nest: The Read-Copy-Update Pattern In Python"
date = "2013-05-08T22:47:45"
description = "A concurrency-control pattern that solves some reader-writer problems without mutexes."
"blog/category" = ["Mongo", "Programming", "Python"]
"blog/tag" = []
enable_lightbox = false
thumbnail = "paper-wasp-closeup@240.jpg"
draft = false
+++

<p><img style="display:block; margin-left:auto; margin-right:auto;" src="paper-wasp-closeup.jpg" alt="Paper Wasp" title="paper-wasp-closeup.jpg" border="0"   />
<a style="color: gray; font-style: italic" href="http://www.mzephotos.com/gallery/insects/paper-wasp.html">&copy; MzePhotos.com, Some Rights Reserved</a></p>
<p>In recent work on PyMongo, I used a concurrency-control pattern that solves a variety of <a href="http://en.wikipedia.org/wiki/Readers-writers_problem">reader-writer problem</a> without mutexes. It's similar to the <a href="http://en.wikipedia.org/wiki/Read-copy-update">read-copy-update</a> technique used extensively in the Linux kernel. I'm dubbing it the Wasp's Nest. Stick with me&mdash;by the end of this post you'll know a neat concurrency pattern, and have a good understanding of how PyMongo handles replica set failovers.</p>
<p><strong>Update:</strong> In this post's first version I didn't know how close my code is to "ready-copy-update". <a href="/blog/wasps-nest-read-copy-update-python/#comment-890288132">Robert Moore schooled me</a> in the comments. I also named it "a lock-free concurrency pattern" and <a href="/blog/wasps-nest-read-copy-update-python/#comment-892664861">Steve Baptiste pointed out</a> that I was using the term wrong. My algorithm merely solves a race condition without adding a mutex, it's not lock-free. I love this about blogging: in exchange for a little humility I get a serious education.</p>
<hr />
<ul>
<li><a href="#the-mission">The Mission</a></li>
<li><a href="#the-bugs">The Bugs</a></li>
<li><a href="#fixing-with-a-mutex">Fixing With A Mutex</a></li>
<li><a href="#and-why-its-not-ideal">...and why it's not ideal</a></li>
<li><a href="#the-wasps-nest-pattern">The Wasp's Nest Pattern</a></li>
</ul>
<h1 id="the-mission">The Mission</h1>

<p>MongoDB is deployed in "replica sets" of identical database servers. A replica set has one primary server and several read-only secondary servers. Over time a replica set's state can change. For example, if the primary's cooling fans fail and it bursts into flames, a secondary takes over as primary a few seconds later. Or a sysadmin can add another server to the set, and once it's synced up it becomes a new secondary.</p>
<p>I help maintain PyMongo, the Python driver for MongoDB. Its <code>MongoReplicaSetClient</code> is charged with connecting to the members of a set and knowing when the set changes state. Replica sets and PyMongo must avoid any single points of failure in the face of unreliable servers and networks&mdash;we must never assume any particular members of the set are available.</p>
<p>Consider this very simplified sketch of a <code>MongoReplicaSetClient</code>:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">class</span> <span style="color: #0000FF; font-weight: bold">Member</span>(<span style="color: #008000">object</span>):
    <span style="color: #BA2121; font-style: italic">&quot;&quot;&quot;Represents one server in the set.&quot;&quot;&quot;</span>
    <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">__init__</span>(<span style="color: #008000">self</span>, pool):
        <span style="color: #408080; font-style: italic"># The connection pool.</span>
        <span style="color: #008000">self</span><span style="color: #666666">.</span>pool <span style="color: #666666">=</span> pool

<span style="color: #008000; font-weight: bold">class</span> <span style="color: #0000FF; font-weight: bold">MongoReplicaSetClient</span>(<span style="color: #008000">object</span>):
    <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">__init__</span>(<span style="color: #008000">self</span>, seeds):
        <span style="color: #008000">self</span><span style="color: #666666">.</span>primary <span style="color: #666666">=</span> <span style="color: #008000">None</span>
        <span style="color: #008000">self</span><span style="color: #666666">.</span>members <span style="color: #666666">=</span> {}
        <span style="color: #008000">self</span><span style="color: #666666">.</span>refresh()

        <span style="color: #408080; font-style: italic"># The monitor calls refresh() every 30 sec.</span>
        <span style="color: #008000">self</span><span style="color: #666666">.</span>monitor <span style="color: #666666">=</span> MonitorThread(<span style="color: #008000">self</span>)

    <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">refresh</span>(<span style="color: #008000">self</span>):
        <span style="color: #408080; font-style: italic"># If we&#39;re already connected, use our list of known</span>
        <span style="color: #408080; font-style: italic"># members. Otherwise use the passed-in list of</span>
        <span style="color: #408080; font-style: italic"># possible members, the &#39;seeds&#39;.</span>
        seeds <span style="color: #666666">=</span> <span style="color: #008000">self</span><span style="color: #666666">.</span>members<span style="color: #666666">.</span>keys() <span style="color: #AA22FF; font-weight: bold">or</span> <span style="color: #008000">self</span><span style="color: #666666">.</span>seeds

        <span style="color: #408080; font-style: italic"># Try seeds until first success.</span>
        ismaster_response <span style="color: #666666">=</span> <span style="color: #008000">None</span>
        <span style="color: #008000; font-weight: bold">for</span> seed <span style="color: #AA22FF; font-weight: bold">in</span> seeds:
            <span style="color: #008000; font-weight: bold">try</span>:
                <span style="color: #408080; font-style: italic"># The &#39;ismaster&#39; command gets info</span>
                <span style="color: #408080; font-style: italic"># about the whole set.</span>
                ismaster_response <span style="color: #666666">=</span> call_ismaster(seed)
                <span style="color: #008000; font-weight: bold">break</span>
            <span style="color: #008000; font-weight: bold">except</span> socket<span style="color: #666666">.</span>error:
                <span style="color: #408080; font-style: italic"># Host down / unresolvable, try the next.</span>
                <span style="color: #008000; font-weight: bold">pass</span>

        <span style="color: #008000; font-weight: bold">if</span> <span style="color: #AA22FF; font-weight: bold">not</span> ismaster_response:
            <span style="color: #008000; font-weight: bold">raise</span> ConnectionFailure()

        <span style="color: #408080; font-style: italic"># Now we can discover the whole replica set.</span>
        <span style="color: #008000; font-weight: bold">for</span> host <span style="color: #AA22FF; font-weight: bold">in</span> ismaster_response[<span style="color: #BA2121">&#39;hosts&#39;</span>]:
            pool <span style="color: #666666">=</span> ConnectionPool(host)
            member <span style="color: #666666">=</span> Member(pool)
            <span style="color: #008000">self</span><span style="color: #666666">.</span>members[host] <span style="color: #666666">=</span> member

        <span style="color: #408080; font-style: italic"># Remove down members from dict.</span>
        <span style="color: #008000; font-weight: bold">for</span> host <span style="color: #AA22FF; font-weight: bold">in</span> <span style="color: #008000">self</span><span style="color: #666666">.</span>members<span style="color: #666666">.</span>keys():
            <span style="color: #008000; font-weight: bold">if</span> host <span style="color: #AA22FF; font-weight: bold">not</span> <span style="color: #AA22FF; font-weight: bold">in</span> ismaster_response[<span style="color: #BA2121">&#39;hosts&#39;</span>]:
                <span style="color: #008000">self</span><span style="color: #666666">.</span>members<span style="color: #666666">.</span>pop(host)

        <span style="color: #008000">self</span><span style="color: #666666">.</span>primary <span style="color: #666666">=</span> ismaster_response<span style="color: #666666">.</span>get(<span style="color: #BA2121">&#39;primary&#39;</span>)

    <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">send_message</span>(<span style="color: #008000">self</span>, message):
        <span style="color: #408080; font-style: italic"># Send an &#39;insert&#39;, &#39;update&#39;, or &#39;delete&#39;</span>
        <span style="color: #408080; font-style: italic"># message to the primary.</span>
        <span style="color: #008000; font-weight: bold">if</span> <span style="color: #AA22FF; font-weight: bold">not</span> <span style="color: #008000">self</span><span style="color: #666666">.</span>primary:
            <span style="color: #008000">self</span><span style="color: #666666">.</span>refresh()

        member <span style="color: #666666">=</span> <span style="color: #008000">self</span><span style="color: #666666">.</span>members[<span style="color: #008000">self</span><span style="color: #666666">.</span>primary]
        pool <span style="color: #666666">=</span> member<span style="color: #666666">.</span>pool
        <span style="color: #008000; font-weight: bold">try</span>:
            send_message_with_pool(message, pool)
        <span style="color: #008000; font-weight: bold">except</span> socket<span style="color: #666666">.</span>error:
            <span style="color: #008000">self</span><span style="color: #666666">.</span>primary <span style="color: #666666">=</span> <span style="color: #008000">None</span>
            <span style="color: #008000; font-weight: bold">raise</span> AutoReconnect()
</pre></div>


<p>We don't know which members will be available when our application starts, so we pass a "seed list" of hostnames to the <code>MongoReplicaSetClient</code>. In <code>refresh</code>, the client tries them all until it can connect to one and run the <code>isMaster</code> command, which returns <a href="http://docs.mongodb.org/manual/reference/command/isMaster/#replica-sets">information about all the members in the replica set</a>. The client then makes a connection-pool for each member and records which one is the primary.</p>
<p>Once <code>refresh</code> finishes, the client starts a <code>MonitorThread</code> which calls <code>refresh</code> again every 30 seconds. This ensures that if we add a secondary to the set it will be discovered soon and participate in load-balancing. If a secondary goes down, <code>refresh</code> removes it from <code>self.members</code>. In <code>send_message</code>, if we discover the primary's down, we raise an error and clear <code>self.primary</code> so we'll call <code>refresh</code> the next time <code>send_message</code> runs.</p>
<h1 id="the-bugs">The Bugs</h1>

<p>PyMongo 2.1 through 2.5 had two classes of concurrency bugs: race conditions and thundering herds.</p>
<p>The race condition is easy to see. Look at the expression <code>self.members[self.primary]</code> in <code>send_message</code>. If the monitor thread runs <code>refresh</code> and pops a member from <code>self.members</code> while an application thread is executing the dictionary lookup, the latter could get a <code>KeyError</code>. Indeed, that is <a href="https://jira.mongodb.org/browse/PYTHON-467">exactly the bug report</a> we received that prompted my whole investigation and this blog post.</p>
<p>The other bug causes a big waste of effort. Let's say the primary server bursts into flames. The client gets a socket error and clears <code>self.primary</code>. Then a bunch of application threads all call <code>send_message</code> at once. They all find that <code>self.primary</code> is <code>None</code>, and all call <code>refresh</code>. This is a duplication of work that only one thread need do. Depending how many processes and threads we have, it has the potential to create a connection storm in our replica set as a bunch of heavily-loaded applications lurch to the new primary. It also compounds the race condition because many threads are all modifying the shared state. I'm calling this duplicated work a <a href="http://en.wikipedia.org/wiki/Thundering_herd_problem">thundering herd problem</a>, although the official definition of thundering herd is a bit different.</p>
<h1 id="fixing-with-a-mutex">Fixing With A Mutex</h1>

<p>We know how to fix race conditions: let's add a mutex! We could lock around the whole body of <code>refresh</code>, and lock around the expression <code>self.members[self.primary]</code> in <code>send_message</code>. No thread sees <code>members</code> and <code>primary</code> in a half-updated state.</p>
<h2 id="and-why-its-not-ideal">...and why it's not ideal</h2>

<p>This solution has two problems. The first is minor: the slight cost of acquiring and releasing a lock for every message sent to MongoDB, especially since it means only one thread can run that section of <code>send_message</code> at a time. A <a href="http://en.wikipedia.org/wiki/Readers%E2%80%93writer_lock">reader-writer lock</a> alleviates the contention by allowing many threads to run <code>send_message</code> as long as no thread is running <code>refresh</code>, in exchange for greater complexity and cost for the single-threaded case.</p>
<p>The worse problem is the behavior such a mutex would cause in a very heavily multithreaded application. While one thread is running <code>refresh</code>, all threads running <code>send_message</code> will queue on the mutex. If the load is heavy enough our application could fail while waiting for <code>refresh</code>, or could overwhelm MongoDB once they're all simultaneously unblocked. Better under most circumstances for <code>send_message</code> to fail fast, saying "I don't know who the primary is, and I'm not going to wait for <code>refresh</code> to tell me." Failing fast raises more errors but keeps the queues small.</p>
<h1 id="the-wasps-nest-pattern">The Wasp's Nest Pattern</h1>

<p>There's a better way, one that requires no locks, is less error-prone, and fixes the thundering-herd problem too. Here's what I did for PyMongo 2.5.1, which we'll release next week.</p>
<p>First, all information about the replica set's state is pulled out of <code>MongoReplicaSetClient</code> and put into an <code>RSState</code> object:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">class</span> <span style="color: #0000FF; font-weight: bold">RSState</span>(<span style="color: #008000">object</span>):
    <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">__init__</span>(<span style="color: #008000">self</span>, members, primary):
        <span style="color: #008000">self</span><span style="color: #666666">.</span>members <span style="color: #666666">=</span> members
        <span style="color: #008000">self</span><span style="color: #666666">.</span>primary <span style="color: #666666">=</span> primary
</pre></div>


<p><code>MongoReplicaSetClient</code> gets one <code>RSState</code> instance that it puts in <code>self.rsstate</code>. This instance is immutable: no thread is allowed to change the contents, only to make a modified copy. So if the primary goes down, <code>refresh</code> doesn't just set <code>primary</code> to <code>None</code> and pop its hostname from the <code>members</code> dict. Instead, it makes a deep copy of the <code>RSState</code>, and updates the copy. Finally, it replaces the old <code>self.rsstate</code> with the new one.</p>
<p>Each of the <code>RSState</code>'s attributes must be immutable and cloneable, too, which requires a very different mindset. For example, I'd been tracking each member's ping time using a 5-sample moving average and updating it with a new sample like so:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">class</span> <span style="color: #0000FF; font-weight: bold">Member</span>(<span style="color: #008000">object</span>):
    <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">add_sample</span>(<span style="color: #008000">self</span>, ping_time):
        <span style="color: #008000">self</span><span style="color: #666666">.</span>samples <span style="color: #666666">=</span> <span style="color: #008000">self</span><span style="color: #666666">.</span>samples[<span style="color: #666666">-4</span>:]
        <span style="color: #008000">self</span><span style="color: #666666">.</span>samples<span style="color: #666666">.</span>append(ping_time)
        <span style="color: #008000">self</span><span style="color: #666666">.</span>avg_ping <span style="color: #666666">=</span> <span style="color: #008000">sum</span>(<span style="color: #008000">self</span><span style="color: #666666">.</span>samples) <span style="color: #666666">/</span> <span style="color: #008000">len</span>(<span style="color: #008000">self</span><span style="color: #666666">.</span>samples)
</pre></div>


<p>But if <code>Member</code> is immutable, then adding a sample means cloning the whole <code>Member</code> and updating it. Like this:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">class</span> <span style="color: #0000FF; font-weight: bold">Member</span>(<span style="color: #008000">object</span>):
    <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">clone_with_sample</span>(<span style="color: #008000">self</span>, ping_time):
        <span style="color: #408080; font-style: italic"># Make a new copy of &#39;samples&#39;</span>
        samples <span style="color: #666666">=</span> <span style="color: #008000">self</span><span style="color: #666666">.</span>samples[<span style="color: #666666">-4</span>:] <span style="color: #666666">+</span> [ping_time]
        <span style="color: #008000; font-weight: bold">return</span> Member(samples)
</pre></div>


<p>Any method that needs to access <code>self.rsstate</code> more than once must protect itself against the state being replaced concurrently. It has to make a local copy of the reference. So the racy expression in <code>send_message</code> becomes:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">rsstate <span style="color: #666666">=</span> <span style="color: #008000">self</span><span style="color: #666666">.</span>rsstate  <span style="color: #408080; font-style: italic"># Copy reference.</span>
member <span style="color: #666666">=</span> rsstate<span style="color: #666666">.</span>members[rsstate<span style="color: #666666">.</span>primary]
</pre></div>


<p>Since the <code>rsstate</code> cannot be modified by another thread, <code>send_message</code> knows its local reference to the state is safe to read.</p>
<p>A few summers ago I was on a Zen retreat in a rural house. We had paper wasps building nests under the eaves. The wasps make their paper from a combination of chewed-up plant fiber and saliva. The nest hangs from a single skinny petiole. It's precarious, but it seems to protect the nest from ants who want to crawl in and eat the larvae. The queen <a href="http://link.springer.com/content/pdf/10.1007%2FBF01253903.pdf">periodically spreads an ant-repellant secretion around the petiole</a>; its slenderness conserves her ant-repellant, and concentrates it in a small area.</p>
<p><img style="display:block; margin-left:auto; margin-right:auto;" src="wasp-nest-bob-p.jpg" alt="Wasp's Nest in Situ" title="wasp-nest-bob-p.jpg" border="0"   />
<span style="color:gray; font-style: italic"><a href="http://www.flickr.com/photos/pondapple/6134653740/">[Source]</a></span></p>
<p>I think of the <code>RSState</code> like a wasp's nest: it's an intricate structure hanging off the <code>MongoReplicaSetClient</code> by a single attribute, <code>self.rsstate</code>. The slenderness of the connection protects <code>send_message</code> from race conditions, just as the thin petiole protects the nest from ants.</p>
<p>Since I was fixing the race condition I fixed the thundering herd as well. Only one thread should run <code>refresh</code> after a primary goes down, and all other threads should benefit from its labor. I nominated the monitor to be that one thread:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">class</span> <span style="color: #0000FF; font-weight: bold">MonitorThread</span>(threading<span style="color: #666666">.</span>Thread):
    <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">__init__</span>(<span style="color: #008000">self</span>, client):
        threading<span style="color: #666666">.</span>Thread<span style="color: #666666">.</span>__init__(<span style="color: #008000">self</span>)
        <span style="color: #008000">self</span><span style="color: #666666">.</span>client <span style="color: #666666">=</span> weakref<span style="color: #666666">.</span>proxy(client)
        <span style="color: #008000">self</span><span style="color: #666666">.</span>event <span style="color: #666666">=</span> threading<span style="color: #666666">.</span>Event()
        <span style="color: #008000">self</span><span style="color: #666666">.</span>refreshed <span style="color: #666666">=</span> threading<span style="color: #666666">.</span>Event()

    <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">schedule_refresh</span>(<span style="color: #008000">self</span>):
        <span style="color: #BA2121; font-style: italic">&quot;&quot;&quot;Refresh immediately.&quot;&quot;&quot;</span>
        <span style="color: #008000">self</span><span style="color: #666666">.</span>refreshed<span style="color: #666666">.</span>clear()
        <span style="color: #008000">self</span><span style="color: #666666">.</span>event<span style="color: #666666">.</span>set()

    <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">wait_for_refresh</span>(<span style="color: #008000">self</span>, timeout_seconds):
        <span style="color: #BA2121; font-style: italic">&quot;&quot;&quot;Block until refresh completes.&quot;&quot;&quot;</span>
        <span style="color: #008000">self</span><span style="color: #666666">.</span>refreshed<span style="color: #666666">.</span>wait(timeout_seconds)

    <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">run</span>(<span style="color: #008000">self</span>):
        <span style="color: #008000; font-weight: bold">while</span> <span style="color: #008000">True</span>:
            <span style="color: #008000">self</span><span style="color: #666666">.</span>event<span style="color: #666666">.</span>wait(timeout<span style="color: #666666">=30</span>)
            <span style="color: #008000">self</span><span style="color: #666666">.</span>event<span style="color: #666666">.</span>clear()

            <span style="color: #008000; font-weight: bold">try</span>:
                <span style="color: #008000; font-weight: bold">try</span>:
                    <span style="color: #008000">self</span><span style="color: #666666">.</span>client<span style="color: #666666">.</span>refresh()
                <span style="color: #008000; font-weight: bold">finally</span>:
                    <span style="color: #008000">self</span><span style="color: #666666">.</span>refreshed<span style="color: #666666">.</span>set()
            <span style="color: #008000; font-weight: bold">except</span> AutoReconnect:
                <span style="color: #008000; font-weight: bold">pass</span>
            <span style="color: #008000; font-weight: bold">except</span>:
                <span style="color: #408080; font-style: italic"># Client was garbage-collected.</span>
                <span style="color: #008000; font-weight: bold">break</span>
</pre></div>


<p>(The weakref proxy prevents a reference cycle and lets the thread die when the client is deleted. The weird try-finally syntax is necessary in Python 2.4.)</p>
<p>The monitor normally wakes every 30 seconds to notice changes in the set, like a new secondary being added. If <code>send_message</code> discovers that the primary is gone, it wakes the monitor early by signaling the event it's waiting on:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">rsstate <span style="color: #666666">=</span> <span style="color: #008000">self</span><span style="color: #666666">.</span>rsstate
<span style="color: #008000; font-weight: bold">if</span> <span style="color: #AA22FF; font-weight: bold">not</span> rsstate<span style="color: #666666">.</span>primary:
    <span style="color: #008000">self</span><span style="color: #666666">.</span>monitor<span style="color: #666666">.</span>schedule_refresh()
    <span style="color: #008000; font-weight: bold">raise</span> AutoReconnect()
</pre></div>


<p>No matter how many threads call <code>schedule_refresh</code>, the work is only done once.</p>
<p>Any <code>MongoReplicaSetClient</code> method that needs to block on <code>refresh</code> can wait for the "refreshed" event:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">rsstate <span style="color: #666666">=</span> <span style="color: #008000">self</span><span style="color: #666666">.</span>rsstate
<span style="color: #008000; font-weight: bold">if</span> <span style="color: #AA22FF; font-weight: bold">not</span> rsstate<span style="color: #666666">.</span>primary:
    <span style="color: #008000">self</span><span style="color: #666666">.</span>monitor<span style="color: #666666">.</span>schedule_refresh()
    <span style="color: #008000">self</span><span style="color: #666666">.</span>monitor<span style="color: #666666">.</span>wait_for_refresh(timeout_seconds<span style="color: #666666">=5</span>)

<span style="color: #408080; font-style: italic"># Get the new state.</span>
rsstate <span style="color: #666666">=</span> <span style="color: #008000">self</span><span style="color: #666666">.</span>rsstate
<span style="color: #008000; font-weight: bold">if</span> <span style="color: #AA22FF; font-weight: bold">not</span> rsstate<span style="color: #666666">.</span>primary:
    <span style="color: #008000; font-weight: bold">raise</span> AutoReconnect()

<span style="color: #408080; font-style: italic"># Proceed normally....</span>
</pre></div>


<p>This pattern mitigates the connection storm from a heavily-loaded application discovering that the primary has changed: only the monitor thread goes looking for the new primary. The others can abort or wait.</p>
<p>The wasp's nest pattern is a simple and high-performance solution to some varieties of reader-writer problem. Compared to mutexes it's easy to understand, and most importantly it's easy to program correctly. For further reading see <a href="https://github.com/mongodb/mongo-python-driver/blob/02b318f9f2cac30c268aa94f2c3d71333409c41f/pymongo/mongo_replica_set_client.py#L109">my notes in the source code</a>.</p>
<p><img style="display:block; margin-left:auto; margin-right:auto;" src="wasps-nest.jpg" alt="Paper wasp and nest" title="wasps-nest.jpg" border="0"   />
<span style="color:gray; font-style: italic"><a href="http://rescuebugblog.typepad.com/rescue_bugblog/2008/10/why-wednesday-1.html">[Source]</a></span></p>
    