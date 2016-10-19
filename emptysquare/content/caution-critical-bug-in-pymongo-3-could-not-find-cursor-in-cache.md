+++
type = "post"
title = "Caution: Critical Bug In PyMongo 3, \"could not find cursor in cache\""
date = "2015-04-15T17:39:28"
description = "If you use multiple mongos servers in a sharded cluster, be cautious upgrading to PyMongo 3, we've just discovered a critical bug."
category = ["Mongo", "Programming", "Python"]
tag = ["pymongo"]
enable_lightbox = false
draft = false
disqus_identifier = "552ed95a5393741c7644f817"
disqus_url = "https://emptysqua.re/blog/552ed95a5393741c7644f817/"
+++

<p>If you use multiple mongos servers in a sharded cluster, be cautious upgrading to PyMongo 3. We've just discovered <a href="https://jira.mongodb.org/browse/PYTHON-898">a critical bug</a> related to our new mongos load-balancing feature.</p>
<p><strong>Update:</strong> <a href="/announcing-pymongo-3-0-1/">PyMongo 3.0.1 was released April 21, 2015</a> with fixes for this and other bugs.</p>
<p>If you create a MongoClient instance with PyMongo 3 and pass the addresses of several mongos servers, like so:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">client <span style="color: #666666">=</span> MongoClient(<span style="color: #BA2121">&#39;mongodb://mongos1,mongos2&#39;</span>)
</pre></div>


<p>...then the client load-balances among the lowest-latency of them. <a href="http://api.mongodb.org/python/current/examples/high_availability.html#mongos-load-balancing">Read the load-balancing documentation for details</a>. This works correctly except when retrieving more than 101 documents, or more than 4MB of data, from a cursor:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">collection <span style="color: #666666">=</span> client<span style="color: #666666">.</span>db<span style="color: #666666">.</span>collection
<span style="color: #008000; font-weight: bold">for</span> document <span style="color: #AA22FF; font-weight: bold">in</span> collection<span style="color: #666666">.</span>find():
    <span style="color: #408080; font-style: italic"># ... do something with each document ...</span>
    <span style="color: #008000; font-weight: bold">pass</span>
</pre></div>


<p>PyMongo wrongly tries to get subsequent batches of documents from random mongos servers, instead of streaming results from the same server it chose for the initial query. The symptom is an OperationFailure with a server error message, "could not find cursor in cache":</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #0044DD">Traceback (most recent call last):</span>
  File <span style="color: #008000">&quot;/usr/local/lib/python2.7/dist-packages/pymongo/cursor.py&quot;</span>, line <span style="color: #666666">968</span>, in __next__
        <span style="color: #008000; font-weight: bold">if</span> <span style="color: #008000">len</span>(<span style="color: #008000">self</span><span style="color: #666666">.</span>__data) <span style="color: #AA22FF; font-weight: bold">or</span> <span style="color: #008000">self</span><span style="color: #666666">.</span>_refresh():
  File <span style="color: #008000">&quot;/usr/local/lib/python2.7/dist-packages/pymongo/cursor.py&quot;</span>, line <span style="color: #666666">922</span>, in _refresh
        <span style="color: #008000">self</span><span style="color: #666666">.</span>__id))
  File <span style="color: #008000">&quot;/usr/local/lib/python2.7/dist-packages/pymongo/cursor.py&quot;</span>, line <span style="color: #666666">838</span>, in __send_message
        codec_options<span style="color: #666666">=</span><span style="color: #008000">self</span><span style="color: #666666">.</span>__codec_options)
  File <span style="color: #008000">&quot;/usr/local/lib/python2.7/dist-packages/pymongo/helpers.py&quot;</span>, line <span style="color: #666666">110</span>, in _unpack_response
        cursor_id)
<span style="color: #FF0000">pymongo.errors.CursorNotFound</span>: cursor id &#39;1025112076089406867&#39; not valid at server
</pre></div>
