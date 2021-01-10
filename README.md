# Random String Generator

This is a string generator that takes a regular expression as argument and returns
strings that match the given regular expression.

The generator supports the following features:

- `[` Start of the character class definition
- `]` End of the character class definition
- `?` 0 or 1 quantifier
- `*` 0 or more quantifier
- `+` 1 or more quantifier
- `{` Start min/max quantifier
- `}` End min/max quantifier
- `|` Start of an alternative branch
- `(` Start subpattern
- `)` End subpattern

Within a character class, the following subpatterns are supported:
`^` Negate the class, but only if the first character
`-` indicates character range

In order to use it, just import generate function from regex_to_string module
using the following instruction:
> from regex_to_string import generate

The generate function takes 2 arguments. The first argument is the regular expression
template and the other is the number of unique string we want to generate.

Some examples:

> generate('/[-+]?[0-9]{1,16}[.][0-9]{1,6}/', 10)

```
7223329.250639
-0905733704286648.1
875.4
+868.16
4134.559
6922348437950086.1781
59558.2623
-08739804757328.9139
316759710853.75668
-440148344686.47493
```

> 'generate('/(1[0-2])|(0[1-9])(:[0-5][0-9]){2} (A|P)M/', 10)

```
12:12:02 PM
12:26:44 AM
11:49:15 AM
03:50:28 AM
10:53:27 AM
09:02:29 AM
09:12:31 AM
02:04:10 PM
05:37:02 PM
11:26:02 PM
```

# Implementation Details
We have a class called StringGenerator. This class has an abstract class called Node
which is inherited by the Literal and CharacterSet classes. Each of these classes
implement a method called render. For Literal class, its just simple, return
the literal. For the characterSet class, we render a random combination from the
set of specified characters.

We have another class called Sequence which just contains a list of node objects and
renders them.

We create an object of the StringGenerator class and initialize it with the regular
expression template. We parse the template and form a sequence of nodes and then render
each Node from the sequence.
