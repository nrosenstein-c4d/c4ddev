# The `c4ddev` API

The **c4ddev** API provides some utilities that are especially useful for
scripting and prototyping in Cinema 4D. All contents of the `c4ddev` library
must be loaded with the `require` module (which is delivered with **c4ddev**,
see the [Contents](contents) page for more information).

```python
import require
localimport = require('c4ddev/scripting/localimport')
# This is a version of localimport that is tuned to work from inside any
# scripting context in Cinema 4D (Tag, Object, XPresso Node).

with localimport(doc):
  import twitter

def main():
  # TODO: Some clever example
```

## Namespaces

- `c4ddev`
- `c4ddev/pypkg`
- `c4ddev/resource`
- `c4ddev/scripting/localimport` -- localimport tuned for Cinema 4D scripting
- `c4ddev/utils` -- utilities that are used by the c4ddev extensions (in `ext/`)
