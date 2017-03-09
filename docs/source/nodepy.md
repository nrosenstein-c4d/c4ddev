[Node.py] is an isolated environment with a new way to load other Python
modules using a `require()` function. It already makes use of the
[`localimport`](localimport) technique, which allows you to still use standard
third party Python modules.

C4DDev provides a script that can build a loader plugin that encapsulates a
Node.py standalone version. To create such a loader, first install Node.py,
which will also give you access to [PPYM], its package manager. Then, instal
C4DDev via PPYM globally to get access to its command-line. The last step is
to generate the loader plugin.

    $ pip install node.py
    $ ppym install @niklas/c4ddev --global
    $ c4ddev build-loader

In fact, C4DDev uses this mechanism itself for its plugins and features.
