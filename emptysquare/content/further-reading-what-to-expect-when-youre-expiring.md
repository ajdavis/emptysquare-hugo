+++
category = ['Python', 'Programming']
date = '2018-02-10T13:45:10.148883'
description = 'Links related to my PyTennessee 2018 talk about Python object destructors.'
draft = false
enable_lightbox = false
tag = []
thumbnail = 'the-body-of-this-death.jpg'
title = "Further Reading About What To Expect When You're Expiring"
type = 'post'
+++

![](the-body-of-this-death.jpg)

At PyTennessee 2018 I gave a talk about writing Python object destructors called What To Expect When You're Expiring: Rules for ``__del__``. The rules for a destructor method are:

1. Don't access modules or globals.
2. Don't access threadlocals.
3. Don't take any locks.

Links to further reading about the subject:

- [PEP 442](https://www.python.org/dev/peps/pep-0442/) makes Rule 1 less necessary. For an entertaining story about this rule, read [A Normal Accident In Python and mod_wsgi](/a-normal-accident-in-python-and-mod-wsgi).
- [Python's Thread Locals Are Weird](/pythons-thread-locals-are-weird). The horror story behind Rule 2: "Don't touch threadlocals".
- [PyPy, Garbage Collection, And A Deadlock](/pypy-garbage-collection-and-a-deadlock): More details about Rule 3.
- [All the code examples used in my talk](https://github.com/ajdavis/what-to-expect-when-youre-expiring).

The images I used in my slides are from:

- [Old Book Illustrations 1](http://www.oldbookillustrations.com/illustrations/body-death/)
- [Old Book Illustrations 2](http://www.oldbookillustrations.com/illustrations/skull-crossbones/)
- [Old Book Illustrations 3](http://www.oldbookillustrations.com/illustrations/position-skeletons/)
- [Old Book Illustrations 4](http://www.oldbookillustrations.com/illustrations/pale-horse/)
- [50 Watts 1](http://50watts.com/Ex-Libris-Mr-Reaper-10)
- [50 Watts 2](http://50watts.com/A-Modern-Dance-of-Death)
- [50 Watts 3](http://50watts.com/Dead-Man-Company)
- [Public Domain Review 1](http://publicdomainreview.org/product/calaveras-riding-bicycles/)
- [Public Domain Review 2](http://publicdomainreview.org/product/calavera-from-oaxaca/)
