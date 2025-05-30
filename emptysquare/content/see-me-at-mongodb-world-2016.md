+++
type = "post"
title = "Come to MongoDB World. We Need To Talk."
date = "2016-06-09T14:39:58"
description = "I'll tell you about the outcome of four years' thought: a smart strategy for resilient MongoDB applications."
category = ["Programming", "MongoDB"]
tag = ["mongodbworld"]
enable_lightbox = false
thumbnail = "ian-mad.png"
draft = false
+++

<p>Please come see me at MongoDB World. It's in New York on June 28 and 29. <a href="http://www.eventbrite.com/e/mongodb-world-2016-registration-19019600136?discount=jessedavis">I'll give you 25% off</a>, I just need to talk to you.</p>
<p>You see, for four years, I've had this guilt hanging over me. It goes back to a winter afternoon in early 2012, when I met a MongoDB customer who was very angry. He'd come to our regular "MongoDB Office Hours" at our old spot in Soho, and he had one question: "When a MongoDB driver handles a network error, what should my code do?"  He demanded to know why I didn't have a simple answer for him.</p>
<p>I'd been working for MongoDB just a few months. This guy, I'll call him Ian, was upset, and I couldn't help him. My guilt has pressed the memory of that day in my brain. I can still see Ian's face, haggard as if he'd been up all night worrying about network errors. We were sitting in a little windowless room, the only free room we could talk in at our little office. We sat side by side on the edge of the table, because the room had no chairs.</p>
<p>I told him there's no single solution that applies to the diverse applications and features people build on MongoDB, and no one approach to all kinds of errors. This did not go over well.</p>
<div style="text-align: center">
<img src="ian-mad.png">
</div>

<p>In the years since, I've worked to answer Ian. First, I wrote <a href="/server-discovery-and-monitoring-in-pymongo-perl-and-c/">the Server Discovery and Monitoring Spec</a>, which all our drivers have now implemented. The spec vastly improves drivers' robustness in the face of network errors and server failovers. Complaints like Ian's are rarer now, because drivers throw exceptions more rarely. But still: how <strong>would</strong> I answer him, if he came into our new office in Times Square today? What's a smart strategy for writing a resilient MongoDB application?</p>
<p>On June 28 in New York, I'm going to answer him. I'm going to talk about a solution four years in the making, which combines the latest driver technology with a wise approach to making MongoDB operations idempotent.</p>
<p>Ian, if you're out there: Come to MongoDB World. We need to talk. I'll give you 25% off the ticket price, my discount code is "jessedavis". Anyone can use it, even if you aren't Ian:</p>
<div style="text-align: center">
<a style="font-weight: bold; font-size: large" href="http://www.eventbrite.com/e/mongodb-world-2016-registration-19019600136?discount=jessedavis">25% off MongoDB World Tickets</a>
</div>

<p><br>
I hope to see you there. I owe you.</p>
