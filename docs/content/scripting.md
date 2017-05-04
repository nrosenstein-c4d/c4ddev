+++
title = "Scripting"
+++

The **C4DDev** API provides some utilities that are especially useful for
scripting and prototyping in Cinema 4D. All contents of the `c4ddev` library
must be loaded with the `c4ddev.require()` function (which is the `require()`
function from the `c4ddev/main` module, exported by Node.py).

```python
from c4ddev import require
localimport = require('c4ddev/scripting/localimport')
# This is a version of localimport that is tuned to work from inside any
# scripting context in Cinema 4D (Tag, Object, XPresso Node).

with localimport(doc):
  import twitter

def main():
  # TODO: Some clever example
```

This is extremely useful when using third party libraries in scripts or
Python Objects/Tags. You can keep the dependencies together with your
Cinema 4D scene file and only make sure that **C4DDev** is installed if
you move the scene around.
