+++
category = ['C', 'MongoDB', 'Programming', 'Python']
date = '2016-12-05T11:50:25.948462'
description = 'How I discovered the ancient secrets of BSD wizards and slew a mutex troll.'
draft = false
enable_lightbox = true
tag = ['getaddrinfo']
thumbnail = 'chest-scroll.jpg'
title = 'Making getaddrinfo Concurrent in Python On Mac OS and BSD'
type = 'post'
+++

![](chest-scroll.jpg)

<p><em>Tell us about the time you made DNS resolution concurrent in Python on Mac and BSD.</em></p>

<p>No, no, you do not want to hear that story, my friends. It is nothing but old lore and <code>#ifdefs</code>.</p>

<p><em>But you made Python more scalable. The saga of Steve Jobs was sung to you by a mysterious wizard with a fanciful nickname! Tell us!</em></p>

<p>Gather round, then. I will tell you how I unearthed a lost secret, unbound Python from old shackles, and banished an ancient and horrible Mutex Troll.</p>

<p>Let us begin at the beginning.</p>

<hr>

<p>A long time ago, in the 1980s, a coven of Berkeley sorcerers crafted an operating system. They named it after themselves: the Berkeley Software Distribution, or BSD. For generations they nurtured it, growing it and adding features. One night, they conjured a powerful function that could resolve hostnames to IPv4 or IPv6 addresses. It was called getaddrinfo. The function was mighty, but in years to come it would grow dangerous, for the sorcerers had not made getaddrinfo thread-safe.</p>

<p>As ages passed, BSD spawned many offspring. There were FreeBSD, OpenBSD, NetBSD, and in time, Mac OS X. Each made its copy of getaddrinfo thread safe, at different times and different ways. Some operating systems retained scribes who recorded these events in the annals. Some did not.</p>

<p>Because getaddrinfo is ringed round with mystery, the artisans who make cross-platform network libraries have mistrusted it. Is it thread safe or not? Often, they hired a Mutex Troll to  stand guard and prevent more than one thread from using getaddrinfo concurrently. The most widespread such library is Python's own socket module, distributed with Python's standard library. On Mac and other BSDs, the Python interpreter hires a Mutex Troll, who demands that each Python thread hold a special lock while calling getaddrinfo.</p>

<p>Behold, my friends, the getaddrinfo lock in Python's socketmodule.c:</p>

{{< highlight c >}}
/* On systems on which getaddrinfo() is believed to not be thread-safe,
(this includes the getaddrinfo emulation) protect access with a lock. */
#if defined(WITH_THREAD) &amp;&amp; (defined(__APPLE__) || \
(defined(__FreeBSD__) &amp;&amp; __FreeBSD_version+0 &lt; 503000) || \
defined(__OpenBSD__) || defined(__NetBSD__) || \
defined(__VMS) || !defined(HAVE_GETADDRINFO))
#define USE_GETADDRINFO_LOCK
#endif

#ifdef USE_GETADDRINFO_LOCK
#define ACQUIRE_GETADDRINFO_LOCK PyThread_acquire_lock(netdb_lock, 1);
#define RELEASE_GETADDRINFO_LOCK PyThread_release_lock(netdb_lock);
#else
#define ACQUIRE_GETADDRINFO_LOCK
#define RELEASE_GETADDRINFO_LOCK
#endif
{{< /highlight >}}

<p>This lock was not widely known. Although Python's Global Interpreter Lock certainly is infamous, the getaddrinfo lock was known only to a battle-worn few. The Mutex Troll required this lock in Python interpreters installed on Mac, NetBSD, OpenBSD, or on FreeBSD before 5.3. I first descried it while hunting a deadlock it caused in PyMongo. Since then, the mercenary troll and I had met in combat again and again: deadlocks, errors, and slowdowns in my Python code led me to renewed confrontation with it.</p>

<p>As I met more Python experts, I learned that they had encountered this hired troll, too. For example, multithreaded Python code that crawls thousands of websites, and must resolve thousands of hosts, <a href="https://emptysqua.re/blog/mac-python-getaddrinfo-queueing/">ran fine on Linux but came to grief on a Mac</a>. Threads would wait in a long queue to acquire the lock before the troll guard would allow them to call getaddrinfo. One very slow DNS resolution would block all the threads behind it, and they would throw timeouts before they could ever grasp the lock.</p>

<p>The day that Python's artisans hired the Mutex Troll it was needed to safeguard getaddrinfo against concurrent threads; but now the troll was no longer needed. I knew that getaddrinfo had been made thread safe on BSD's children, especially the most famous of them: Mac OS X. Many modern programs that call getaddrinfo concurrently suffer no harm. The MongoDB server, for example, runs fine on Mac without a getaddrinfo lock nor a troll to enforce it. But the mercenary's contract was eternal, and in the decades it stood guard over the lock it had grown corrupt and greedy. The time had come to banish the horrid thing. Whenever I read that comment from some past craftsman about "systems on which <code>getaddrinfo()</code> is believed to not be thread-safe", my ire boiled hotter. Why enthrall ourselves to mere belief, not knowing the truth?</p>

<p>One winter morning last year, I stood before my companions in the daily status meeting and asked leave to endeavor on a quest. I told them about the Mutex Troll and how it had held Mac and BSD coders hostage for generations. I made a great boast: I would defeat the Mutex Troll in Python and free the threads. Gladly my fellows at MongoDB granted me leave to go on the journey. "Banish the troll for the good of all!" they cried. They raised their flagons of Diet Coke and drank to my good fortune.</p>

<p>I donned my war-gear and sallied from MongoDB's castle. But to dispel the Mutex Troll's power in Python, it is not enough to say "perchance getaddrinfo once was broken, but now it is surely mended". <em>When</em> was getaddrinfo fixed, and how? And how could I prove it to the Python core developers? These developers, unlike MongoDB coders, must support all ancient versions of OS X to the dawn of time. To convince them, I would need to know the answer for certain. I decided ask an Apple engineer to aid my cause.</p>

<p>Apple engineers are not like you and me — they are a shy and secretive folk. They publish only what code they must from Darwin. Their comings and goings are recorded in no bug tracker, their works in no changelog. To learn their secrets, one must delve deep.</p>

<p>Through wild hills I journeyed to a tower where Apple clerics once gathered. I entered the deserted tower and found carved into the wall a <a href="http://opensource.apple.com//source/Libinfo/Libinfo-222.4.12/lookup.subproj/getaddrinfo.3">man page for getaddrinfo on OS X 10.4</a>, which warned:</p>

<pre>
getaddrinfo(3)

BSD Library Functions Manual

BUGS:
The implementation of getaddrinfo() is not thread-safe.

December 20, 2004
</pre>

<p>I read <a href="http://opensource.apple.com//source/Libinfo/Libinfo-222.4.12/lookup.subproj/getaddrinfo.c">the source for 10.4's getaddrinfo</a>. Uncertain what I beheld, I guessed I saw the data race: <code>getaddrinfo</code> calls <code>gai_lookupd</code>, which reads and writes a global static variable <code>gai_proc</code>. It seemed ill-wrought for multithreading.</p>

<p>On OS X 10.5, <a href="http://opensource.apple.com//source/Libinfo/Libinfo-278/lookup.subproj/getaddrinfo.3">the warning had vanished</a> from the man page, and the getaddrinfo function <a href="http://opensource.apple.com//source/Libinfo/Libinfo-278/lookup.subproj/getaddrinfo.c">was largely rewritten</a>. Should I believe that the bug was fixed then, a decade ago? I wept bitterly over the years of needless toil that programmers and processors had suffered at the hands of the troll. I pitied them, but I did not falter. I would prove that they were free of the troll's domination. Yet, diffing one version of getaddrinfo to the next was unprofitable. I did not understand what I saw! I needed an answer from Apple.</p>

<p>To ask a question of the Apple engineers, my friends, you must <a href="https://developer.apple.com/support/purchase-activation/">leave $99 of silver coins</a> in a hollow oak tree. Then, wait. It may take a day, or a season, but an Apple engineer will come and whisper in your ear, and bind you to a secret pact that you must never reveal what you have been told. The engineer will give you an Asking Ring. This you must use to ask a second question <a href="https://developer.apple.com/programs/whats-included/">within a year and a day</a>, or its power is lost.</p>

<p>I returned to MongoDB and asked my companions for some silver coins, which they gave me gladly. Then, on the first night after the first day of the year, I left them in the hollow oak, with my question:</p>

<blockquote>
<p>"Has getaddrinfo been fixed? Can you give me a public statement or a link to a resolved bug in a tracker? I need a way, not only to know it was fixed, but to prove it to others."</p>
</blockquote>

<p>I did not yet know what my second question would be.</p>

<p>Twelve days and twelve nights I waited, refreshing my email. Is today the day? Or today? The twelfth morning, January 13, I awoke to see an ancient box, of rusted hinge and hoared with lichen, resting by my bed. The box opened, exhaling the dust of forgotten smithies where the first network code was forged. Slowly, I reached in. I lifted out a scroll marked with assembly codes and unfurled it with a crackle.</p>

<p>My friends, I cannot tell you all I learned from that message. The secrets that were spoken to me, I am bound to keep. But I may relate a part of it, the story of a wizard both brilliant and foolish named Jobs.</p>

<blockquote>
<p>…and it came to pass, that Jobs was exiled from Apple. His crown and throne were taken from him and he was banished from his company. He wandered deep into the forest where he gathered a coven of witches to conjure a new operating system called NeXT, a child of BSD. A daemon called "lookupd" with the power to resolve hosts was bound to serve within it. Years passed. Jobs's fellows at Apple, hearing rumors of NeXT's greatness, sent emissaries to beg Jobs to return.</p>

<p>With Jobs restored as their king, the Apple engineers wrought the first versions of OS X. It, too, was an offspring of BSD, and its DNS system was a mix of new OS X features, mDNSResponder and Open Directory, along with the daemon lookupd from NeXT, and libresolv from an old BSD.</p>
</blockquote>

<p>"Aha!" I cried. It was these OS X versions whose getaddrinfo was not thread-safe. When Python was first ported to Mac, it rightly hired a Mutex Troll to guard getaddrinfo and only allow one host resolution at a time. Unfurling the scroll more, I read on.</p>

<blockquote>
<p>In version 10.5 the system was cleaned up to depend on OS X's mDNSResponder consistently; in the process getaddrinfo became thread-safe. Now, <a href="http://opensource.apple.com//source/Libinfo/Libinfo-476/lookup.subproj/libinfo.c">getaddrinfo calls down</a> to the <a href="http://opensource.apple.com//source/Libinfo/Libinfo-476/lookup.subproj/mdns_module.c">"mdns" module</a> in libinfo.</p>
</blockquote>

<p>Next to "libinfo", the scroll's author had written in the margin, "The presence and name of this library is a remnant from the original NetInfo architecture."</p>

<blockquote>
<p>The "mdns" module uses something called the DNS-SD API, which is well-known to be thread safe. The DNS-SD API is part of the <a href="http://opensource.apple.com//source/mDNSResponder/mDNSResponder-576.30.4/">mDNSResponder project</a>. The key function is <a href="http://opensource.apple.com//source/mDNSResponder/mDNSResponder-576.30.4/mDNSShared/dnssd_clientstub.c">DNSServiceQueryRecord</a>. As you can see, it does an IPC over to the mDNSResponder process, at which point thread safety is assured.</p>
</blockquote>

<p>The scroll was signed in an ornate hand:</p>

<blockquote>
<p>Share and Enjoy,</p>

<p>Quinn "The Eskimo!"</p>
</blockquote>

<p>It was a message from the loremaster Quinn, the <a href="https://twitter.com/thequinntaylor/status/743833222828564481">gray-haired</a>, the mighty-fingered hacker, <a href="http://www.mactech.com/articles/mactech/Vol.16/16.06/Jun00FactoryFloor/index.html">the legendary</a>, The Eskimo, who had named himself from a Bob Dylan lyric, who shouts the Hitchhiker's Guide battle cry "<a href="http://anarchistturtle.com/Quinn/WWW/ShareAndEnjoy.wav">Share and Enjoy!</a>"</p>

<p>In the dusty wooden chest, beneath the place the scroll had been, was an Asking Ring. I left it there for the day when I would need to ask a second question.</p>

<p>The Eskimo's message had spurred my courage. I knew what I had to do: I would prove that getaddrinfo, called concurrently, failed on 10.4 and worked on a modern Mac. Once I had done that the Mutex Troll's power would be dispelled. But now I had to get my hands on a 10.4 VM. I went on eBay and acquired an antique DVD.</p>

<figure class="has-lightbox">

<img src="dvd.png" alt="image of hand holding Mac OS X Tiger DVD" data-jslghtbx="/img/post/the-saga-of-concurrent-dns-in-python-and-the-defeat-of-the-wicked-mutex-troll/full/antique-tiger-dvd.png">

</figure>


<p>Arduous days and nights I toiled, Googling by candlelight for the incantations that could breathe the ancient spirit to life in VirtualBox. At last, the creature arose:</p>

<figure class="has-lightbox">

<img src="about-this-mac-tiger.png" alt="OS X 10.4 desktop with About This Mac window" data-jslghtbx="/img/post/the-saga-of-concurrent-dns-in-python-and-the-defeat-of-the-wicked-mutex-troll/full/about-this-mac-tiger.png">

</figure>


<p>Now I needed advice from BSD witches: How should I test getaddrinfo on this old OS X?</p>

<p>There is a <a href="http://www.nycbug.org/index.cgi">tiny coven of NYC BSD users</a> who meet at the tavern called Stone Creek, near my dwelling. They are aged and fierce, but I made the <a href="http://www.mckusick.com/beastie/shirts/bsdunix.html">Sign of the Trident</a> and supplicated them humbly for advice, and they were kindly to me. One NetBSD developer named Christos Zoulas showed me <a href="https://nxr.netbsd.org/xref/src/tests/lib/libpthread/h_resolv.c">NetBSD's getaddrinfo test</a>, which resolves a hundred hostnames with ten threads. I plucked the test from <a href="http://cvsweb.netbsd.org/bsdweb.cgi/?only_with_tag=MAIN">NetBSD's code-hoard, which rests in heaps in a CVS repo</a>.</p>

<figure class="has-lightbox">

<img src="stone-creek.png" alt="Photo of Stone Creek Bar &amp; Lounge" data-jslghtbx="/img/post/the-saga-of-concurrent-dns-in-python-and-the-defeat-of-the-wicked-mutex-troll/full/stone-creek.png">

</figure>


<p>The next task of my quest required a compiler. Happily, XCode 2 comes with the 10.4 DVD, so I installed it, and compiled the NetBSD getaddrinfo test.</p>

<p>I prayed the test would fail, for then I would have reproduced the bug: I'd have shown that getaddrinfo was not thread-safe on 10.4, and so, assuming the test passed on a modern OS X, I could show that the Mutex Troll's reason for being was obsolete. My heart quivered and I prayed to the spirits of ancient code-smiths as I raised my fingers to the keyboard and invoked the program:</p>

<p><code>./h_resolv_test</code></p>

<p>Thank the spirits who smiled on my fortune! The test failed.</p>

<p>I compiled the same test on my laptop running OS X 10.10 and it passed. I could even see the evidence of getaddrinfo's concurrency on my Mac: more threads reduced the total time to resolve all hosts.</p>

<p>To the green and happy kingdom of the Pythonistas I hastened with my news. "‘Tis mended! The getaddrinfo bug on OS X was fixed a decade ago, in 10.5. The reign of the Mutex Troll shall be ended." <a href="http://bugs.python.org/issue25924">I related the story of my testing, and of The Eskimo's secret letter to me.</a></p>

<p>Now was the time to use my second question, for I needed to discover how to <code>#ifdef</code> for Mac OS 10.5. I returned to the lichened chest and took up the Asking Ring. Wearing it on my finger, I spoke: "What preprocessor symbol can I rely on to tell me if OS X is 10.5 or newer?" The ring blazed up with heat and I cast it from me. I listened for an answer, but there was none. Despondent, I lay down and slept.</p>

<p>The next morning, the ring had vanished, and in the chest there was a new scroll from The Eskimo with my answer:</p>

<blockquote>
<p>"Include <code>AvailabilityMacros.h</code> and check for <code>MAC_OS_X_VERSION_10_5</code>."</p>
</blockquote>

<p>I had acquired all the knowledge and weapons I needed. I could fulfill the boast I had made months before, to banish the Mutex Troll and free Mac users from the getaddrinfo lock:</p>

```diff
-#if defined(WITH_THREAD) &amp;&amp; (defined(__APPLE__) || \
+#if defined(WITH_THREAD) &amp;&amp; ( \
+    (defined(__APPLE__) &amp;&amp; \
+        MAC_OS_X_VERSION_MIN_REQUIRED &lt; MAC_OS_X_VERSION_10_5) || \
(defined(__FreeBSD__) &amp;&amp; __FreeBSD_version+0 &lt; 503000) || \
defined(__OpenBSD__) || defined(__NetBSD__) || \
defined(__VMS) || !defined(HAVE_GETADDRINFO))
#define USE_GETADDRINFO_LOCK
#endif
```

<p>This patch was approved by Guido van Rossum and merged by a core developer, Ned Deily. And Guido did praise me, saying, "Thanks for the thorough work!"</p>

<p>Now look closely at the code, my friends, and you will see that Python on FreeBSD 5.3 and later was already free from the troll. The knight Maxim Sobolev updated <a href="http://bugs.python.org/issue1288833">Python in 2005 to allow concurrent hostname resolution there.</a></p>

<p>But OpenBSD and NetBSD yet suffered the demands of the Mutex Troll! OpenBSD's <a href="http://www.openbsd.org/plus54.html">getaddrinfo had been thread safe since 2013</a>, there is no need for the lock on that OS. And as for NetBSD, its getaddrinfo was fixed long ago in 2004, by the very same Christos Zoulas who had answered my call for aid when I went to the BSD witches in the tavern. My blood was still hot from my victory in OS X, so <a href="http://bugs.python.org/issue26406">I made short work of the lock on</a> the remaining BSDs. Their annals were well-kept and easily found, unlike Apple's, and I had no trouble persuading the Python developers that no guard was needed on those OSes. Without a word, the mercenary troll shouldered its axe and trudged off in search of other patrons on other platforms. Never again would it hold hostage the worthy smiths forging Python code on BSD.</p>

<p>I pondered that VMS was still on the list of non-thread-safe getaddrinfo implementations. Had VMS fixed its getaddrinfo? Could Python do concurrent resolution there too, now?</p>

<p>But my sword-arm was weary. I retired, leaving that foe to prove the mettle of some future hero.</p>
***

<span style="color:gray">(Cross-posted from the <a href="https://engineering.mongodb.com/post/the-saga-of-concurrent-dns-in-python-and-the-defeat-of-the-wicked-mutex-troll/">MongoDB Engineering Journal</a>)</span>

<span style="color: gray">Illustration by <a href="http://www.terrymarks.net/">Terry Marks</a></span>
