+++
category = ['Programming', 'MongoDB', 'Python', 'Motor']
date = '2016-10-26T07:16:27.893238'
description = 'Switches from greenlets to a thread pool, and updates from PyMongo 2.8 to 2.9.'
draft = false
enable_lightbox = true
tag = []
thumbnail = 'motor-musho.png'
title = 'Announcing Motor 0.7'
type = 'post'
+++

<p><img style="display:block; margin-left:auto; margin-right:auto;" src="/motor-0-7/motor-musho.png" alt="Motor logo by Musho Rodney Alan Greenblat" title="motor-musho.png" border="0" /></p>

Three weeks after I released the beta, I'm proud to present Motor 0.7.

For asynchronous I/O Motor now uses a thread pool, which is faster and simpler than the prior implementation with greenlets. It no longer requires the greenlet package, and now requires the futures backport package on Python 2. [Read the beta announcement to learn more about the switch from greenlets to threads](/motor-0-7-beta/).

Install with:

```
python -m pip install motor
```

This version updates the PyMongo dependency from 2.8.0 to 2.9.x, and wraps PyMongo 2.9's new APIs.

Since the beta release, I've fixed one fun bug, [a manifestation in Motor of the same import deadlock I fixed in PyMongo, Tornado, and Gevent last year](/weird-green-bug/).

The next release will be Motor 1.0, which will be out in less than a month.
Most of Motor 1.0's API is now implemented in Motor 0.7, and APIs that will be removed in Motor 1.0 are now deprecated and raise warnings.

This is a large release, please read the documentation carefully:

- [Motor Changelog](http://motor.readthedocs.io/en/latest/changelog.html)
- [Motor 1.0 Migration Guide](http://motor.readthedocs.io/en/latest/migrate-to-motor-1.html)
- [All Jira tickets for Motor 0.7](https://jira.mongodb.org/issues/?filter=20674)

If you encounter any issues, [please file them in Jira](https://jira.mongodb.org/browse/MOTOR).

Peace,  
&mdash;A. Jesse Jiryu Davis
