+++
type = "post"
title = "Review of \"Building Node Applications with MongoDB and Backbone\""
date = "2013-03-23T12:42:26"
description = "The O'Reilly book on cutting-edge web development encourages some bad habits but also demonstrates a lot of useful, elegant patterns."
category = ["MongoDB", "Programming", "Review"]
tag = ["backbone", "node"]
enable_lightbox = false
thumbnail = "building-node-applications.jpg"
draft = false
disqus_identifier = "514ddacb5393742deda6b6c2"
disqus_url = "https://emptysqua.re/blog/514ddacb5393742deda6b6c2/"
+++

<p>Mike Wilson's O'Reilly book from December 2012 introduces some hip web development techniques by building a book-long example of a social networking app. Besides introducing MongoDB, Backbone, and Node, he shows the beauty and remarkable concision of <a href="http://jade-lang.com/">Jade</a>, <a href="http://requirejs.org/">Require.js</a>, and <a href="http://mongoosejs.com/">Mongoose</a>. He demonstrates good patterns for organizing your code in an application of substantial complexity, covers a lot of ground in few pages, and concludes with an unusually feature-complete chat-server example that weaves together all the layers of the stack. Wilson has some dangerous habits readers shouldn't emulate, but on balance his book teaches well.</p>
<p><img alt="Building node applications" border="0" src="building-node-applications.jpg" style="display:block; margin-left:auto; margin-right:auto;" title="building-node-applications.jpg"/></p>
<p>By necessity, the book jumps frequently between Node and Backbone, models and views, HTML and Javascript. It's the nature of web development that each new feature requires changes in many places, and it's hard to stay oriented. Wilson maintains a corrected version of each chapter's code <a href="https://github.com/Swiftam/book-node-mongodb-backbone">on Github</a>; use that instead of relying entirely on the examples in the book.</p>
<p>I've built one large front-end Javascript application with <a href="http://backbonejs.org/">Backbone</a>, and I floundered at organizing it. Although Backbone is rigorous (hence the name) about separating models and views, higher-level questions are underspecified: how should the code be split among files? Whose responsibility is it to create the models and views? Wilson uses Require.js to neatly slice code into files and to declare the dependencies among them. In his example application, the Backbone router is responsible for instantiating all models and views. As the book progresses and his example application grows, the routes, models, and views remain focused and decoupled. It's a compelling design. I wish I'd known.</p>
<p>Wilson spends an early chapter building a login system for his example app, before implementing any features. He even salts his password hashes to defend against rainbow tables. An author less secure in his convictions would fear losing his reader's attention, but Wilson insists on doing the right thing. And rightly so: readers will paste his examples and put them into production, so the examples should be complete.</p>
<p>On the other hand, Wilson's introduction to MongoDB misses some marks. It's only 12 pages, so why did he spend two of them on MapReduce? MapReduce has always been intended for big batch processes, not web applications. MongoDB books and talks have long over-emphasized MapReduce, which should be confined to a niche. The <a href="http://docs.mongodb.org/manual/applications/aggregation/">aggregation framework</a>, on the other hand, is general-purpose and was released months before Wilson's book; it should have been covered instead.</p>
<p>Wilson also shows a MongoDB pattern that risks losing updates and is needlessly slow: When a user adds a contact in his social-networking site, Wilson's code fetches the whole user document, adds the contact, and saves the whole document back:</p>

{{<highlight javascript>}}
app.post('/accounts/:id/contact', function(req,res) {
  var accountId = req.params.id;
  var contactId = req.param('contactId', null);

  models.Account.findById(accountId, function(account) {
    models.Account.findById(contactId, function(contact) {
      models.Account.addContact(account, contact);
      account.save();
    });
  });

  // Note: Not in callback - this endpoint returns immediately and
  // processes in the background
  res.send(200);
});
{{< / highlight >}}

<p>(I've edited for brevity; the <a href="https://github.com/Swiftam/book-node-mongodb-backbone/blob/master/ch08/app.js#L161">whole code is on GitHub</a>.) Note that if two requests are updating the same account, the first one's updates are lost. <a href="http://docs.mongodb.org/manual/reference/operator/addToSet/">$addToSet</a> would have solved this, and would be more efficient too.</p>
<p>Equally worrisome is Wilson's tendency to drop errors on the floor instead of reporting them to the user, as shown at the bottom of this function. He argues "we are accepting the small but rare inconvenience in order to serve the majority of requests at an accelerated speed." This is a terrible argument for silencing errors, especially since the front-end framework needn't block the user from interacting with the UI while it waits for the server response.</p>
<p>A book like this seems intended to show best practices, and patterns that encourage correctness. Some of the hardest patterns to learn are error-handling in Node and concurrency control in MongoDB. I wish Wilson had devoted half the attention he placed on security to these two topics.</p>
<p>But I'm only mad at these flaws because the book they mar is a good one. As Wilson builds up his architecture piece by piece, the patterns appear both usable and elegant, and capable of staying clean as the app grows. Wilson uses <a href="http://backbonejs.org/#Events">Backbone custom named events</a> like "app:loggedin" or "chat:start" to coordinate his front-end code, instead of letting views directly call methods on other views. A novice Backbone user might not see the tremendous value of decoupling views this way, but take it from me—it's a great idea.</p>
<p>The book concludes with a long chat example. Chat examples with Socket.io and Node are legion—indeed, obligatory—but the completeness of this one, including its integration with Backbone, is a tour de force. If you plan to use either Node or Backbone this book has excellent recommendations for structuring a large app, and even if you're not building with any of the frameworks Wilson covers, his examples can inspire you to write more concise and decoupled code.</p>
