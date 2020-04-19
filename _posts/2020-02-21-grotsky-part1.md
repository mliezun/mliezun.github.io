---
layout: post
title: "Grotsky Part 1: Syntax"
excerpt: "Part 1 of building my own laguage series. Defining the syntax of grotsky toy language."
author: "Miguel Liezun"
tags: parser,lexer,interpreter
---

# Grotsky Part 1: Syntax

### Syntax Restrictions

- No use of semicolon `;`
- Block statements delimited by `begin` and `end`
- Function definition using `fn` keyword
- Logic operators in plain english `or`, `and`, `not`
- Conditional statements use the following keywords: `if`, `elif`, `else`
- There is no switch statement
- Class definition with `class` keyword
- Arithmetic operations: `*`, `/`, `-`, `+`, `^`
- Grouping with parentheses `()`
- Native support for python-like lists and dictionaries: `[]`, `{}`
- Support for enhanced for loop: `for i, el in array`
- Keywords and identifiers can only use alphabethic characters

### Primitives

- `nil`
- Integers
- Floats
- Booleans
- Strings
- Lists
- Dictionaries

### Example of functions and operations

```ruby
## Arithmethic
print(2^10 - 2323*3)
# Output: -5945
print(2^(12*3+400/-4+10*5/2))
# Output: 1.8189894035458565e-12

## Logic
print(true or false)
# Output: true (short circuit)
print(false and true)
# Output: false (short circuit)

## Conditionals
if 3 > 2 or (1 < 3 and 2 == 2) begin
    print('Condition is true')
end
elif 3 == 4 begin
    print('Condition 2 is true')
end
else begin
    print('Conditions are false')
end

## Lists
for i in [1, 2, 3, 4] begin
    print(i)
end

let lst = [1, 2, 3, 4]
lst[0] = -1
print(lst) # Output: [-1, 2, 3, 4]
print(lst[1:3]) # Output: [2, 3]

## Dictionaries
# (dictionaries and lists not allowed as keys)
let dct = {
    "Key1": "Val1",
    2: "Val2",
    true: false
}
for key, val in dct begin
    print(key, val)
end

## Functions
fn square(x)
begin
    return x^2
end

fn operate(x, operation)
begin
    return operation(x)
end

## Clojure
fn makeCounter()
begin
    let n = 0
    return fn() begin
        n = n+1
        return n
    end
end

## Classes
class Counter
begin
    init(start) begin
        self.start = start
    end
    count() begin
        self.start = self.start+1
        return self.start
    end
end

class CounterTwo
begin
    count() begin
        return super.count()*2
    end
end
```

### Syntax definition

Let's build a syntax definition in backus naur format that will be easy to parse with a recursive descent parser.

#### Expresions

```
expression      → assignment;
list            → "[" arguments? "]";
dictionary      → "{" dict_elements? "}";
dict_elements   → keyval ("," keyval)*;
keyval          → expression ":" expression;
assignment      → (call ".")? IDENTIFIER "=" assignment | access;
access          → logic_or ("[" slice "]")*;
logic_or        → logic_and ("or" logic_and)*;
logic_and       → equality ("and" equality)*;
equality        → comparison (("!=" | "==") comparison)*;
comparison      → addition ((">" | ">=" | "<" | "<=") addition)*;
addition        → multiplication (("-" | "+") multiplication)*;
multiplication  → power (("/" | "*") power)*;
power           → unary ("^" unary)*;
unary           → ("not" | "-") unary | call;
call            → primary ("(" arguments? ")" | "." IDENTIFIER)*;
arguments       → expression ("," expression)*;
slice           → (":" expression)
                | (":" expression ":" expression)
                | (":" ":" expression)
                | expression
                | (expression ":")
                | (expression ":" expression)
                | (expression ":" ":" expression)
                | (expression ":" expression ":" expression);
primary         → NUMBER
                | STRING
                | "false"
                | "true"
                | "nil"
                | IDENTIFIER
                | "(" expression ")"
                | fnAnon
                | list
                | dictionary;
fnAnon          → "fn" "(" parameters? ")" block;
```

#### Statements

```
program        → declaration* EOF;
declaration    → classDecl | funDecl | varDecl | statement;
classDecl      → "class" IDENTIFIER ( "<" IDENTIFIER )? "begin" methodDecl* "end" NEWLINE;
methodDecl     → "class"? function;
funDecl        → "fn" function ;
function       → IDENTIFIER "(" parameters? ")" block ;
parameters     → IDENTIFIER ( "," IDENTIFIER )* ;
varDecl        → "let" IDENTIFIER ("=" expression)? NEWLINE;
statement      → forStmt
                | ifStmt
                | returnStmt
                | whileStmt
                | exprStmt
                | block;
exprStmt       → expression NEWLINE;
forStmt        → "for"  (classicFor | newFor) statement;
classicFor     → (varDecl | exprStmt | ",") expression? "," expression?;
newFor         → IDENTIFIER ("," IDENTIFIER)? "in" expression;
ifStmt         → "if" expression statement ("elif" expression statement)* ("else" statement)?;
returnStmt     → "return" expression? NEWLINE;
whileStmt      → "while" expression statement;
block          → "begin" NEWLINE declaration* "end" NEWLINE;
```

That's it! The next step is to build a lexer and a parser.
