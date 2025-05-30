+++
type = "post"
title = "Server Discovery And Monitoring In PyMongo, Perl, And C"
date = "2015-05-19T23:09:35"
description = "Our drivers' algorithms to discover and stay connected to your server, replica set, or sharded cluster."
category = ["C", "MongoDB", "Programming", "Python"]
tag = ["pymongo"]
enable_lightbox = false
draft = false
+++

<p><em>(Cross-posted from the MongoDB Blog.)</em></p>
<p>How does a MongoDB driver discover and monitor a single server, a set of mongos servers, or a replica set? How does it determine what types of servers they are? How does it keep this information up to date? How does it discover an entire replica set given an initial host list, and how does it respond to stepdowns, elections, reconfigurations, network error, or the loss of a server?</p>
<p>In the past each MongoDB driver answered these questions a little differently, and mongos differed a little from the drivers. We couldn't answer questions like, "Once I add a secondary to my replica set, how long does it take for the driver to start using it?" Or, "How does a driver detect when the primary steps down, and how does it react?"</p>
<p>To standardize our drivers, I wrote the Server Discovery And Monitoring Spec, with David Golden, Craig Wilson, Jeff Yemin, and Bernie Hackett. Beginning with this spring's next-generation driver releases, all our drivers conform to the spec and answer these questions the same. Or, where there's a legitimate reason for them to differ, there are as few differences as possible and each is clearly explained in the spec. Even in cases where several answers seem equally good, drivers agree on one way to do it.</p>
<p>The spec describes how a driver monitors a topology:</p>
<blockquote>
<p><em>Topology:</em> The state of your deployment. What type of deployment it is, which servers are available, and what type of servers (mongos, primary, secondary, ...) they are.</p>
</blockquote>
<p>The spec covers all MongoDB topologies, but replica sets are the most interesting. So I'll explain the spec's algorithm for replica sets by telling the story of your application as it passes through life stages: it starts up, discovers a replica set, and reaches a steady state. Then there is a crisis&mdash;I spill coffee on your primary server's motherboard&mdash;and a resolution&mdash;the replica set elects a new primary and the driver discovers it.</p>
<p>At each stage we'll observe a typical multi-threaded driver, PyMongo 3.0, a typical single-threaded driver, the Perl Driver 1.0, and a hybrid, the C Driver 1.2. (I implemented PyMongo's server discovery and monitoring. David Golden wrote the Perl version, and Samantha Ritter and Jason Carey wrote the one in C.)</p>
<p>To conclude, I'll tell you our strategy for verifying spec compliance in ten programming languages, and I'll share links for further reading.</p>
<h1 id="startup">Startup</h1>
<p>When your application initializes, it creates a MongoClient. In Python:</p>

```python
client = MongoClient(
   "mongodb://hostA,hostB/?replicaSet=my_rs")
```


<p>In Perl:</p>

```perl
my $client = MongoDB::MongoClient->new({
    host => "mongodb://hostA,hostB/?replicaSet=my_rs"
});
```

<p>In C, you can either create a client directly:</p>

```c
mongoc_client_t *client = mongoc_client_new (
    "mongodb://hostA,hostB/?replicaSet=my_rs");
```

<p>Or create a client pool:</p>

```c
mongoc_uri_t *uri = mongoc_uri_new (
   "mongodb://hostA,hostB/?replicaSet=my_rs");

mongoc_client_pool_t *pool = mongoc_client_pool_new (uri);
mongoc_client_t *client = mongoc_client_pool_pop (pool);
```


<p>A crucial improvement of the next gen drivers is, the constructor no longer blocks while it makes the initial connection. Instead, the constructor does no network I/O. PyMongo launches a background thread per server (two threads in this example) to initiate discovery, and returns control to your application without blocking. Perl does nothing until you attempt an operation; then it connects on demand.</p>
<p>In the C Driver, if you create a client directly it behaves like the Perl Driver: it connects on demand, on the main thread. But the C Driver's client pool launches one background thread to discover and monitor all servers.</p>
<p>The spec's "no I/O in constructors" rule is a big win for web applications that use our next gen drivers: In a crisis, your app servers might be restarted while your MongoDB servers are unreachable. Your application should not throw an error at startup, when it constructs the client object. It starts up disconnected and tries to reach your servers until it succeeds.</p>
<h1 id="discovery">Discovery</h1>
<p>The initial host list you provide is called the "seed list":</p>
<blockquote>
<p><em>Seed list:</em> The initial list of server addresses provided to the MongoClient.</p>
</blockquote>
<p>The seed list is the stepping-off point for the driver's journey of discovery. As long as one seed is actually an available replica set member, the driver will discover the whole set and stay connected to it indefinitely, as described below. Even if every member of the set is replaced with a new host, like the <a href="http://en.wikipedia.org/wiki/Ship_of_Theseus">Ship of Theseus</a>, it is still the same replica set and the driver remains connected to it.</p>
<p>I tend to think of a driver as a tiny economy of information about your topology. Monitoring supplies information, and your application's operations demand information. Their demands are defined in David Golden's <a href="http://www.mongodb.com/blog/post/server-selection-next-generation-mongodb-drivers">Server Selection Spec</a>, while the method of supplying information is defined here, in the Server Discovery And Monitoring Spec. In the beginning, there is no information, and the monitors rush to supply some. I'll talk more about the demand side later, in the "Crisis" section.</p>
<h1 id="multi-threaded">Multi-threaded</h1>
<p>Let's start with PyMongo. In PyMongo, like other multi-threaded drivers, the MongoClient constructor starts one monitor thread each for "hostA" and "hostB".</p>
<blockquote><p><em>Monitor</em>: A thread or async task that occasionally checks the state of one server.</p></blockquote>
<p>Each monitor connects to its assigned server and executes the <a href="http://docs.mongodb.org/manual/reference/command/isMaster">"ismaster" command</a>. Ignore the command's archaic name, which dates from the days of master-slave replication, long superseded by replica sets. The ismaster command is the client-server handshake. Let's say the driver receives hostB's response first:</p>

```javascript
ismaster = {
    "setName": "my_rs",
    "ismaster": false,
    "secondary": true,
    "hosts": [
        "hostA:27017",
        "hostB:27017",
        "hostC:27017"]}
```


<p>hostB confirms it belongs to your replica set, informs you that it is a secondary, and lists the members in the replica set config. PyMongo sees a host it didn't know about, hostC, so it launches a new thread to connect to it.</p>
<p>If your application threads are waiting to do any operations with the MongoClient, they block while awaiting discovery. But since PyMongo now knows of a secondary, if your application is waiting to do a secondary read, it can now proceed:</p>

```python
db = client.get_database(
    "dbname",
    read_preference=ReadPreference.SECONDARY)

# Unblocks when a secondary is found.
db.collection.find_one()
```


<p>Meanwhile, discovery continues. PyMongo waits for ismaster responses from hostA and hostC. Let's say hostC responds next, and its response includes "ismaster": true:</p>

```javascript
ismaster = {
    "setName": "my_rs",
    "ismaster": true,
    "secondary": false,
    "hosts": [
        "hostA:27017",
        "hostB:27017",
        "hostC:27017"]}
```


<p>Now PyMongo knows the primary, so all reads and writes are unblocked. PyMongo is still waiting to hear back from hostA; once it does, it can use hostA for secondary reads as well.</p>
<h1 id="single-threaded">Single-threaded</h1>
<p>Multithreaded Perl code is problematic, so the Perl Driver doesn't launch a thread per host. How, then does it discover your set? When you construct a MongoClient it does no I/O. It waits for you to begin an operation before it connects. Once you do, it scans the hosts serially, initially in random order.</p>
<blockquote>
<p><em>Scan:</em> A single-threaded driver's process of checking the state of all servers.</p>
</blockquote>
<p>Let's say the driver begins with hostB, a secondary. Here's a detail I didn't show you earlier: replica set members tell you who they think the primary is. HostB's reply includes "primary": "hostC:27017":</p>

```javascript
ismaster = {
    "setName": "my_rs",
    "ismaster": false,
    "secondary": true,
    "primary": "hostC:27017",
    "hosts": [
        "hostA:27017",
        "hostB:27017",
        "hostC:27017"]}
```


<p>The Perl Driver uses this hint to put hostC next in the scan order, because connecting to the primary is its top priority. It checks hostC and confirms that it's primary. Finally, it checks hostA to ensure it can connect, and discovers that hostA is another secondary. Scanning is now complete and the driver proceeds with your application's operation.</p>
<h1 id="hybrid">Hybrid</h1>
<p>The C driver has two <em>modes</em> for server discovery and monitoring: single-threaded and pooled. Single-threaded mode is optimized for embedding the C Driver within languages like PHP: PHP applications deploy many single-threaded processes connected to MongoDB. Each process uses the same connections to scan the topology as it uses for application operations, so the total connection count from many processes is kept to a minimum.</p>
<p>Other applications should use pooled mode: as we shall see, in pooled mode a background thread monitors the topology, so the application need not block to scan it.</p>
<h2 id="c-drivers-single-threaded-mode">C Driver's single-threaded mode</h2>
<p>The C driver scans servers on the main thread, if you construct a single client:</p>

```c
mongoc_client_t *client = mongoc_client_new (
      "mongodb://hostA,hostB/?replicaSet=my_rs");
```


<p>In single-threaded mode, the C Driver blocks to scan your topology periodically with the main thread, just like the Perl Driver. But unlike the Perl Driver's serial scan, the C Driver checks all servers in parallel. Using a non-blocking socket per member, it begins a check on each member concurrently, and uses the asynchronous "poll" function to receive events from the sockets, until all have responded or timed out. The driver updates its topology as ismaster calls complete. Finally it ends the scan and returns control to your application.</p>
<p>Whereas the Perl Driver's topology scan lasts for the sum of all server checks (including timeouts), the C Driver's topology scan lasts only the maximum of any one check's duration, or the connection timeout setting, whichever is shorter. Put another way, in single-threaded mode the C Driver fans out to begin all checks concurrently, then fans in once all checks have completed or timed out. This "fan out, fan in" topology scanning method gives the C Driver an advantage scanning very large replica sets, or sets with several high-latency members.</p>
<h2 id="c-drivers-pooled-mode">C Driver's pooled mode</h2>
<p>To activate the C Driver's pooled mode, make a client pool:</p>

```c
mongoc_uri_t *uri = mongoc_uri_new (
   "mongodb://hostA,hostB/?replicaSet=my_rs");

mongoc_client_pool_t *pool = mongoc_client_pool_new (uri);
mongoc_client_t *client = mongoc_client_pool_pop (pool);
```

<p>The pool launches one background thread for monitoring. When the thread begins, it fans out and connects to all servers in the seed list, using non-blocking sockets and a simple event loop. As it receives ismaster responses from the servers, it updates its view of your topology, the same as a multi-threaded driver like PyMongo does. When it discovers a new server it begins connecting to it, and adds the new socket to the list of non-blocking sockets in its event loop.</p>
<p>As with PyMongo, when the C Driver is in background-thread mode, your application's operations are unblocked as soon as monitoring discovers a usable server. For example, if your C code is blocked waiting to insert into the primary, it is unblocked as soon as the primary is discovered, rather than waiting for all secondaries to be checked too.</p>
<h1 id="steady-state">Steady State</h1>
<p>Once the driver has discovered your whole replica set, it periodically re-checks each server. The periodic check is necessary to keep track of your network latency to each server, and to detect when a new secondary joins the set. And in some cases periodic monitoring can head off errors, by proactively discovering when a server is offline.</p>
<p>By default, the monitor threads in PyMongo check their servers every ten seconds, as does the C Driver's monitor in background-thread mode. The Perl driver, and the C Driver in single-threaded mode, block your application to re-scan the replica set once per minute.</p>
<p>If you like my supply-and-demand model of a driver, the steady state is when your application's demand for topology information is satisfied. The driver occasionally refreshes its stock of information to make sure it's ready for future demands, but there is no urgency.</p>
<h1 id="crisis">Crisis</h1>
<p>So I wander into your data center, swirling my cappuccino, and I stumble and spill it on hostC's motherboard. Now your replica set has no primary. What happens next?</p>
<p>When your application next writes to the primary, it gets a socket timeout. Now it knows the primary is gone. Its demand for information is no longer in balance with supply. The next attempt to write blocks until a primary is found.</p>
<p>To meet demand, the driver works overtime. How exactly it responds to the crisis depends on which type of monitoring it uses.</p>
<p><strong>Multi-threaded:</strong> In drivers like PyMongo, the monitor threads wait only half a second between server checks, instead of ten seconds. They want to know as soon as possible if the primary has come back, or if one of the secondaries has been elected primary.</p>
<p><strong>Single-threaded:</strong> Drivers like the Perl Driver sleep half a second between scans of the topology. The application's write operation remains blocked until the driver finds the primary.</p>
<p><strong>C Driver Single-Threaded:</strong> In single-threaded mode, the C Driver sleeps half a second between scans, just like the Perl Driver. During the scan the driver launches non-blocking "ismaster" commands on all servers concurrently, as I described above.</p>
<p><strong>C Driver Pooled Mode:</strong> Each time the driver's monitor thread receives an ismaster response, schedules that server's next ismaster call on the event loop only a half-second in the future.</p>
<h1 id="resolution">Resolution</h1>
<p>Your secondaries, hostA and hostB, promptly detect my sabotage of hostC, and hold an election. In MongoDB 3.0, the election takes just a couple seconds. Let's say hostA becomes primary.</p>
<p>A half second or less later, your driver rechecks hostA and sees that it is now the primary. It unblocks your application's writes and sends them to hostA. In PyMongo, the monitor threads relax, and return to their slow polling strategy: they sleep ten seconds between server checks. Same for the C Driver's monitor in background-thread mode. The Perl Driver, and the C Driver in single-threaded mode, do not rescan the topology for another minute. Demand and supply are once again in balance.</p>
<h1 id="compliance-testing">Compliance Testing</h1>
<p>I am particularly excited about the unit tests that accompany the Server Discovery And Monitoring Spec. We have 38 tests that are specified formally in YAML files, with inputs and expected outcomes for a range of scenarios. For each driver we write a test runner that feeds the inputs to the driver and verifies the outcome. This ends confusion about what the spec means, or whether all drivers conform to it. You can track our progress toward full compliance in MongoDB's issue tracker.</p>
<h1 id="further-study">Further Study</h1>
<p>The spec is long but tractable. It explains the monitoring algorithm in very fine detail. You can read a summary, and the spec itself, here:</p>
<ul>
<li><a href="https://github.com/mongodb/specifications/blob/master/source/server-discovery-and-monitoring/server-discovery-and-monitoring-summary.rst">A summary of the spec.</a></li>
<li><a href="https://github.com/mongodb/specifications/blob/master/source/server-discovery-and-monitoring/server-discovery-and-monitoring.rst">The Server Discovery And Monitoring Spec.</a></li>
<li><a href="https://github.com/mongodb/specifications/tree/master/source/server-discovery-and-monitoring">The spec source, including the YAML test files.</a></li>
<li><a href="https://www.mongodb.com/presentations/mongodb-drivers-and-high-availability-deep-dive">My MongoDB World 2015 talk, "MongoDB Drivers And High Availability: Deep Dive", in which I describe PyMongo 3's implementation of the spec. Also useful for a reasonable retry strategy.</a></li>
</ul>
<p>Its job is to describe the demand side of the driver's information economy. For the supply side, read my colleague David Golden's <a href="http://www.mongodb.com/blog/post/server-selection-next-generation-mongodb-drivers">article on his Server Selection Spec</a>.</p>
