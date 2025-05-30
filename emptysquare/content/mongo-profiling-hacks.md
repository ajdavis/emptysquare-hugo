+++
type = "post"
title = "Mongo profiling hacks"
date = "2011-11-18T18:04:47"
description = "Log the line number of your code that made each MongoDB query."
category = ["MongoDB", "Programming"]
tag = []
enable_lightbox = false
draft = false
+++

<p>Two interesting things about MongoDB.</p>
<p><strong>Primary thing</strong>: Mongo introduced a <a href="http://www.mongodb.org/display/DOCS/Advanced+Queries#AdvancedQueries-%24comment">$comment
option</a>
to queries in version 2.0.0. The comment shows up in the profiler log.
Try this on the Mongo shell:</p>

{{<highlight javascript>}}
> db.setProfilingLevel(2)
> db.my_collection.find()._addSpecial("$comment", 'my comment')
> db.setProfilingLevel(0)
{{< / highlight >}}

<p>The '$comment' value is stored in the profiling data, where it's easy
to search for:</p>

{{<highlight javascript>}}
> db.system.profile.find({'query.$comment':'my comment'})
{
    "ns" : "test.my_collection",
    "query" : { "query" : { }, "$comment" : "my comment" },
    "millis" : 3,
    // lots of other info ...
}
{{< / highlight >}}

<p>You could use this to tag queries with any data you want. An obvious use
is to store the file and line of the source code that made the call. In
Python:</p>

{{<highlight python3>}}
import pymongo, inspect

def find(collection, query):
    frame_info = inspect.stack()[1]
    comment = '%s:%s in %s' % (frame_info[1], frame_info[2], frame_info[3])
    return collection.find({ '$query': query, '$comment': comment })

def my_function():
    db = pymongo.Connection('localhost').db
    print list(find(db.foo, {}))

my_function()
{{< / highlight >}}

<p>Everywhere you call the function find() I defined above, Python will
send to Mongo the filename, line number, and name of the function that
made the call. (As long as Mongo's profiling level is set to 2.) You
could query later for, say, the slowest call to find():</p>

{{<highlight javascript>}}
> db.system.profile.find({'query.$comment':{$exists:1}}).sort({millis:-1})[0]
{
    "ts" : ISODate("2011-11-18T22:45:21.938Z"),
    "op" : "query",
    "ns" : "www.foo",
    "query" : {
        "$comment" : "/Users/emptysquare/.virtualenvs/tmp/add_comment.py:16 in my_function",
        "$query" : {

        }
    },
    "nscanned" : 3,
    "nreturned" : 3,
    "responseLength" : 125,
    "millis" : 0,
    "client" : "127.0.0.1",
    "user" : ""
}
{{< / highlight >}}

<p>Neat, right?</p>
<p><strong>Secondary thing:</strong> There might be a time when you want to simulate a
very time-consuming Mongo query, but you don't have enough data to
actually slow Mongo down. Add a busy loop to the query's \$where clause:</p>

{{<highlight javascript>}}
> // This will pause 1 second per row
> db.my_collection.find({
$where:'function() {'+
       'var d = new Date((new Date()).getTime() + 1*1000);' +
       'while (d > (new Date())) { }; return true;}'
})
{{< / highlight >}}

<p>Of course, you can combine this busy-wait clause with any regular find()
filter.</p>
