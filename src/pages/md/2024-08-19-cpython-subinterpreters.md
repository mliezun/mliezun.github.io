---
title: "Finding and fixing a bug in Python subinterpreters"
excerpt: "Lately, I've been working with Python C-API. I wanted to use subinterpreters with their own GIL to unlock the performance gains promised by being able to execute many threads in parallel which was not possible before Python 3.12."
author: "Miguel Liezun"
tags: python,compiler,caddy,go,programming,c,subinterpreters,gil
---

# Finding and fixing a bug in Python subinterpreters

### tldr

- Filed an [issue](https://github.com/python/cpython/issues/117482) in CPython.
- Sent a [PR](https://github.com/python/cpython/pull/117660). 
- My code was garbage and was not merged, but helped to get the issue fixed.

## Backstory

Lately, I've been working with Python C-API. I wanted to use subinterpreters with their own GIL to unlock the performance gains promised by being able to execute many threads in parallel which was not possible before Python 3.12.

The reason is that I've been building a Caddy web server plugin called: [Caddy Snake](https://github.com/mliezun/caddy-snake).

The plugin let's users embed a Python interpreter and serve requests directly from [Caddy](https://caddyserver.com).

Caddy is written in Go, and to interact with Python I had to use CGO, a compatibility layer that makes it easy to call C functions from Go.

To improve performance I wanted to use the new feature of having separate GIL per subinterpreter so requests could be served by many threads at the same time.

Today I saw a [great blogpost](https://izzys.casa/2024/08/463-python-interpreters/) about finding a bug in subinterpreters and that inspired me to write about my experience.


## The issue

I started [coding up](https://github.com/mliezun/caddy-snake/pull/9/files) a basic implementation to see if I could serve simple requests from subinterpreters.

From the get go I found that requests were failing in Python version 3.12 but working for previous versions thanks to CI tests.

The failure was constrained to a C function where the HTTP status code was being converted from string to int: `strtol(statusCode)`.

By printing the content of the `statusCode` variable I found the following difference.

In main interpreter:

```
200
```

In a subinterpreter:

```text
&lt;HttpStatusCode.OK: 200&gt;
```

I managed to track down the enum that was causing this. Then I crafted some code to try to reproduce the error in a standard Python interpreter.

I came up with this:

```python
import _xxsubinterpreters as interpreters


script = """from enum import _simple_enum, IntEnum

@_simple_enum(IntEnum)
class MyEnum:
    DATA = 1
    
print(str(MyEnum.DATA))
"""

exec(script)
# Output: 1

interp_id = interpreters.create(isolated=False)
interpreters.run_string(interp_id, script)
# Output: &lt;MyEnum.DATA: 1&gt;, Expected: 1
```

That piece of code executes the same python code in both the main interpreter and a freshly created subinterpreter. The output should be the same, but it's not. The problem was independent of running with a separate GIL or with the same GIL.

Checking the `__str__` methods I could see that they were clearly different.

In main interpreter:

```python
...
print(MyEnum.DATA.__str__)
# Output: &lt;method-wrapper '__repr__' of MyEnum object at 0x7f9a09a2e910&gt;
```

In subinterpreter:

```python
...
print(MyEnum.DATA.__str__)
# Output: &lt;method-wrapper '__str__' of MyEnum object at 0x7f9a099a5e90&gt;
```

In the main interpreter the method wraps `__repr__`.
In the subinterpreter it wraps `__str__`.

At this point I couldn't believe what I was looking at. When your program has a bug you always assume is your fault, it's rare to see the case where the problem is in the INTERPRETER.

But to my own disbelief I had found a problem with the CPython implementation.

## Doing my homework

After that I decided that I was gonna do the right thing: file an issue in Github telling what I just witnessed.

First thing first: read the guide on [how to contribute to python](https://devguide.python.org/#contributing).

This is what you should always do when contributing to a project because you might find that your problem is actually not worth reporting or that it was already solved in the `main` development branch.

I made sure to test with all supported Python versions `3.8, 3.9, 3.10, 3.11, 3.12, 3.13` and in both Linux and macOS.

The problem was only present in 3.12 and 3.13, after subinterpreters with separate GIL was introduced.


## The community is awesome

In less than 1 hour and a half of posting the issue I got a response from a member of the Python Triage Team: "Bisected to [de64e75](https://github.com/python/cpython/commit/de64e7561680fdc5358001e9488091e75d4174a3)".

I thought to myself: "that is awesome, this is happening so fast!".

Then others pointed out that you could reproduce it with a shorter script:

```python
import _xxsubinterpreters as interpreters

script = """print(int.__str__)"""


exec(script)
# Output: &lt;slot wrapper '__str__' of 'object' objects&gt;

interp_id = interpreters.create()
interpreters.run_string(interp_id, script)
# Output: &lt;slot wrapper '__str__' of 'int' objects&gt;
```

Having the exact commit where this problem was introduced and a concise way of seeing what the underlying problem is, I decided to give try to fix the issue myself. Diving into the CPython codebase.

## Diving into CPython

The commit where the problem was introduced [de64e75](https://github.com/python/cpython/commit/de64e7561680fdc5358001e9488091e75d4174a3) has 185 additions and 86 deletions, and changes only 5 files.

If you take a look at it the most suspicious one is `typeobject.c`, you can see that it's changing some behavior in the MRO: Method Resolution Order. Which is the way methods are "inherited" from one class to another in Python.

I thought that was related because in the subinterpreter the `int` class inherits the method
 `__str__` instead of 
 `__repr__`. That was not the real issue, but I was correct about the file where the problem was.

Debugging was done in the good old fashioned way, adding print statements all over the place.

With my printing mechanism I managed to find out that the function that creates those `&lt;slot wrapper ...&gt;` objects is called
 `type_ready()`.

That slot wrapper is a function that calls code from a type-slot. For example the `int` type defines a slot called 
`tp_str`. That slot is a C function that knows how to convert the object into a string. That C function is wrapped into a Python function which is executed when you do 
`str(5)`.

I could see that `type_ready()` was called the first time from the main interpreter, and the second time from a subinterpreter, but this time it added more stuff.

One would expect that `type_ready()` gives the same result wether executed from a subinterpreter or from the main interpreter. The builtin types (
    `int`, 
    `str`, 
    `float`, 
    `bool`, ...) should be the same in all cases.

Another group of changes in the `typeobject.c` file was a lot of functions that obtain attributes from a builtin type, for example 
`lookup_tp_dict()`:

```C
static inline PyObject *
lookup_tp_dict(PyTypeObject *self)
{
+   if (self->tp_flags &amp; _Py_TPFLAGS_STATIC_BUILTIN) {
+       PyInterpreterState *interp = _PyInterpreterState_GET();
+       static_builtin_state *state = _PyStaticType_GetState(interp, self);
+       assert(state != NULL);
+       return state->tp_dict;
+   }
    return self->tp_dict;
}
```

This function is obtaining the `tp_dict` property from a type. Which is a dictionary that stores attributes/methods of the class.

In this case the entire if-statement was added. If you take a closer look you can infer what's happening. Before we just obtained the value by doing `self->tp_dict`. 
Now, if it's a builtin type, we read the value from the interpreter state `state->tp_dict`.

With this information I started to dig deeper to see if I could find the exact place where the extra attributes were being added.

Taking `int.__str__` as an example to see what was going on:

<ol>
<li> The `type_ready()` function gets executed as part of the main interpreter initialization process.</li>
<li> The function starts "readying" the `int` type: 
`tp_dict` gets filled by 
`type_ready_fill_dict()`, one of the thing this function does is lookup which slots are *not empty* and add them to the dict, for 
`int` the 
`tp_str` slot is empty.</li>
<li> After that, `type_ready_inherit()` gets called, and copies the 
`tp_str` slot from object to int.</li>
<li> The init process for the main interpreter finishes and we're ready to start with the second interpreter.</li>
<li> In this case, the `tp_str` slot is not empty for 
`int`, it was filled by step 3. So it gets added to the dict by 
`type_ready_fill_dict()`.</li>
<li> The program continues and we see different behavior depending on which interpreter we run.</li>
</ol>

The problem here is that inside `type_ready()` we expect 
`type_ready_fill_dict()` to be called before 
`type_ready_inherit()`. Which is true for the main interpreter but not for the subinterpreter. Also, this is caused because all the slots in 
`int` are shared except for 
`tp_dict` which is stored in each interpreter.


### Summary

To summarize the problem: `type_ready()` didn't receive a "clean" type. It was receiving a type with slots partially filled.

Some slots were filled because they were shared among interpreters, others like `tp_dict` were not shared. That caused inconsistencies between executions of 
`type_ready()`.


## The solution?

Given my lack of experience working in the CPython codebase I decided that the simplest solution was to make a quick and dirty solution.

My solution was to check if `type_ready()` was being called from a subinterpreter and in that case cleanup the base type so it looked the same as in the main interpreter.

It boils down to adding this function:

```C
static int
fix_builtin_slot_wrappers(PyTypeObject *self, PyInterpreterState *interp)
{
    assert(self->tp_flags &amp; _Py_TPFLAGS_STATIC_BUILTIN);
    assert(!_Py_IsMainInterpreter(interp));

    // Getting subinterpreter state
    managed_static_type_state *state = _PyStaticType_GetState(interp, self);
    assert(state != NULL);

    // Getting main interpreter state
    PyInterpreterState *main_interp = _PyInterpreterState_Main();
    managed_static_type_state *main_state = _PyStaticType_GetState(main_interp, self);
    assert(main_state != NULL);

    // Check wich attributes the type has in subinterpreter and it doesn't have
    // in the main interpreter. Store them in keys_to_remove.
    int res = -1;
    PyObject* keys_to_remove = PyList_New(0);
    if (keys_to_remove == NULL) {
        goto finally;
    }
    Py_ssize_t i = 0;
    PyObject *key, *value;
    while (PyDict_Next(state->tp_dict, &amp;i, &amp;key, &amp;value)) {
        if (!PyDict_Contains(main_state->tp_dict, key)) {
            if (PyList_Append(keys_to_remove, key) &lt; 0) {
                goto finally;
            }
        }
    }

    // Go through keys_to_remove and remove those attributes from
    // the base type in the subinterpreter.
    Py_ssize_t list_size = PyList_Size(keys_to_remove);
    for (Py_ssize_t i = 0; i &lt; list_size; i++) {
        PyObject* key = PyList_GetItem(keys_to_remove, i);
        if (PyDict_DelItem(state->tp_dict, key) &lt; 0) {
            goto finally;
        }
    }

    res = 0;

finally:
    Py_XDECREF(keys_to_remove);
    return res;
}
```

Then at the end of `type_ready()`, call that function for builtin types and only if we're in a subinterpreter:


```C
    if (type->tp_flags &amp; _Py_TPFLAGS_STATIC_BUILTIN) {
        PyInterpreterState *interp = _PyInterpreterState_GET();
        if (!_Py_IsMainInterpreter(interp)) {
            if (fix_builtin_slot_wrappers(type, interp) < 0) {
                return -1;
            }
        }
    }
```

And that's it. That was my solution. And it worked like a charm.


## The wait

After sending a [PR](https://github.com/python/cpython/pull/117660) with my proposed changes I waited for a couple months until I saw some real activity.

[Eric Snow](https://github.com/ericsnowcurrently) is in charge of the subinterpreters implementations. He found a better more focused solution that was less fragile and took into account what would happen if the interpreter was reinitialized.

In the end I decided to close my PR because Eric's pushed the real solution into a separate PR.

I think it would have been cool to ship code to be included in all python interpreters around the world. But I'm happy my analysis helped solve the issue.

In Python 3.12.5 the fix was released: [https://docs.python.org/release/3.12.5/whatsnew/changelog.html#core-and-builtins](https://docs.python.org/release/3.12.5/whatsnew/changelog.html#core-and-builtins)


## Thanks!

I wanted to say thanks again to all Python contributors that helped get this solved. From my experience I felt welcome by the community and that they cared about the time and effort I put in.

I would say it was a great experience that I hope to repeat. And my cheers go to the Python community for setting up such an easy to follow process.
