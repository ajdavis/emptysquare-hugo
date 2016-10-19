+++
type = "post"
title = "MotorConnection Has Been Renamed MotorClient"
date = "2012-12-18T17:02:48"
description = ""
category = ["Mongo", "Motor", "Programming", "Python"]
tag = []
enable_lightbox = false
thumbnail = "motor-musho@240.png"
draft = false
disqus_identifier = "50d0e7c55393741451a1ff2c"
disqus_url = "https://emptysqua.re/blog/50d0e7c55393741451a1ff2c/"
+++

<p><img src="motor-musho.png" alt="Motor" title="Motor" border="0"   /></p>
<p>As it was foretold, so has it come to pass. The omens all are satisfied, the prophecy fulfilled.</p>
<p>Last month <a href="/pymongos-new-default-safe-writes/">I wrote about</a> PyMongo renaming its main classes from <code>Connection</code> to <code>MongoClient</code> and from <code>ReplicaSetConnection</code> to <code>MongoReplicaSetClient</code>. For consistency, I promised to rename <a href="/motor/">Motor</a>'s main classes, too: from <code>MotorConnection</code> to <code>MotorClient</code> and from <code>MotorReplicaSetConnection</code> to <code>MotorReplicaSetClient</code>. <a href="https://github.com/ajdavis/mongo-python-driver/commit/3aa4948d13858f3ebf286256c5af3263e3f6eeb5">Now I've done so</a>.</p>
<h1 id="migration">Migration</h1>
<ol>
<li>Obviously, anywhere you refer to <code>MotorConnection</code> or <code>MotorReplicaSetConnection</code>, replace it with <code>MotorClient</code> or <code>MotorReplicaSetClient</code>.</li>
<li>More subtly, if you use the <code>sync_connection</code> method, that's changed to <a href="http://motor.readthedocs.org/en/stable/api/motor_client.html#motor.MotorClient.sync_client"><code>sync_client</code></a>.</li>
</ol>
<p>I've updated this blog to run on the latest version of Motor, <a href="https://github.com/ajdavis/motor-blog/commit/0c91d721a2bdb108cbf9c629542c9a8c0579bd02">you can see the commit here</a>.</p>
