+++
type = "post"
title = "Day Of The Thread"
date = "2013-10-31T15:56:48"
description = "Pitfalls to avoid when submitting a patch to the core Python team."
category = ["Programming", "Python"]
tag = ["threading"]
enable_lightbox = false
thumbnail = "day-of-the-dead-final.jpg"
draft = false
disqus_identifier = "5272b1065393740368ee7116"
disqus_url = "https://emptysqua.re/blog/5272b1065393740368ee7116/"
+++

<p><img alt="Day of the Thread" src="day-of-the-thread.jpg" style="display:block; margin-left:auto; margin-right:auto;" title="Day of the Thread"/></p>
<p>If you think you’ve found a bug in Python, what’s next? I'll guide you through the process of submitting a patch, so you can avoid its pitfalls and find the shortest route to becoming a Python contributor!</p>
<p>This is the final post in a three part series. In <a href="/night-of-the-living-thread/">Night of the Living Thread</a> I fixed a bug in Python's threading implementation, so that threads wouldn't become zombies after a fork. In <a href="/dawn-of-the-thread/">Dawn of the Thread</a> I battled zombie threads in Python 2.6. Now, in the horrifying conclusion, I return to the original bugfix and submit it to the core Python team. Humanity's last hope is that we can get a patch accepted and stop the zombie threads...before it's too late.</p>
<p>The action starts when I <a href="http://bugs.python.org/review/18418">open a bug in the Python bug tracker</a>. The challenge is to make a demonstration of the bug. I need to convince the world that I'm not crazy: the dead really are rising and walking the earth! Luckily I have a short script from <a href="/night-of-the-living-thread/">Night of the Living Thread</a> that shows the zombification process clearly.</p>
<p><img alt="Day of the Dead" src="day-of-the-dead-head.jpg" style="display:block; margin-left:auto; margin-right:auto;" title="Day of the Dead"/></p>
<p>Next I have to fix the bug and submit a patch. I'm confused here, since the bug is in Python 2.7 and 3.3: do I submit fixes for both versions? The right thing to do is clone the Python source:</p>

{{<highlight plain>}}
hg clone http://hg.python.org/cpython
{{< / highlight >}}

<p>I fix the bug at the tip of the default branch. The <a href="http://docs.python.org/devguide/patch.html">Lifecycle of a Patch</a> doc in the Python Developer's Guide tells me to make a patch with <code>hg diff</code>. I attach it to the bug report by hitting the "Choose File" button and then "Submit Changes."</p>
<p>After this, the Python Developer's Guide is no more use. The abomination I am about to encounter isn't described in any guide: The Python bug tracker is a version of Roundup, hacked to pieces and sewn together with a code review tool called Rietveld. The resulting botched nightmare is covered in scabs, stitches, and suppurating wounds. It's a revolting Frankenstein's monster. (And I thought this was only a zombie movie.)</p>
<p>When I upload a patch to the bug tracker, Roundup, it is digested and spit out into the code review tool, Rietveld. <a href="http://bugs.python.org/review/18418/#ps8819">It shows up like this</a>, so a Python core developer can critique my bugfix. Charles-François Natali is my reviewer. He suggests a cleaner bugfix <a href="/night-of-the-living-thread/">which you can read about in my earlier post</a>, and shows me how to improve my unittest.</p>
<p>Tragically, a week passes before I <em>know</em> he's reviewed my patch. I keep visiting the issue in Roundup expecting to see comments there, but I'm not looking where I should be: there's a little blue link in Roundup that says "review", which leads to Rietveld. That's where I should go to see feedback. Precious time is lost as hordes of zombie threads continue to ravage the landscape.</p>
<p><img alt="Day of the Dead street" src="day-of-the-dead-street.jpg" style="display:block; margin-left:auto; margin-right:auto;" title="Day of the Dead street"/></p>
<p>Even worse, my Gmail account thinks Rietveld's notifications are spam. It turns out that the bug tracker was once breached by spammers and used to send spam in the past, so Gmail is quick to characterize all messages from bugs.python.org as spam. I override Gmail's spam filter with a new filter:</p>
<p><img alt="Gmail python filter" src="gmail-python-filter.png" style="display:block; margin-left:auto; margin-right:auto;" title="Gmail python filter"/></p>
<p>Once I make the changes Charles-François suggests, I try to re-upload my patch. Clicking "Add Another Patch Set" in Rietveld doesn't work: it shows a page with a TypeError and a traceback. So I follow the instructions to upload a patch using the <code>upload.py</code> script from the command line and that throws an exception, too. I can't even cry out for help: <a href="http://psf.upfronthosting.co.za/roundup/meta/issue517">hitting "reply" to add a comment in Rietveld fails</a>. I tremble in fear.</p>
<p><img alt="Day of the Dead hands" src="day-of-the-dead-hands.jpg" style="display:block; margin-left:auto; margin-right:auto;" title="Day of the Dead hands"/></p>
<p>Just when humanity's doom seems inevitable, I find a way out: It turns out I must upload my new patch as an additional attachment to the issue in Roundup. Then Roundup, after some delay, applies it to the code review in Rietveld. Finally, I can address Charles-François's objections, and he accepts my patch! Roundup informs me when he <a href="http://bugs.python.org/msg196581">applies my changes to the 2.7, 3.3, and default branches</a>.</p>
<p>As the darkness lifts I reflect on how contributing to Python has benefited me, despite the horror. For one thing, I learned a few things about Python. I learned that every module in the standard library imports its dependencies like this example from threading.py:</p>

{{<highlight python3>}}
from time import time as _time, sleep as _sleep
{{< / highlight >}}

<p>When you execute a statement like <code>from threading import *</code>, Python only imports names that don't begin with an underscore. So renaming imported items is a good way to control which names a module exports by default, an alternative to the <code>__all__</code> list.</p>
<p>The code-review process also taught me about <a href="http://docs.python.org/2/library/unittest.html#unittest.TestCase.addCleanup">addCleanup()</a>, which is sometimes a nicer way to clean up after a test than either <code>tearDown</code> or a try/finally block. And I learned that concurrency bugs are easier to reproduce in Python 2 with <code>sys.setcheckinterval(0)</code> and in Python 3 with <code>sys.setswitchinterval(1e-6)</code>.</p>
<p>But the main benefit of contributing to Python is the satisfaction and pride I gain: Python is my favorite language. I love it, and I saved it from zombies. Heroism is its own reward.</p>
<p><img alt="Day of the Dead final" src="day-of-the-dead-final.jpg" style="display:block; margin-left:auto; margin-right:auto;" title="Day of the Dead final"/></p>
