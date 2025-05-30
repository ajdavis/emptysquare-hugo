+++
type = "post"
title = "What It's Like To Work For 10gen"
date = "2013-02-28T18:36:30"
description = "Robot battles, concurrency bugs, and loyalty."
category = ["MongoDB", "Programming"]
tag = []
enable_lightbox = false
thumbnail = "bot.jpg"
draft = false
+++

<p>My colleague Kristina Chodorow wrote a post <a href="http://www.kchodorow.com/blog/2011/10/18/on-working-at-10gen/">on working at 10gen</a> with which I was a bit obsessed when I applied for a gig here in late 2011. Recently I've had an eventful couple weeks: I went to Miami, won a robot battle, and helped the Ruby driver team fix some bugs. Seems like a good time to add to the "Working at 10gen" genre.</p>
<hr />
<p>10gen, the MongoDB company, is as distributed as our database. We're spread around four continents, partly because we hired interesting people wherever they were, and partly to support our customers in their regions and time zones. Once a year everyone comes together, this time in Miami. My room had an acceptable vista:</p>
<p><img style="display:block; margin-left:auto; margin-right:auto;" src="IMG_0333.jpg" alt="IMG 0333" title="IMG_0333.jpg" border="0"   /></p>
<p>There was a hot tub on my balcony but I was the only one so equipped. Please don't tell my colleagues.</p>
<p>At our annual meetings we have nerdy contests. Last year, rocket building. This year, Lego robots that we programmed to push each other off a table.</p>
<p>The basic robot kit comes programmed to turn in a circle, and when it detects something in front of it, it charges. The 10gen teams came up with designs a little more sophisticated. Most bots had color-sensors pointed at the table's surface in front of them, so they could turn away from the edge without falling off. By far the cleverest hack I saw was this:</p>
<p><img style="display:block; margin-left:auto; margin-right:auto;" src="bot.jpg" alt="Bot" title="bot.jpg" border="0"   /></p>
<p><span style="color: gray">Photo: <a href="https://twitter.com/GaryMurakami" style="color: gray">Gary Murakami</a></span></p>
<p>The robot has a black stripe taped to its front and rear shovels, which slips under the opponent's color-sensor. The opponent sees the stripe, thinks it's about to fall off the table, and turns away&mdash;and falls off the table.</p>
<p>Despite its brilliance, this subterfuge lost to my team's strategy. (Disclosure: I was doing customer support when they built the bot, so I take no credit.) We had a slow, powerful machine with a high shovel in front. Because it was high, the shovel tilted our opponents upward off their treads and robbed them of traction. It wasn't a very smart robot, but mechanics and brute force won the prize.</p>
<p>The kits were quite expensive, I hear. We tried not to bang them up too badly, or lose any parts, so we could donate them to a local middle school.</p>
<p>It's this combination of enjoyment with care-taking that I loved about the Miami meeting. We play like kids but we are not children. We never forgot that we're spending other people's money when we meet: aside from a few hours of robot-fighting, we spent our two and a half days in Miami holed up in conference rooms planning our future. Our event planner Samantha made it clear that we were not to spend any extra time in Miami on the company's dime. If we weren't on a plane home within a few hours of its ending, our expenses were our own. It sounds harsh but it's a mature attitude: we must take the greatest care with the capital entrusted to us.</p>
<p>The final day of our meeting, the Ruby driver team had a crisis. A customer reported that the driver was <a href="https://jira.mongodb.org/browse/RUBY-545">leaving cursors unclosed on replica-set members</a>, because it sent the <code>killCursors</code> message to the wrong member. The Ruby team is normally four coders: Tyler Brock, Gary Murakami, Emily Stolfo, and Brandon Black. But Bernie Hackett and I from the Python team, and Jeff Yemin from Java, joined to take a look. Ruby Team Plus dug into the customer's reports and I learned that the driver was in a novel operating environment, and it was not thriving there. It was running in JRuby with a big thread pool, which exposed threading issues that had lain dormant for months. Not only was it leaving cursors open, but <a href="https://jira.mongodb.org/browse/RUBY-554">the JRuby BSON extension had concurrency bugs</a>, and there was a strange performance degradation in the connection pool. I spent my time looking for connection-pool bugs and found a neat puzzler: I'm going to write about that in my next post.</p>
<p>Ruby Team Plus formed in a conference room in Miami, and drifted apart after we nailed down the last of the bugs by video-chat, nine intense days later. (Much more intense for the core Rubyists than for me.) No manager said, "You guys should help the Ruby team." We thought we could be useful, so we helped. I admire this about 10gen. I also admire that we piled in to help a customer without checking whether they had some Special Diamond Premium contract. They'd found bugs we needed to fix, so we worked nights and weekends to fix them. (And once they were fixed, we made it up to ourselves with some time off.)</p>
<p>That's what it's like to work for 10gen. I'm proud of us, and I'm having the time of my life.</p>
<p><img style="display:block; margin-left:auto; margin-right:auto;" src="miami-beach.jpg" alt="Miami beach" title="miami-beach.jpg" border="0"   /></p>
<p><span style="color: gray">Photo: <a href="https://twitter.com/GaryMurakami" style="color: gray">Gary Murakami</a> again</span></p>
