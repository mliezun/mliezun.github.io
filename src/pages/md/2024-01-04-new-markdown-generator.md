---
title: "Generating posts using markdown"
excerpt: "Custom Markdown parser and HTML generator using Grotsky, my toy programming language that powers this blog. Up until now I've used a hacky HTML generator that relies on lists. Now Im integrating a simple MD parser that makes easier to write new articles."
author: "Miguel Liezun"
tags: markdown,parser,blog
---


# Generating posts using markdown

This is pretty standard for Github pages. But in this case, the parser has been written by me. It takes some subset of markdown and compiles it to HTML.

Only what you see in this post is what's supported.

## Code blocks

Standard code block:

```
Hello, this is a code block!
```

Syntax highlighting:

```python
from functools import reduce, partial
import operator

mul = partial(reduce, operator.mul)
print("Factorial of 5:", mul(range(1, 6)))
```

## Unordered list

- This
- is an
- unordered list

## Bolds, Italics and Inline code

Some text can be **bolded**, while some other can be in *Italics*.

But the best is to have `print("inline code")`.

## Links and images

[Link to the blog source code where you can see how the parser works (tldr: is awful).](https://github.com/mliezun/mliezun.github.io/blob/master/src/parse_md.gr)

Picture of NYC:

![Picture of NYC](/assets/images/nyc.jpg "Picture of NYC")

# HEADINGS

There's a thing you haven't noticed so far. There's support for different kinds of headings. You can see them in increasing order here:

###### Microscopic

##### Small

#### Good

### Pretty good

## Big

# Good bye!

Thanks for checking out the blog. I've done this to reduce the complexity of creating new blogposts. It was a headache before.

Hopefully now I'll write more. Stay tuned.

