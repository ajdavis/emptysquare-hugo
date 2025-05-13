+++
type = "post"
title = "Copying A Python Function's Signature"
date = "2012-06-18T22:37:09"
description = "A supplement to functools.wraps."
category = ["Programming", "Python"]
tag = []
enable_lightbox = false
thumbnail = "john-hancock-sig.png"
draft = false
+++

<p><img src="john-hancock-sig.png" style="display:block; margin-left:auto; margin-right:auto;" title="John Hancock's signature"/></p>
<p>Like all Python programmers, I'm writing a minimal blogging platform. In
my particular case, I'm building my blog using Tornado, MongoDB, and an
experimental MongoDB driver I wrote, which I'll announce soon. Rather
than build an admin UI where I can create, edit, and delete blog posts,
I rely on <a href="http://www.red-sweater.com/marsedit/">MarsEdit</a>. My blog
simply implements the portion of the metaWeblog XML-RPC API that
MarsEdit uses. To implement this API I use Josh Marshall's excellent
<a href="https://github.com/joshmarshall/tornadorpc">Tornado-RPC</a> package.</p>
<p>With Tornado-RPC, I declare my particular handlers (e.g., the
<code>metaWeblog.getRecentPosts</code> handler), and Tornado-RPC introspects my
methods' signatures to check if they're receiving the right arguments at
run time:</p>

{{<highlight python3>}}
args, varargs, varkw, defaults = inspect.getargspec(func)
{{< / highlight >}}

<p>This is fantastic. But my XML-RPC handlers tend to all have similar
signatures:</p>

{{<highlight python3>}}
def metaWeblog_newPost(self, blogid, user, password, struct, publish):
    pass

def metaWeblog_editPost(self, postid, user, password, struct, publish):
    pass

def metaWeblog_getPost(self, postid, user, password):
    pass
{{< / highlight >}}

<p>I want to check that the user and password are correct in each handler
method, without duplicating a ton of code. The obvious approach is a
decorator:</p>

{{<highlight python3>}}
@auth
def metaWeblog_newPost(self, blogid, user, password, struct, publish):
    pass

def auth(fn):
    argspec = inspect.getargspec(fn)

    @functools.wraps(fn)
    def _auth(*args, **kwargs):
        self = args[0]
        user = args[argspec.args.index('user')]
        password = args[argspec.args.index('password')]
        if not check_authentication(user, password):
            self.result(xmlrpclib.Fault(
                403, 'Bad login/pass combination.'))
        else:
            return fn(*args, **kwargs)

    return _auth
{{< / highlight >}}

<p>Simple enough, right? My decorated method checks the user and password,
and either returns an authentication fault, or executes the wrapped
method.</p>
<p>Problem is, a simple <code>functools.wraps()</code> isn't enough to fool
Tornado-RPC when it inspects my handler methods' signatures using
<code>inspect.getargspec()</code>. <code>functools.wraps()</code> can change a wrapper's
module, name, docstring, and __dict__ to the wrapped function's
values, but it doesn't change the wrapper's actual method signature.</p>
<p>Inspired by <a href="http://www.voidspace.org.uk/python/mock/">Mock</a>, I found
this solution:</p>

{{<highlight python3>}}
def auth(fn):
    argspec = inspect.getargspec(fn)

    def _auth(*args, **kwargs):
        user = args[argspec.args.index('user')]
        password = args[argspec.args.index('password')]
        if not check_authentication(user, password):
            self.result(xmlrpclib.Fault(403, 'Bad login/pass combination.'))
        else:
            return fn(*args, **kwargs)

    # For tornadorpc to think _auth has the same arguments as fn,
    # functools.wraps() isn't enough.
    formatted_args = inspect.formatargspec(*argspec)
    fndef = 'lambda %s: _auth%s' % (
        formatted_args.lstrip('(').rstrip(')'), formatted_args)

    fake_fn = eval(fndef, {'_auth': _auth})
    return functools.wraps(fn)(fake_fn)
{{< / highlight >}}

<p>Yes, <code>eval</code> is evil. But for this case, it's the only way to create a
new wrapper function with the same signature as the wrapped function. My
decorator formats a string like:</p>

{{<highlight python3>}}
lambda self, blogid, user, password, struct, publish:\
        _auth(self, blogid, user, password, struct, publish)
{{< / highlight >}}

<p>And evals it to create a lambda. This lambda is the final wrapper. It's
what the <code>@auth</code> decorator returns in lieu of the wrapped function. Now
when Tornado-RPC does <code>inspect.getargspec()</code> on the wrapped function to
check its arguments, it thinks the wrapper has the proper method
signature.</p>
