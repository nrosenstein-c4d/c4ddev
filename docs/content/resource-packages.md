+++
title = "Resource Packages"
+++

Resource packages allow you to more efficiently manage plugin resource files
and translations by merging all information into a single file. Resource
packages have the `.rpkg` suffix and are converted to real Cinema 4D resource
files by using the [`c4ddev rpkg`](cli#rpkg) command.

## Example

    # Must be the first statement in a .rpkg file. The (XXX) part is optional.
    ResourcePackage(Ocube)

    # It is common to assign the actual Plugin ID already in the description
    # resource header file, so people can just include the header and also have
    # the plugin ID available. In our description, we also use it as the object
    # name (i.e. `NAME Ocube;` ).
    Ocube: 5405
      us: Cube
      de: Würfel

    # We can save ourselves some writing by using SetPrefix().
    SetPrefix(PRIM_CUBE_)

    LENGTH: 1001
      us: Size
      de: Größe
    SEGMENTS: 1002
      us: Segments
      de: Segmente

    # Unset the prefix.
    SetPrefix()

    # A symbol without ID is placed only into the Stringtable, except for
    # the c4d_symbols, where the ID is automatically incremented starting
    # from 10000.
    DEBUGSECTION:
      us: Debug Section
      de: Debug Bereich

A file called `c4d_symbols.rpkg` will be handled special and generate the respective
`c4d_symbols.h` and `c4d_strings.str` files.

    $ c4ddev rpkg res/c4d_symbols.rpkg res/Ocube.rpkg
    Writing c4d_symbols.h ...
    Writing strings_de/c4d_strings.str ...
    Writing strings_us/c4d_strings.str ...
    Writing description/Ocube.h ...
    Writing strings_de/description/Ocube.str ...
    Writing strings_us/description/Ocube.str ...

## Syntax & Behaviour

* The `ResourcePackage` line is mandatory and must be the first line in the file
* Comments begin with a number sign (`#`) and continue until the end of the line
* Assigning a fixed ID number to a symbol is mandatory
* Special characters in the localization are allowed (use `\n` for a newline and `\t` for a tab)
* If the file is named `c4d_symbols.rpkg`, it will automatically be created in the res folder
  directly instead of the descriptions folder

