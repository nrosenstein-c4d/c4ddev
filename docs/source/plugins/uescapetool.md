String resources require special characters to be escaped with unicode
escape sequences in the format of `\UXXXX`. The "Unicode Escape Tool"
can handle this for you. Just enter or paste the stringtable or text
and you can convert it.

![Unicode Escape Tool Screenshot](https://i.imgur.com/Phon0PT.png)

!!!info "Resource Packages"
    You don't need this tool if you make use of [ResourcePackages](../cli/rpkg).
    Non-ascii characters will be escaped automatically when a stringtable
    is generated from the ResourcePackage.