+++
type = "post"
title = "API Evolution the Right Way"
description = ""
category = []
tag = []
draft = true
enable_lightbox = false
+++

![](dragon.png)

![](praise-the-creator.png)

![](paul-archibald-octave-caron-woman-at-her-easel.png)

```py3
class Reptile:
    @property
    def teeth(self):
        return 'sharp fangs'

    @property
    def wings(self):
        return 'majestic wings'
```

```py3
# Python 2.
bool(datetime.time(9, 30)) == True
bool(datetime.time(0, 0)) == False
```

```py3
def create_event(day,
                 start_time=None,
                 end_time=None):
    if end_time and not start_time:
        raise ValueError(
            "Can't pass end_time"
            " without start_time")

# The coven meets from midnight until 4am.
create_event(datetime.date.today(),
             datetime.time(0, 0),
             datetime.time(4, 0))
```

```py3
def create_event(day,
                 start_time=None,
                 end_time=None):
    if end_time is not None and start_time is None:
        raise ValueError(
            "Can't pass end_time"
            " without start_time")
```

![](bite.jpg)

```py3
# Python 3.
bool(datetime.time(9, 30)) == True
bool(datetime.time(0, 0)) == True
```

Avoid bad features.

![](feathers.png)

Minimize features.

> Features are like children: conceived in a moment of passion, they must be supported for years.

```py3
async def my_coroutine():
    pass

print(my_coroutine())
```

{{< highlight text "prestyles=background-color: black; color: lightgreen !important; padding: 1em 0.5em" >}}
&lt;coroutine object my_coroutine at 0x10bfcbac8&gt;
{{< / highlight >}}

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

> ``sys.set_coroutine_wrapper`` was added to solve a specific problem: asyncio debug mode wanting to track where coroutine objects are created, so that when unawaited coroutines are GC'ed, the warning they print can include a traceback."
>
> &mdash; Nathaniel Smith

![](horns.png)
