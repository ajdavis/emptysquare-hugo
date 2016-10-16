+++
type = "post"
title = "An Event synchronization primitive for Ruby"
date = "2013-02-09T13:40:53"
description = "A port of Python's threading.Event synchronization primitive for Ruby"
categories = ["Programming"]
tags = ["threading"]
enable_lightbox = false
draft = false
+++

<p>I helped some Ruby friends implement a rendezvous (aka a <a href="http://en.wikipedia.org/wiki/Barrier_%28computer_science%29">barrier</a>). I'm accustomed to using an <a href="http://docs.python.org/2/library/threading.html#threading.Event">Event</a> to implement a rendezvous in Python but Ruby doesn't have Events, only Mutexes and ConditionVariables. That's fine, Python's Event is implemented in terms of a mutex and a condition, so it's easy to make an Event in Ruby:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">class</span> <span style="color: #0000FF; font-weight: bold">Event</span>
    <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">initialize</span>
        <span style="color: #19177C">@lock</span> <span style="color: #666666">=</span> <span style="color: #880000">Mutex</span><span style="color: #666666">.</span>new
        <span style="color: #19177C">@cond</span> <span style="color: #666666">=</span> <span style="color: #880000">ConditionVariable</span><span style="color: #666666">.</span>new
        <span style="color: #19177C">@flag</span> <span style="color: #666666">=</span> <span style="color: #008000">false</span>
    <span style="color: #008000; font-weight: bold">end</span>

    <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">set</span>
        <span style="color: #19177C">@lock</span><span style="color: #666666">.</span>synchronize <span style="color: #008000; font-weight: bold">do</span>
            <span style="color: #19177C">@flag</span> <span style="color: #666666">=</span> <span style="color: #008000">true</span>
            <span style="color: #19177C">@cond</span><span style="color: #666666">.</span>broadcast
       <span style="color: #008000; font-weight: bold">end</span>
    <span style="color: #008000; font-weight: bold">end</span>

    <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">wait</span>
        <span style="color: #19177C">@lock</span><span style="color: #666666">.</span>synchronize <span style="color: #008000; font-weight: bold">do</span>
            <span style="color: #008000; font-weight: bold">if</span> <span style="color: #AA22FF; font-weight: bold">not</span> <span style="color: #19177C">@flag</span>
                <span style="color: #19177C">@cond</span><span style="color: #666666">.</span>wait(<span style="color: #19177C">@lock</span>)
            <span style="color: #008000; font-weight: bold">end</span>
        <span style="color: #008000; font-weight: bold">end</span>
    <span style="color: #008000; font-weight: bold">end</span>
<span style="color: #008000; font-weight: bold">end</span>
</pre></div>


<p>Ruby's <code>cond.wait(lock)</code> pattern is interesting&mdash;you enter a lock so you can call <code>wait</code>, then <code>wait</code> releases the lock so another thread can <code>broadcast</code> the condition, and finally <code>wait</code> reacquires the lock before continuing.</p>
<p>I didn't implement <code>is_set</code> since it's unreliable (another thread can change it between the time you check the value and the time you act upon the information) and I didn't do <code>clear</code> since you can just replace the Event with a fresh one.</p>
    