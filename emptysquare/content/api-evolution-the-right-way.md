+++
category = ['Python']
date = 2018-11-09T15:50:13.374520
description = "Ten covenants that responsible library authors keep with their users."
draft = false
enable_lightbox = false
tag = ['python3', 'best']
thumbnail = 'dragon.jpg'
title = 'API Evolution the Right Way'
type = 'post'
+++

![](dragon.jpg)

Imagine you are a creator deity, designing a body for a creature. In your benevelonce, you wish for the creature to evolve over time: first, because it must respond to changes in its environment, and second, because your wisdom grows and you think of better designs for the beast. It shouldn't remain  in the same body forever!

![](praise-the-creator.jpg)

The creature, however, might be relying on features of its present anatomy. You can't add wings or change its scales without warning. It needs an orderly process to adapt its lifestyle to its new body. How can you, as a responsible designer in charge of this creature's natural history, gently coax it toward ever greater improvements?

![](creator.jpg)

It's the same for responsible library maintainers. We keep our promises to the people who depend on our code: we release bugfixes and useful new features. We sometimes delete features if that's beneficial for the library's future. We continue to innovate, but we don't break the code of people who use our library. How can we fulfill all those goals at once?

# Add Useful Features

Your library shouldn't stay the same for eternity: you should add features that your make your library better for your users.
For example, if you have a Reptile class and it would be useful to have wings for flying, go for it.

{{< highlight py3 "hl_lines=6 7 8 9" >}}
class Reptile:
    @property
    def teeth(self):
        return 'sharp fangs'

    # If wings are useful, add them!
    @property
    def wings(self):
        return 'majestic wings'
{{< / highlight >}}

But beware, features come with risk.
Consider the following feature in the Python standard library, and let us see what went wrong with it.

```py3
bool(datetime.time(9, 30)) == True
bool(datetime.time(0, 0)) == False
```

This is peculiar: converting any time object to a boolean yields True, except for midnight. (Worse, the rules for timezone-aware times are even stranger.)
I've been writing Python for more than a decade but I didn't discover this rule until last week. What kind of bugs can this odd behavior cause in users' code?

Consider a calendar application with a function that creates events. If an event has an end time, the function requires it to also have a start time:

```py3
def create_event(day,
                 start_time=None,
                 end_time=None):
    if end_time and not start_time:
        raise ValueError("Can't pass end_time without start_time")

# The coven meets from midnight until 4am.
create_event(datetime.date.today(),
             datetime.time(0, 0),
             datetime.time(4, 0))
```

Unfortunately for witches, an event starting at midnight fails this validation. A careful programmer who knows about the quirk at midnight can write this function correctly, of course:

```py3
def create_event(day,
                 start_time=None,
                 end_time=None):
    if end_time is not None and start_time is None:
        raise ValueError("Can't pass end_time without start_time")
```

But this subtlety is worrisome. If a library creator wanted to make an API that bites users, a "feature" like the boolean conversion of midnight works nicely.

![](bite.jpg)

The responsible creator's goal, however, is to make your library easy to use correctly.

This feature was written by Tim Peters when he first made the datetime module in 2002. Even founding Pythonistas like Tim make mistakes. [The quirk was removed](https://bugs.python.org/issue13936), and all times are True now.

```py3
# Python 3.5 and later.

bool(datetime.time(9, 30)) == True
bool(datetime.time(0, 0)) == True
```

Programmers who didn't know about the oddity of midnight are saved from obscure bugs, but it makes me nervous to think about any code that actually relies on the weird old behavior and didn't notice the change. It would have been better if this bad feature were never implemented at all. This leads us to the first promise of any library maintainer:

<div style="text-align: center; font-weight: bold"><p>
First Covenant:<br>Avoid Bad Features
</p></div>

The most painful change to make is when you have to delete a feature. One way to avoid bad features is to add few features in general! Make no public method, class, function, or property without a good reason. Thus:

<div style="text-align: center; font-weight: bold"><p>
Second Covenant:<br>Minimize Features
</p></div>

Features are like children: conceived in a moment of passion, they must be supported for years.
Don't do anything silly just because you can. Don't add feathers to a snake!

![](feathers.jpg)

But of course, there are plenty of occasions when users need something from your library that it does not yet offer. How do you choose the right feature to give them? Here's another cautionary tale.

# A Cautionary Tale From asyncio

As you may know, when you call a coroutine function, it returns a coroutine object:

```py3
async def my_coroutine():
    pass

print(my_coroutine())
```

{{< highlight text "prestyles=background-color: black; color: lightgreen !important; padding: 1em 0.5em" >}}
<coroutine object my_coroutine at 0x10bfcbac8>
{{< / highlight >}}

Your code must "await" this object to actually run the coroutine. It's easy to forget this, so the asyncio developers wanted a "debug mode" that catches this mistake. Whenever a coroutine is destroyed without being awaited, the debug mode prints a warning with a traceback to the line where it was created.

When Yury Selivanov implemented the debug mode, he added as its foundation a "coroutine wrapper" feature. The wrapper is a function that takes in a coroutine and returns anything at all. Yury used it to install the warning logic on each coroutine, but someone else could use it to turn coroutines into the string "hi!":


```py3
import sys

def my_wrapper(coro):
    return 'hi!'

sys.set_coroutine_wrapper(my_wrapper)

async def my_coroutine():
    pass

print(my_coroutine())
```

{{< highlight text "prestyles=background-color: black; color: lightgreen !important; padding: 1em 0.5em" >}}
hi!
{{< / highlight >}}

That is one hell of a customization. It changes the very meaning of "async". Calling set_coroutine_wrapper once will globally and permanently change all coroutine functions.
It is, [as Nathaniel Smith wrote](https://bugs.python.org/issue32591), "a problematic API" which is prone to misuse and had to be removed. The asyncio developers could have avoided the pain of deleting the feature if they'd better shaped it to its purpose. Responsible creators must keep this in mind:

<div style="text-align: center; font-weight: bold"><p>
Third Covenant:<br>Keep Features Narrow
</p></div>

Luckily, Yury had the good judgment to mark this feature provisional, so asyncio users knew not to rely on it. Nathaniel was free to replace set_coroutine_wrapper with a narrower feature that only customized the traceback depth:

```py3
import sys

sys.set_coroutine_origin_tracking_depth(2)

async def my_coroutine():
    pass

print(my_coroutine())
```

{{< highlight text "prestyles=background-color: black; color: lightgreen !important; padding: 1em 0.5em" >}}
<coroutine object my_coroutine at 0x10bfcbac8>

RuntimeWarning:'my_coroutine' was never awaited

Coroutine created at (most recent call last)
  File "script.py", line 8, in <module>
    print(my_coroutine())
{{< / highlight >}}

This is much better. There's no more global setting that can change coroutines' type, so asyncio users need not code as defensively. Deities should all be as farsighted as Yury:

<div style="text-align: center; font-weight: bold"><p>
Fourth Covenant:<br>Mark Experimental Features "Provisional"
</p></div>

If you have merely a hunch that your creature wants horns and a quadruple-forked tongue, introduce the features but mark them "provisional".

![](horns.jpg)

You might discover that the horns are adventitious but the quadruple-forked tongue is useful after all. In the next release of your library you can delete the former and mark the latter official.

# Deleting Features

No matter how wisely we guide our creature's evolution, there may come a time when it's best to delete an official feature. For example, you might have created a lizard, and now you choose to delete its legs. Perhaps you want to transform this awkward creature into a sleek and modern python.

![](lizard-to-snake.jpg)

There are two main reasons to delete features. First, you might discover a feature was a bad idea, through user feedback or your own growing wisdom. That was the case with the quirky behavior of midnight. Or, the feature might have been well-adapted to your library's environment at first, but the ecology changes. Perhaps another deity invents mammals. Your creature wants to squeeze into their little burrows and eat the tasty mammal filling, so it has to lose its legs.

![](mammal.jpg)

Similarly, the Python standard library deletes features in response to changes in the language itself. Consider asyncio's Lock. It has been awaitable ever since "await" was added as a keyword:

{{< highlight py3 "hl_lines=4" >}}
lock = asyncio.Lock()

async def critical_section():
    await lock
    try:
        print('holding lock')
    finally:
        lock.release()
{{< / highlight >}}

But now, we can do "async with lock":

{{< highlight py3 "hl_lines=4" >}}
lock = asyncio.Lock()

async def critical_section():
    async with lock:
        print('holding lock')
{{< / highlight >}}

The new style is much better! It's short, and less prone to mistakes in a big function with other try-except blocks. Since "there should be one and preferably only one obvious way to do it" [the old syntax is deprecated in Python 3.7](https://bugs.python.org/issue32253) and it will be banned soon.

It's inevitable that ecological change will have this effect on your code too, so learn to delete features gently. Before you do so, consider the cost or benefit of deleting it. Responsible maintainers are reluctant to make their users change a large amount of their code, or change their logic. (Remember how painful it was when Python 3 removed the "u" string prefix, before it was added back.) If the code changes are mechanical, however, like a simple search and replace, or if the feature is dangerous, it may be worth deleting.

<div style="text-align: center"><p style="font-size: 1.5em; font-weight: bold">
Whether to Delete a Feature
</p></div>

![](scale.jpg)

<table class="pro-con" style="width: 100%; text-align: center; font-size: 1.3em; line-height: 1.5em; margin-bottom: 1em">
<thead>
<tr>
<th>Con</th>
<th>Pro</th>
</tr>
</thead>

<tbody>
<tr>
<td>Code must change</td>
<td>Change is mechanical</td>
</tr>

<tr>
<td>Logic must change</td>
<td>Feature is dangerous</td>
</tr>
</tbody>
</table>

In the case of our hungry lizard, we decide to delete its legs so it can slither into a mouse's hole and eat it. How do we go about this? We could just delete the ``walk`` method, changing code from this:

```py3
class Reptile:
    def walk(self):
        print('step step step')
```

To this:

{{< highlight py3 >}}
class Reptile:
    def slither(self):
        print('slide slide slide')
{{< / highlight >}}

That's not a good idea, the creature is used to walking! Or, in terms of a library, your users have code that relies on the existing method. When they upgrade to the latest version of your library, their code will break.

{{< highlight py3 "hl_lines=6" >}}
# User's code. Oops!
Reptile.walk()
{{< / highlight >}}

Therefore responsible creators make this promise:

<div style="text-align: center; font-weight: bold"><p>
Fifth Covenant:<br>Delete Features Gently
</p></div>

There's a few steps involved in deleting a feature gently. Starting with a lizard that walks with its legs, you first add the new method, "slither". Next, deprecate the old method.

```py3
import warnings

class Reptile:
    def walk(self):
        warnings.warn(
            "walk is deprecated, use slither",
            DeprecationWarning, stacklevel=2)
        print('step step step')

    def slither(self):
        print('slide slide slide')
```

The Python warnings module is quite powerful. By default it prints warnings to stderr, only once per code location, but you can silence warnings or turn them into exceptions, among other options.

As soon as you add this warning to your library, PyCharm and other IDEs render the deprecated method with a strikethrough. Users know right away that the method is due for deletion.

<pre><code>Reptile().<span style="text-decoration: line-through">walk()</span></code></pre>

What happens when they run their code with the upgraded library?

{{< highlight text "prestyles=background-color: black; color: lightgreen !important; padding: 1em 0.5em" >}}
> python3 script.py

DeprecationWarning: walk is deprecated, use slither
  script.py:14: Reptile().walk()

step step step
{{< / highlight >}}

By default, they see a warning on stderr, but the script succeeds and prints "step step step". The warning's traceback shows what line of the user's code must be fixed. (That's what the "stacklevel" argument does: it shows the call site that users need to change, not the line where the warning is generated.) Notice that the error message is instructive, it describes what a library user must do to migrate to the new version.

Your users will want to test their code and prove they call no deprecated library methods. Warnings alone won't make unittests fail, but exceptions will. Python has a command-line option to turn deprecation warnings into exceptions:

{{< highlight text "prestyles=background-color: black; color: lightgreen !important; padding: 1em 0.5em" >}}
> python3 -Werror::DeprecationWarning script.py

Traceback (most recent call last):
  File "script.py", line 14, in <module>
    Reptile().walk()
  File "script.py", line 8, in walk
    DeprecationWarning, stacklevel=2)
DeprecationWarning: walk is deprecated, use slither
{{< / highlight >}}

Now, "step step step" is not printed, because the script terminates with an error.

So once you've released a version of your library that warns about the deprecated "walk" method, you can delete it safely in the next release. Right?

Consider what your library's users might have in their projects' requirements:

```
# User's requirements.txt has a dependency on the reptile package.
reptile
```

The next time they deploy their code, they'll install the latest version of your library. If they haven't yet handled all deprecations then their code will break, because it still depends on "walk". You need to be gentler than this. There are three more promises you must keep to your users: to maintain a changelog, choose a version scheme, and write an upgrade guide.

<div style="text-align: center; font-weight: bold"><p>
Sixth Covenant:<br>Maintain a Changelog
</p></div>

Your library must have a change log; its main purpose is to announce when a feature that your users rely on is deprecated or deleted.

<div style="border: 1px solid black; padding: 0.5em; margin-bottom: 1em">
<p style="font-weight: bold; text-align: center">Changes in Version 1.1</p>

<p><strong>New features</strong></p>

<ul><li>New function Reptile.slither()</li></ul>

<p><strong>Deprecations</strong></p>

<ul><li>Reptile.walk() is deprecated and will be removed in version 2.0, use slither()</li></ul></div>

Responsible creators use version numbers to express how a library has changed, so users can make informed decisions about upgrading. A "version scheme" is a language for communicating the pace of change.

<div style="text-align: center; font-weight: bold"><p>
Seventh Covenant:<br>Choose a Version Scheme
</p></div>

There are two schemes in widespread use, [semantic versioning](https://semver.org) and time-based versioning. I recommend semantic versioning for nearly any library. The Python flavor thereof is defined in [PEP 440](https://www.python.org/dev/peps/pep-0440/), and tools like "pip" understand semantic version numbers.

If you choose semantic versioning for your library, you can delete its legs gently with version numbers like:

> 1.0: First "stable" release, with walk()<br>
> 1.1: Add slither(), deprecate walk()<br>
> 2.0: Delete walk()

Your users should depend on a range of your library's versions like so:

```
# User's requirements.txt.
reptile>=1,<2
```

This allows them to upgrade automatically within a major release, receiving bugfixes and potentially raising some deprecation warnings, but not upgrading to the **next** major release and risking a change that breaks their code.

If you follow time-based version your releases might be numbered thus:

> 2017.06.0: A release in June 2017<br>
> 2018.11.0: Add slither(), deprecate walk()<br>
> 2019.04.0: Delete walk()

And users can depend on your library like:

```
# User's requirements.txt for time-based version.
reptile==2018.11.*
```

This is terrific, but how do your users know your versioning scheme and how to test their code for deprecations? You have to advise them how to upgrade.

<div style="text-align: center; font-weight: bold"><p>
Eighth Covenant:<br>Write an Upgrade Guide
</p></div>

Here's how a responsible library creator might guide users:

<div style="border: 1px solid black; padding: 0.5em; margin-bottom: 1em">
<p style="font-weight: bold; text-align: center">Upgrading to 2.0</p>

<p><strong>Migrate from Deprecated APIs</strong></p>

<p>See the <span style="color: blue; text-decoration: underline">changelog</span> for deprecated features.</p>

<p><strong>Enable Deprecation Warnings</strong></p>

<p>Upgrade to 1.1 and test your code with:</p>

<code>python -Werror::DeprecationWarning</code>
<br>
<br>
<p>Now it's safe to upgrade.</p></div>

You must teach users how to handle deprecation warnings by showing them the command line options. Not all Python programmers know this&mdash;I certainly have to look up the syntax each time. And take note, you must **release** a version that prints warnings from each deprecated API, so users can test with that version before upgrading again. In this example, version 1.1 is the bridge release. It allows your users to rewrite their code incrementally, fixing each deprecation warning separately until they have entirely migrated to the latest API. They can test changes to their code, and changes in your library, independently from each other, and isolate the cause of bugs.

If you chose semantic versioning, this transitional period lasts until the next major release, from 1.x to 2.0, or from 2.x to 3.0, and so on. The gentle way to delete a creature's legs is to give it at least one version in which to adjust its lifestyle. Don't remove the legs all at once!

![](skink.jpg)

Version numbers, deprecation warnings, the changelog, and the upgrade guide work together to gently evolve your library without breaking the covenant with your users. The [Twisted project's Compatibility Policy](https://twistedmatrix.com/documents/current/core/development/policy/compatibility-policy.html) explains this beautifully:

> "The First One's Always Free"
>
> Any application which runs without warnings may be upgraded one minor version of Twisted.
>
> In other words, any application which runs its tests without triggering any warnings from Twisted should be able to have its Twisted version upgraded at least once with no ill effects except the possible production of new warnings.

Now, we creator deities have gained the wisdom and power to add features by adding methods, and to delete them gently. We can also add features by adding parameters, but this brings a new level of difficulty. Are you ready?

# Adding Parameters

Imagine that you just gave your snake-like creature a pair of wings. Now you must allow it the choice whether to move by slithering or flying. Currently its "move" function takes one parameter:

```py3
# Your library code.
def move(direction):
    print(f'slither {direction}')

# A user's application.
move('north')
```

You want to add a "mode" parameter, but this breaks your users' code if they upgrade, because they pass only one argument:

{{< highlight py3 "hl_lines=7" >}}
# Your library code.
def move(direction, mode):
    assert mode in ('slither', 'fly')
    print(f'{mode} {direction}')

# A user's application. Error!
move('north')
{{< / highlight >}}

A truly wise creator promises not to break users' code this way.

<div style="text-align: center; font-weight: bold"><p>
Ninth Covenant:<br>Add Parameters Compatibly
</p></div>

To keep this covenant, add each new parameter with a default value that preserves the original behavior.

```py3
# Your library code.
def move(direction, mode='slither'):
    assert mode in ('slither', 'fly')
    print(f'{mode} {direction}')

# A user's application.
move('north')
```

Over time, parameters are the natural history of your function's evolution. They're listed oldest first, each with a default value. Library users can pass keyword arguments to opt in to specific new behaviors, and accept the defaults for all others.

```py3
# Your library code.
def move(direction,
         mode='slither',
         turbo=False,
         extra_sinuous=False,
         hail_lyft=False):
    # ...

# A user's application.
move('north', extra_sinuous=True)
```

There is a danger, however, that a user might write code like this:

```py3
# A user's application, poorly-written.
move('north', 'slither', False, True)
```

What happens if, in the next major version of your library, you get rid of one of the parameters, like "turbo"?

```py3
# Your library code, next major version. "turbo" is deleted.
def move(direction,
         mode='slither',
         extra_sinuous=False,
         hail_lyft=False):
    # ...


# A user's application, poorly-written.
move('north', 'slither', False, True)
```

The user's code still compiles, and this is a bad thing. The code stopped moving extra-sinuously and started hailing a Lyft, which was not the intention. I trust that you can predict what I'll say next: deleting a parameter requires several steps. First, of course, deprecate the "turbo" parameter. I like a technique like this one that detects whether any user's code is relying on this parameter:

```py3
# Your library code.
_turbo_default = object()

def move(direction,
         mode='slither',
         turbo=_turbo_default,
         extra_sinuous=False,
         hail_lyft=False):
    if turbo is not _turbo_default:
        warnings.warn(
            "'turbo' is deprecated",
            DeprecationWarning,
            stacklevel=2)
    else:
        # The old default.
        turbo = False
```

But your users might not notice the warning. Warnings are not very loud: they can be suppressed, or lost in log files. Users might heedlessly upgrade to the next major version of your library, the version that deletes "turbo". Their code will run without error and silently do the wrong thing! As the Zen of Python says, "Errors should never pass silently." Indeed, reptiles hear poorly, so you must correct them very loudly when they make mistakes.

![](loudly.jpg)

The best way to protect your users is with Python 3's star syntax, which requires callers to pass keyword arguments.

```py3
# Your library code.
# All arguments after "*" must be passed by keyword.
def move(direction,
         *,
         mode='slither',
         turbo=False,
         extra_sinuous=False,
         hail_lyft=False):
    # ...

# A user's application, poorly-written.
# Error! Can't use positional args, keyword args required.
move('north', 'slither', False, True)
```

With the star in place, this is the only syntax allowed:

```py3
# A user's application.
move('north', extra_sinuous=True)
```

Now when you delete "turbo", you can be certain any user code that relies on it will fail loudly. If your library also supports Python 2, there's no shame in that, you can simulate the star syntax thus ([credit to Brett Slatkin](http://www.informit.com/articles/article.aspx?p=2314818)):

```py3
# Your library code, Python 2 compatible.
def move(direction, **kwargs):
    mode = kwargs.pop('mode', 'slither')
    sinuous = kwargs.pop('extra_sinuous', False)
    lyft = kwargs.pop('hail_lyft', False)

    if kwargs:
        raise TypeError('Unexpected kwargs: %r'
                        % kwargs)

    # ...
```

Requiring keyword arguments is a wise choice, but it requires foresight. If you allow an argument to be passed positionally, you cannot convert it to keyword-only in a later release. So, add the star now. You can observe in the asyncio API that it uses the star pervasively in constructors, methods, and functions. Even though "Lock" only takes one optional parameter so far, the asyncio developers added the star right away. This is providential.

```py3
# In asyncio.
class Lock:
    def __init__(self, *, loop=None):
        # ...

```

Now we've gained the wisdom to change methods and parameters while keeping our covenant with users. The time has come to try the most challenging kind of evolution: changing behavior without changing either methods or parameters.

# Changing Behavior

Let's say your creature is a rattlesnake, and you want to teach it a new behavior.

![](rattlesnake.jpg)

Sidewinding! The creature's body will appear the same, but its behavior will change. How can we prepare it for this step of its evolution?

![](sidewinding.jpg)

A responsible creator can learn from the following example in the Python standard library, when behavior changed without a new function or parameters. Once upon a time, the os.stat function was introduced to get file statistics, like the creation time. At first, times were always integers.

```pycon
>>> os.stat('file.txt').st_ctime
1540817862
```

One day, the core developers decided to use floats for os.stat times, to give sub-second precision. But they worried that existing user code wasn't ready for the change.
They created a setting in Python 2.3, "stat_float_times", that was false by default. A user could set it to True to opt in to floating-point timestamps.

```pycon
>>> # Python 2.3.
>>> os.stat_float_times(True)
>>> os.stat('file.txt').st_ctime
1540817862.598021
```

Starting in Python 2.5, float times became the default, so any new code written for 2.5 and later could ignore the setting and expect floats. Of course, you could set it to False to keep the old behavior, or set it to True to ensure the new behavior in all Python versions, and prepare your code for the day when stat_float_times is deleted.

Ages passed. In Python 3.1 the setting was deprecated to prepare people for the distant future, and finally, after its decades-long journey, [the setting was removed](https://bugs.python.org/issue31827). Float times are now the only option. It's a long road, but responsible deities are patient because we know this gradual process has a good chance of saving users from unexpected behavior changes.

<div style="text-align: center; font-weight: bold"><p>
Tenth Covenant:<br>Change Behavior Gradually
</p></div>

Here are the steps:

* Add a flag to opt in to the new behavior, default False, warn if it's False<br>
* Change default to True, deprecate flag entirely<br>
* Remove the flag

If you follow semantic versioning, the versions might be like so:

<style>
.versions-table td, th {
   padding: 1em;
}
</style>

<table style="width: 100%; font-size: large" class="versions-table" rules="rows">
<thead>
<tr>
<th style="text-align: center">Library version</th><th style="text-align: center">Library API</th><th style="text-align: center">User code</th>
</tr>
</thead>
<tbody>
<tr>
<tr><td>1.0</td><td>No flag</td><td>Expect old behavior</td>
<tr><td>1.1</td><td>Add flag, default False,<br>
warn if it's False </td><td>Set flag True,<br>
handle new behavior</td></tr>
<tr><td>2.0</td><td>Change default to True,<br>
deprecate flag entirely</td><td>Handle new behavior</td></tr>
<tr><td>3.0</td><td>Remove flag</td><td>Handle new behavior</td></tr>
</table>

You need **two** major releases to complete the maneuver. If you had gone straight from "Add flag, default False, warn if it's False" to "Remove flag" without the intervening release, your users' code would be unable to upgrade. User code written correctly for 1.1, which sets the flag to True and handles the new behavior, must be able to upgrade to the next release with no ill effect except new warnings, but if the flag were deleted in the next release that code would break. A responsible deity never violates the Twisted policy: "The First One's Always Free."

# The Responsible Creator

![](demeter.jpg)

Our ten covenants belong loosely in three categories:

### Evolve Cautiously

1. Avoid Bad Features
2. Minimize Features
3. Keep Features Narrow
4. Mark Experimental Features "Provisional"
5. Delete Features Gently

### Record History Rigorously

6. Maintain a Changelog
7. Choose a Version Scheme
8. Write an Upgrade Guide

### Change Slowly and Loudly

9. Add Parameters Compatibly
10. Change Behavior Gradually

If you keep these covenants with your creature, you'll be a responsible creator deity. Your creature's body can evolve over time, forever improving and adapting to changes in its environment, but without sudden changes the creature isn't prepared for. If you maintain a library, keep these promises to your users, and you can innovate your library without breaking the code of the people who rely on you.

***

Illustrations:

* [The World's Progress, The Delphian Society, 1913](https://www.gutenberg.org/files/42224/42224-h/42224-h.htm)
* [Essay Towards a Natural History of Serpents, Charles Owen, 1742](https://publicdomainreview.org/product-att/artist/charles-owen/)
* [On the batrachia and reptilia of Costa Rica: With notes on the herpetology and ichthyology of Nicaragua and Peru, Edward Drinker Cope, 1875](https://archive.org/details/onbatrachiarepti00cope/page/n3)
* [Natural History, Richard Lydekker et. al., 1897](https://www.flickr.com/photos/internetarchivebookimages/20556001490)
* [Mes Prisons, Silvio Pellico, 1843](https://www.oldbookillustrations.com/illustrations/stationery/)
* [Tierfotoagentur / m.blue-shadow](https://www.alamy.com/mediacomp/ImageDetails.aspx?ref=D7Y61W)
* [From Los Angeles Public Library, 1930](https://www.vintag.es/2013/06/riding-alligator-c-1930s.html)
