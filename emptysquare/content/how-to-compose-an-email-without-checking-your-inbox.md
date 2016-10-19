+++
type = "post"
title = "How To Send An Email Without Checking Your Inbox"
date = "2016-02-03T15:42:37"
description = "Go straight to GMail's \"compose\" window without being distracted by your incoming messages."
category = ["Uncategorized"]
tag = []
enable_lightbox = false
thumbnail = "stationery@240.jpg"
draft = false
+++

<p><img alt="" src="stationery.jpg" /></p>
<p>This year I'm experimenting with a number of anti-distraction techniques. One is the latest fad, Pomodoro, in which I set a 25-minute timer to do one task, and one task only. Another is, I've dethroned GMail from its pinned tab in my browser. The idea is to choose more consciously when to check my email, instead of always having it open.</p>
<p>But what if my current task requires <em>sending</em> an email? If I open GMail, by default I see my inbox, and I risk being tempted by some juicy new subject line and forgetting what I intended to focus on.</p>
<p>I've found a way to send an email without seeing my inbox. This URL goes straight to a GMail compose-message window:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">https://mail.google.com/mail/u/?view=cm
</pre></div>


<p>(I suppose that "cm" stands for "compose message".)</p>
<p>If you're logged into multiple Google accounts, as I always am, you can specify one with "authuser":</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">https://mail.google.com/mail/u/?authuser=jesse@emptysquare.net&amp;view=cm
</pre></div>


<p>You could just bookmark this in your browser, but I've gone a step further. I set this up with the <a href="https://www.alfredapp.com/">Alfred</a> app for Mac, so when I open Alfred and type "esq" it brings me to a compose-message window:</p>
<p><img alt="" src="alfred-compose-message.gif" /></p>
<p>To create the workflow, I used Alfred's standard template "open custom URL", and set the URL to this:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">https://mail.google.com/mail/u/?authuser=jesse@emptysquare.net&amp;view=cm&amp;to={query}
</pre></div>


<p>Now I can type "esq" to start writing a message or, if I know the email address, I can type "esq ADDRESS".</p>
<p>Wish me luck. I'm going to try to stick to my Pomodoro technique for a while, and I hope the ability to send messages without seeing my inbox will help me focus.</p>
<hr />
<p><em><a href="http://www.oldbookillustrations.com/illustrations/stationery/">Image: Tony Johannot, 1843.</a></em></p>
