+++
title = "Plugins"
+++

## C4D IDE

Also a very old plugin that is not very progressed and also currently provides
two different approaches to implementing a Python IDE in Cinema 4D.

![C4D-IDE 01](c4dide-01.png)
![C4D-IDE 02](c4dide-02.png)

## PyObject

An alternative to the Cinema 4D standard Python Generator object that allows
you to implement a number of other `ObjectData` methods.

![PyObject Screenshot](pyobject.png)

## PyShader

This simple Cinema 4D plugin allows you to write shaders on-the-fly or
prototype for a native shader plugin.

![PyShader Screenshot](pyshader.png)

## Unicode Escape Tool

String resources require special characters to be escaped with unicode
escape sequences in the format of `\UXXXX`. The "Unicode Escape Tool"
can handle this for you. Just enter or paste the stringtable or text
and you can convert it.

![Unicode Escape Tool Screenshot](uescapetool.png)

!!! note "Resource Packages"
    You don't need this tool if you make use of [ResourcePackages](../cli#c4ddev-rpkg).
    Non-ascii characters will be escaped automatically when a stringtable
    is generated from the ResourcePackage.

## Scripting Server

See [Scripting](scripting)
