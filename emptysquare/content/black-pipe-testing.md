+++
type = "post"
title = "Black Pipe Testing: Preface"
date = "2015-10-06T09:02:18"
description = "Traditional \"black box\" testing can't fully validate MongoDB clients and other connected applications. Here's a convenient way to test the whole program."
category = ["C", "Mongo", "Programming", "Python"]
tag = ["black-pipe", "testing"]
enable_lightbox = false
thumbnail = "lower-east-side-pipes@240.jpg"
draft = false
disqus_identifier = "55fa3cb65393742358c9c1f1"
disqus_url = "https://emptysqua.re/blog/55fa3cb65393742358c9c1f1/"
series = ["black-pipe"]
+++

<p><a href="https://www.flickr.com/photos/emptysquare/477797865"><img style="display:block; margin-left:auto; margin-right:auto;" src="lower-east-side-pipes.jpg" alt="Pipes" title="Pipes" /></a></p>
<p>A "black box" test runs your code with some input and verifies its output,
without peering at internal data. You toss something in and out pops the result, like toast.</p>
<p>A black box test's advantage is this: it depends only on your output,
so you can freely change your code without changing the
test, confident that if the test passes, your changes are right. On the other hand, if the
test depends on your code's internals, you must change your code and
the test simultaneously, impairing the test's integrity.</p>
<p>At MongoDB we test PyMongo with a mix of black box and white box tests.
The white box tests do operations with PyMongo, for example database queries, then they check that PyMongo's internal state is correct.
The black box tests only check PyMongo's output.</p>
<p>But I have come to the following realization: a MongoDB driver is not a box. It's a pipe.
Its input and output are at two ends.</p>
<p>One end of the pipe is the driver's API. Its inputs are method calls, like calls to <code>find()</code> or <code>insert_one()</code>, and its outputs are the methods' return values or side effects. Black box tests cover this end very well.</p>
<p>But the other end of the pipe is the driver's network connection, where the driver outputs TCP messages to MongoDB servers, and takes as input
the server responses. This, too, is a public API, but black box testing alone does not validate this end. To validate the driver's whole public surface, we must treat the driver as a black pipe.</p>
<p>This year I implemented a tool for black pipe testing called
<a href="http://mockupdb.readthedocs.org/">MockupDB</a>. It is a <a href="http://docs.mongodb.org/meta-driver/latest/legacy/mongodb-wire-protocol/">MongoDB wire protocol</a> server written in Python, with three
sets of features to aid tests:</p>
<ol>
<li>It speaks the whole wire protocol over TCP, just like a MongoDB server. You can even connect to it with the mongo shell.</li>
<li>It can run in the same Python process as PyMongo. A black pipe test neatly interleaves PyMongo calls and MockupDB calls to choreograph a sequence of requests and responses.</li>
<li>MockupDB has a rich API for validating the messages PyMongo sends.</li>
</ol>
<p>I got this idea for testing MongoDB drivers when I saw Christian Hergert's implementation of it in the C Driver. Inspired by Christian's code, I ported it to Python and created the more convenient and featureful MockupDB for testing PyMongo.</p>
<p>MockupDB is not limited to testing PyMongo: I have used it to test
the C Driver in several crises, with gratifying results. And I hope you can
use it to test your application, whether written in Python or another language,
to check its reactions in scary scenarios. A MockupDB server can fail, hang, vanish, and otherwise misbehave
in ways that a real MongoDB server does its best not to.</p>
<p>Even if you are not a MongoDB user, MockupDB's example as a tool for black pipe testing
might help you re&euml;xamine how to test all interfaces of a connected application.</p>
<p>In the next few weeks I will share a series of articles about black pipe testing. Stick with me; this will be electrifying! At least, I promise to make it as electrifying as a series of articles about software testing can be.</p>
