import io
import os
import re
import sys

from setuptools import setup


def restify():
  if os.path.isfile('README.md'):
    if os.system('pandoc -s README.md -o README.rst') != 0:
      print('----------------------------------------------------------')
      print('WARNING: pandoc command failed, could not restify README.md')
      print('----------------------------------------------------------')
      if sys.stdout.isatty():
        if sys.version_info[0] >= 3:
          input("Enter to continue... ")
        else:
          raw_input("Enter to continue... ")
    else:
      with io.open('README.rst', encoding='utf8') as fp:
        text = fp.read()
      # Remove ".. raw:: html\n\n    ....\n" stuff, it results from using
      # raw HTML in Markdown but can not be properly rendered in PyPI.
      text = re.sub('..\s*raw::\s*html\s*\n\s*\n\s+[^\n]+\n', '', text, re.M)
      with io.open('README.rst', 'w', encoding='utf8') as fp:
        fp.write(text)
      return text


setup(
  name="localimport",
  version="1.7.3",
  description="Isolated import of Python Modules",
  long_description=restify(),
  author="Niklas Rosenstein",
  author_email="rosensteinniklas@gmail.com",
  url='https://github.com/NiklasRosenstein/localimport',
  py_modules=["localimport"],
  keywords=["import", "embedded", "modules", "packages"],
  classifiers=[
    'Development Status :: 5 - Production/Stable',
    'Environment :: Other Environment', 'Environment :: Plugins',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: Implementation :: CPython',
    'Programming Language :: Python :: Implementation :: Jython',
    'Programming Language :: Python :: Implementation :: PyPy',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Topic :: Utilities'
  ])
