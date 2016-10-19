+++
type = "post"
title = "reStructured Text With Chrome And LiveReload"
date = "2014-10-06T11:41:12"
description = "An effective little workflow for writing RST."
category = ["Programming", "Python"]
tag = []
enable_lightbox = false
thumbnail = "disabled@240.png"
draft = false
disqus_identifier = "5430ba9d5393740961f61a4b"
disqus_url = "https://emptysqua.re/blog/5430ba9d5393740961f61a4b/"
+++

<p>I've found a useful set of tools for writing RST, when I must. I'll show you how to configure LiveReload and Chrome to make the experience of writing RST's tortured syntax somewhat bearable.</p>
<p>(This article is an improvement over <a href="/restructuredtext-in-pycharm-firefox-and-anger/">the method I wrote about last year</a>.)</p>
<h1 id="livereload">LiveReload</h1>
<p>I bought <a href="https://itunes.apple.com/us/app/livereload/id482898991?mt=12">LiveReload</a> from the Mac App Store for $10, and opened it. Under "Monitored Folders" I added my project's home directory: I was updating <a href="https://github.com/mongodb/motor/tree/master/doc">Motor's documentation</a> so I added the "motor/doc" directory.</p>
<p><img style="display:block; margin-left:auto; margin-right:auto;" src="livereload-1.png" alt="LiveReload" title="LiveReload" /></p>
<p>Next to "Monitoring 44 file extensions" I hit "Options" and added "rst" as a 45th.</p>
<p><img style="display:block; margin-left:auto; margin-right:auto;" src="livereload-2.png" alt="LiveReload file extension options" title="LiveReload file extension options" /></p>
<p>Then I checked "Run custom command after processing changes" and hit "Options". In the popup dialog I added the command for building Motor's documentation. It's a typical Sphinx project, so the build command is:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">/Users/emptysquare/.virtualenvs/motor/bin/sphinx-build \
  -b html -d _build/doctrees . _build/html
</pre></div>


<p>Note that I specified the full path to the virtualenv'ed sphinx script.</p>
<p>That's all there is to configuring LiveReload. Hit the green box on the lower right of its main window to see the build command's output. Now whenever you change an RST file you should see some Sphinx output scroll by:</p>
<p><img style="display:block; margin-left:auto; margin-right:auto;" src="livereload-output.png" alt="LiveReload Sphinx output" title="LiveReload Sphinx output" /></p>
<h1 id="chrome">Chrome</h1>
<p>Next, <a href="http://feedback.livereload.com/knowledgebase/articles/86242-how-do-i-install-and-use-the-browser-extensions-">follow LiveReload's instructions for installing the Chrome extension</a>. Pay attention to LiveReload's tip: "If you want to use it with local files, be sure to enable 'Allow access to file URLs' checkbox in Tools &gt; Extensions &gt; LiveReload after installation."</p>
<p>Now open one of the HTML files Sphinx made, and click the LiveReload icon on your browser to enable it. The difference between "enabled" and "disabled" is damn subtle. This is disabled:</p>
<p><img style="display:block; margin-left:auto; margin-right:auto;" src="disabled.png" alt="Disabled" title="Disabled" /></p>
<p>This is enabled:</p>
<p><img style="display:block; margin-left:auto; margin-right:auto;" src="enabled.png" alt="Enabled" title="Enabled" /></p>
<p>The icon plays it close to the chest, but if you hover your mouse over it, it'll admit whether it's enabled or not.</p>
<p>Back at the LiveReload application, you'll now see "1 browser connected."</p>
<p>Try it out! Now you can make changes to your RST and see it live in your browser. I don't think I'll ever learn to type RST's syntax reliably, but at least now, I can see at once whether I've typed it right or not.</p>
