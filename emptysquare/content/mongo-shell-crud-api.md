+++
type = "post"
title = "The MongoDB Shell's New CRUD API"
date = "2015-08-31T13:49:24"
description = "We took a reader's suggestion and updated the shell to match drivers' methods to create, retrieve, update, and delete data."
category = ["MongoDB", "Programming"]
tag = []
enable_lightbox = false
thumbnail = "leaf-on-water.jpg"
draft = false
+++

<p><img alt="Leaf on water" src="leaf-on-water.jpg" style="display:block; margin-left:auto; margin-right:auto;" title="Leaf on water"/></p>
<p>We released the latest development version of MongoDB the other week. The <a href="http://blog.mongodb.org/post/127802855483/mongodb-317-is-released">official announcement</a> focuses on bug fixes, but I'm much more excited about a new feature: the mongo shell includes the new CRUD API! In addition to the old <code>insert</code>, <code>update</code>, and <code>remove</code>, the shell now supports <code>insertMany</code>, <code>replaceOne</code>, and a variety of other new methods.</p>
<p>Why do I care about this, and why should you?</p>
<p>MongoDB's next-generation drivers, released this spring, include <a href="https://www.mongodb.com/blog/post/consistent-crud-api-next-generation-mongodb-drivers">the new API for CRUD operations</a>, but the shell did not initially follow suit. My reader Nick Milon <a href="/announcing-pymongo-3/#comment-1955330570">commented</a> that this is a step in the wrong direction: drivers are now less consistent with the shell. He pointed out, "developers switch more often between a driver and shell than drivers in different programming languages." So <a href="https://jira.mongodb.org/browse/SERVER-17953">I proposed the feature</a>, Christian Kvalheim coded it, and Kay Kim is updating the user's manual.</p>
<p>It's satisfying when a stranger's suggestion is so obviously right that we hurry to implement it.</p>
<p>The shell is now more consistent with the drivers than ever before. But beyond that, the new API is just better. For example, the old <code>insert</code> method could take one document or many, and its return value didn't include the new ids:</p>

{{<highlight javascript>}}
> // the old insert API
> db.test.insert({_id: 1})
WriteResult({ "nInserted" : 1 })
> db.test.insert([{_id: 2}, {_id: 3}, {_id: 4}])
BulkWriteResult({
    "writeErrors" : [ ],
    "writeConcernErrors" : [ ],
    "nInserted" : 3,
    "nUpserted" : 0,
    "nMatched" : 0,
    "nModified" : 0,
    "nRemoved" : 0,
    "upserted" : [ ]
})
{{< / highlight >}}

<p>The new API better distinguishes single- and bulk-insert, and returns more useful results:</p>

{{<highlight javascript>}}
> // the new CRUD API
> db.test2.insertOne({_id: 1})
{
    "acknowledged" : true,
    "insertedId" : 1
}
> db.test2.insertMany([{_id: 2}, {_id: 3}, {_id: 4}])
{ 
    "acknowledged" : true,
    "insertedIds" : [ 2, 3, 4 ]
}
{{< / highlight >}}

<p>The old <code>insert</code> method remains in the shell indefinitely, however: we know there are heaps of scripts written with the old methods and we don't plan to drop them.</p>
<p>On to the next operation. The shell's <code>update</code> is famously ill-designed. No one can remember the order of the "upsert" and "multi" options, and defaulting "multi" to false stumped generations of new users:</p>

{{<highlight javascript>}}
> // the old update API
> db.test.update(
... {_id: 1},
... {$set: {x: 1}},
... true              /* upsert */,
... false             /* multi */
)
WriteResult({
    "nMatched" : 0,
    "nUpserted" : 1,
    "nModified" : 0,
    "_id" : 1
})
{{< / highlight >}}

<p>The new <code>updateOne</code> method is much easier to use correctly:</p>

{{<highlight javascript>}}
> // the new update API
> db.test2.updateOne(
... {_id: 1},
... {$set: {x: 1}},
... {upsert: true}
)
{
    "acknowledged" : true,
    "matchedCount" : 0,
    "modifiedCount" : 0,
    "upsertedId" : 1
}
{{< / highlight >}}

<p>We introduce <code>updateMany</code> for multi-updates.</p>
<p>Another flaw in the old <code>update</code> was, if you forgot the $-sign on an operator, you replaced a whole document instead of modifying it:</p>

{{<highlight javascript>}}
> // the old replace API
> db.test.update(
... {_id: 1},
... {set: {x: 1}}  // OOPS!!
)
WriteResult({
    "nMatched" : 1,
    "nUpserted" : 0,
    "nModified" : 1
})
> // document was replaced
> db.test.findOne()
{ "_id" : 1, "set" : { "x" : 1 } }
{{< / highlight >}}

<p>Now, replacing a document and updating it are kept distinct, preventing mistakes:</p>

{{<highlight javascript>}}
> // the new update API catches mistakes
> db.test2.updateOne(
... {_id: 1},
... {set: {x: 1}}
)
Error: the update operation document must contain atomic operators
>
> // explicitly replace with "replaceOne"
> db.test2.replaceOne(
... {_id: 1},
... {x: 1}
)
{
    "acknowledged" : true,
    "matchedCount" : 1,
    "modifiedCount" : 1
}
> db.test2.findOne()
{ "_id" : 1, "x" : 1 }
{{< / highlight >}}

<p>The old <code>remove</code> method is full of surprises: it defaults "multi" to true, although "multi" is false for updates:</p>

{{<highlight jac    >}}
> // the old delete API
> db.test.remove({})  // remove EVERYTHING!!
{{< / highlight >}}

<p>The new methods let you say clearly which you want:</p>

{{<highlight javascript>}}
> // the new delete API
> db.test2.deleteOne({})
{ "acknowledged" : true, "deletedCount" : 1 }
> db.test2.deleteMany({})
{ "acknowledged" : true, "deletedCount" : 3 }
{{< / highlight >}}

<p>MongoDB's <code>findAndModify</code> command is powerful, and its options are impossible to learn.</p>

{{<highlight javascript>}}
> // the old findAndModify
> db.test.findAndModify({
... query: {_id: 1},
... update: {$set: {x: 1}},
... new: true
... })
{ "_id" : 1, "x" : 1 }
> db.test.findAndModify({
... query: {_id: 1},
...  // REPLACE the document!
... update: {field: 'value'},
...  // Return previous doc.
... new: false
... })
{ "_id" : 1, "x" : 1 }
> db.test.findAndModify({
... query: {_id: 1},
... remove: true
... })
{ "_id" : 1, "field" : "value" }
{{< / highlight >}}

<p>So we've split the one overloaded <code>findAndModify</code> into three:</p>

{{<highlight javascript>}}
> // the new API
> db.test2.findOneAndUpdate(
... {_id: 1},
... {$set: {x: 1}},
... {returnNewDocument: true}
... )
{ "_id" : 1, "x" : 1 }
> db.test2.findOneAndReplace(
... {_id: 1},
... {field: 'value'},
... {returnNewDocument: false}
... )
{ "_id" : 1, "x" : 1 }
> db.test2.findOneAndDelete({_id: 1})
{ "_id" : 1, "field" : "value" }
{{< / highlight >}}

<p>This is not a complete description of the changes. The <code>find</code>, <code>findOne</code>, and other query methods have standardized new options while preserving compatibility with old scripts. There's also a new <code>bulkWrite</code> method that's easier and more efficient than the old Bulk API. We'll have complete documentation for the new shell API when we publish the manual for MongoDB 3.2. Meanwhile, read <a href="https://www.mongodb.com/blog/post/consistent-crud-api-next-generation-mongodb-drivers">Jeremy Mikola's article about the CRUD API</a>, and <a href="https://github.com/mongodb/specifications/blob/master/source/crud/crud.rst">the spec itself</a> is quite legible, too.</p>
<p>Since the old <code>insert</code>, <code>update</code>, and <code>remove</code> are so pervasive in our users' code we have no plans to drop them or make backwards-incompatible changes.</p>
<p>I'm so glad we took the time to implement the new CRUD API in the shell. It was a big effort building, testing, and documenting it—the <a href="https://github.com/mongodb/mongo/commit/8c8da71903a3325d4df19faaf2745f23bfbe7302">diff for the initial patch alone</a> is frightening—but it's well worth it to give the next generation of developers a consistent experience when they first learn MongoDB. Thanks again to Nick Milon for giving us the nudge.</p>
<hr/>
<p><span style="color:gray"><a href="https://www.flickr.com/photos/wwarby/11567626776">Image: William Warby</a></span></p>
