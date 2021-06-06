+++
type = "post"
title = "Python Coroutines"
date = "2011-10-26T16:52:26"
description = "David Beazley's Curious Course on Coroutines and Concurrency in Python is the best coroutine tutorial I've seen. It makes an essential distinction between generators, from which you pull data, like this: def squares(): for i in [ ... ]"
category = ["Programming", "Python"]
tag = []
enable_lightbox = false
draft = false
disqus_identifier = "72 http://emptysquare.net/blog/?p=72"
disqus_url = "https://emptysqua.re/blog/72 http://emptysquare.net/blog/?p=72/"
+++

<p>David Beazley's <a href="http://www.dabeaz.com/coroutines/index.html">Curious Course on Coroutines and
Concurrency</a> in Python is
the best coroutine tutorial I've seen.</p>
<p>It makes an essential distinction between <strong>generators</strong>, from which you <strong>pull</strong> data, like this:</p>

{{<highlight python3>}}
def squares():
  for i in range(10):
    yield i * i # send data

for j in squares():
  print j
{{< / highlight >}}

<p>... and <strong>coroutines</strong>, through which you <strong>push</strong> data, like this:</p>

{{<highlight python3>}}
def line_printer():
  buf = ''
  try:
    while True:
      buf += (yield) # receive data
      parts = buf.split('\n')
      if len(parts) > 1:
        # We've received 1 or more new lines, print them
        for part in parts[:-1]: print part
        buf = parts[-1]
  except GeneratorExit:
    # Someone has called close() on this generator, print
    # the last of the buffer
    if buf: print buf

# push random chars, and sometimes newlines, into the coroutine
import random
coroutine = line_printer()
coroutine.next() # start coroutine
for i in range(1000):
  random_char = chr(random.randint(ord('a'), ord('z') + 1))
  if ord(random_char) > ord('z'):
    random_char = '\n'
  coroutine.send(random_char)

coroutine.close()
{{< / highlight >}}

<p>I plan to spend a lot of time with coroutines in the next few months, in particular seeing how they can simplify coding in asynchronous Python web frameworks.</p>
