---
layout: post
title: "Grotsky Part 3: Interpreting"
excerpt: "Part 3 of building my own laguage series. Interpreting expressions and statement, traversing the Abstract Syntax Tree."
author: "Miguel Liezun"
tags: interpreter,expression,ast
---

## It's slow! 🤢

My interpreter it's really, really, wait for it... *Really slow*.

An example of a bad performing grotsky code:

```
# fib: calculates the n-th fibonacci number recursively
fn fib(n) begin
    if n < 2 return n
    return fib(n-2) + fib(n-1)
end
println(fib(30))
```

#### Running the code

```
$ time ./grotsky examples/fib.g
```

Gives a wooping result of:

```
832040

real    0m11,154s
user    0m11,806s
sys     0m0,272s
```

Almost twelve seconds!!! 🤣🤣🤣

Comparing with a similar python code

```
def fib(n):
    if n < 2: return n
    return fib(n-2) + fib(n-1)
print(fib(30))
```

Gives a result of:

```
832040

real    0m0,423s
user    0m0,387s
sys     0m0,021s
```

That means, my interpreter is at least 20 times slower than Cpython.

#### Why is it so slow?

[Here is an explanation](https://www.reddit.com/r/golang/comments/5kv2xx/why_is_golangs_performance_worse_than_javas_in/).

As the person from the first comment states, go garbage collector is not well suited for this kind of scenario with heavy allocation of objects.

> Go's GC is not generational, so allocation requires (comparatively speaking) much more work. It's also tuned for low latency (smallest pause when GC has to stop the program) at the expense of throughput (i.e. total speed). This is the right trade-off for most programs but doesn't perform optimally on micro-benchmarks that measure throughtput.


Setting the gc percent at 800 (100 by default) more than halves the time that the function takes to compute:

```
$ time GOGC=800 ./grotsky examples/fib.g 
832040

real    0m5,110s
user    0m5,182s
sys     0m0,061s
```

## Interpreting functions

Callable interface

```go
type callable interface {
	arity() int
	call(exec *exec, arguments []interface{}) interface{}
}
```

*All grotsky functions must be an object that implements the callable interface.*

For that I defined two kind of structs:

```go
type function struct {
	declaration   *fnStmt
	closure       *env
	isInitializer bool
}

type nativeFn struct {
	arityValue int
	callFn  func(exec *exec, arguments []interface{}) interface{}
}
```

#### nativeFn

Let's you define standard functions available on all grotsky interpreters. Line `println`.

```go
func (n *nativeFn) arity() int {
	return n.arityValue
}

func (n *nativeFn) call(exec *exec, arguments []interface{}) interface{} {
	return n.callFn(exec, arguments)
}
```

From that, println would be pretty straight forward:

```go
...

var println nativeFn
println.arityValue = 1
println.callFn = func(exec *exec, arguments []interface{}) interface{} {
    fmt.Println(arguments[0])
    return nil
}
...
```


#### Ordinary grotsky functions

For ordinary grotsky functions the things are a little bit messier.

First I got to introduce the `environment` that is an object that holds `map[string]interface{}` as a dictionary for variables in the local scope and a pointer to another environment that contains variables for the outer scope.

```go
type env struct {
	state *state

	enclosing *env
	values    map[string]interface{}
}

func newEnv(state *state, enclosing *env) *env {
	return &env{
		state:     state,
		enclosing: enclosing,
		values:    make(map[string]interface{}),
	}
}

func (e *env) get(name *token) interface{} {
	if value, ok := e.values[name.lexeme]; ok {
		return value
	}
	if e.enclosing != nil {
		return e.enclosing.get(name)
	}
	e.state.runtimeErr(errUndefinedVar, name)
	return nil
}

func (e *env) define(name string, value interface{}) {
	e.values[name] = value
}
```

As you can see, the define method creates a variable on the local scope, and the get methods tries to retrieve a variable first from the local scope and then from the outer scope.

Let's see how functions are implemented.

```go
func (f *function) arity() int {
	return len(f.declaration.params)
}

func (f *function) call(exec *exec, arguments []interface{}) (result interface{}) {
	env := newEnv(exec.state, f.closure)
	for i := range f.declaration.params {
		env.define(f.declaration.params[i].lexeme, arguments[i])
	}

	defer func() {
		if r := recover(); r != nil {
			if returnVal, isReturn := r.(returnValue); isReturn {
				result = returnVal
			} else {
				panic(r)
			}
		}
	}()

	exec.executeBlock(f.declaration.body, env)

	return nil
}
```

Function `arity` is pretty simple.

The function `call` takes an `exec` object, that is no more than an instance of the interpreter, and the arguments to the function as an array of objects. Then creates a new environment the is surrounded by the environment local to the function definition and defines all the function parameters. Then comes the tricky part, first there is a deferred call to an anonymous function, let's ignore that for a moment, in the end, the function `executeBlock` gets called. Let's see what that function does:

```go
func (e *exec) executeBlock(stmts []stmt, env *env) {
	previous := e.env
	defer func() {
		e.env = previous
	}()
	e.env = env
	for _, s := range stmts {
		e.execute(s)
	}
}
```

What's happening here is that the interpreter steps into the new environment, saving the previous environment in a variable, and execute all given statements, after that it restores the environment to the previous one. Exactly as a function does.

#### What happens when you hit a `return`

```go
type returnValue interface{}

...

func (e *exec) visitReturnStmt(stmt *returnStmt) R {
	if stmt.value != nil {
		panic(returnValue(stmt.value.accept(e)))
	}
	return nil
}
```

When you get to a return node in the ast, the nodes panics with a return value. This has to do with the fact that you need to go up the call stack and finish the execution of the function, otherwise the function will keep it's execution.

That's the reason of the deferred function we forgot a couple seconds ago:

```go
func (f *function) call(exec *exec, arguments []interface{}) (result interface{}) {
    ...

    defer func() {
		if r := recover(); r != nil {
			if returnVal, isReturn := r.(returnValue); isReturn {
				result = returnVal
			} else {
				panic(r)
			}
		}
    }()

    ...
}
```

This function recovers from a panic. If the value recovered is of type `returnValue` it recovers successfully and sets the result value of the function call to the return value, else it panics again.

## Hasta la vista, baby

That's it for now. There are a lot of nifty stuff to keep talking about. But I think it's enough for now.

Remember to check out the [source code](https://github.com/mliezun/grotsky). And stay tuned for more.
