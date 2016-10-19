+++
type = "post"
title = "Experiences Migrating to Lektor"
date = "2016-01-16T10:04:13"
description = "What I learned porting my blog to Armin Ronacher's new static site generator."
category = ["Programming", "Python"]
tag = ["lektor"]
enable_lightbox = false
thumbnail = "association@240.png"
draft = false
+++

<p><img alt="" src="Medieval_writing_desk.jpg" /></p>
<p>Over the last few weeks I've ported this blog, with over 400 articles, to Armin Ronacher's new static site generator <a href="http://getlektor.com">Lektor</a>. Lektor will grow and mature for years to come, but it isn't too early to write up my experience rebuilding a substantial site with it.</p>
<p>These observations fall into two categories. One is the comparison between Lektor and my homemade blog software, Motor-Blog. The other is the comparison between running a dynamic server versus deploying a static site.</p>
<h1 id="lektor-vs-motor-blog">Lektor vs Motor-Blog</h1>
<p>Motor-Blog is my basic blog engine written in Python. I don't recommend you use it. I wrote it to exercise my async MongoDB driver, <a href="https://motor.rtfd.org/">Motor</a>. Since the blog engine was just a side-project I skipped the hard part: I never wrote an editor. Instead, I implemented enough of WordPress's XML-RPC API that I could edit my blog with a commercial WordPress client, MarsEdit. I never loved MarsEdit. Its Markdown editor is merely competent, it isn't built for sharing code samples, and adding multiple images to an article (which I do often) is a chore.</p>
<p>Now with Lektor, my articles are just Markdown files on my hard drive, and I edit them with any tool at hand. I import images simply by resizing them all in one batch (a snap with Photoshop) and dropping them in a directory. I can include them all in my Markdown using an emacs macro, a Python script, or whatever I choose. Since the article is a local text file, the power of my programming tools is easily brought to bear.</p>
<p>But most of the time, I'm writing prose. Lektor can run a local server and show a basic in-browser editor, but I don't use it. Instead, I manage my project with PyCharm, my favorite Python IDE, which does a fine job of searching and organizing my Markdown files. I edit the Markdown with MacDown.</p>
<p>MacDown's rendering isn't perfect, since a <code>contents.lr</code> file has some non-Markdown metadata, but it's perfectly good for editing. As a surprising bonus, images display correctly.</p>
<p>I've configured my system to make it easy to switch between PyCharm and MacDown. First, I associate all Lektor's content files, which are called <code>contents.lr</code>, with MacDown:</p>
<p><img alt="File association" src="association.png" /></p>
<p>Now if I type <code>open contents.lr</code> in the Mac OS command line, it opens the file in MacDown. Next, in PyCharm, I configure <code>open</code> as an "external tool":</p>
<p><img alt="&quot;open&quot; external tool" src="open-external-tool.png" /></p>
<p>I associate this tool with a keyboard combo so that, whenever I highlight or open one of these <code>contents.lr</code> files in PyCharm, I can switch to MacDown with keystroke.</p>
<p>Publishing a draft is completely manual. It begins with an article in a <code>contents.lr</code> file like this:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">
title: Experiences Migrating to Lektor
&#45;&#45;&#45;
pub_date:
&#45;&#45;&#45;
body:

Over the last few weeks I've ported my blog....
</pre></div>

<p>I remove the <code>_discoverable: no</code> line, and set <code>pub_date</code> to now. To generate publication dates, I've configured what PyCharm calls a "live template":</p>
<p><img alt="" src="live-template.png" /></p>
<p>When I type "nnow" in PyCharm and hit Tab, it inserts a properly-formatted datetime.</p>
<p>Lektor is brand new. And it isn't a blog engine: it's a <em>framework</em> for building static site generators, including blog engines. It's flexible and general, but lacks some features for my daily needs. I built what I needed and contributed to Lektor when appropriate. For example, I needed "previous" / "next" navigation between consecutive blog posts, basic tagging, an Atom feed, and support for the datetime type. Throughout, Armin has been extraordinarily responsive on the <a href="https://gitter.im/lektor/lektor">Lektor IM channel</a>, guiding and encouraging me and accepting my patches.</p>
<p>For now, Lektor generates simple sites. If you're like me&mdash;a Python programmer willing to tinker&mdash;then it's a rewarding hobby to generate a complex site using Lektor's elegant API. Hacking on Lektor itself is a pleasure: the code and community are equally charming. Soon I expect Lektor will rival Jekyll and Pelican for its rich set of features, plugins, and themes.</p>
<h1 id="dynamic-vs-static">Dynamic vs Static</h1>
<p>The greater change, I think, is the one from a dynamic site backed by a running server, versus a static one.</p>
<p>My old blog ran on Tornado, backed by MongoDB and fronted with NGINX. This was overpowered but at least it was configurable. I added any kind of redirects I wanted, and I installed an SSL certificate and forced all traffic to HTTPS.</p>
<p>When I migrated to Lektor, I first deployed to GitHub Pages. They're free, and Lektor ships with support for this configuration. But you cannot really redirect from one URL on your site to another: only HTML redirects work. Those are fine if the visitor is a browser, but not for other clients. In particular, Planet Python's aggregation script stopped updating my feed.</p>
<p>Worse, I couldn't use my domain "emptysqua.re" with HTTPS on GitHub Pages, and there's no way to redirect from HTTPS to HTTP. Stale HTTPS links just time out, slowly and painfully. Any secure links to my old site from the outside world failed.</p>
<p>After enduring GitHub Pages with clenched teeth for a week, I redeployed to <a href="https://surge.sh">surge.sh</a>. The Surge interface's minimalism is so bold it's shocking. For example, I kept looking on the Surge website for a place to sign up, until I realized: it's <em>all</em> on the command line, including entering my credit card number. Once I overcame my false assumptions, moving my site to Surge took an hour or less, including SSL configuration.</p>
<p><strong>Update:</strong> A problem with Surge is that it <a href="https://github.com/sintaxi/surge/issues/119">re-uploads my entire site from my laptop each time I deploy</a>. That's simple and effective for small sites. But I have 400 articles, all illustrated, so my site weighs almost a gigabyte. The breaking point came to me yesterday when I was trying to publish a blog post from an airplane and found it was impossible to stay online long enough to complete the upload. I switched to <a href="https://www.netlify.com/">Netlify</a> today and it seems great.</p>
<hr />
<p><a href="https://commons.wikimedia.org/wiki/File:Medieval_writing_desk.jpg">Image: Medieval writing desk</a></p>
