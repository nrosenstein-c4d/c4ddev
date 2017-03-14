    Usage: c4ddev symbols [OPTIONS]

    Options:
      -f, --format FORMAT      The output format, one of {class,file,json}.
                               Defaults to class.
      -o, --outfile FILENAME
      -d, --res-dir DIRECTORY  One or more resource directories to parse for
                               symbols. If the option is not specified, `res/`
                               will be used.
      --help                   Show this message and exit.

Extracts the resource symbols from all header files in `res/` directory or the
directory/ies specified via `-d,--res-dir` and formats them as a Python class,
Python file or JSON.

```
$ pwd
/Users/niklas/Applications/Cinema 4D R18/plugins/myplugin
$ c4ddev symbols

exec ("""class res(object):
 # Automatically generated with c4ddev v1.3.
 project_path = os.path.dirname(__file__)
 def string(self, name, *subst):
  result = __res__.LoadString(getattr(self, name))
  for item in subst: result = result.replace('#', item, 1)
  return result
 def tup(self, name, *subst):
  return (getattr(self, name), self.string(name, *subst))
 def path(self, *parts):
  path = os.path.join(*parts)
  if not os.path.isabs(path):
   path = os.path.join(self.project_path, path)
  return path
 file = path  # backwards compatibility
 def bitmap(self, *parts):
  b = c4d.bitmaps.BaseBitmap()
  if b.InitWith(self.path(*parts))[0] != c4d.IMAGERESULT_OK: return None
  return b
 MYSYMBOL = 1000
 MYOTHERSYMBOLS = 1001
 res=res()""")
```

__Available Formats__

  - Python class (`class`) [default] -- Can be copied into the Python plugin source
  - Python file (`file`)  -- Can be loaded as a module (make use of [`localimport`](localimport))
  - JSON (`json`) -- Can be loaded using the `json` module
