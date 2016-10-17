+++
type = "post"
title = "Third Normal Form and Ultimate Truth"
date = "2012-02-14T01:31:57"
description = "I have an opinion: most people learned about relational databases as if RDBMSes were designed to store the ultimate truth about some data. They figured that once the schema had been properly diagrammed and normalized, then they could [ ... ]"
"blog/category" = ["Programming", "Python", "Mongo"]
"blog/tag" = []
enable_lightbox = false
draft = false
legacyid = "310 http://emptysquare.net/blog/?p=310"
+++

<p>I have an opinion: most people learned about relational databases as if
RDBMSes were designed to store the ultimate truth about some data. They
figured that once the schema had been properly diagrammed and
normalized, then they could load all their data into it, and finally,
start doing some queries.</p>
<p>To pick on an easy target, look at <a href="http://en.wikipedia.org/wiki/Database_design">Wikipedia's article on schema
design</a>. It summarizes the
two steps a designer must take:</p>
<ol>
<li>Determine the relationships between the different data elements.</li>
<li>Superimpose a logical structure upon the data on the basis of these
    relationships.</li>
</ol>
<p>Do you see a step that's missing? If you've deployed and maintained a
large-scale application you'll probably see what the Wikipedia authors
omitted. In fact, it's the first step: Figure out what <strong>one</strong> question
your database must answer. Then, design your schema to answer that
question as fast as possible. And now you're done. Come to think of it,
you never had to do steps 1 and 2 at all.</p>
<p>There's a total disconnect between the approaches of introductory SQL
courses and real-world application development, and I think this
disconnect is slowing down adoption of NoSQL.</p>
<p>Consider Facebook Messages. After a (now rather well-publicized)
evaluation process, <a href="https://www.facebook.com/note.php?note_id=454991608919">Facebook chose
HBase</a>, a NoSQL
data store, as the main database for their message system. I haven't
talked to anyone there, but I figure they chose it based on this
criterion:</p>
<p><strong>How fast will our database answer the question, "What are this user's
most recent 10 messages?"</strong></p>
<p>They chose the database system that could answer that question the
fastest, and they designed the best schema they could think of to answer
that question. Anything else they need to ask HBase may be slow, or
difficult, but that doesn't matter, because "What are this user's most
recent 10 messages?" probably accounts for 99% of the load on their
system.</p>
<p>If you learned about databases in college, following some textbook, I
expect you were guided through a long process of modeling real-world
data using rows and columns, to express some profound truth about the
data. Then, you were introduced to SQL, with which you could query the
data. At the end of the course, maybe there was a brief discussion of
database performance. Probably not.</p>
<p>Data at the scale that the largest websites handle doesn't work that
way. Large applications design their schemas to answer one question as
quickly as possible, and no other considerations are significant.</p>
<p>The next time you read about a NoSQL database you might wonder, "What
about foreign keys, or normalization? What about transactions? Why can't
I define secondary indexes? Why are range queries prohibited?" (I'm just
picking some limitations at random—each system is different.) Consider
who built these new database systems, and what their experience has
been. The ideas behind NoSQL databases mostly originated at places like
Google, Amazon, and Yahoo. They build huge systems, and huge systems'
loads are usually dominated by a handful of queries. Companies build
their database systems from the ground up to optimize the performance of
these queries. NoSQL databases encourage you to figure out ahead of
time, "What one question do I need to answer?" Figure that out, and
choose your database software and your schema based on that. Nothing
else really matters.</p>
    