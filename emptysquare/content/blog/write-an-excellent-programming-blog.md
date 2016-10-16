+++
type = "post"
title = "Write An Excellent Programming Blog"
date = "2014-06-26T10:44:05"
description = "I want you to write. You can help us by writing just as much as by hacking. Besides, it's the best way to learn: writing is thinking."
categories = ["Programming", "Python"]
tags = []
enable_lightbox = false
thumbnail = "vermeer-writing.jpg"
draft = false
+++

<p><img style="display:block; margin-left:auto; margin-right:auto;" src="vermeer-writing.jpg" alt="Vermeer, Lady Writing a Letter with her Maid" title="Vermeer, Lady Writing a Letter with her Maid" /></p>
<p>I want you to write. Not just code. Also words.</p>
<p>If you're a member of the open source community, you can help us by writing about programming, just as much as by actually programming. And writing helps you, too: you can become better known and promote your ideas.</p>
<p>Even more importantly, writing is thinking. There is no more thorough way to understand than to explain in writing.</p>
<div class="toc">
<ul>
<li><a href="#why">Why?</a></li>
<li><a href="#what">What?</a><ul>
<li><a href="#story">Story</a></li>
<li><a href="#opinion">Opinion</a></li>
<li><a href="#how-to">How-To</a></li>
<li><a href="#how-something-works">How Something Works</a></li>
<li><a href="#reviews">Reviews</a></li>
</ul>
</li>
<li><a href="#how-do-you-find-an-audience">How do you find an audience?</a></li>
<li><a href="#how-do-you-improve">How do you improve?</a></li>
<li><a href="#how-do-you-make-the-time">How do you make the time?</a></li>
<li><a href="#conclusion">Conclusion</a></li>
</ul>
</div>
<h1 id="why">Why?</h1>
<p>It doesn't matter how narrow your expertise is. If you know better than anyone how to parse New York City subway schedules, I want you to write about it. If you've taught your cat to care for a Tamagotchi, I <em>definitely</em> want you to write about it. Whatever your expertise is, show me what you know. Then when I have a question about your specialty, I'll know to come to you for help.</p>
<p>For example, the author of <a href="https://pypi.python.org/pypi/happybase/">HappyBase</a>, a Python driver for HBase, emailed me for advice when he began his project. He knew from my blog that I work on a couple MongoDB drivers, and he had very sophisticated questions for me about connection pooling. Working with him was stimulating, and it was a very efficient way for me to contribute to a popular project.</p>
<p>Being known in your community as an expert or as a cogent explainer helps you. You're more likely to get patches accepted by projects, get talks accepted by conferences, get users, get a job.</p>
<p>Writing an explanation of a bug requires you to think it through, better than any other technique. My faith in writing-as-thinking is so fervent that when I see a tricky bug my first step is to start an article. That is what I did when I hit a bug in PyMongo's connection pool last year. It turns out that in Python 2.6, <a href="/blog/another-thing-about-pythons-threadlocals/">assigning to a threadlocal is not thread-safe</a>. I am not nearly smart enough, dear reader, to discover such an intricate race condition unless I consolidate each step of the discovery by explaining it in writing. </p>
<h1 id="what">What?</h1>
<p>I notice roughly five formats among the best articles by programmers: stories, opinions, how-tos, how things work, and reviews. If you want to write but you haven't chosen a topic, or don't know how to approach it, this will get you started.</p>
<h2 id="story">Story</h2>
<p>"I'm going to tell you a story about Foo, how it taught me Bar, and led to Baz. First this happened, then that happened. And that's the story of Foo."</p>
<p>Ideas:</p>
<ul>
<li><a href="https://groups.google.com/forum/#!topic/mongodb-user/UoqU8ofp134">We had an outage, this is the post-mortem.</a></li>
<li><a href="/blog/recap-open-source-bridge/">I went to a conference, heard talks, met people, learned something.</a></li>
<li><a href="http://meghangill.com/2013/06/05/how-i-survived-a-tough-mudder-with-my-fitbit-intact/">I survived a tough mudder and so did my FitBit.</a></li>
<li><a href="/blog/good-night-sweet-hamster/">I had dwarf hamsters. They died. I grieved, then accepted.</a></li>
</ul>
<p>We are innately interested in stories about people. You need not be confessional or icky. If I get to know you a little through your blog, your technical articles feel warmer, and I remember who you are.</p>
<h2 id="opinion">Opinion</h2>
<p>"Thesis. Points of evidence. Response to likely objections. Restatement of thesis." Just like we learned in high school. The most important thing is that you don't simply have an opinion, but you have a compelling and interesting argument to support it.</p>
<p>Avoid useless controversy like "product Foo is bad" or "Bar is better than Foo." You have nothing to gain by attacking others. Mr. Miyagi says: Karate for defense only.</p>
<p>Ideas:</p>
<ul>
<li>Foo is going to be the Next Big Thing.</li>
<li>Bar works great with Baz.</li>
<li><a href="http://alexgaynor.net/2014/may/19/service/">Open source authors have a grave responsibility to their users.</a></li>
<li><a href="http://jvns.ca/blog/2014/04/26/i-dont-feel-guilty-about-not-contributing-to-open-source/">It's okay not to contribute to open source.</a></li>
<li><a href="/blog/so-youre-coming-to-a-career-fair/">College students do career fairs wrong.</a></li>
</ul>
<h2 id="how-to">How-To</h2>
<p>"Doing Foo is important under the given conditions. I'm going to show you how to Foo. Do this, then do that. There, now I've shown you how to Foo. You should go out and do Foo."</p>
<p>A how-to must be motivated: you must begin by telling your reader when and why it is important to know.</p>
<p>Ideas:</p>
<ul>
<li>How do you debug a crash, memory leak, or race condition?</li>
<li><a href="http://www.kennethreitz.org/essays/growing-open-source-seeds">How do you cultivate an open source project?</a></li>
<li><a href="http://speaking.io/plan/repetition/">How do you prepare a talk?</a></li>
<li><a href="http://meghangill.com/2012/03/11/how-to-run-a-tech-conference-part-1-getting-started/">How do you run a conference?</a></li>
<li>Any time you solve a problem, write down how you did it!</li>
</ul>
<h2 id="how-something-works">How Something Works</h2>
<p>"Do you wonder how Foo works? I'm going to show you how Foo is implemented. It does this and that. Now I've shown you how it works."</p>
<p>Almost every technology I hold in awe has been easier to understand, when I read its source code, than I feared it would be. Writing an explanation of it is a good excuse to dive in and find out.</p>
<p>A "how something works" article need not be motivated. Sure, some readers might want to know how something works in order to use it better. But there are people like me who want to know how almost everything works, and we are your audience for this article. People who don't want to know can move along.</p>
<p>Ideas:</p>
<ul>
<li>How does the Django ORM generate SQL?</li>
<li>How does socket.settimeout() work?</li>
<li><a href="http://akaptur.github.io/blog/2014/06/11/of-syntax-warnings-and-symbol-tables/">Why does this Python code raise a SyntaxWarning?</a></li>
<li><a href="http://late.am/post/2012/06/18/what-the-heck-is-an-xrange">How does xrange work?</a></li>
</ul>
<h2 id="reviews">Reviews</h2>
<p>"I read, saw, played, or used something. This is what it is. This is what my experience was like. The thing has these strengths and weaknesses. In conclusion, it's best when evaluated by certain criteria."</p>
<p>It's tempting to evaluate a book, movie, game, or project on a good&ndash;bad axis, but this isn't very useful. Mostly describe and analyze instead of evaluating. Tell me what the thing is good <em>for</em>.</p>
<p>Ideas:</p>
<ul>
<li>Technical books! They need not be recent, though staying abreast of publications in your area is good. Reading a book with the intent to review it makes you read more closely, and teaches you about good technical writing too. <a href="/blog/building-node-applications-mongodb-backbone/">Here's my review of O'Reilly's "Building Node Applications with MongoDB and Backbone"</a>.</li>
<li>Others' software projects. But be gentle.</li>
<li>Games, movies, music, books that are not about programming: Writing reviews is excellent practice, and warms your blog.</li>
</ul>
<h1 id="how-do-you-find-an-audience">How do you find an audience?</h1>
<p>Please don't care about reach. Reach is not the aim of writing about programming. <a href="http://sethgodin.typepad.com/seths_blog/2013/09/what-does-the-fox-say.html">Seth Godin</a>: "Most of the time, you'll aim to delight the masses and you'll fail. So much easier to aim for the smallest possible audience, not the largest, to build long-term value among a trusted, delighted tribe, to create work that matters and stands the test of time."</p>
<p>Since you don't care about reach, don't waste time on SEO. Your goal is not to get lots of hits. You aren't BuzzFeed. Random visitors aren't valuable to you, because you don't show ads. Instead, your goal is to attract specialists in your field so you can share ideas with them. Luckily, you can reach these specialists without much effort.</p>
<p>First, find the aggregator your community reads. I write a lot about Python, and the <a href="http://planet.python.org/">Planet Python</a> aggregator is by far my best channel for distributing articles. Any article I put in the "Python" category is included in its feed, and that guarantees a few hundred visits. <a href="https://github.com/python/planet">Send a pull request to have your feed included in Planet Python</a>. (And be patient, it's run by volunteers with busy lives.) If you write about another language or technology with a large community, find its aggregators and request to be included in them.</p>
<p>Tweeting your articles has some value. More valuable is posting your article on a relevant subreddit. <a href="https://training.kalzumeus.com/newsletters/archive/content-marketing-strategy">And use your own home page to send visitors to your best articles</a>, don't just display the most recent ones there.</p>
<p>You can try your luck on Hacker News, but I have concluded that no one serious goes there, so I do not either.</p>
<h1 id="how-do-you-improve">How do you improve?</h1>
<p>Write. Emulate the best bloggers and the best articles.</p>
<p>Don't emulate Daring Fireball, GigaOM, or TechCrunch. These are industry news sites, ultimately devoted to one question: which companies' stocks will go up, and which will go down? This is not your expertise. Besides, it's boring. Emulate writers like these instead:</p>
<p>Glyph Lefkowitz. In <a href="https://glyph.twistedmatrix.com/2014/02/unyielding.html">"Unyielding"</a>, he argues that async's greatest strength is not that it is efficient, but that it makes race conditions easier to avoid.</p>
<p>Kristina Chodorow. <a href="http://www.kchodorow.com/blog/2013/04/09/stock-option-basics/">"Stock Option Basics"</a> tells a personal story about quitting a startup, and describes better than most writers how stock options work. In <a href="http://www.kchodorow.com/blog/2011/01/25/why-command-helpers-suck/">"Why Command Helpers Suck"</a> she publicly and convincingly criticizes some MongoDB design decisions because they discourage users from advancing their understanding. Her <a href="http://www.kchodorow.com/blog/2013/01/15/intro-to-fail-points/">article on MongoDB unittesting</a> is very specialized, but I've referred to it many times since it fills a woeful gap in the MongoDB developer docs. Kristina's funny and amiable voice works well on her blog and in O'Reilly's "MongoDB: The Definitive Guide".</p>
<p>Armin Ronacher. His <a href="http://lucumr.pocoo.org/2011/2/1/exec-in-python/">"Exec in Python"</a> article is long, incredibly thorough, and timeless. It takes an hour or more to read. It took him days to write, I'm sure, and he continued correcting it after publication. It brings insights into the Python 2 and 3 runtimes, how web2py works, and builds an argument for how it should work instead.</p>
<p>Julia Evans is loose and exuberant in her blog, the same as when she speaks. But don't be fooled, <a href="http://jvns.ca/blog/2014/06/06/should-my-conference-do-anonymous-review/">her argument for anonymizing conference proposals</a> is meticulous. So is <a href="http://jvns.ca/blog/2014/06/19/machine-learning-isnt-kaggle-competitions/">her guide to applying machine learning to business problems</a>.</p>
<p>Graham Dumpleton's <a href="https://github.com/GrahamDumpleton/wrapt/tree/master/blog">magisterial series on Python decorators</a> obsoletes all other writing on that topic.</p>
<p>At Open Source Bridge a group of writers made <a href="/blog/resources-for-writing-about-programming/">a list of additional writers to emulate, and tips for improving our writing about programming</a>.</p>
<h1 id="how-do-you-make-the-time">How do you make the time?</h1>
<p>Writing doesn't have to be a regular time-suck, because there is no need to publish regularly or often. Most of your value is in infrequent, deep articles. Furthermore, there's no rush to write an article now, because the best subjects are evergreen. <a href="https://training.kalzumeus.com/newsletters/archive/content-marketing-strategy">Patrick McKenzie</a>: "You can, and should, make the strategic decision that you'll primarily write things which retain their value. It takes approximately the same amount of work to create great writing which lasts versus creating great writing which ages quickly."</p>
<p>(That's my second link to the same essay, it's that good.)</p>
<p>So take your time. When you have a good idea or an unusual experience, you'll be moved to write.</p>
<h1 id="conclusion">Conclusion</h1>
<p>You know something very specific about programming that's worth explaining. Or you have a new way to explain a common topic. Either way, I want you to share your knowledge in writing. Explaining will deepen your understanding as nothing else can. If you don't know what to write about, riff off the ideas I suggested, or get inspired by great blogs. Craft articles of lasting value.</p>
    