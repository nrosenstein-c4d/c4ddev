# `nr.parse`

&ndash; A simple text scanning/lexing/parsing library.

# API Documentation

Generated with [Pydoc-Markdown](https://github.com/NiklasRosenstein/pydoc-markdown).

__Table of Contents__

* [nr.parse](#py-nr.parse)
    * [Classes](#py-classes)

<h1 id="py-nr.parse"><small>module</small> nr.parse</h1>


This is a simple library to tokenize and parse languages ranging from simple
to complex grammatics and semantics. It has been developed specifically for
the recursive decent parser technique, although it might work well with other
parsing techniques as well.

The most basic class is the 
`Scanner` which is a simple wrapper for a string
that counts line and column numbers as it allows you to step through every
character in that string. The 
`Scanner` is sufficient in many simple parsing
tasks.

Next up is the 
`Lexer` which converts characters yielded by the 
`Scanner` into a
stream of 
`Token`#s using a set of 
`Rule`#s.


<h2 id="py-classes">Classes</h2>

<h3 id="py-nr.parse.Scanner"><small>class</small> Scanner</h3>

```python
Scanner(self, text)
```

This class is used to step through text character by character and keep track
of the line and column numbers of each passed character. The Scanner will
only tread line-feed as a newline.

__Parameters__

- __text (str)__: The text to parse. Must be a `str` in Python 3 and may also be
  a `unicode` object in Python 2.

__Attributes__


- `text (str)`: The *text* passed to the constructor.
- `index (int)`: The cursor position in the text.
- `lineno (int)`: The line-number of the cursor in the text.
- `colno (int)`: The column-number of the cursor in the text.
- `cursor (Cursor)`: The combination of 
`index`, 
`lineno` and 
`colno`.
- `char (str)`: The current character at the Scanner's position. Is
  an empty string at the end of the 
`text`.


<h4 id="py-nr.parse.Scanner.seek"><small>function</small> seek()</h4>

```python
Scanner.seek(self, offset, mode='set', renew=False)
```

Moves the cursor of the Scanner to or by *offset* depending on the *mode*.
Is is similar to a file's `seek()` function, however the *mode* parameter
also accepts the string-mode values `'set'`, `'cur'` and `'end'`.

Note that even for the `'end'` mode, the *offset* must be negative to
actually reach back up from the end of the file.

If *renew* is set to True, the line and column counting will always begin
from the start of the file. Keep in mind that this could can be very slow
because it has to go through each and every character until the desired
position is reached.

Otherwise, if *renew* is set to False, it will be decided if counting from
the start is shorter than counting from the current cursor position.


<h4 id="py-nr.parse.Scanner.next"><small>function</small> next()</h4>

```python
Scanner.next(self)
```
Move on to the next character in the text.

<h4 id="py-nr.parse.Scanner.readline"><small>function</small> readline()</h4>

```python
Scanner.readline(self)
```
Reads a full line from the scanner and returns it.

<h4 id="py-nr.parse.Scanner.match"><small>function</small> match()</h4>

```python
Scanner.match(self, regex, flags=0)
```

Matches the specified *regex* from the current character of the *scanner*
and returns the result. The Scanners column and line numbers are updated
respectively.

__Arguments__

- __regex (str, Pattern)__: The regex to match.
- __flags (int)__: The flags to use when compiling the pattern.


<h4 id="py-nr.parse.Scanner.getmatch"><small>function</small> getmatch()</h4>

```python
Scanner.getmatch(self, regex, group=0, flags=0)
```

The same as 
`Scanner.match()`, but returns the captured group rather than
the regex match object, or None if the pattern didn't match.


<h4 id="py-nr.parse.Scanner.restore"><small>function</small> restore()</h4>

```python
Scanner.restore(self, cursor)
```
Moves the scanner back (or forward) to the specified cursor location.

<h3 id="py-nr.parse.Lexer"><small>class</small> Lexer</h3>

```python
Lexer(self, scanner, rules=None)
```

This class is used to split text into 
`Token`#s using a 
`Scanner` and a list
of 
`Rule`#s.

__Parameters__

- __scanner (Scanner)__: The scanner to read from.
- __rules (list of Rule)__: A list of rules to match. The order in the list
  determines the order in which the rules are matched.

__Attributes__

- `scanner (Scanner)`:
- `rules (list of Rule)`:
- `rules_map (dict of (object, Rule))`:
  A dictionary mapping the rule name to the rule object. This is
  automatically built when the Lexer is created. If the 
`rules`
  are updated in the lexer directly, 
`update()` must be called.
- `skippable_rules (list of Rule)`:
  A list of skippable rules built from the 
`rules` list. 
`update()` must be
  called if any of the rules or the list of rules are modified.
- `token (Token)`:
  The current token. After the Lexer is created and 
`next()` method has NOT
  been called, the value of this attribute is 
`None`. At the end of the input,
  the token is type 
`eof`.


<h4 id="py-nr.parse.Lexer.update"><small>function</small> update()</h4>

```python
Lexer.update(self)
```

Updates the 
`rules_map` dictionary and 
`skippable_rules` list based on the

`rules` list. Must be called after 
`rules` or any of its items have been
modified. The same rule name may appear multiple times.

__Raises__

- `TypeError`: if an item in the `rules` list is not a rule.


<h4 id="py-nr.parse.Lexer.expect"><small>function</small> expect()</h4>

```python
Lexer.expect(self, *names)
```

Checks if the current 
`token`#s type name matches with any of the specified
*names*. This is useful for asserting multiple valid token types at a
specific point in the parsing process.

__Arguments__

- __names (str)__: One or more token type names. If zero are passed,
  nothing happens.

__Raises__

- `UnexpectedTokenError`: If the current 
`token`#s type name does not match
  with any of the specified *names*.


<h4 id="py-nr.parse.Lexer.accept"><small>function</small> accept()</h4>

```python
Lexer.accept(self, *names, **kwargs)
```

Extracts a token of one of the specified rule names and doesn't error if
unsuccessful. Skippable tokens might still be skipped by this method.

__Arguments__

- __names (str)__: One or more token names that are accepted.
- __kwargs__: Additional keyword arguments for 
`next()`.

__Raises__

- `ValueError`: if a rule with the specified name doesn't exist.


<h4 id="py-nr.parse.Lexer.next"><small>function</small> next()</h4>

```python
Lexer.next(self, *expectation, **kwargs)
```

Parses the next token from the input and returns it. The new token can be
accessed from the 
`token` attribute after the method was called.

If one or more arguments are specified, they must be rule names that are to
be expected at the current position. They will be attempted to be matched
first (in the specicied order). If the expectation could not be met, an

`UnexpectedTokenError` is raised.

An expected Token will not be skipped, even if its rule defines it so.

__Arguments__

- __expectation (str)__: The name of one or more rules that are expected from the
  current position of the parser. If empty, the first matching token of ALL
  rules will be returned. In this case, skippable tokens will be skipped.
- __as_accept (bool)__: If passed True, this method behaves the same as the
  
`accept()` method. The default value is 
`False`.
- __weighted (bool)__: If passed True, the tokens specified with *expectations*
  are checked first, effectively giving them a higher priority than other
  they would have from the order in the 
`rules` list. The default value is
  
`False`.

__Raises__

- `ValueError`: if an expectation doesn't match with a rule name.
- `UnexpectedTokenError`: Ff an expectation is given and the expectation
  wasn't fulfilled. Only when *as_accept* is set to 
`False`.
- `TokenizationError`: if a token could not be generated from the current
  position of the Scanner.


<h3 id="py-nr.parse.Rule"><small>class</small> Rule</h3>

```python
Rule(self, name, skip=False)
```

Base class for rule objects that are capable of extracting a 
`Token` from
the current position of a 
`Scanner`.

__Attributes__

- `name (str)`: The name of the rule. This name must be passed to the
  
`Token.type` member when 
`tokenize()` returns a valid token.
- `skip (bool)`: If 
`True`, the rule is treated as a skippable rule. If the
  rule is encountered in the 
`Lexer` and matched, the generated token will
  be discarded entirely.


<h4 id="py-nr.parse.Rule.tokenize"><small>function</small> tokenize()</h4>

```python
Rule.tokenize(self, scanner)
```

Attempt to extract a token from the position of the *scanner* and return it.
If a non-#Token instance is returned, it will be used as the tokens value.
Any value that evaluates to 
`False` will make the Lexer assume that the rule
couldn't capture a Token.

The 
`Token.value` must not necessarily be a string though, it can be any data
type or even a complex datatype, only the user must know about it and handle
the token in a special manner.


<h3 id="py-nr.parse.Regex"><small>class</small> Regex</h3>

```python
Regex(self, name, regex, flags=0, skip=False)
```

A rule to match a regular expression. The 
`Token` generated by this rule
contains the match object as its value, not a plain string.

__Attributes__

- `regex (Pattern)`: A compiled regular expression.


<h3 id="py-nr.parse.Keyword"><small>class</small> Keyword</h3>

```python
Keyword(self, name, string, case_sensitive=True, skip=False)
```

This rule matches an exact string (optionally case insensitive)
from the scanners current position.

__Attributes__

- `string (str)`: The keyword string to match.
- `case_sensitive (bool)`: Whether matching is case-senstive or not.


<h3 id="py-nr.parse.Charset"><small>class</small> Charset</h3>

```python
Charset(self, name, charset, at_column=-1, skip=False)
```

This rule consumes all characters of a given set and returns all characters
it consumes.

__Attributes__

- `charset (frozenset of str)`: A set of characters to consume.
- `at_column (int)`: Match the charset only at a specific column index in
  the input text. This is useful to create a separate indentation token type
  apart from the typical whitespace token. Defaults to #-1.


<h3 id="py-nr.parse.TokenizationError"><small>class</small> TokenizationError</h3>

```python
TokenizationError(self, token)
```

This exception is raised if the stream can not be tokenized at a given
position. The `Token` object that an object is initialized with is an invalid
token with the cursor position and current scanner character as its value.


<h3 id="py-nr.parse.UnexpectedTokenError"><small>class</small> UnexpectedTokenError</h3>

```python
UnexpectedTokenError(self, expectation, token)
```

This exception is raised when the 
`Lexer.next()` method was given one or more
expected token types but the extracted token didn't match the expected types.


---

<p align="center">Copyright &copy; 2018 Niklas Rosenstein</p>
