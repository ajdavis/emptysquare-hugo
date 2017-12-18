+++
category = ['Mongo', 'Motor', 'Programming', 'Python']
date = '2017-12-18T15:47:17.208014'
description = 'Adds change streams, causal consistency, retryable writes, and more. Drops Python 2.6, MongoDB 2.4, and Tornado 3.'
draft = false
enable_lightbox = false
tag = []
thumbnail = 'motor-musho.png'
title = 'Motor 1.2.0'
type = 'post'
+++

<p><img style="display:block; margin-left:auto; margin-right:auto;" src="motor-musho.png" alt="Motor" border="0" /></p>

I'm excited to announce version 1.2.0 of Motor, my async Python driver for MongoDB. Motor works with Python 2.7 and 3.4+, and it supports async MongoDB applications using either Tornado or asyncio. Version 1.2.0 is not substantially changed from the release candidate I announced last week, please [read that post for all the details about this version of Motor](/motor-1-2-release-candidate).

Install Motor with pip:

```text
python -m pip install -U motor
```

<a href="https://jira.mongodb.org/browse/MOTOR/">If you find issues, file a bug and I'll respond promptly.</a> But if it works for you, don't be silent!&mdash;<a href="https://twitter.com/jessejiryudavis">tweet at me</a> and tell me.
