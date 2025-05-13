+++
type = "post"
title = "Undoing Gevent's monkey-patching"
date = "2012-04-05T15:23:08"
description = ""
category = ["Programming", "Python"]
tag = ["gevent", "unittest"]
enable_lightbox = false
draft = false
+++

<h1 id="update">Update</h1>
<p>I'm a genius: simply executing <code>reload(socket)</code> undoes Gevent's
<code>patch_socket()</code>. Obviously, this only applies to new sockets created
after executing <code>reload</code>, but that's good enough for my unittests. The
dumb solution below is preserved for hysterical porpoises.</p>
<h1 id="prior">Prior</h1>
<p>I ran into an odd problem while testing the next release of PyMongo, the
Python driver for MongoDB which I help develop. We're improving its
support for <a href="http://www.gevent.org/">Gevent</a>, so we're of course doing
additional tests that begin with:</p>

{{<highlight python3>}}
from gevent import monkey; monkey.patch_socket()
{{< / highlight >}}

<p>Now, some tests rely on this patching, and some rely on <strong>not</strong> being
patched. Gevent doesn't provide an <code>unpatch_socket</code>, so I had a clever
idea: I'll fork a subprocess with
<a href="http://docs.python.org/library/multiprocessing.html">multiprocessing</a>,
do the test there, and return its result to the parent process in a
<code>multiprocessing.Value</code>. Then subsequent tests won't be affected by the
patching.</p>

{{<highlight python3>}}
SUCCESS = 1
FAILURE = 0

def my_test(outcome):
    from gevent import monkey; monkey.patch_socket()
    # do the test ....
    outcome.value = SUCCESS

class Test(unittest.TestCase):
    def test(self):
        outcome = multiprocessing.Value('i', FAILURE)
        multiprocessing.Process(
            target=my_test,
            args=(outcome,)
        ).start().join()

        self.assertEqual(SUCCESS, outcome.value)
{{< / highlight >}}

<p>Nice and straightforward, right? In sane operating systems this worked
great. On Windows it broke horribly. When I did <code>python setup.py test</code>,
instead of executing <code>my_test()</code>, multiprocessing on Windows restarted
the whole test suite, which started another whole test suite, ...
Apparently, since Windows can't <code>fork()</code>, multiprocessing re-imports
your script and attempts to execute the proper function within it. If
the test suite is begun with <code>python setup.py test</code>, then everything
goes haywire. This <a href="http://mail.python.org/pipermail/python-list/2011-February/1266451.html">problem with multiprocessing and unittests on
Windows</a>
was discussed on the Python mailing list last February.</p>
<p>After some gloomy minutes, I decided to look at what <code>patch_socket()</code> is
doing. Turns out it's simple, so I wrote a version which allows
unpatching:</p>

{{<highlight python3>}}
def patch_socket(aggressive=True):
    """Like gevent.monkey.patch_socket(), but stores old socket attributes
    for unpatching.
    """
    from gevent import socket
    _socket = __import__('socket')

    old_attrs = {}
    for attr in (
        'socket', 'SocketType', 'create_connection', 'socketpair', 'fromfd'
    ):
        if hasattr(_socket, attr):
            old_attrs[attr] = getattr(_socket, attr)
            setattr(_socket, attr, getattr(socket, attr))

    try:
        from gevent.socket import ssl, sslerror
        old_attrs['ssl'] = _socket.ssl
        _socket.ssl = ssl
        old_attrs['sslerror'] = _socket.sslerror
        _socket.sslerror = sslerror
    except ImportError:
        if aggressive:
            try:
                del _socket.ssl
            except AttributeError:
                pass

    return old_attrs


def unpatch_socket(old_attrs):
    """Take output of patch_socket() and undo patching."""
    _socket = __import__('socket')

    for attr in old_attrs:
        if hasattr(_socket, attr):
            setattr(_socket, attr, old_attrs[attr])


def patch_dns():
    """Like gevent.monkey.patch_dns(), but stores old socket attributes
    for unpatching.
    """
    from gevent.socket import gethostbyname, getaddrinfo
    _socket = __import__('socket')

    old_attrs = {}
    old_attrs['getaddrinfo'] = _socket.getaddrinfo
    _socket.getaddrinfo = getaddrinfo
    old_attrs['gethostbyname'] = _socket.gethostbyname
    _socket.gethostbyname = gethostbyname

    return old_attrs


def unpatch_dns(old_attrs):
    """Take output of patch_dns() and undo patching."""
    _socket = __import__('socket')

    for attr in old_attrs:
        setattr(_socket, attr, old_attrs[attr])
{{< / highlight >}}

<p>In Gevent's version, calling <code>patch_socket()</code> calls <code>patch_dns()</code>
implicitly, in mine you must call both:</p>

{{<highlight python3>}}
class Test(unittest.TestCase):
    def test(self):
        old_socket_attrs = patch_socket()
        old_dns_attrs = patch_dns()

        try:
            # do test ...
        finally:
            unpatch_dns(old_dns_attrs)
            unpatch_socket(old_socket_attrs)
{{< / highlight >}}

<p>Now I don't need multiprocessing at all.</p>
