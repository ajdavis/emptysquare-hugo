+++
type = "post"
title = "reStructuredText in PyCharm, Firefox, and Anger"
date = "2013-04-10T11:09:07"
description = "An only-somewhat-shitty workflow for writing reST."
category = ["Programming", "Python"]
tag = []
enable_lightbox = false
thumbnail = "auto-reload.png"
draft = false
disqus_identifier = "5165808353937474b99b1857"
disqus_url = "https://emptysqua.re/blog/5165808353937474b99b1857/"
+++

<p>I spend a lot of time writing Python package documentation in reST. Nevertheless, I find reST's markup permanently unlearnable, so I format docs by trial and error: I type a few backticks and colons and angle-brackets and random crap, <code>sphinx-build</code> the docs as HTML, and see if they look okay. </p>
<p>Here's some tools to support this expert workflow.</p>
<p><strong>PyCharm</strong>: <a href="http://www.jetbrains.com/pycharm/">My favorite Python IDE</a> has basic syntax-highlighting and auto-completion for reST. It's not much, but it far exceeds the amount of reStructuredText syntax that can fit in my tiny brain. It really shines when I'm embedding Python code examples in my docs: PyCharm gives me full IDE support, including automatically adding imports, auto-completing method names and parameters, and nearly all the help I get when editing normal Python files.</p>
<p>There's <a href="http://plugins.jetbrains.com/plugin?pr=idea&amp;pluginId=7177">a file-watcher plugin for PyCharm</a> that seems like a nice way to rebuild docs when the source files change, but it's not yet compatible with the latest version of PyCharm. So instead:</p>
<p><strong>Watchdog</strong>: I install the <a href="https://pypi.python.org/pypi/watchdog">watchdog Python package</a>, which watches files and directories for changes. Watchdog gives me a command-line tool called <code>watchmedo</code>. (I find this fact unlearnable, too; why isn't the tool called <code>watchdog</code> the same as the package?) I tell it to watch my package's files for changes and rebuild the docs whenever I save a file:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">watchmedo shell-command --command<span style="color: #666666">=</span><span style="color: #BA2121">&quot;sphinx-build doc build&quot;</span> .
</pre></div>


<p>Now that I can regenerate HTML automatically, I need a way to reload the browser window automatically:</p>
<p><strong>auto-reload</strong> is a <a href="https://addons.mozilla.org/en-US/firefox/addon/auto-reload/">Firefox extension</a> that detects any tab with a <code>file://</code> URL and reloads it when the file changes. In my testing it seems to detect changes in linked files (CSS and Javascript) too. A nice little bar slides down to tell me when it's reloading. That way I know that the reason the page is still a mess is because my reST is still wrong, not because it hasn't reloaded:</p>
<p><img style="display:block; margin-left:auto; margin-right:auto;" src="auto-reload.png" alt="Auto reload" title="auto-reload.png" border="0"   /></p>
<p>This little suite of tools deals well with invoking Sphinx and reloading my web page, so I can focus on the task at hand: trying to write reStructuredText, which is a loathsome afterbirth expelled from the same womb as XML and TeX.</p>
