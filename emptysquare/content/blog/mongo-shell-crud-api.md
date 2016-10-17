+++
type = "post"
title = "The MongoDB Shell's New CRUD API"
date = "2015-08-31T13:49:24"
description = "We took a reader's suggestion and updated the shell to match drivers' methods to create, retrieve, update, and delete data."
"blog/category" = ["Mongo", "Programming"]
"blog/tag" = []
enable_lightbox = false
thumbnail = "leaf-on-water@240.jpg"
draft = false
+++

<p><img style="display:block; margin-left:auto; margin-right:auto;" src="leaf-on-water.jpg" alt="Leaf on water" title="Leaf on water" /></p>
<p>We released the latest development version of MongoDB the other week. The <a href="http://blog.mongodb.org/post/127802855483/mongodb-317-is-released">official announcement</a> focuses on bug fixes, but I'm much more excited about a new feature: the mongo shell includes the new CRUD API! In addition to the old <code>insert</code>, <code>update</code>, and <code>remove</code>, the shell now supports <code>insertMany</code>, <code>replaceOne</code>, and a variety of other new methods.</p>
<p>Why do I care about this, and why should you?</p>
<p>MongoDB's next-generation drivers, released this spring, include <a href="https://www.mongodb.com/blog/post/consistent-crud-api-next-generation-mongodb-drivers">the new API for CRUD operations</a>, but the shell did not initially follow suit. My reader Nick Milon <a href="/blog/announcing-pymongo-3/#comment-1955330570">commented</a> that this is a step in the wrong direction: drivers are now less consistent with the shell. He pointed out, "developers switch more often between a driver and shell than drivers in different programming languages." So <a href="https://jira.mongodb.org/browse/SERVER-17953">I proposed the feature</a>, Christian Kvalheim coded it, and Kay Kim is updating the user's manual.</p>
<p>It's satisfying when a stranger's suggestion is so obviously right that we hurry to implement it.</p>
<p>The shell is now more consistent with the drivers than ever before. But beyond that, the new API is just better. For example, the old <code>insert</code> method could take one document or many, and its return value didn't include the new ids:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #666666">&gt;</span> <span style="color: #408080; font-style: italic">// the old insert API</span>
<span style="color: #666666">&gt;</span> db.test.insert({_id<span style="color: #666666">:</span> <span style="color: #666666">1</span>})
WriteResult({ <span style="color: #BA2121">&quot;nInserted&quot;</span> <span style="color: #666666">:</span> <span style="color: #666666">1</span> })
<span style="color: #666666">&gt;</span> db.test.insert([{_id<span style="color: #666666">:</span> <span style="color: #666666">2</span>}, {_id<span style="color: #666666">:</span> <span style="color: #666666">3</span>}, {_id<span style="color: #666666">:</span> <span style="color: #666666">4</span>}])
BulkWriteResult({
    <span style="color: #BA2121">&quot;writeErrors&quot;</span> <span style="color: #666666">:</span> [ ],
    <span style="color: #BA2121">&quot;writeConcernErrors&quot;</span> <span style="color: #666666">:</span> [ ],
    <span style="color: #BA2121">&quot;nInserted&quot;</span> <span style="color: #666666">:</span> <span style="color: #666666">3</span>,
    <span style="color: #BA2121">&quot;nUpserted&quot;</span> <span style="color: #666666">:</span> <span style="color: #666666">0</span>,
    <span style="color: #BA2121">&quot;nMatched&quot;</span> <span style="color: #666666">:</span> <span style="color: #666666">0</span>,
    <span style="color: #BA2121">&quot;nModified&quot;</span> <span style="color: #666666">:</span> <span style="color: #666666">0</span>,
    <span style="color: #BA2121">&quot;nRemoved&quot;</span> <span style="color: #666666">:</span> <span style="color: #666666">0</span>,
    <span style="color: #BA2121">&quot;upserted&quot;</span> <span style="color: #666666">:</span> [ ]
})
</pre></div>


<p>The new API better distinguishes single- and bulk-insert, and returns more useful results:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #666666">&gt;</span> <span style="color: #408080; font-style: italic">// the new CRUD API</span>
<span style="color: #666666">&gt;</span> db.test2.insertOne({_id<span style="color: #666666">:</span> <span style="color: #666666">1</span>})
{
    <span style="color: #BA2121">&quot;acknowledged&quot;</span> <span style="color: #666666">:</span> <span style="color: #008000; font-weight: bold">true</span>,
    <span style="color: #BA2121">&quot;insertedId&quot;</span> <span style="color: #666666">:</span> <span style="color: #666666">1</span>
}
<span style="color: #666666">&gt;</span> db.test2.insertMany([{_id<span style="color: #666666">:</span> <span style="color: #666666">2</span>}, {_id<span style="color: #666666">:</span> <span style="color: #666666">3</span>}, {_id<span style="color: #666666">:</span> <span style="color: #666666">4</span>}])
{ 
    <span style="color: #BA2121">&quot;acknowledged&quot;</span> <span style="color: #666666">:</span> <span style="color: #008000; font-weight: bold">true</span>,
    <span style="color: #BA2121">&quot;insertedIds&quot;</span> <span style="color: #666666">:</span> [ <span style="color: #666666">2</span>, <span style="color: #666666">3</span>, <span style="color: #666666">4</span> ]
}
</pre></div>


<p>The old <code>insert</code> method remains in the shell indefinitely, however: we know there are heaps of scripts written with the old methods and we don't plan to drop them.</p>
<p>On to the next operation. The shell's <code>update</code> is famously ill-designed. No one can remember the order of the "upsert" and "multi" options, and defaulting "multi" to false stumped generations of new users:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #666666">&gt;</span> <span style="color: #408080; font-style: italic">// the old update API</span>
<span style="color: #666666">&gt;</span> db.test.update(
... {_id<span style="color: #666666">:</span> <span style="color: #666666">1</span>},
... {$set<span style="color: #666666">:</span> {x<span style="color: #666666">:</span> <span style="color: #666666">1</span>}},
... <span style="color: #008000; font-weight: bold">true</span>              <span style="color: #408080; font-style: italic">/* upsert */</span>,
... <span style="color: #008000; font-weight: bold">false</span>             <span style="color: #408080; font-style: italic">/* multi */</span>
)
WriteResult({
    <span style="color: #BA2121">&quot;nMatched&quot;</span> <span style="color: #666666">:</span> <span style="color: #666666">0</span>,
    <span style="color: #BA2121">&quot;nUpserted&quot;</span> <span style="color: #666666">:</span> <span style="color: #666666">1</span>,
    <span style="color: #BA2121">&quot;nModified&quot;</span> <span style="color: #666666">:</span> <span style="color: #666666">0</span>,
    <span style="color: #BA2121">&quot;_id&quot;</span> <span style="color: #666666">:</span> <span style="color: #666666">1</span>
})
</pre></div>


<p>The new <code>updateOne</code> method is much easier to use correctly:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #666666">&gt;</span> <span style="color: #408080; font-style: italic">// the new update API</span>
<span style="color: #666666">&gt;</span> db.test2.updateOne(
... {_id<span style="color: #666666">:</span> <span style="color: #666666">1</span>},
... {$set<span style="color: #666666">:</span> {x<span style="color: #666666">:</span> <span style="color: #666666">1</span>}},
... {upsert<span style="color: #666666">:</span> <span style="color: #008000; font-weight: bold">true</span>}
)
{
    <span style="color: #BA2121">&quot;acknowledged&quot;</span> <span style="color: #666666">:</span> <span style="color: #008000; font-weight: bold">true</span>,
    <span style="color: #BA2121">&quot;matchedCount&quot;</span> <span style="color: #666666">:</span> <span style="color: #666666">0</span>,
    <span style="color: #BA2121">&quot;modifiedCount&quot;</span> <span style="color: #666666">:</span> <span style="color: #666666">0</span>,
    <span style="color: #BA2121">&quot;upsertedId&quot;</span> <span style="color: #666666">:</span> <span style="color: #666666">1</span>
}
</pre></div>


<p>We introduce <code>updateMany</code> for multi-updates.</p>
<p>Another flaw in the old <code>update</code> was, if you forgot the $-sign on an operator, you replaced a whole document instead of modifying it:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #666666">&gt;</span> <span style="color: #408080; font-style: italic">// the old replace API</span>
<span style="color: #666666">&gt;</span> db.test.update(
... {_id<span style="color: #666666">:</span> <span style="color: #666666">1</span>},
... {set<span style="color: #666666">:</span> {x<span style="color: #666666">:</span> <span style="color: #666666">1</span>}}  <span style="color: #408080; font-style: italic">// OOPS!!</span>
)
WriteResult({
    <span style="color: #BA2121">&quot;nMatched&quot;</span> <span style="color: #666666">:</span> <span style="color: #666666">1</span>,
    <span style="color: #BA2121">&quot;nUpserted&quot;</span> <span style="color: #666666">:</span> <span style="color: #666666">0</span>,
    <span style="color: #BA2121">&quot;nModified&quot;</span> <span style="color: #666666">:</span> <span style="color: #666666">1</span>
})
<span style="color: #666666">&gt;</span> <span style="color: #408080; font-style: italic">// document was replaced</span>
<span style="color: #666666">&gt;</span> db.test.findOne()
{ <span style="color: #BA2121">&quot;_id&quot;</span> <span style="color: #666666">:</span> <span style="color: #666666">1</span>, <span style="color: #BA2121">&quot;set&quot;</span> <span style="color: #666666">:</span> { <span style="color: #BA2121">&quot;x&quot;</span> <span style="color: #666666">:</span> <span style="color: #666666">1</span> } }
</pre></div>


<p>Now, replacing a document and updating it are kept distinct, preventing mistakes:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #666666">&gt;</span> <span style="color: #408080; font-style: italic">// the new update API catches mistakes</span>
<span style="color: #666666">&gt;</span> db.test2.updateOne(
... {_id<span style="color: #666666">:</span> <span style="color: #666666">1</span>},
... {set<span style="color: #666666">:</span> {x<span style="color: #666666">:</span> <span style="color: #666666">1</span>}}
)
<span style="color: #008000">Error</span><span style="color: #666666">:</span> the update operation <span style="color: #008000">document</span> must contain atomic operators
<span style="color: #666666">&gt;</span>
<span style="color: #666666">&gt;</span> <span style="color: #408080; font-style: italic">// explicitly replace with &quot;replaceOne&quot;</span>
<span style="color: #666666">&gt;</span> db.test2.replaceOne(
... {_id<span style="color: #666666">:</span> <span style="color: #666666">1</span>},
... {x<span style="color: #666666">:</span> <span style="color: #666666">1</span>}
)
{
    <span style="color: #BA2121">&quot;acknowledged&quot;</span> <span style="color: #666666">:</span> <span style="color: #008000; font-weight: bold">true</span>,
    <span style="color: #BA2121">&quot;matchedCount&quot;</span> <span style="color: #666666">:</span> <span style="color: #666666">1</span>,
    <span style="color: #BA2121">&quot;modifiedCount&quot;</span> <span style="color: #666666">:</span> <span style="color: #666666">1</span>
}
<span style="color: #666666">&gt;</span> db.test2.findOne()
{ <span style="color: #BA2121">&quot;_id&quot;</span> <span style="color: #666666">:</span> <span style="color: #666666">1</span>, <span style="color: #BA2121">&quot;x&quot;</span> <span style="color: #666666">:</span> <span style="color: #666666">1</span> }
</pre></div>


<p>The old <code>remove</code> method is full of surprises: it defaults "multi" to true, although "multi" is false for updates:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #666666">&gt;</span> <span style="color: #408080; font-style: italic">// the old delete API</span>
<span style="color: #666666">&gt;</span> db.test.remove({})  <span style="color: #408080; font-style: italic">// remove EVERYTHING!!</span>
</pre></div>


<p>The new methods let you say clearly which you want:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #666666">&gt;</span> <span style="color: #408080; font-style: italic">// the new delete API</span>
<span style="color: #666666">&gt;</span> db.test2.deleteOne({})
{ <span style="color: #BA2121">&quot;acknowledged&quot;</span> <span style="color: #666666">:</span> <span style="color: #008000; font-weight: bold">true</span>, <span style="color: #BA2121">&quot;deletedCount&quot;</span> <span style="color: #666666">:</span> <span style="color: #666666">1</span> }
<span style="color: #666666">&gt;</span> db.test2.deleteMany({})
{ <span style="color: #BA2121">&quot;acknowledged&quot;</span> <span style="color: #666666">:</span> <span style="color: #008000; font-weight: bold">true</span>, <span style="color: #BA2121">&quot;deletedCount&quot;</span> <span style="color: #666666">:</span> <span style="color: #666666">3</span> }
</pre></div>


<p>MongoDB's <code>findAndModify</code> command is powerful, and its options are impossible to learn.</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #666666">&gt;</span> <span style="color: #408080; font-style: italic">// the old findAndModify</span>
<span style="color: #666666">&gt;</span> db.test.findAndModify({
... query<span style="color: #666666">:</span> {_id<span style="color: #666666">:</span> <span style="color: #666666">1</span>},
... update<span style="color: #666666">:</span> {$set<span style="color: #666666">:</span> {x<span style="color: #666666">:</span> <span style="color: #666666">1</span>}},
... <span style="color: #008000; font-weight: bold">new</span><span style="color: #666666">:</span> <span style="color: #008000; font-weight: bold">true</span>
... })
{ <span style="color: #BA2121">&quot;_id&quot;</span> <span style="color: #666666">:</span> <span style="color: #666666">1</span>, <span style="color: #BA2121">&quot;x&quot;</span> <span style="color: #666666">:</span> <span style="color: #666666">1</span> }
<span style="color: #666666">&gt;</span> db.test.findAndModify({
... query<span style="color: #666666">:</span> {_id<span style="color: #666666">:</span> <span style="color: #666666">1</span>},
...  <span style="color: #408080; font-style: italic">// REPLACE the document!</span>
... update<span style="color: #666666">:</span> {field<span style="color: #666666">:</span> <span style="color: #BA2121">&#39;value&#39;</span>},
...  <span style="color: #408080; font-style: italic">// Return previous doc.</span>
... <span style="color: #008000; font-weight: bold">new</span><span style="color: #666666">:</span> <span style="color: #008000; font-weight: bold">false</span>
... })
{ <span style="color: #BA2121">&quot;_id&quot;</span> <span style="color: #666666">:</span> <span style="color: #666666">1</span>, <span style="color: #BA2121">&quot;x&quot;</span> <span style="color: #666666">:</span> <span style="color: #666666">1</span> }
<span style="color: #666666">&gt;</span> db.test.findAndModify({
... query<span style="color: #666666">:</span> {_id<span style="color: #666666">:</span> <span style="color: #666666">1</span>},
... remove<span style="color: #666666">:</span> <span style="color: #008000; font-weight: bold">true</span>
... })
{ <span style="color: #BA2121">&quot;_id&quot;</span> <span style="color: #666666">:</span> <span style="color: #666666">1</span>, <span style="color: #BA2121">&quot;field&quot;</span> <span style="color: #666666">:</span> <span style="color: #BA2121">&quot;value&quot;</span> }
</pre></div>


<p>So we've split the one overloaded <code>findAndModify</code> into three:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #666666">&gt;</span> <span style="color: #408080; font-style: italic">// the new API</span>
<span style="color: #666666">&gt;</span> db.test2.findOneAndUpdate(
... {_id<span style="color: #666666">:</span> <span style="color: #666666">1</span>},
... {$set<span style="color: #666666">:</span> {x<span style="color: #666666">:</span> <span style="color: #666666">1</span>}},
... {returnNewDocument<span style="color: #666666">:</span> <span style="color: #008000; font-weight: bold">true</span>}
... )
{ <span style="color: #BA2121">&quot;_id&quot;</span> <span style="color: #666666">:</span> <span style="color: #666666">1</span>, <span style="color: #BA2121">&quot;x&quot;</span> <span style="color: #666666">:</span> <span style="color: #666666">1</span> }
<span style="color: #666666">&gt;</span> db.test2.findOneAndReplace(
... {_id<span style="color: #666666">:</span> <span style="color: #666666">1</span>},
... {field<span style="color: #666666">:</span> <span style="color: #BA2121">&#39;value&#39;</span>},
... {returnNewDocument<span style="color: #666666">:</span> <span style="color: #008000; font-weight: bold">false</span>}
... )
{ <span style="color: #BA2121">&quot;_id&quot;</span> <span style="color: #666666">:</span> <span style="color: #666666">1</span>, <span style="color: #BA2121">&quot;x&quot;</span> <span style="color: #666666">:</span> <span style="color: #666666">1</span> }
<span style="color: #666666">&gt;</span> db.test2.findOneAndDelete({_id<span style="color: #666666">:</span> <span style="color: #666666">1</span>})
{ <span style="color: #BA2121">&quot;_id&quot;</span> <span style="color: #666666">:</span> <span style="color: #666666">1</span>, <span style="color: #BA2121">&quot;field&quot;</span> <span style="color: #666666">:</span> <span style="color: #BA2121">&quot;value&quot;</span> }
</pre></div>


<p>This is not a complete description of the changes. The <code>find</code>, <code>findOne</code>, and other query methods have standardized new options while preserving compatibility with old scripts. There's also a new <code>bulkWrite</code> method that's easier and more efficient than the old Bulk API. We'll have complete documentation for the new shell API when we publish the manual for MongoDB 3.2. Meanwhile, read <a href="https://www.mongodb.com/blog/post/consistent-crud-api-next-generation-mongodb-drivers">Jeremy Mikola's article about the CRUD API</a>, and <a href="https://github.com/mongodb/specifications/blob/master/source/crud/crud.rst">the spec itself</a> is quite legible, too.</p>
<p>Since the old <code>insert</code>, <code>update</code>, and <code>remove</code> are so pervasive in our users' code we have no plans to drop them or make backwards-incompatible changes.</p>
<p>I'm so glad we took the time to implement the new CRUD API in the shell. It was a big effort building, testing, and documenting it&mdash;the <a href="https://github.com/mongodb/mongo/commit/8c8da71903a3325d4df19faaf2745f23bfbe7302">diff for the initial patch alone</a> is frightening&mdash;but it's well worth it to give the next generation of developers a consistent experience when they first learn MongoDB. Thanks again to Nick Milon for giving us the nudge.</p>
<hr />
<p><span style="color:gray"><a href="https://www.flickr.com/photos/wwarby/11567626776">Image: William Warby</a></span></p>
    