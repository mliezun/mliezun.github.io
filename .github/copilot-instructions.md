---
applyTo: "*.gr"
---
This is a static blog generator using Grotsky, a toy programming language that I made.

Syntax of the language:
```grotsky
Listen on TCP Socket

let socket = net.listenTcp("127.0.0.1:6500")
while true {
    let conn = socket.accept()
    io.println("Received connection from:", conn.address())
    conn.write("ok\n")
    conn.close()
}

Try from console:

$ telnet localhost 6500
Trying 127.0.0.1...
Connected to localhost.
Escape character is '^]'.
ok
Connection closed by foreign host.

Outputs:

Received connection from: 127.0.0.1:52238

Make your own Grep

Store the following script in a file called grep.gr:

# Join a list of strings separated by space " "
fn join(list) {
	let out = ""
	for let i = 0; i < list.length; i = i + 1 {
		out = out + list[i]
		if i < list.length - 1 {
			out = out + " "
		}
	}
	return out
}

# Check that a pattern was provided
if process.argv.length == 1 {
	io.println("Usage:\n\tgrep [pattern ...]")
	return 1
}

# Join argv[1:] into a pattern
let pattern = join(process.argv[1:])

# Read first line
let line = io.readln()

# While we are not in EOF
#   Check that line matches pattern and print it
#   Consume next line
while line != nil {
	if re.match(pattern, line) {
		io.println(line)
	}
	line = io.readln()
}

Then it can be used like this:

$ cat file.txt | ./grotsky grep.gr pattern

And it will print all lines that match the "pattern".

We can also package it as a single binary by doing the following commands.

$ ./grotsky compile grep.gr
$ ./grotksy embed grep.grc

Now we should have a grep.exe in our directory. And we can use it:

$ chmod +x grep.exe
$ cat file.txt | ./grep.exe pattern

Should work the same as the previous example.
Language Spec
Literals

    strings: "String A"
    bytes: [0, 1, 10, 20]
    numbers: 10, 10.04, 3.14, -1
    booleans: true, false
    lists: ["a", 1, 2]
    dicts: {"a": 1}
    classes: class MyClass {}
    objects: MyClass()
    functions: fn () {}
    native: native modules or imported modules
    nil

    NOTE: nil represents the "null" or "None" value used in other languages and represents the absence of a value.

Print: Hello World

io.println("Hello world!")

Comments

# Comments start with '#'

Arithmetic Expressions

io.println(
    1+(2+5*10)/2,
    2^4
)

Outputs

27 16

Comparison and Logical Expressions

io.println(
    true and (false or true),
    1 > 2 and 5 <= 10
)

Outputs:

true false

Lists

let list = [
    "a",
    "b",
    "c",
    "d",
    "e"
]

io.println(list)

Outputs:

["a", "b", "c", "d", "e"]

Dicts

let dict = {
    "a": 1,
    "b": 2,
    "c": 3
}

io.println(dict)

Outputs:

{"c": 3, "a": 1, "b": 2}

Conditionals

let a = 10
if a > 10 {
    io.println("a is bigger than ten")
} elif a > 5 {
    io.println("a is less than or equal to ten and bigger than five")
} else {
    io.println("a is less than or equal to five")
}

Outputs:

a is less than or equal to ten and bigger than five

Loops
While Loop

let str = ""
while True {
    if str.length == 10 {
        break
    }
    str = str + "a"
}
io.println(str)

Outputs:

aaaaaaaaaa

Classic For Loop

let list = []
for let i = 0; i < 10; i = i + 1 {
    list = list + [i]
}
io.println(list)

Outputs:

[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

Enhanced For-Loop
Iterate List

let list = [0, 1, 2, 3, 4]
for i in list {
    io.println(i)
}

Outputs:

0
1
2
3
4

Iterate Dict

let dict = {
    "a": 1,
    "b": 2,
    "c": 3
}
for k, v in dict {
    io.println(k, v)
}

Outputs:

b 2
c 3
a 1

Unpacked List of Lists

let listOfLists = [
    ["a", 1, 3],
    ["b", 2, 4],
    ["c", 3, 5]
]
for x, y, z in listOfLists {
    io.println(x, y, z)
}

Outputs:

a 1 3
b 2 4
c 3 5

Functions and Closures

fn makeCounter() {
    let n = -1
    fn wrap() {
        n = n + 1
        return n
    }
    return wrap
}

let counter = makeCounter()

io.println(counter())
io.println(counter())
io.println(counter())

Outputs:

1
2
3

Classes
Simple Class

class A {
    init(n) {
        this.n = n
    }

    print() {
        io.println("N:", this.n)
    }
}

let a = A(10)
a.print()

Outputs:

N: 10

Superclasses

class A {
    print() {
        io.println("Printing:", this.text)
    }

    appendToText(text) {
        this.text = this.text + text
    }
}

class B < A { # Inherits from A
    init() {
        this.text = ""
    }

    appendToText(text) {
        if this.text.length + text.length < 5 {
            super.appendToText(text) # Call to method on superclass
        }
    }
}

let b = B()
b.appendToText("Hello!") # str.length > 5
b.print()
b.appendToText("Hell")
b.print()

Outputs:

Printing: 
Printing: Hell

Magic Methods

Available magic methods: add, sub, div, mod, mul, pow, neg, eq, neq, lt, lte, gt, gte.

class Magic {
    init(value) {
        this.value = value
    }

    add(other) {
        # Addition as in result = this + other
        this.value = this.value + other.value
    }

    print() {
        io.println("Magic is:", this.value)
    }
}

let a = Magic(1)
a + Magic(2)
a.print()

Outputs:

Magic is: 3

Modules

File utils.gr:

fn map(list, mapFn) {
    let out = []
    for e in list {
        out = out + [mapFn(e)]
    }
    return out
}

Usage:

let utils = import("utils.gr")
let list = [0, 1, 2, 3, 4]
io.println(utils.map(list, fn (e) 2 ^ e))

Outputs:

[1, 2, 4, 8, 16]

Env Variables

let lang = env.Get("LANG")
io.println(lang)

Outputs:

en_US.UTF-8

Try-Catch

try {
    let utils = import("utils.gr")
} catch err {
    io.println(err)
}

Outputs:

open utils.gr: no such file or directory

Std Library

Included with the Grotksy interpreter.

io
    io.println(arg0, ...) -> nil
    io.readln() -> str | nil
    io.clock() -> number
    io.readFile(path) -> str
    io.writeFile(path, content) -> nil
    io.listDir(path) -> list
    io.fileExists(path) -> bool
    io.mkdirAll(path, permissions) -> nil

strings
    strings.toLower(str) -> str
    strings.toUpper(str) -> str
    strings.ord(str) -> number
    strings.chr(number) -> str
    strings.asNumber(str) -> number
    strings.split(str) -> list
    strings.compare(str0, str1) -> number

type
    type(object) -> str

env
    env.get(variable) -> str
    env.set(variable) -> nil

import
    import() -> native

net
    net.listenTcp(hostport) -> listener
        listener.address() -> str
        listener.close() -> nil
        listener.accept() -> connection
            connection.address() -> str
            connection.close() -> nil
            connection.read() -> str
            connection.write(str) -> number

re
    re.find(pattern, target) -> list
    re.match(pattern, target) -> bool

process
    process.argv -> list
```

Please make sure to generate code using this syntax.
