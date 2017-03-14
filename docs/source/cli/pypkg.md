    Usage: c4ddev pypkg [OPTIONS] [CONFIG]

    Options:
      --help  Show this message and exit.

The **pypkg** command compiles Python modules and packages into `.pyc` files
and merges them into a Python Egg archive or directory. This is useful to
protect your Python code and to distribute your Python plugin.

!!!note
    Keep in mind that you should always use [`localimport`](localimport)
    to import any third-party Python modules from a Cinema 4D plugin in
    order to keep the global importer state clean.

__Example Configuration__ (`.pypkg`)

This is a real-world example configuration file.

```json
{
  "zipped": true,
  "output": "res/modules{target}/mylibs.egg",
  "include": [
    "devel/res.py",
    "../vendor/python/c4dtools/c4dtools",
    "../vendor/python/nr/nr"
  ]
}
```
