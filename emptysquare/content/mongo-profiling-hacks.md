+++
type = "post"
title = "Mongo profiling hacks"
date = "2011-11-18T18:04:47"
description = "Log the line number of your code that made each MongoDB query."
category = ["MongoDB", "Programming"]
tag = []
enable_lightbox = false
draft = false
disqus_identifier = "174 http://emptysquare.net/blog/?p=174"
disqus_url = "https://emptysqua.re/blog/174 http://emptysquare.net/blog/?p=174/"
+++

<p>Two interesting things about MongoDB.</p>
<p><strong>Primary thing</strong>: Mongo introduced a <a href="http://www.mongodb.org/display/DOCS/Advanced+Queries#AdvancedQueries-%24comment">$comment
option</a>
to queries in version 2.0.0. The comment shows up in the profiler log.
Try this on the Mongo shell:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">&gt; db.setProfilingLevel(2)
&gt; db.my_collection.find()._addSpecial(&quot;$<span style="color: #19177C">comment</span>&quot;, &#39;my comment&#39;)
&gt; db.setProfilingLevel(0)
</pre></div>


<p>The '$comment' value is stored in the profiling data, where it's easy
to search for:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">&gt; db.system.profile.find(<span style="border: 1px solid #FF0000">{</span>&#39;query.$<span style="color: #19177C">comment</span>&#39;:&#39;my comment&#39;})
<span style="border: 1px solid #FF0000">{</span>
    &quot;ns&quot; : &quot;test.my_collection&quot;,
    &quot;query&quot; : <span style="border: 1px solid #FF0000">{</span> &quot;query&quot; : <span style="border: 1px solid #FF0000">{</span> }, &quot;$<span style="color: #19177C">comment</span>&quot; : &quot;my comment&quot; },
    &quot;millis&quot; : 3,
    // lots of other info ...
}
</pre></div>


<p>You could use this to tag queries with any data you want. An obvious use
is to store the file and line of the source code that made the call. In
Python:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">import</span> <span style="color: #0000FF; font-weight: bold">pymongo</span><span style="color: #666666">,</span> <span style="color: #0000FF; font-weight: bold">inspect</span>

<span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">find</span>(collection, query):
    frame_info <span style="color: #666666">=</span> inspect<span style="color: #666666">.</span>stack()[<span style="color: #666666">1</span>]
    comment <span style="color: #666666">=</span> <span style="color: #BA2121">&#39;</span><span style="color: #BB6688; font-weight: bold">%s</span><span style="color: #BA2121">:</span><span style="color: #BB6688; font-weight: bold">%s</span><span style="color: #BA2121"> in </span><span style="color: #BB6688; font-weight: bold">%s</span><span style="color: #BA2121">&#39;</span> <span style="color: #666666">%</span> (frame_info[<span style="color: #666666">1</span>], frame_info[<span style="color: #666666">2</span>], frame_info[<span style="color: #666666">3</span>])
    <span style="color: #008000; font-weight: bold">return</span> collection<span style="color: #666666">.</span>find({ <span style="color: #BA2121">&#39;$query&#39;</span>: query, <span style="color: #BA2121">&#39;$comment&#39;</span>: comment })

<span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">my_function</span>():
    db <span style="color: #666666">=</span> pymongo<span style="color: #666666">.</span>Connection(<span style="color: #BA2121">&#39;localhost&#39;</span>)<span style="color: #666666">.</span>db
    <span style="color: #008000; font-weight: bold">print</span> <span style="color: #008000">list</span>(find(db<span style="color: #666666">.</span>foo, {}))

my_function()
</pre></div>


<p>Everywhere you call the function find() I defined above, Python will
send to Mongo the filename, line number, and name of the function that
made the call. (As long as Mongo's profiling level is set to 2.) You
could query later for, say, the slowest call to find():</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #666666">&gt;</span> db.system.profile.find({<span style="color: #BA2121">&#39;query.$comment&#39;</span><span style="color: #666666">:</span>{$exists<span style="color: #666666">:1</span>}}).sort({millis<span style="color: #666666">:-1</span>})[<span style="color: #666666">0</span>]
{
    <span style="color: #BA2121">&quot;ts&quot;</span> <span style="color: #666666">:</span> ISODate(<span style="color: #BA2121">&quot;2011-11-18T22:45:21.938Z&quot;</span>),
    <span style="color: #BA2121">&quot;op&quot;</span> <span style="color: #666666">:</span> <span style="color: #BA2121">&quot;query&quot;</span>,
    <span style="color: #BA2121">&quot;ns&quot;</span> <span style="color: #666666">:</span> <span style="color: #BA2121">&quot;www.foo&quot;</span>,
    <span style="color: #BA2121">&quot;query&quot;</span> <span style="color: #666666">:</span> {
        <span style="color: #BA2121">&quot;$comment&quot;</span> <span style="color: #666666">:</span> <span style="color: #BA2121">&quot;/Users/emptysquare/.virtualenvs/tmp/add_comment.py:16 in my_function&quot;</span>,
        <span style="color: #BA2121">&quot;$query&quot;</span> <span style="color: #666666">:</span> {

        }
    },
    <span style="color: #BA2121">&quot;nscanned&quot;</span> <span style="color: #666666">:</span> <span style="color: #666666">3</span>,
    <span style="color: #BA2121">&quot;nreturned&quot;</span> <span style="color: #666666">:</span> <span style="color: #666666">3</span>,
    <span style="color: #BA2121">&quot;responseLength&quot;</span> <span style="color: #666666">:</span> <span style="color: #666666">125</span>,
    <span style="color: #BA2121">&quot;millis&quot;</span> <span style="color: #666666">:</span> <span style="color: #666666">0</span>,
    <span style="color: #BA2121">&quot;client&quot;</span> <span style="color: #666666">:</span> <span style="color: #BA2121">&quot;127.0.0.1&quot;</span>,
    <span style="color: #BA2121">&quot;user&quot;</span> <span style="color: #666666">:</span> <span style="color: #BA2121">&quot;&quot;</span>
}
</pre></div>


<p>Neat, right?</p>
<p><strong>Secondary thing:</strong> There might be a time when you want to simulate a
very time-consuming Mongo query, but you don't have enough data to
actually slow Mongo down. Add a busy loop to the query's \$where clause:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #666666">&gt;</span> <span style="color: #408080; font-style: italic">// This will pause 1 second per row</span>
<span style="color: #666666">&gt;</span> db.my_collection.find({
$where<span style="color: #666666">:</span><span style="color: #BA2121">&#39;function() {&#39;</span><span style="color: #666666">+</span>
       <span style="color: #BA2121">&#39;var d = new Date((new Date()).getTime() + 1*1000);&#39;</span> <span style="color: #666666">+</span>
       <span style="color: #BA2121">&#39;while (d &gt; (new Date())) { }; return true;}&#39;</span>
})
</pre></div>


<p>Of course, you can combine this busy-wait clause with any regular find()
filter.</p>
