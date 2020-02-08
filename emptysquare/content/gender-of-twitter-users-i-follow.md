+++
type = "post"
title = "72% Of The People I Follow On Twitter Are Men"
date = "2016-06-23T22:44:47"
description = "Know your number: use my app to estimate the gender distribution of your friends on Twitter."
category = ["Programming", "Python"]
tag = []
enable_lightbox = false
thumbnail = "abacus.jpg"
draft = false
disqus_identifier = "/blog/gender-of-twitter-users-i-follow"
disqus_url = "https://emptysqua.re/blog//blog/gender-of-twitter-users-i-follow/"
+++

<p><img alt="Description: Black and white photo. A boy stands behind a very large abacus that fills the image. He looks up at the ball he is moving on one of the abacus's wires, above his eye-level. Behind him are two schoolchildren and a chalkboard with indistinct writing and diagrams." src="abacus.jpg" /></p>
<p>At least, that's my estimate. Twitter does not ask users their gender, so <a href="https://www.proporti.onl/">I have written a program that guesses</a> based on their names. Among those who follow me, the distribution is even worse: 83% are men. None are gender-nonbinary as far as I can tell.</p>
<p>The way to fix the first number is not mysterious: I should notice and seek more women experts tweeting about my interests, and follow them.</p>
<p>The second number, on the other hand, I can merely influence, but I intend to improve it as well. My network on Twitter should represent the software industry's diverse future, not its unfair present.</p>
<hr />
<h1 id="how-did-i-measure-it">How Did I Measure It?</h1>
<p>I set out to estimate the gender distribution of the people I follow&mdash;my "friends" in Twitter's jargon&mdash;and found it surprisingly hard. <a href="https://analytics.twitter.com">Twitter analytics</a> readily shows me the converse, an estimate of my followers' gender:</p>
<p><img alt="Description: Chart titled, &quot;Your current follower audience size is 1,455&quot;. A tall bar on the left is labeled, &quot;Male, 83%&quot;. A short bar on the right is labeled &quot;Female, 17%&quot;." src="twitter-analytics.png" /></p>
<p>So, Twitter analytics divides my followers' accounts among male, female, and unknown, and tells me the ratio of the first two groups. (Gender-nonbinary folk are absent here&mdash;they're lumped in with the Twitter accounts  of organizations, and those whose gender is simply <em>unknown</em>.) But Twitter doesn't tell me the ratio of my friends. <a href="http://english.stackexchange.com/questions/14952/that-which-is-measured-improves">That which is measured improves</a>, so I searched for a service that would measure this number for me, and found <a href="https://moz.com/followerwonk/">FollowerWonk</a>.</p>
<p>FollowerWonk guesses my friends are 71% men. Is this a good guess? For the sake of validation, I compare FollowerWonk's estimate of my <em>followers</em> to Twitter's estimate:</p>
<table class="table table-striped" style="margin:auto; width: 450px; margin-bottom: 20px">
<tr><td colspan=3 align=center style="font-weight: bold">Twitter analytics</td></tr><tr><td>&nbsp;</th><td>men</td><td>women</td></tr>

      <tr><td style="font-weight: bold">Followers</td><td>83%</td>
        <td>17%</td>
      </tr>

<tr><td colspan=3 align=center style="font-weight: bold">FollowerWonk</td></tr><tr><td>&nbsp;</th><td>men</td><td>women</td></tr>

      <tr><td style="font-weight: bold">Followers</td><td>81%</td>
        <td>19%</td>
      </tr>

      <tr><td style="font-weight: bold">Friends I follow</td>
        <td>72%</td>
        <td>28%</td>
      </tr>

    </tbody></table>

<p>My followers show up 81% male here, close to the Twitter analytics number. So far so good. If FollowerWonk and Twitter agree on the gender ratio of my followers, that suggests FollowerWonk's estimate of the people I follow (which Twitter doesn't analyze) is reasonably good. With it, I can make a habit of measuring my numbers, and improve them.</p>
<p>At $30 a month, however, checking my friends' gender distribution with FollowerWonk is a pricey habit. I don't need all its features anyhow. Can I solve <em>only</em> the gender-distribution problem economically?</p>
<p>Since FollowerWonk's numbers seem reasonable, I tried to reproduce them. Using Python and <a href="https://github.com/bear/python-twitter/graphs/contributors">some nice Philadelphians' Twitter API wrapper</a>, I began downloading the profiles of all my friends and followers. I immediately found that Twitter's rate limits are miserly, so I randomly sampled only a subset of users instead.</p>
<p>I wrote a rudimentary program that searches for a pronoun or gender announcement in each of my friends' profiles. For example, a profile description that includes "she/her" probably belongs to a woman, a description with "they/them" is <a href="https://nonbinary.wiki/w/index.php?title=Pronouns">probably nonbinary</a>. <a href="https://github.com/ajdavis/twitter-gender-distribution/blob/master/analyze.py">You can see all the gender announcements my program checks for in the source code</a>.</p>
<p>But most don't state their pronouns: for these, the best gender-correlated information is the "name" field: for example, @gvanrossum's name field is "Guido van Rossum", and the first name "Guido" suggests that @gvanrossum is male. Where pronouns were not announced, I decided to use first names to estimate my numbers.</p>
<p>My script passes parts of each name to the <a href="https://pypi.python.org/pypi/SexMachine/">SexMachine</a> library to guess gender. SexMachine has predictable downfalls, like mistaking "Brooklyn Zen Center" for a woman named "Brooklyn", but its estimates are as good as FollowerWonk's and Twitter's: </p>
<table class="table table-striped" style="margin:auto; width: 450px; margin-bottom: 20px">
      <thead style="font-weight: bold"><tr><th>&nbsp;</th><th>nonbinary</th><th>men</th><th>women</th><th>no gender,<br>unknown</th></tr></thead>
      <tbody><tr><td style="font-weight: bold">Friends I follow</td><td>1</td><td>168</td><td>66</td><td>173</td></tr>
      <tr>
        <td>&nbsp;</td>
        <td>0%</td>
        <td>72%</td>
        <td>28%</td>
        <td>&nbsp;</td>
      </tr>
      <tr><td style="font-weight: bold">Followers</td><td>0</td><td>459</td><td>108</td><td>433</td></tr>
      <tr>
        <td>&nbsp;</td>
        <td>0%</td>
        <td>81%</td>
        <td>19%</td>
        <td>&nbsp;</td>
      </tr>

    </tbody></table>

<p>(Based on all 408 friends and a sample of 1000 followers.)</p>
<h1 id="know-your-number">Know Your Number</h1>
<p>I want you to check your Twitter network's gender distribution, too. So I've deployed "Proportional" to PythonAnywhere's handy service for $10 a month:</p>
<div style="text-align: center; margin-bottom: 20px">
<a style="font-weight: bold; font-size: large" href="https://www.proporti.onl/">www.proporti<span style="opacity: 0.5; color: gray">.</span>onl</a>
</div>

<p>The application may rate-limit you or otherwise fail, so use it gently. <a href="https://github.com/ajdavis/twitter-gender-distribution">The code is on GitHub</a>. It includes a command-line tool, as well.</p>
<p>Who is represented in your network on Twitter? Are you speaking and listening to the same unfairly distributed group who have been talking about software for the last few decades, or does your network look like the software industry of the future? Let's know our numbers and improve them.</p>
<hr />
<p><a href="https://www.flickr.com/photos/35168673@N03/3793255026"><span style="color: gray">Image: Cyclopedia of Photography 1975.</span></a></p>
