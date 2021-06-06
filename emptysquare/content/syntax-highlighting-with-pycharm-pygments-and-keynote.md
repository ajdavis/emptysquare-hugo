+++
type = "post"
title = "Syntax Highlighting With PyCharm, Pygments, and Keynote"
date = "2012-06-06T18:15:45"
description = "I'm prepping talks for a few conferences. I think I've got my workflow down for syntax highlighting slides in Keynote on my Mac. &#8203;1. \"pip install pygments\", not in a virtualenv but in your default Python. &#8203;2. Make a Bash script [ ... ]"
category = ["Programming", "Python"]
tag = []
enable_lightbox = false
thumbnail = "keynote-auto-correction.png"
draft = false
disqus_identifier = "590 http://emptysquare.net/blog/?p=590"
disqus_url = "https://emptysqua.re/blog/590 http://emptysquare.net/blog/?p=590/"
+++

<p>I'm prepping talks for a few conferences. I think I've got my workflow
down for syntax highlighting slides in Keynote on my Mac.</p>
<p>​1. "pip install pygments", not in a virtualenv but in your default
Python.</p>
<p>​2. Make a Bash script like:</p>

{{<highlight shell>}}
#!/bin/bash
/usr/local/bin/pygmentize -f rtf -O "style=friendly,fontface=Courier Bold" "$1" | pbcopy
{{< / highlight >}}

<p>Make sure it's chmod'ed executable and on your path. Now you can do
<code>pyg myscript.py</code> and then paste the syntax-highlighted code into
Keynote. The result is pretty nice; at some point I may make a Pygments
style optimized for presentations:</p>
<p><img src="pygments-output.png" style="display:block; margin-left:auto; margin-right:auto;" title="Pygments output"/></p>
<p>​3. In Keynote, turn off all auto-correction:</p>
<p><img src="keynote-auto-correction.png" style="display:block; margin-left:auto; margin-right:auto;" title="Keynote auto-correction"/></p>
<p>​4. Bonus round: PyCharm integration. In PyCharm's preferences, choose
"External Tools," hit the "+", and fill out the dialog like so:</p>
<p><img src="pycharm-edit-tool.png" style="display:block; margin-left:auto; margin-right:auto;" title="PyCharm Edit Tool"/></p>
<p>You can leave "Open Console" checked while you're getting things
working.</p>
<p>Finally, in the "Keymap" section of PyCharm's vast settings dialog,
search for "pyg" in the filter box, right-click on it, and assign a
hotkey of your choice to the tool. I chose Command-Y because it was
bound to some weird function I don't use.</p>
<p><img src="pycharm-hotkey.png" style="display:block; margin-left:auto; margin-right:auto;" title="PyCharm assign hotkey"/></p>
<p>Now whenever you're editing a file in PyCharm, you can save it and hit
Command-Y, then switch to Keynote and paste.</p>
<p>Readers, if anyone can tell me how to adjust the default font size in
Pygments for RTF output specifically, that'd be great.</p>
