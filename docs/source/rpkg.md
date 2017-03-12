# Resource Packages

Resource packages allow you to more efficiently manage plugin resource files
and translations by merging all information into a single file. Resource
packages have the `.rpkg` suffix and are converted to real Cinema 4D resource
files by using the [`c4ddev rpkg`](cli#rpkg) command.

    ResourcePackage(Ocube)  # Mandatory, (XXX) part is optional
    Ocube: 5405
      us: Cube
      de: Würfel
    # Save ourselves some writing.
    SetPrefix(PRIM_CUBE_)
    # Basic Attributes
    LENGTH: 1001
      us: Size
      de: Größe
    SEGMENTS: 1002
      us: Segments
      de: Segmente
    SetPrefix()
    # A symbol without ID is placed only into the Stringtable, except for
    # the c4d_symbols, where the ID is automatically incremented starting
    # from 10000.
    DEBUGSECTION:
      us: Debug Section
      de: Debug Bereich
    # More symbols to follow ...

A file called `c4d_symbols.rpkg` will be handled special and generate the respective
`c4d_symbols.h` and `c4d_strings.str` files.

    $ c4ddev.py rpkg res/c4d_symbols.rpkg res/Ocube.rpkg
    Writing c4d_symbols.h ...
    Writing strings_de/c4d_strings.str ...
    Writing strings_us/c4d_strings.str ...
    Writing description/Ocube.h ...
    Writing strings_de/description/Ocube.str ...
    Writing strings_us/description/Ocube.str ...

### `.rpkg` Format Information

* The `ResourcePackage` line is mandatory and must be the first line in the file
* Comments begin with a number sign (`#`) and continue until the end of the line
* Assigning a fixed ID number to a symbol is mandatory
* Special characters in the localization are allowed (use `\n` for a newline and `\t` for a tab)
* If the file is named `c4d_symbols.rpkg`, it will automatically be created in the res folder
  directly instead of the descriptions folder
