+++
type = "post"
title = "Rules of Thumb for Methods and Functions"
date = "2014-06-19T09:08:04"
description = "How I stay sane when designing an object-oriented architecture."
category = ["Programming", "Python"]
tag = []
enable_lightbox = false
thumbnail = "le-pouce.jpg"
draft = false
+++

<p><img style="display:block; margin-left:auto; margin-right:auto;" src="le-pouce.jpg" alt="Le Pouce, sculpture in Paris" title="Le Pouce, sculpture in Paris" /><a href="https://www.flickr.com/photos/paveita/3195664073/"><span style="color:gray">[Source]</span></a></p>
<p>The Python team at MongoDB is partially rewriting <a href="https://pypi.python.org/pypi/pymongo/">PyMongo</a>. The next version, 3.0,
aims to be faster, more flexible, and more maintainable than the current 2.x series.
There is nothing like the satisfaction of pulling out the weeds and making a fresh patch of ground for new code.</p>
<p>A design flaw in the current PyMongo is that a large number of instance methods have return values and side effects.
For example, MongoClient has a private <code>_check_response_to_last_error</code> method.
It takes a binary message from the server and returns a parsed version of it.
But depending on what errors it finds in the server message,
the method sometimes clears the client's connection pool,
or changes all threads' socket affinities,
or wipes its cached information about who the primary server is.
Just looking at the method's signature doesn't tell me all the things it could do:
since it's an instance method of MongoClient, it could change any part of the MongoClient's state.</p>
<p>This gets gnarly, quickly.</p>
<p>In most cases these mixed methods did one thing at first: they only returned a value, or only changed state. And then we had to fix something and the
easiest way was to add a side-effect or add a return value. And so the road
to hell was paved.</p>
<p>I want to minimize the temptation for these mixed methods in PyMongo 3. My
main strategy is to minimize methods, period. My rules of thumb are these:</p>
<ul>
<li>If it accesses private instance variables, it's an instance method. Everything else can and should be a function.</li>
<li>When a method is necessary, it should set a private variable, or it should have a return value. Not both.</li>
</ul>
<p>No rule should followed without exception, of course. And there will be a handful of exceptions to these rules. But on the whole I think this limits the risk and complexity of methods in PyMongo. What do you think?</p>
