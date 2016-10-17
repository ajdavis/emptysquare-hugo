+++
type = "post"
title = "2014: My Year In Review"
date = "2015-01-02T19:04:34"
description = "A year crammed with Python and Zen, and looking forward to another one."
"blog/category" = ["Mongo", "Motor", "Python", "Zen"]
"blog/tag" = []
enable_lightbox = false
thumbnail = "manhattan@240.jpg"
draft = false
+++

<p><img style="display:block; margin-left:auto; margin-right:auto;" src="manhattan.jpg" alt="Manhattan" title="Manhattan" /></p>
<p>I'm inspired by <a href="http://therealkatie.net/blog/2014/dec/31/looking-back-and-looking-forward-2014/">Katie Cunningham's blog post "looking back and looking forward"</a> to review my year and the prospects for 2015.</p>
<h1 id="2014">2014</h1>
<h2 id="python">Python</h2>
<p>Most of the code I wrote this year was open source Python for MongoDB: <a href="/blog/pymongo-2-7-rc0/">Bernie Hackett and I shipped PyMongo 2.7</a>, and we began <a href="/blog/good-idea-at-the-time-pymongo/">an overhaul of PyMongo to correct its regrettable designs</a>, which we'll release in a couple months as PyMongo 3.0.</p>
<p>I made two versions of Motor, my non-blocking MongoDB driver for Tornado. <a href="/blog/motor-0-2-released/">Motor 0.2 was a near-rewrite</a> of the driver, while <a href="/blog/motor-0-3-released/">Motor 0.3 was a more routine set of improvements</a>.</p>
<p>I spent a large part of the year specifying logic in YAML and English instead of Python: I wrote the <a href="/blog/server-discovery-and-monitoring-spec/">Server Discovery And Monitoring Spec</a> to standardize how all MongoDB drivers talk to clusters of database servers.</p>
<p>For the first time, I added a feature to the Python standard library: I wrote a set of <a href="https://docs.python.org/3/library/asyncio-sync.html#queues">queue classes for asyncio</a>, which shipped with Python 3.4 in March.</p>
<h2 id="speaking">Speaking</h2>
<p>I spoke at some neat conferences: PyCon, OSCON, MongoDB World. I lost my nervousness and had fun, even on the big PyCon stage. The foremost conference in my affections this year, as always, was Open Source Bridge. It's put on by <a href="http://stumptownsyndicate.org/">the Stumptown Syndicate</a>, whose mission is to "create resilient, radically inclusive tech and maker communities that empower positive change." The generosity of that statement is really put into practice at the conference.</p>
<h2 id="mentorship">Mentorship</h2>
<p>To my surprise, I had a good time mentoring three young coders. In the year previous, I'd done all I could to shirk my responsibilities as a mentor, and the result was predictable: I failed at mentorship and everyone was mad at me. This year I turned it around. I guided a pair of interns as they contributed to the high-performance <a href="https://bitbucket.org/djcbeach/monary/src">Monary driver</a>. They weren't just successful at improving Monary&mdash;they got a talk into a local Python conference, and decided to work at MongoDB full time when they graduate. When my interns went back to school I was assigned a talented new hire to continue the project. She was just as productive as my interns had been, and presented her work to a data science conference.</p>
<p>I had not expected to feel so fulfilled by these junior coders' achievements. I've had to update how I see myself: what I care about, what my purpose is. For years I've resisted roles that take time from my own coding, but now I've tasted the fruit of leadership. I'm going to speak about this at PyTennessee in February and <a href="http://emptysqua.re/blog/mentoring/">write about it soon</a>.</p>
<h2 id="zen">Zen</h2>
<p>My Zen practice is developing similarly: my teacher Enkyo Roshi asked me to be the Village Zendo's shuso, the "practice leader", this winter. So far, my duties have been mainly logistical, and not too strenuous. But over the next three months I'll help set the agenda for our temple, and in March I'll give my first dharma talk. The group will test me in dharma combat. If I pass, I'll be a senior student in our sangha and a regular speaker on Zen. The same way that my role as an individual coder is ending at work, my self-focused practice is over, replaced by practicing for the sake of my community.</p>
<h2 id="regrets">Regrets</h2>
<p>With all this excitement, I had to put some pursuits on hold. I took just a handful of good photos this year, and read hardly any good books. My one trip abroad was so abbreviated that I flew all the way to Taipei and only spent one day sightseeing.</p>
<h1 id="2015">2015</h1>
<h2 id="writing-and-speaking">Writing and Speaking</h2>
<p>What's 2015 about? I'm already committed to a frightening volume of writing and speaking: I'm giving <a href="https://us.pycon.org/2015/schedule/talks/list/">two talks at PyCon</a> and I hope to speak at MongoDB World and Open Source Bridge again. I also have the intimidating assignment of a chapter in the <a href="http://aosabook.org/en/index.html">Architecture of Open Source Applications</a> series. Fortunately, I have a very smart coauthor.</p>
<h2 id="python_1">Python</h2>
<p>I'll keep writing open source Python at MongoDB. We're going to release an overhauled PyMongo and say goodbye to five years of accumulated cruft. The current PyMongo is a very high-quality codebase, but the anguish of maintaining that level of quality despite all its baggage is not something I'll miss. Motor, meanwhile, will gain superpowers: it won't just support Tornado, but also asyncio, and perhaps even Twisted. If I achieve this Python async trifecta, expect me to brag about it at length.</p>
<p>I want to make a big contribution to a non-MongoDB Python package this year. Much like I added queues to asyncio in 2014, I'm going to add locks and queues to Tornado. The synchronization primitives currently living in my <a href="https://toro.readthedocs.org/en/stable/">Toro</a> package will become part of Tornado.</p>
<h2 id="c">C</h2>
<p>Despite all these Python commitments, 2015 will be the year I become bilingual. The plan is, I'm going to become sufficiently expert in C that I can join MongoDB's C Driver team, perhaps even lead it. Like my other plans, this one is intimidating. I'll need a great mentor, and I'm lucky to have one: our current C driver developer Jason Carey has agreed to show me the ropes. Wish me luck.</p>
<h2 id="zen_1">Zen</h2>
<p>I have a great Zen mentor too: <a href="http://villagezendo.org/teachers/roshi-enkyo-ohara/">Enkyo Roshi</a> has for some reason decided that I should become a senior Zen student this year, and I have to trust she knows what she's doing. If all goes well, I'll start giving dharma talks at the Village Zendo and at Sing Sing this year. I have a lot of opinions about Zen, but that won't amount to much when it comes time to speak. So please, wish me luck with this, too.</p>
    