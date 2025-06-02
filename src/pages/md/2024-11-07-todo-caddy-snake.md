---
title: "Caddy Snake improvements"
excerpt: "I've been planning on improving Caddy Snake, making it more stable and easier to use. Right now, I want to add automatic test for Django, and build binaries and Docker images for arm64 and riscv64. I'd also like to turn it into a Python package so you can plug it straight into your code."
author: "Miguel Liezun"
tags: programming,python,code,algorithms
---

# Caddy Snake improvements

I've been planning on improving Caddy Snake, making it more stable and easier to use. Right now, I want to add automatic test for Django, and build binaries and Docker images for arm64 and riscv64. I'd also like to turn it into a Python package so you can plug it straight into your code.

## Fix/add/test support for Django

I've tried to use it a couple times just to test that it works and seems to have been broken. I'd like to test it a little bit more to make sure it works and solve all the bugs.

Also add an automatic test so that I'm sure it doesn't break after I make some changes.

## Make sure we don't get segfaults on tests anymore

Sometimes I get random segfaults when tests run on CI. I'd like to take time to investigate this and fix the issues.

## Add support for arm64 and riscv64

For now I'm only building caddy-snake for Linux x86_64. It would be cool to distribute more binaries for different OSes and CPU architectures.

For example:

- linux / x86_64 / arm64 / riscv64

- macOS / x86_64 / arm64

- windows / x86_64 / arm64

Also deliver docker images for all of those.


## Expose as python package that can be used directly

```python
import caddysnake

from flask import Flask

app = Flask(__name__)

@app.route("/hello")
def hello():
 return "Hello world"
 
if __name__ == "__main__":
    caddysnake.run(app=app, host="localhost:8082")
```

## Better performance and isolation

Complete the work of integrating subinterpreters in caddy-snake.

[https://github.com/mliezun/caddy-snake/pull/9](https://github.com/mliezun/caddy-snake/pull/9)

Track performance compared to other web servers and improve it.

