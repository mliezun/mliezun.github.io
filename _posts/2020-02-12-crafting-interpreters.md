---
layout: post
title: "Crafting interpreters"
excerpt: "Lox language interpreter based on the book craftinginterpreters.com by Bob Nystrom."
author: "Miguel Liezun"
tags: interpreter,parser,lexer
---

# Crafting interpreters

I've just finished the section 2 of the book _Crafting Interpreters_, and I wanted to upload it to github right away.

Take a look at the [source code](https://github.com/mliezun/jlox).

Beside the lox specification I've added:

- The keyword `until` that is a variation of `while` loops (as in ruby). also
- `print` is a function instead of a statement.
- `eval` function that let's you eval source code in runtime.
- Class methods.

I'll implement another language interpreter, this time using `golang` and with a syntax similar to ruby.
