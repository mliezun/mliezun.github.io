---
layout: post
title: "Mlisp: My own lisp implementation compiled to WASM"
excerpt: "Lisp implementation written in C that compiles to WASM with emscripten."
author: "Miguel Liezun"
tags: lisp,wasm,emcc,C/C++,emscripten
---

# Mlisp, My own lisp implementation

[Mlisp](https://github.com/mliezun/mlisp) a tiny lispy language based on the book [Build Your Own Lisp](http://www.buildyourownlisp.com/).

The interpreter is written in C and compiled directly to WASM. You can try it in this page by openning the developer console of your browser and typing `Mlisp.interpret("+ 2 2")` or using the repl shown below.

## Interface

To be able to access C functions from your browser you have to export them. Let's see how we can define a function that is exported.

```C
#if __EMSCRIPTEN__
EMSCRIPTEN_KEEPALIVE
#endif
int mlisp_init();
```

When compilen with `emcc` the emscripten compiler to wasm, you have to add `EMSCRIPTEN_KEEPALIVE` macro before your function so it doesn't get optimized away.

The exported functions in this project are:

```C
int mlisp_init();
char *mlisp_interpret(char *input);
void mlisp_cleanup();
```

The project is then compiled with: 

```
emcc -std=c99  -Wall -O3 -s WASM=1 -s EXTRA_EXPORTED_RUNTIME_METHODS='["cwrap"]'
```

That means that you would be able to access the exported functions using a `cwrap` that let's you wrap a C function call from a Javascript function call.

This compilation generates two files `mlisp.js` and `mlisp.wasm`.

The javascript file defines a `Module` that provides useful tool to access exported functions.

### Let's start using it

```js
const Mlisp = {
    init: Module.cwrap('mlisp_init', 'number', []),
    interpret: Module.cwrap('mlisp_interpret', 'string', ['string']),
    cleanup: Module.cwrap('mlisp_cleanup', 'void', []),
};

// Init interpreter
Mlisp.init();

// Run some commands
console.log(Mlisp.interpret("+ 2 2"));

// Cleanup interpreter
Mlisp.cleanup();
```

## Automated Build & Release from github

I made a github workflow for this project to automatically build and release so you can retrieve them from [Github](https://github.com/mliezun/mlisp/releases/tag/refs%2Fheads%2Fmaster).


## REPL

<script src="/assets/mlisp/mlisp.js"></script>

<style>
.container-centered {
  display: flex;
  justify-content: center;
}

.vertical-centered {
  display: block;
}
</style>

<div class="container-centered">
    <div class="vertical-centered" style="width: 50vw">
        <textarea id="show-repl" disabled style="min-width: 50vw; max-width: 50vw; min-height: 20vh"></textarea>
        <input id="input-command" type="text" style="min-width: 50vw; max-width: 50vw" placeholder="> Input some commands">
    </div>
</div>

<script type="application/javascript">
var A = {
    mlisp: null,
    init () {
        const node = document.getElementById('input-command');
        node.addEventListener("keyup", (event) => {
            if (event.key === "Enter") {
                this.handleInput(event);
            }
        });
    },
    handleInput(ev) {
        if (!this.mlisp) {
            window.Mlisp = {
                init: Module.cwrap('mlisp_init', 'number', []),
                interpret: Module.cwrap('mlisp_interpret', 'string', ['string']),
                cleanup: Module.cwrap('mlisp_cleanup', 'void', []),
            };
            this.mlisp = window.Mlisp;
            this.mlisp.init();
        }
        const node = ev.target;
        const cmd = node.value;
        if (!cmd) {
            return;
        }
        const output = document.getElementById('show-repl');
        const result = this.mlisp.interpret(cmd);
        node.value = null;
        output.value += `> ${cmd}\n\t${result}\n`;
    }
};

A.init();
</script>



## Interesting commands to try out

- `foldl`: Fold left (same as reduce left)
    - `(foldl + 0 {1 2 3 4 5})`: Sum of elements
- `filter`
    - `(filter (\ {e} {> e 3}) {1 2 3 4 5 6})`: Elements bigger than 3
- `map`
    - `(foldl * 1 (map (\ {e} {* e 2}) {1 1 1 1 1}))`: Multiply elements by 2 and then multiply all elements

