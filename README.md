# Personal blog by Miguel Liezun.

This blog is made with [Grotsky](https://github.com/mliezun/grotsky) a toy programming language I made to learn about interpreters and compilers.

[Visit the blog](https://mliezun.github.io)


## Project Overview

```
/
    scripts/
        convert_from_md.py  # -> Used to migrate from jekyll to new templating implementation
        download_grotsky_binary.sh  # -> Downloads grotsky executable for your platform
        generate_site.sh  # -> Generates html files
        start_dev_server.sh  # -> Starts dev server
    src/
        pages/*  # -> Blog posts are stored here
        generate_site.gr  # Grotsky script to generate html files
        html.gr  # Template engine implementation
        http.gr  # HTTP Server for Development
        router.gr  # Router for HTTP requests
        static.gr  # Serves static files (assets: js, img, css)
        utils.gr  # Various utilities (functions: map, filter, foldl, each, ...)
        web.gr   # Main file, startup development server, setup router and render pages
```

### Serve locally

```
$ make clean
$ make serve
```

### Generate HTML Files

```
$ make clean
$ make generate
```

A new folder `docs/` will be generated, all the files will be inside.
