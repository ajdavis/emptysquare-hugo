+++
type = "post"
title = "Toro 1.0, the Final Release"
date = "2015-09-01T12:11:13"
description = "This version includes a new RWLock. Further development of Toro's ideas continues in Tornado itself."
"blog/category" = ["Programming", "Python"]
"blog/tag" = ["tornado"]
enable_lightbox = false
thumbnail = "toro@240.png"
draft = false
legacyid = "55e5cd3b5393741c7067811a"
+++

<p><img style="display:block; margin-left:auto; margin-right:auto;" src="toro.png" alt="Toro" title="toro.png" border="0"   /></p>
<p>I just shipped Toro with a new feature contributed by <a href="https://github.com/alexander-gridnev">Alexander Gridnev</a>: a <a href="http://toro.readthedocs.org/en/stable/classes.html#rwlock">readers-writer lock, or "RWLock"</a>. It protects a shared data structure by allowing multiple coroutines to lock it for reads. As soon as a coroutine wants to modify the structure it requests a write-lock and waits for all readers to release their locks. While a writer is waiting, all readers and writers queue. Once the writer releases the lock, readers or the next writer can acquire it.</p>
<p>An RWLock is a common optimization for multithreaded code in other languages, but Python threads specifically have no use for one: the Global Interpreter Lock prevents multiple readers from actually doing parallel computation with the shared data, so in multithreaded Python there's no advantage to an RWLock compared to a plain Lock. Thus there's no RWLock in Python's standard threading module.</p>
<p>For async code, however, I could see the advantage of an RWLock. Async Python allows concurrent I/O operations in a single thread. There might be some shared external data that can be retrieved or modified, say a RESTful resource that doesn't implement the desired locking semantics on its own. With Alexander's new RWLock, coroutines in a Tornado process can now safely share such a resource, ensuring that reader coroutines wait for the lock as little as possible, while writer coroutines can gain exclusive access to the resource when needed.</p>
<p>I recognized the usefulness of this kind of lock so I took the contribution. Besides, asyncio expert <a href="https://github.com/aio-libs/aiorwlock">Andrew Svetlov made an RWLock for asyncio</a> so I thought Tornado deserved one, too. Toro was a good place for such a class to make its temporary home. RWLock is Toro 1.0's sole new feature.</p>
<p>And now it's the end of the line: Toro is both completed and deprecated. <a href="http://www.tornadoweb.org/en/stable/releases/v4.2.0.html#new-modules-tornado-locks-and-tornado-queues">Toro's locks and queues were merged into Tornado 4.2</a>, and further development on those ideas will continue in Tornado itself from now on. Indeed, <a href="https://github.com/tornadoweb/tornado/pull/1476">Ben Darnell has just updated Tornado's locks and queues for Python 3.5's new <code>async</code> and <code>await</code> statements</a>. <a href="https://github.com/ajdavis/toro/pull/12">I've recommended to Alexander that he spin off his RWLock for Tornado into a separate package</a>, to stand alone the same as asyncio's RWLock does.</p>
<p>Toro is among my favorite and most complete works, <a href="/blog/tornado-locks-and-queues/">you can read my thoughts on its retirement in my May article</a>.</p>
    