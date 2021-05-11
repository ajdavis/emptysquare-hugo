+++
type = "post"
title = "PyMongo And Key Order In Subdocuments"
date = "2015-03-18T14:18:42"
description = "Workarounds for a common irritation using Python and MongoDB."
category = ["MongoDB", "Programming", "Python"]
tag = []
enable_lightbox = false
draft = false
disqus_identifier = "54ee3da05393740964f73d0b"
disqus_url = "https://emptysqua.re/blog/54ee3da05393740964f73d0b/"
+++

<p><em>Or,</em> "Why does my query work in the shell but not PyMongo?"</p>
<p>Variations on this question account for a large portion of the Stack Overflow questions I see about PyMongo, so let me explain once for all.</p>
<p>MongoDB stores documents in a binary format called <a href="http://bsonspec.org/">BSON</a>.
Key-value pairs in a BSON document can have any order (except that <code>_id</code>
is always first). The mongo shell preserves key order when reading and writing
data. Observe that "b" comes before "a" when we create the document and when it
is displayed:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #666666">&gt;</span> <span style="color: #408080; font-style: italic">// mongo shell.</span>
<span style="color: #666666">&gt;</span> db.collection.insert( {
...     <span style="color: #BA2121">&quot;_id&quot;</span> <span style="color: #666666">:</span> <span style="color: #666666">1</span>,
...     <span style="color: #BA2121">&quot;subdocument&quot;</span> <span style="color: #666666">:</span> { <span style="color: #BA2121">&quot;b&quot;</span> <span style="color: #666666">:</span> <span style="color: #666666">1</span>, <span style="color: #BA2121">&quot;a&quot;</span> <span style="color: #666666">:</span> <span style="color: #666666">1</span> }
... } )
WriteResult({ <span style="color: #BA2121">&quot;nInserted&quot;</span> <span style="color: #666666">:</span> <span style="color: #666666">1</span> })
<span style="color: #666666">&gt;</span> db.collection.find()
{ <span style="color: #BA2121">&quot;_id&quot;</span> <span style="color: #666666">:</span> <span style="color: #666666">1</span>, <span style="color: #BA2121">&quot;subdocument&quot;</span> <span style="color: #666666">:</span> { <span style="color: #BA2121">&quot;b&quot;</span> <span style="color: #666666">:</span> <span style="color: #666666">1</span>, <span style="color: #BA2121">&quot;a&quot;</span> <span style="color: #666666">:</span> <span style="color: #666666">1</span> } }
</pre></div>


<p>PyMongo represents BSON documents as Python dicts by default, and the order
of keys in dicts is not defined. That is, a dict declared with the "a" key
first is the same, to Python, as one with "b" first:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #000080; font-weight: bold">&gt;&gt;&gt; </span><span style="color: #008000; font-weight: bold">print</span> {<span style="color: #BA2121">&#39;a&#39;</span>: <span style="color: #666666">1.0</span>, <span style="color: #BA2121">&#39;b&#39;</span>: <span style="color: #666666">1.0</span>}
<span style="color: #888888">{&#39;a&#39;: 1.0, &#39;b&#39;: 1.0}</span>
<span style="color: #000080; font-weight: bold">&gt;&gt;&gt; </span><span style="color: #008000; font-weight: bold">print</span> {<span style="color: #BA2121">&#39;b&#39;</span>: <span style="color: #666666">1.0</span>, <span style="color: #BA2121">&#39;a&#39;</span>: <span style="color: #666666">1.0</span>}
<span style="color: #888888">{&#39;a&#39;: 1.0, &#39;b&#39;: 1.0}</span>
</pre></div>


<p>Therefore, Python dicts are not guaranteed to show keys in the order they are
stored in BSON. Here, "a" is shown before "b":</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #000080; font-weight: bold">&gt;&gt;&gt; </span><span style="color: #008000; font-weight: bold">print</span> collection<span style="color: #666666">.</span>find_one()
<span style="color: #888888">{u&#39;_id&#39;: 1.0, u&#39;subdocument&#39;: {u&#39;a&#39;: 1.0, u&#39;b&#39;: 1.0}}</span>
</pre></div>


<p>To preserve order when reading BSON, use the <code>SON</code> class,
which is a dict that remembers its key order. First, get a handle to the
collection, configured to use <code>SON</code> instead of dict. In <a href="/pymongo-3-beta/">PyMongo 3.0</a> do this like:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #000080; font-weight: bold">&gt;&gt;&gt; </span><span style="color: #008000; font-weight: bold">from</span> <span style="color: #0000FF; font-weight: bold">bson</span> <span style="color: #008000; font-weight: bold">import</span> CodecOptions, SON
<span style="color: #000080; font-weight: bold">&gt;&gt;&gt; </span>opts <span style="color: #666666">=</span> CodecOptions(document_class<span style="color: #666666">=</span>SON)
<span style="color: #000080; font-weight: bold">&gt;&gt;&gt; </span>opts
<span style="color: #888888">CodecOptions(document_class=&lt;class &#39;bson.son.SON&#39;&gt;,</span>
<span style="color: #888888">             tz_aware=False,</span>
<span style="color: #888888">             uuid_representation=PYTHON_LEGACY)</span>
<span style="color: #000080; font-weight: bold">&gt;&gt;&gt; </span>collection_son <span style="color: #666666">=</span> collection<span style="color: #666666">.</span>with_options(codec_options<span style="color: #666666">=</span>opts)
</pre></div>


<p>Now, documents and subdocuments in query results are represented with
<code>SON</code> objects:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #000080; font-weight: bold">&gt;&gt;&gt; </span><span style="color: #008000; font-weight: bold">print</span> collection_son<span style="color: #666666">.</span>find_one()
<span style="color: #888888">SON([(u&#39;_id&#39;, 1.0), (u&#39;subdocument&#39;, SON([(u&#39;b&#39;, 1.0), (u&#39;a&#39;, 1.0)]))])</span>
</pre></div>


<p>The subdocument's actual storage layout is now visible: "b" is before "a".</p>
<p>Because a dict's key order is not defined, you cannot predict how it will be
serialized <strong>to</strong> BSON. But MongoDB considers subdocuments equal only if their
keys have the same order. So if you use a dict to query on a subdocument it may
not match:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #000080; font-weight: bold">&gt;&gt;&gt; </span>collection<span style="color: #666666">.</span>find_one({<span style="color: #BA2121">&#39;subdocument&#39;</span>: {<span style="color: #BA2121">&#39;a&#39;</span>: <span style="color: #666666">1.0</span>, <span style="color: #BA2121">&#39;b&#39;</span>: <span style="color: #666666">1.0</span>}}) <span style="color: #AA22FF; font-weight: bold">is</span> <span style="color: #008000">None</span>
<span style="color: #888888">True</span>
</pre></div>


<p>Swapping the key order in your query makes no difference:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #000080; font-weight: bold">&gt;&gt;&gt; </span>collection<span style="color: #666666">.</span>find_one({<span style="color: #BA2121">&#39;subdocument&#39;</span>: {<span style="color: #BA2121">&#39;b&#39;</span>: <span style="color: #666666">1.0</span>, <span style="color: #BA2121">&#39;a&#39;</span>: <span style="color: #666666">1.0</span>}}) <span style="color: #AA22FF; font-weight: bold">is</span> <span style="color: #008000">None</span>
<span style="color: #888888">True</span>
</pre></div>


<p>... because, as we saw above, Python considers the two dicts the same.</p>
<p>There are two solutions. First, you can match the subdocument field-by-field:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #000080; font-weight: bold">&gt;&gt;&gt; </span>collection<span style="color: #666666">.</span>find_one({<span style="color: #BA2121">&#39;subdocument.a&#39;</span>: <span style="color: #666666">1.0</span>,
<span style="color: #000080; font-weight: bold">... </span>                     <span style="color: #BA2121">&#39;subdocument.b&#39;</span>: <span style="color: #666666">1.0</span>})
<span style="color: #888888">{u&#39;_id&#39;: 1.0, u&#39;subdocument&#39;: {u&#39;a&#39;: 1.0, u&#39;b&#39;: 1.0}}</span>
</pre></div>


<p>The query matches any subdocument with an "a" of 1.0 and a "b" of 1.0,
regardless of the order you specify them in Python or the order they are stored
in BSON. Additionally, this query now matches subdocuments with additional
keys besides "a" and "b", whereas the previous query required an exact match.</p>
<p>The second solution is to use a <code>SON</code> to specify the key order:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #000080; font-weight: bold">&gt;&gt;&gt; </span>query <span style="color: #666666">=</span> {<span style="color: #BA2121">&#39;subdocument&#39;</span>: SON([(<span style="color: #BA2121">&#39;b&#39;</span>, <span style="color: #666666">1.0</span>), (<span style="color: #BA2121">&#39;a&#39;</span>, <span style="color: #666666">1.0</span>)])}
<span style="color: #000080; font-weight: bold">&gt;&gt;&gt; </span>collection<span style="color: #666666">.</span>find_one(query)
<span style="color: #888888">{u&#39;_id&#39;: 1.0, u&#39;subdocument&#39;: {u&#39;a&#39;: 1.0, u&#39;b&#39;: 1.0}}</span>
</pre></div>


<p>The key order you use when you create a <code>SON</code> is preserved
when it is serialized to BSON and used as a query. Thus you can create a
subdocument that exactly matches the subdocument in the collection.</p>
<p>For more info, see the <a href="http://docs.mongodb.org/manual/tutorial/query-documents/#embedded-documents">MongoDB Manual entry on subdocument matching</a>.</p>
