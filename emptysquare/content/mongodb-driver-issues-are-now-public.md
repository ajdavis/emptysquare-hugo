+++
type = "post"
title = "MongoDB Driver Issues Are Now Public"
date = "2015-03-03T13:46:43"
description = "We're opening our ticket tracker so you can see all cross-language issues."
category = ["MongoDB", "Python"]
tag = ["pymongo"]
enable_lightbox = false
thumbnail = "forest.jpg"
draft = false
disqus_identifier = "54b97c8a5393740964f676a0"
disqus_url = "https://emptysqua.re/blog/54b97c8a5393740964f676a0/"
+++

<p><img style="display:block; margin-left:auto; margin-right:auto;" src="forest.jpg" alt="Forest" title="Forest" /></p>
<p>For the last year, the MongoDB drivers team has focused on standardizing <a href="http://docs.mongodb.org/ecosystem/drivers/">our eleven official drivers</a>. Gradually, we're cleaning up inconsistent behaviors and APIs. Ideally, users and our customer-support team need to learn MongoDB once, instead of re-learning MongoDB in each programming language. We're also sharing our bugfixes among drivers: if I made a mistake, there's a good chance someone else made the same mistake in another language. We publish our bugfixes to the team so everyone can check their code.</p>
<p>We've tracked these cross-language bugs and standards in a private Jira project, "DRIVERS". <a href="https://jira.mongodb.org/browse/DRIVERS">Last week, that project went public</a>. Anyone can comment, browse tickets, and create new ones.</p>
<p>In the past you could see issues in each driver's project, like the "PYTHON" or "JAVA" projects. Those were always public. But not the umbrella DRIVERS tickets. We felt that we needed a private place to propose and debate features, for a few reasons: We wanted to talk about specific customers' requirements in confidence, and we wanted to discuss controversial features frankly among ourselves, before getting the community's opinion. We worried that if we didn't have a private place to discuss them in Jira, we'd use email and lose the advantages of a ticket-tracking system. The cross-language bugfixes didn't need to be private but they were by default, since they were in the same project as the cross-language features.</p>
<p>But we changed our minds about these private discussions. The MongoDB server's tickets have always been public, after all. Our drivers are open source and we develop in the open, so the DRIVERS project should be open too. We'll still use private comments when we discuss particular customers' needs, of course. But now the default for DRIVERS tickets is open, not closed.</p>
