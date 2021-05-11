+++
type = "post"
title = "A Curious Concurrency Case"
date = "2013-03-03T16:14:09"
description = "A subtle performance bug in the MongoDB Ruby driver's connection pool."
category = ["MongoDB", "Programming"]
tag = ["ruby"]
enable_lightbox = false
thumbnail = "percentage-unused-sockets.png"
draft = false
disqus_identifier = "5133b83353937431d6bf0c88"
disqus_url = "https://emptysqua.re/blog/5133b83353937431d6bf0c88/"
+++

<p>Last month, the team in charge of 10gen's Ruby driver for MongoDB ran into a few concurrency bugs, reported by a customer running the driver in JRuby with a large number of threads and connections. I've barely written a line of Ruby in my life, but <a href="/what-its-like-to-work-for-10gen/">I jumped in to help for a week</a> anyway.</p>
<p>I helped spot a very interesting performance bug in the driver's connection pool. The fix was easy, but thoroughly characterizing the bug turned out to be complex. Here's a record of my investigation.</p>
<hr />
<p>The Ruby driver's pool assigns a socket to a thread when the thread first calls <code>checkout</code>, and that thread stays pinned to its socket for life. Until the pool reaches its configured <code>max_size</code>, each new thread has a bespoke socket created for it. Additional threads are assigned random existing sockets. When a thread next calls <code>checkout</code>, if its socket's in use (by another thread) the requesting thread waits in a queue.</p>
<p>Here's a simplified version of the pool:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">class</span> <span style="color: #0000FF; font-weight: bold">Pool</span>
  <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">initialize</span>(max_size)
    <span style="color: #19177C">@max_size</span>       <span style="color: #666666">=</span> max_size
    <span style="color: #19177C">@sockets</span>        <span style="color: #666666">=</span> <span style="color: #666666">[]</span>
    <span style="color: #19177C">@checked_out</span>    <span style="color: #666666">=</span> <span style="color: #666666">[]</span>
    <span style="color: #19177C">@thread_to_sock</span> <span style="color: #666666">=</span> {}
    <span style="color: #19177C">@lock</span>           <span style="color: #666666">=</span> <span style="color: #880000">Mutex</span><span style="color: #666666">.</span>new
    <span style="color: #19177C">@queue</span>          <span style="color: #666666">=</span> <span style="color: #880000">ConditionVariable</span><span style="color: #666666">.</span>new
  <span style="color: #008000; font-weight: bold">end</span>

  <span style="color: #408080; font-style: italic"># Check out an existing socket or create a</span>
  <span style="color: #408080; font-style: italic"># new socket if max_size not exceeded.</span>
  <span style="color: #408080; font-style: italic"># Otherwise, wait for the next socket.</span>
  <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">checkout</span>
    tid <span style="color: #666666">=</span> <span style="color: #880000">Thread</span><span style="color: #666666">.</span>current<span style="color: #666666">.</span>object_id
    <span style="color: #008000">loop</span> <span style="color: #008000; font-weight: bold">do</span>
      <span style="color: #19177C">@lock</span><span style="color: #666666">.</span>synchronize <span style="color: #008000; font-weight: bold">do</span>
        <span style="color: #008000; font-weight: bold">if</span> sock <span style="color: #666666">=</span> <span style="color: #19177C">@thread_to_sock</span><span style="color: #666666">[</span>tid<span style="color: #666666">]</span>

          <span style="color: #408080; font-style: italic"># Thread wants its prior socket</span>
          <span style="color: #008000; font-weight: bold">if</span> <span style="color: #666666">!</span><span style="color: #19177C">@checked_out</span><span style="color: #666666">.</span>include?(sock)
            <span style="color: #408080; font-style: italic"># Acquire the socket</span>
            <span style="color: #19177C">@checked_out</span> <span style="color: #666666">&lt;&lt;</span> sock
            <span style="color: #008000; font-weight: bold">return</span> sock
          <span style="color: #008000; font-weight: bold">end</span>

        <span style="color: #008000; font-weight: bold">else</span>

          <span style="color: #008000; font-weight: bold">if</span> <span style="color: #19177C">@sockets</span><span style="color: #666666">.</span>size <span style="color: #666666">&lt;</span> <span style="color: #19177C">@max_size</span>

            <span style="color: #408080; font-style: italic"># Assign new socket to thread</span>
            sock <span style="color: #666666">=</span> create_connection
            <span style="color: #19177C">@thread_to_sock</span><span style="color: #666666">[</span>tid<span style="color: #666666">]</span> <span style="color: #666666">=</span> sock
            <span style="color: #008000; font-weight: bold">return</span> sock

          <span style="color: #008000; font-weight: bold">elsif</span> <span style="color: #19177C">@checked_out</span><span style="color: #666666">.</span>size <span style="color: #666666">&lt;</span> <span style="color: #19177C">@sockets</span><span style="color: #666666">.</span>size

            <span style="color: #408080; font-style: italic"># Assign random socket to thread</span>
            sock <span style="color: #666666">=</span> available<span style="color: #666666">[</span><span style="color: #008000">rand</span>(available<span style="color: #666666">.</span>length)<span style="color: #666666">]</span>
            <span style="color: #19177C">@thread_to_sock</span><span style="color: #666666">[</span>tid<span style="color: #666666">]</span> <span style="color: #666666">=</span> sock
            <span style="color: #008000; font-weight: bold">return</span> sock

          <span style="color: #008000; font-weight: bold">end</span>

        <span style="color: #008000; font-weight: bold">end</span>

        <span style="color: #408080; font-style: italic"># Release lock, wait to try again</span>
        <span style="color: #19177C">@queue</span><span style="color: #666666">.</span>wait(<span style="color: #19177C">@lock</span>)
      <span style="color: #008000; font-weight: bold">end</span>
    <span style="color: #008000; font-weight: bold">end</span>
  <span style="color: #008000; font-weight: bold">end</span>

  <span style="color: #408080; font-style: italic"># Return a socket to the pool.</span>
  <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">checkin</span>(socket)
    <span style="color: #19177C">@lock</span><span style="color: #666666">.</span>synchronize <span style="color: #008000; font-weight: bold">do</span>
      <span style="color: #19177C">@checked_out</span><span style="color: #666666">.</span>delete(socket)
      <span style="color: #19177C">@queue</span><span style="color: #666666">.</span>signal
    <span style="color: #008000; font-weight: bold">end</span>
  <span style="color: #008000; font-weight: bold">end</span>
<span style="color: #008000; font-weight: bold">end</span>
</pre></div>


<p>When a thread returns a socket, it signals the queue and wakes the next thread in line. That thread goes to the top of the loop and tries again to acquire its socket. The bug is in <code>checkin</code>: if the next thread in the queue is waiting for a <strong>different</strong> socket than the one just checked in, it may fail to acquire its socket, and it will sleep again.</p>
<p>When I first saw this I thought there must be the possibility of a deadlock. After all, if threads sometimes call <code>checkin</code> without really waking other threads, mustn't there come a time when everyone's waiting and no one has a socket?</p>
<p>I wrote a Python script to simulate the Ruby pool and ran it for a few thousand ticks, with various numbers of threads and sockets. It never deadlocked.</p>
<p>So I had to stop coding and start thinking.</p>
<hr />
<p>Let's say there are N threads and S sockets. N can be greater than, less than, or equal to S. Doesn't matter. Assume the pool has already created all S sockets, and all N threads have sockets assigned. Each thread either:</p>
<ol>
<li>Has checked out its socket, and is going to return it and signal the queue, or</li>
<li>Is waiting for its socket, or will ask for it in the future, or</li>
<li>Has returned its socket and will never ask for it again.</li>
</ol>
<p>To deadlock, all threads must be in state 2.</p>
<p>To reach that point, we need N - 1 threads in state 2 and have the Nth thread transition from 1 to 2. (By definition it doesn't go from state 3 to 2.) But when the Nth thread returns its socket and signals the queue, all sockets are now returned, so the next awakened thread won't wait again&mdash;its socket is available, so it goes to state 1. Thus, no deadlock.</p>
<p>The old code definitely wasn't efficient. It's easy to imagine cases where all a socket's threads were waiting, even though one of them could have been running. Let's say there are 2 sockets and 4 threads:</p>
<ol>
<li>Thread 1 has Socket A checked out, Thread 2 has Socket B, Thread 3 is waiting for A, Thread 4 is waiting for B, and they're enqueued like [3, 4].</li>
<li>Thread 2 returns B, signals the queue.</li>
<li>Thread 3 wakes, can't get A, waits again.</li>
</ol>
<p>At this point, Thread 4 should be running, since its Socket B is available, but it's waiting erroneously for Thread 1 to return A before it wakes.</p>
<p><a href="https://jira.mongodb.org/browse/RUBY-556">So we changed the code</a> to do <code>queue.broadcast</code> instead of <code>signal</code>, so <code>checkin</code> wakes all the threads, and we <a href="https://rubygems.org/gems/mongo/versions/1.8.3.rc0">released the fixed driver</a>. In the future, even better code may prevent multiple threads from contending for the same socket at all.</p>
<p>The bugfix was obvious. It's much harder to determine exactly how bad the bug was&mdash;how common is it for a socket to be unused?</p>
<hr />
<p>In <a href="https://gist.github.com/ajdavis/4991105">my simulated pool</a> there are 10 sockets. Each thread uses its socket for 1&#8209;20 seconds, sleeps one second, and asks for its socket again. I counted how many sockets were in use each second, and subtracted that from S&nbsp;*&nbsp;total_time to get an inefficiency factor:</p>
<p><img style="display:block; margin-left:auto; margin-right:auto;" src="percentage-unused-sockets.png" alt="Percentage unused sockets" title="percentage-unused-sockets.png" border="0"   /></p>
<p>If N=S=10, threads never wait but there's some fake "inefficiency" due to the 1-second sleep. For larger numbers of threads the sleep time becomes irrelevant (because there's always another thread ready to use the socket), but <code>signal</code> adds an inefficiency that declines very slowly from 8% as the number of threads increases. A pool that uses <code>broadcast</code>, in contrast, can saturate its sockets if it has more than 30 threads.</p>
<p>I spent hours (mostly on planes) trying to determine why the inefficiency factor acts this way&mdash;why 8%? Shouldn't it be worse? And why does it fall, slowly, as N rises? But I'm calling it quits now. Leave a comment if you have any insights, but I'm satisfied that the old pool was wasteful and that the new one is a substantial improvement.</p>
