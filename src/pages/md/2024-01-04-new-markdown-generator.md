---
title: "Generating posts using markdown"
excerpt: "Custom Markdown parser and HTML generator using Grotsky, my toy programming language that powers this blog. Up until now I've used a hacky HTML generator that relies on lists. Now Im integrating a simple MD parser that makes easier to write new articles."
author: "Miguel Liezun"
tags: advent-of-code, programming, solution, 2023, day-20
---


# Hello

[Im here.](https://google.com)
Also here.

Second paragraph.

### Code block check

```python
from functools import reduce

reduce(lambda a, b: b**a%(2**20-1), range(1, 10))
```

##### Unordered list

- abc
- hello: here
- based: there
