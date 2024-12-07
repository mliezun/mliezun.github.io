---
title: "One Liners"
excerpt: "Writing common introductory algorithms in Python in one line. Experimenting with the capabilities of Python to be an expressive and concise language. We'll later explore if writing
code this way actually makes sense or not."
author: "Miguel Liezun"
tags: programming,python,code,algorithms
---


# One Liners

Writing common introductory algorithms in Python in one line. Experimenting with the capabilities of Python to be an expressive and concise language. We'll later explore if writing
code this way actually makes sense or not.

## Iterative fibonacci

```python
fib = lambda n: ((a:=0, b:=1, aux:=0), [(aux:=b, b:=a+b, a:=aux) for i in range(n)])[-1][-1][0]
```

Thanks to the walrus operator we can define new local variables in an expression. This is much more inefficient in terms of memory that the good old imperative one because it stores every intermediate result in a list just to use the last value in the end.

## Recursive fibonacci

```python
fib = lambda n: n if n &lt; 2 else fib(n-1)+fib(n-2)
```

This is quite clean IMO, but either way recursive fibonacci is very wasteful because it uses 2**n function calls when not memoized.
