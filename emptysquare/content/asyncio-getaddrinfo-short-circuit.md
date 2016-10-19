+++
type = "post"
title = "How To Play Foul With getaddrinfo()"
date = "2016-03-13T22:28:40"
description = "Why connection timeouts are unfair with asyncio on Mac, and how we fixed it."
category = ["Python", "Mongo", "Programming", "Motor"]
tag = ["getaddrinfo"]
enable_lightbox = false
thumbnail = "kay-petre@240.jpg"
draft = false
+++

<p><img alt="A team competing in the 1912 Monte Carlo Rally" src="Russo-balt_s24-55_ralli_monte-karlo_1.jpg" /></p>
<p>I'm the referee for a road rally. You have to drive from New York to San Francisco in 48 hours, but&mdash;here's the catch&mdash;I'm going to start my stopwatch <em>before</em> you can look at the map. Worse, there are hundreds of other drivers who need the map, and only one driver can use it at a time. If you're unlucky, you could spend the whole 48 hours waiting in line.</p>
<p>Sound fair? Not to me. But this was how my library, Motor, worked with asyncio. In this article, <a href="/blog/getaddrinfo-on-macosx/">the third of my four-part series about Python's <code>getaddrinfo</code> on Mac</a>, I'll tell you how Guido van Rossum, Yury Selivanov, and I fixed asyncio so it could referee a fair race.</p>
<h1 id="an-unfair-stopwatch">An Unfair Stopwatch</h1>
<p>Motor is my async Python driver for MongoDB. Back in December, a data scientist at the Washington Post reported that on his Mac, Motor timed out trying to connect to MongoDB, even if MongoDB was running on the local machine. The cause is this: his script had begun to download hundreds of remote feeds, and each of those downloads required a DNS lookup. On Mac OS X, Python only permits one call to <code>getaddrinfo</code> at a time.</p>
<p>It's like my unfair road rally: Motor starts a 20-second timer, then calls asyncio's <code>create_connection</code>. Now asyncio needs to the <code>getaddrinfo</code> lock, but there are hundreds of tasks in line ahead of it. By the time it gets the lock, resolves "localhost" and starts to open a socket, the timeout has ended and Motor cancels the task.</p>
<p><img alt="Marcel Renault during the 1903 Paris–Madrid race" src="Marcel_Renault_1903.jpg" /></p>
<h1 id="fixing-the-rules">Fixing The Rules</h1>
<p>I proposed three solutions to the asyncio team, none perfect. Guido responded with two more:</p>
<ul>
<li><strong>Modify asyncio</strong> so if you pass it something that looks like a numerical address it skips calling <code>getaddrinfo</code>.</li>
</ul>
<p>The idea here is for Motor to run <code>getaddrinfo</code> itself. Then it starts the timer and passes the IP address to asyncio. Now the race is fair: Motor only counts how long asyncio spends actually connecting.</p>
<p>Guido's other idea seemed daunting:</p>
<ul>
<li><strong>Do the research</strong> to prove that <code>getaddrinfo</code> on OS X is thread-safe and submit a patch that avoids the <code>getaddrinfo</code> lock on those versions of OS X.</li>
</ul>
<p>I decided to leave the archeological research for another day when I was feeling more Indiana Jonesy. I could modify asyncio right away.</p>
<p><img alt="Luigi Fagioli competing in the 1928 Targo Florio race" src="Luigi_Fagioli_at_the_1928_Targa_Florio.jpg" /></p>
<h1 id="fixing-the-rules-isnt-simple">Fixing The Rules Isn't Simple</h1>
<p>Guido's initial proposal sounded easy enough. If Motor has resolved a host to the IP address "1.2.3.4", and executes this:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">yield from</span> loop<span style="color: #666666">.</span>create_connection(Protocol, <span style="color: #BA2121">&#39;1.2.3.4&#39;</span>, <span style="color: #666666">80</span>)
</pre></div>


<p>... then asyncio should see that "1.2.3.4" is already an IP address, and <strong>skip the <code>getaddrinfo</code> call</strong>. Instead, asyncio should choose the proper address family, socket type, protocol, and so on, as if it had called <code>getaddrinfo</code>, but without ever waiting in line.</p>
<p>It would be as if your co-pilot showed up with a route already planned. You wouldn't get in line to use the map; you'd jump in your rally car and start driving.</p>
<p>I set off to write some Python 3 code that recognizes an IP address and constructs a fake <code>getaddrinfo</code> response. A useful module called <code>ipaddress</code> was added to the standard library in Python 3.3, so implementing recognition went swimmingly:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">try</span>:
    addr <span style="color: #666666">=</span> ipaddress<span style="color: #666666">.</span>IPv4Address(host)
<span style="color: #008000; font-weight: bold">except</span> <span style="color: #D2413A; font-weight: bold">ValueError</span>:
    <span style="color: #008000; font-weight: bold">try</span>:
<span style="background-color: #ffffcc">        addr <span style="color: #666666">=</span> ipaddress<span style="color: #666666">.</span>IPv6Address(host<span style="color: #666666">.</span>partition(<span style="color: #BA2121">&#39;%&#39;</span>)[<span style="color: #666666">0</span>])
</span>    <span style="color: #008000; font-weight: bold">except</span> <span style="color: #D2413A; font-weight: bold">ValueError</span>:
        <span style="color: #408080; font-style: italic"># Host isn&#39;t an IP address, can&#39;t skip getaddrinfo.</span>
        <span style="color: #008000; font-weight: bold">return</span> <span style="color: #008000; font-weight: bold">None</span>
</pre></div>


<p>That <code>partition</code> call is needed to remove the IP address's <a href="https://en.wikipedia.org/wiki/IPv6_address#Link-local_addresses_and_zone_indices">zone index</a> if it has one. For example the IPv6 address for "localhost" might be "fe80::1%lo0", which specifies the "loopback 0" interface. <strong>Yury, Guido, and I had never heard of zone indexes before</strong>, but we figured it out and carried on.</p>
<p>Recognizing an IP address isn't enough, because converting a host name to an IP address isn't all that <code>getaddrinfo</code> does. What about the other parameters: family, socket type, protocol, flags? Each of these inputs to <code>getaddrinfo</code> influences its return value. I needed to reproduce this logic accurately in pure Python, without getting in line to use the actual <code>getaddrinfo</code> call.</p>
<p>Consider how <code>getaddrinfo</code> infers the protocol from the socket type: <code>SOCK_STREAM</code> implies TCP, <code>SOCK_DGRAM</code> implies UDP. So I tried the obvious code:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">if</span> socket_type <span style="color: #666666">==</span> SOCK_STREAM:
    proto <span style="color: #666666">=</span> IPPROTO_TCP
<span style="color: #008000; font-weight: bold">elif</span> socket_type <span style="color: #666666">==</span> SOCK_DGRAM:
    proto <span style="color: #666666">=</span> IPPROTO_UDP
</pre></div>


<p>But on Linux, and Linux only, the socket type is a bitmask that can be combined with the flags <code>SOCK_NONBLOCK</code> and <code>SOCK_CLOEXEC</code>. So the check <code>socket_type == SOCK_STREAM</code> is wrong on Linux. I had to test a bitwise "and" instead:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">if</span> socket_type <span style="color: #666666">&amp;</span> SOCK_STREAM:
    proto <span style="color: #666666">=</span> IPPROTO_TCP
<span style="color: #008000; font-weight: bold">elif</span> socket_type <span style="color: #666666">&amp;</span> SOCK_DGRAM:
    proto <span style="color: #666666">=</span> IPPROTO_UDP
</pre></div>


<p>Again and again, I thought I had finished, but the socket-programming API has innumerable corners and platform differences. Although Guido's idea was simple&mdash;teach asyncio to recognize an already-resolved IP address and simulate a <code>getaddrinfo</code> response&mdash;it required 15 revisions before I'd straightened out the kinks and satisfied Yury and Guido.</p>
<p>On the 16th revision, we merged. The fix will ship with Python 3.4.5, 3.5.2, and 3.6.0.</p>
<p>I wrote, </p>
<blockquote>
<p>This has certainly been educational.</p>
</blockquote>
<p>Yury replied,</p>
<blockquote>
<p>For me too. :)</p>
</blockquote>
<hr />
<p><img alt="Rally driver Kay Petre in 1937" src="kay-petre.jpg" /></p>
<h1 id="this-is-not-the-end">This Is Not The End</h1>
<p>So I gave you a way to skip the line. If you planned your route beforehand, you can get right in your car and start driving.</p>
<p>And yet: as you peel out from the starting line and accelerate toward San Francisco, you feel a pang. You glance in the rearview mirror and see all those other drivers, the ones who didn't come prepared, waiting in line to use the map. Wasn't there some better way? Couldn't they all just...share the map?</p>
<p>They can. Stay tuned for the final installment of this series about Python's <code>getaddrinfo</code> on Mac.</p>
<hr />
<p>Links:</p>
<ul>
<li><a href="https://github.com/python/asyncio/pull/302">The asyncio pull request to allow skipping <code>getaddrinfo</code></a>.</li>
<li><a href="https://groups.google.com/forum/#!topic/python-tulip/-SFI8kkQEj4/discussion">Mailing list discussion with the asyncio team</a>.</li>
<li><a href="https://jira.mongodb.org/browse/MOTOR-100">The Motor bug report</a>.</li>
<li><a href="/blog/getaddrinfo-on-macosx/">This four-part series about <code>getaddrinfo</code> on Mac</a>.</li>
</ul>
<p><img alt="Mrs Gordon Simpson and Joan Richmond smoke cigarettes in their rally car, 1934" src="gordon-simpson-joan-richmond.jpg" /></p>
<p>Images:</p>
<ul>
<li><a href="https://en.wikipedia.org/wiki/Rallying#/media/File:Russo-balt_s24-55_ralli_monte-karlo_1.jpg">1912 Monte Carlo Rally team</a></li>
<li><a href="https://en.wikipedia.org/wiki/Rallying#/media/File:Marcel_Renault_1903.jpg">Marcel Renault during the 1903 Paris–Madrid race</a></li>
<li><a href="https://en.wikipedia.org/wiki/Targa_Florio">Luigi Fagioli competing in the 1928 Targo Florio race</a></li>
<li><a href="http://silodrome.com/lady-racing-drivers-brooklands/">Rally driver Kay Petre in 1937</a></li>
<li><a href="http://silodrome.com/lady-racing-drivers-brooklands/">Mrs Gordon Simpson and Joan Richmond smoke cigarettes in their rally car, 1934</a></li>
</ul>
