+++
type = "post"
title = "Porting From PyMongo To Motor"
date = "2013-09-24T17:55:26"
description = "How can you port a complex application from blocking to non-blocking style without rewriting all your code at once?"
category = ["MongoDB", "Motor", "Programming", "Python"]
tag = []
enable_lightbox = false
thumbnail = "F5_tornado_Elie_Manitoba_2007.jpg"
draft = false
+++

<p><a href="http://commons.wikimedia.org/wiki/File:F5_tornado_Elie_Manitoba_2007.jpg"><img alt="Tornado" src="F5_tornado_Elie_Manitoba_2007.jpg" style="display:block; margin-left:auto; margin-right:auto;" title="Tornado"/>
</a></p>
<p>Distressingly often, I see good programmers building applications with a flawed stack: PyMongo plus Tornado. Tornado is an asynchronous Python web framework, and PyMongo is a blocking driver for MongoDB. Obviously, any lengthy PyMongo operation blocks the event loop and hobbles its throughput.</p>
<p>I'm the author of <a href="http://motor.readthedocs.org/en/stable/">Motor</a>, a non-blocking driver for MongoDB and Tornado. I wrote it as an async alternative to PyMongo. If you have a Tornado application and want to add MongoDB to your toolset, I hope you'll connect to it with Motor. Of course, most of your MongoDB operations still need to be well-tuned, but if you're using Motor, a handful of slow queries won't destroy your application's total throughput.</p>
<p>But what if you've already written a large application with Tornado and PyMongo? At every layer of your code, you've relied on PyMongo's simple blocking interface:</p>

{{<highlight python3>}}
# Using PyMongo.
def get_document():
    document = db.collection.find_one()
    return document
{{< / highlight >}}

<p>To port a function from PyMongo to Motor, you either have to switch to a callback style:</p>

{{<highlight python3>}}
# Using Motor with a callback.
def get_document(callback):
    db.collection.find_one(callback=callback)
{{< / highlight >}}

<p>...or use a Tornado coroutine:</p>

{{<highlight python3>}}
# Using Motor with a coroutine.
@gen.coroutine
def get_document():
    document = yield motor.Op(db.collection.find_one)
    raise gen.Return(document)
{{< / highlight >}}

<p>Either way, the caller of your function must also be ported to a callback or coroutine style. So must its caller, and the caller above it.... Is there any way to update your code incrementally, or must it be rewritten all at once?</p>
<p>David Stainton, an acquaintance of mine on the Tornado mailing list, has recently ported a 10,000-line Tornado app from PyMongo to Motor. He tried a few angles of attack and learned which approach is best for incrementally rewriting a large application. He wrote a thorough and pragmatic article on <a href="http://david415.wordpress.com/2013/09/07/porting-tornado-app-from-pymongo-to-motor/">porting a Tornado app from PyMongo to Motor</a>; you should go read it.</p>
