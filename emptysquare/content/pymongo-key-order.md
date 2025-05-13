+++
type = "post"
title = "PyMongo And Key Order In Subdocuments"
date = "2015-03-18T14:18:42"
description = "Workarounds for a common irritation using Python and MongoDB."
category = ["MongoDB", "Programming", "Python"]
tag = []
enable_lightbox = false
draft = false
+++

<p><em>Or,</em> "Why does my query work in the shell but not PyMongo?"</p>
<p>Variations on this question account for a large portion of the Stack Overflow questions I see about PyMongo, so let me explain once for all.</p>
<p>MongoDB stores documents in a binary format called <a href="http://bsonspec.org/">BSON</a>.
Key-value pairs in a BSON document can have any order (except that <code>_id</code>
is always first). The mongo shell preserves key order when reading and writing
data. Observe that "b" comes before "a" when we create the document and when it
is displayed:</p>

{{<highlight javascript>}}
> // mongo shell.
> db.collection.insert( {
...     "_id" : 1,
...     "subdocument" : { "b" : 1, "a" : 1 }
... } )
WriteResult({ "nInserted" : 1 })
> db.collection.find()
{ "_id" : 1, "subdocument" : { "b" : 1, "a" : 1 } }
{{< / highlight >}}

<p>PyMongo represents BSON documents as Python dicts by default, and the order
of keys in dicts is not defined. That is, a dict declared with the "a" key
first is the same, to Python, as one with "b" first:</p>

{{<highlight python3>}}
>>> print {'a': 1.0, 'b': 1.0}
{'a': 1.0, 'b': 1.0}
>>> print {'b': 1.0, 'a': 1.0}
{'a': 1.0, 'b': 1.0}
{{< / highlight >}}

<p>Therefore, Python dicts are not guaranteed to show keys in the order they are
stored in BSON. Here, "a" is shown before "b":</p>

{{<highlight python3>}}
>>> print collection.find_one()
{u'_id': 1.0, u'subdocument': {u'a': 1.0, u'b': 1.0}}
{{< / highlight >}}

<p>To preserve order when reading BSON, use the <code>SON</code> class,
which is a dict that remembers its key order. First, get a handle to the
collection, configured to use <code>SON</code> instead of dict. In <a href="/pymongo-3-beta/">PyMongo 3.0</a> do this like:</p>

{{<highlight python3>}}
>>> from bson import CodecOptions, SON
>>> opts = CodecOptions(document_class=SON)
>>> opts
CodecOptions(document_class=<class 'bson.son.SON'>,
             tz_aware=False,
             uuid_representation=PYTHON_LEGACY)
>>> collection_son = collection.with_options(codec_options=opts)
{{< / highlight >}}

<p>Now, documents and subdocuments in query results are represented with
<code>SON</code> objects:</p>

{{<highlight python3>}}
>>> print collection_son.find_one()
SON([(u'_id', 1.0), (u'subdocument', SON([(u'b', 1.0), (u'a', 1.0)]))])
{{< / highlight >}}

<p>The subdocument's actual storage layout is now visible: "b" is before "a".</p>
<p>Because a dict's key order is not defined, you cannot predict how it will be
serialized <strong>to</strong> BSON. But MongoDB considers subdocuments equal only if their
keys have the same order. So if you use a dict to query on a subdocument it may
not match:</p>

{{<highlight python3>}}
>>> collection.find_one({'subdocument': {'a': 1.0, 'b': 1.0}}) is None
True
{{< / highlight >}}

<p>Swapping the key order in your query makes no difference:</p>

{{<highlight python3>}}
>>> collection.find_one({'subdocument': {'b': 1.0, 'a': 1.0}}) is None
True
{{< / highlight >}}

<p>... because, as we saw above, Python considers the two dicts the same.</p>
<p>There are two solutions. First, you can match the subdocument field-by-field:</p>

{{<highlight python3>}}
>>> collection.find_one({'subdocument.a': 1.0,
...                      'subdocument.b': 1.0})
{u'_id': 1.0, u'subdocument': {u'a': 1.0, u'b': 1.0}}
{{< / highlight >}}

<p>The query matches any subdocument with an "a" of 1.0 and a "b" of 1.0,
regardless of the order you specify them in Python or the order they are stored
in BSON. Additionally, this query now matches subdocuments with additional
keys besides "a" and "b", whereas the previous query required an exact match.</p>
<p>The second solution is to use a <code>SON</code> to specify the key order:</p>

{{<highlight python3>}}
>>> query = {'subdocument': SON([('b', 1.0), ('a', 1.0)])}
>>> collection.find_one(query)
{u'_id': 1.0, u'subdocument': {u'a': 1.0, u'b': 1.0}}
{{< / highlight >}}

<p>The key order you use when you create a <code>SON</code> is preserved
when it is serialized to BSON and used as a query. Thus you can create a
subdocument that exactly matches the subdocument in the collection.</p>
<p>For more info, see the <a href="http://docs.mongodb.org/manual/tutorial/query-documents/#embedded-documents">MongoDB Manual entry on subdocument matching</a>.</p>
