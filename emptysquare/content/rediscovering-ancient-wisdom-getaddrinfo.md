+++
type = "post"
title = "Rediscovering Ancient Wisdom With getaddrinfo"
description = ""
category = ["Python", "Programming"]
tag = ["getaddrinfo"]
enable_lightbox = false
thumbnail = "kon-tiki-2.jpg"
draft = true
disqus_identifier = "/blog/rediscovering-ancient-wisdom-getaddrinfo"
disqus_url = "https://emptysqua.re/blog//blog/rediscovering-ancient-wisdom-getaddrinfo/"
+++

<p>"When do you want to bet it was fixed?" I asked Jason and Drew. "I bet it was fixed ten years ago," said Drew. "But somehow nobody knows."</p>
<p>I was talking with my two colleagues in MongoDB's New York office. I have no windows where I sit, so I like to wander over to their side of the office  and gaze out at the water towers across 44th Street. On this particular day in November last year, I also had a question for them. Was the <code>getaddrinfo</code>  function thread-safe on Mac OS X?</p>
<p>Once in ancient times, it definitely wasn't thread-safe. Therefore, the ancient Python implementors added a mutex prevent concurrent <code>getaddrinfo</code> calls. This hurts performance, of course, and it creates spurious timeouts when Python threads spend too long waiting for the lock. It can even deadlock a Python program, if one thread forks while another is holding the mutex. I'd poured hours into debugging to work around all these pitfalls in my Python code that fall, but the question was bright in my mind: what if Python's mutex wasn't necessary? What if <code>getaddrinfo</code> is thread-safe on Mac now?</p>
<p>The first step was simply to test it. I wrote a C program to start a bunch of threads and call <code>getaddrinfo</code> from each in parallel&mdash;it worked. Folks of the NYC BSD User Group suggested I apply NetBSD's <a href="http://cvsweb.netbsd.org/bsdweb.cgi/src/tests/lib/libpthread/h_resolv.c">self-test for parallel <code>getaddrinfo</code> calls</a> and that worked, too. So, I theorized that the ancient Apple coders had fixed <code>getaddrinfo</code>, but the history had been forgotten.</p>
<hr />
<p>When Drew wanted to be that <code>getaddrinfo</code> had been thread-safe on Mac for ten years, I didn't take him up on it. Some intuition whispered to me, too, that ten years was the right number. Somehow, everyone had once known that it was <em>not</em> thread-safe. Then, it was fixed, but no one knew.</p>
<p>Google dug up an archive of a Mac OS X 10.4 man page. I unrolled it, blew off the dust, and read:</p>
<blockquote>
<p><strong>BUGS</strong></p>
<p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;The implementation of <code>getaddrinfo()</code> is not thread-safe.</p>
</blockquote>
<p>But on my laptop running OS X 10.10, <code>man getaddrinfo</code> has no bugs section at all. Rummaging among the archives, I found that the thread-safety warning had disappeared in the 10.5 release. But, had the ancient programmers really fixed it in 10.5, or had some scribe simply forgotten to copy the forewarning? Only one way to know for sure....</p>
<hr />
<p>I had to prove that my thread-safety tests were effective. They passed on 10.10, but I had to see them fail on 10.4. Next stop: eBay.</p>
<p>TIGER DVD</p>
<p>It certainly took some doing to get the antique clockwork running in VirtualBox, but I oiled the gears and replaced a spring, and received this blast from the past:</p>
<p><img alt="" src="mac-os-x-tiger.png" /></p>
<p>Sure enough, if I cracked open its primitive Terminal app and ran <code>man getaddrinfo</code>, there was the thread-safety warning. And what if I ran NetBSD's parallel test there? Aha! It fails. The test had proven that the ancients really did have a problem, and they really fixed it.</p>
<p>get the lore from apple</p>
<p>find the diff</p>
<p>fix cpython</p>
<p>bonus: other bsds</p>
<ul>
<li><a href="/getaddrinfo-on-macosx/">This four-part series about <code>getaddrinfo</code> on Mac</a>.</li>
</ul>
