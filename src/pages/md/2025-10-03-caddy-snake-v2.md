---
title: "Serving Python apps using the Caddy web server"
excerpt: "Caddy is an enterprise grade web server and reverse proxy. I recently released a new version of `caddysnake` a plugin to serve python apps more easily using Caddy without the need of installing another server like gunicorn, uvicorn, hypercorn or others."
author: "Miguel Liezun"
tags: go,python,web,server,wsgi,asgi
image: /assets/images/OIP-3356949409.jpg
---


# Serving Python apps using Caddy web server

Caddy is an enterprise grade web server and reverse proxy. I recently released a new version of `caddysnake` a plugin to serve python apps more easily using Caddy without the need of installing another server like gunicorn, uvicorn, hypercorn or others.

![Stock image of a server](/assets/images/OIP-3356949409.jpg)

In this latest release there are some new features to explore:

- Distribution of a single caddy binary with bundled python.
- Added `python-server` subcommand.
- Multiple worker process.
- Package in PyPI available for a quick way to install: `caddysnake`.

## Distribution of single binary

The latest release is [available on github](https://github.com/mliezun/caddy-snake/releases).

Now you can see for example `caddy-standalone-3.10-x86_64_v2-unknown-linux-gnu.zip` as an available asset to download.

After downloading and unzipping you get a single binary named `caddy`. This packages an entire Python distribution inside so you now don't have the need to install it on the target system.

This would be useful for docker images since now you don't have to install the correct python version, just include the caddy binary and that carries along all of its dependencies.


## Python server subcommand

With the new release you get a shorthand `caddy python-server`.

This will configure a virtual `Caddyfile` and run the server for you.

For example if you have `main.py` file with a Flask app inside you'll simply run:

```
caddy python-server -t wsgi -a main:app
```

This will start serving request on http://localhost:9080/ by default.

See more settings with `caddy python-server --help`.

## Multiple worker processes

Up until now caddysnake has been serving request from a single python processes, given that the GIL hasn't been removed yet that means we were not fully utilizing all the cores available.

Now by default caddysnake starts as many processes as cores you have in your cpu, configurable with `--workers <n>`.

This increases throughput but also overhead of communication between the Go and Python processes.

## Package available in PyPI


Now it's possible to install `caddysnake` as a package using pip:

```
pip install caddysnake
caddysnake python-server --help
```

This is a quick way to get started without the need to compile caddy yourself.

