+++
type = "post"
title = "Black Pipe Testing: In Summary"
date = "2015-12-01T08:44:56"
description = "Black pipe testing does not replace other kinds of tests, but there are two scenarios where it shines."
category = ["C", "MongoDB", "Programming", "Python"]
tag = ["black-pipe"]
enable_lightbox = false
thumbnail = "rainy-montreal_2644619595_o.jpg"
draft = false
disqus_identifier = "565d0ffc1e31ec1d48845680"
disqus_url = "https://emptysqua.re/blog/565d0ffc1e31ec1d48845680/"
series = ["black-pipe"]
+++

<p><a href="https://www.flickr.com/photos/emptysquare/2644619595/"><img style="display:block; margin-left:auto; margin-right:auto;" src="rainy-montreal_2644619595_o.jpg" alt="Pipe in Montreal" title="Pipe in Montreal" /></a></p>
<p>Every conversation I hear about testing seems to go thus:</p>
<p>"Here's a useful way to test!"</p>
<p>"But if you only test that way, you won't catch all the bugs."</p>
<p>I would like us, the open source community, to move on from this conversation. Each testing method is useful for some kinds of software, and each accomplishes some goals. But none is plenipotent. There is no silver bullet.</p>
<p>So the next time someone proposes unit testing, please don't object: "Unit tests can't catch integration bugs." Nor, when you hear about integration tests, should you object: "Integration tests don't reveal bugs as early as unit tests." Instead, consider whether each method is being applied where appropriate, or if some other method would be better in this particular circumstance.</p>
<p>It's the same with <a href="/black-pipe-testing-series/">this series of articles I've written about "black pipe" testing</a>. I make no claim that my testing method is perfect, certain, and complete. Please don't replace your other tests with black pipe tests wholesale. I have merely identified a color in the spectrum that ranges between unit tests and integration tests, and named it. And I have distinguished two scenarios where I think black pipe testing is a superior way to test connected applications.</p>
<p>The first scenario is when your code's observable behavior is correct, even if it misbehaves at the network layer. In this case, a black pipe test can watch the wire and check that your code sends the messages you expect. I describe a case like this in <a href="/black-pipe-testing-pymongo/">Testing PyMongo As A Black Pipe</a>: PyMongo would appear correct even if it sent outdated wire protocol messages to MongoDB. I need a black pipe test to validate that PyMongo uses the latest MongoDB wire protocol.</p>
<p>Second, black pipe tests can reliably test rare events, like network timeouts, hangups, and resets. These events are hard to trigger during integration testing. If you want to continuously test your code's reaction to a timeout, for example, it may not be practical to stop a network interface at exactly the moment when your test is exercising the relevant code. But a black pipe test impersonates the server and reacts predictably to each message your code sends.</p>
<p>Black pipe tests are a useful complement to your existing methods. If you have bad tests or untested code that falls into one of these two scenarios, I hope my articles offer you the tool you did not know you lacked.</p>
<p>I hope you apply this method to servers besides MongoDB. Take inspiration from <a href="/black-pipe-testing-pymongo/">MockupDB's API</a> in Python, or the <a href="/libmongoc-black-pipe-testing-mock-server/"><code>mock_server_t</code> functions in C</a>, but impersonate some other server: a mock PostgreSQL server, for example, could be used to test thousands of different client libraries and applications. A mock LDAP or SMTP server would be similarly useful. And if you write a RESTful HTTP server with testing methods as expressive and convenient as MockupDB's, the number of Python client libraries you could help test would be practically numberless.</p>
<hr />
<p>Further reading:</p>
<ul>
<li><a href="http://late.am/post/2015/04/20/good-test-bad-test.html">Dan Crosta's "Good Test, Bad Test"</a></li>
<li><a href="http://www.curiousefficiency.org/posts/2015/07/asyncio-tcp-echo-server.html">Nick Coghlan's "Client and Server in Python 3.5"</a></li>
</ul>
<hr />
<p><a href="https://www.flickr.com/photos/emptysquare/2644619595/"><span style="color:gray">Image: a pipe in Montreal</span></a></p>
