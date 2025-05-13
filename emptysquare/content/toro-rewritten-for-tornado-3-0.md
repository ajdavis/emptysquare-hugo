+++
type = "post"
title = "Toro Rewritten for Tornado 3.0"
date = "2013-04-12T16:27:58"
description = ""
category = ["Programming", "Python"]
tag = ["tornado"]
enable_lightbox = false
thumbnail = "toro.png"
draft = false
+++

<p><img alt="Toro" border="0" src="toro.png" style="display:block; margin-left:auto; margin-right:auto;" title="toro.png"/></p>
<p><a href="/pycon-lightning-talk-about-toro/">Speaking of my package Toro</a>, I've just released version 0.5. Toro provides semaphores, queues, and so on, for advanced control flows with Tornado coroutines. </p>
<p>Version 0.5 is a rewrite, motivated by two recent events. First, the release of Tornado 3.0 has introduced a much more convenient coroutine API, and I wanted Toro to support the modern style. Second, I <a href="http://code.google.com/p/tulip/source/detail?r=f83dba559f89">contributed a version of Toro's queues to Tulip</a>, and the queues changed a bit in the process. As much as possible, I updated Toro to match the API of Tulip's locks and queues, for consistency's sake.</p>
<p>In previous versions, most Toro methods had to be wrapped in <code>gen.Task</code>, which made for weird-looking code. But using Toro is now quite graceful. For example, a producer-consumer pair:</p>

{{<highlight python3>}}
q = toro.Queue()

@gen.coroutine
def producer():
    for item in range(5):
        print 'Sending', item
        yield q.put(item)

@gen.coroutine
def consumer():
    while True:
        item = yield q.get()
        print '\t\t', 'Got', item

consumer()
producer()
IOLoop.current().start()
{{< / highlight >}}

<p>Another nice new feature: <code>Semaphore.acquire</code> and <code>Lock.acquire</code> can be used with the <code>with</code> statement:</p>

{{<highlight python3>}}
lock = toro.Lock()

@gen.coroutine
def f():
   with (yield lock.acquire()):
       print "We're in the lock"

   print "Out of the lock"
{{< / highlight >}}

<p>More <a href="http://toro.readthedocs.org/en/stable">examples are in the docs</a>. Enjoy!</p>
