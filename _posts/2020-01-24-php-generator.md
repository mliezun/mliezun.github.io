---
layout: post
title: "Reinventing the Wheel: PHP Generators"
excerpt: "Attempt of a lunatic to recreate functionalities that a language already has using the same language, and failing."
author: "Miguel Liezun"
tags: php, generators
---

# Reinventing the Wheel: PHP Generators

## First thing first. How a generator works?

### Starting back at C

Let's create a function that each time we call it we get the next number of the fibonacci sequence.

```c
int fibonacci()
{
    static int a = 0;
    static int b = 1;
    int aux = b;
    b = a + b;
    a = aux;
    return a;
}
```

If we call fibonacci(), the first time we'll get 1, the second time 1, the third 2, the fourth 3, and so on...

This happens because we declared variables `a, b` to be static. This means that they mantain the value after the function returns. Normally, what happens (if we don't declare a variable as static) is that the variables inside the function don't mantain the values of the last execution.

### First generator for PHP

The equivalent function in PHP is pretty similar to C's approach.

```php
<?php

function fibonacci()
{
    static $a = 0;
    static $b = 1;
    $aux = $b;
    $b = $a + $b;
    $a = $aux;
    return $a;
}

$out = [];

for ($i = 1; $i <= 10; $i++) {
    $out[] = fibonacci();
}

echo implode(', ', $out) . "\n";

/*
Output: 1, 1, 2, 3, 5, 8, 13, 21, 34, 55
*/
```

Let's compare this to the `real` PHP version using `yield`.

```php
<?php

function fibonacci($N)
{
    $a = 0;
    $b = 1;
    for ($i = 0; $i < $N; $i++) {
        $aux = $b;
        $b = $a + $b;
        $a = $aux;
        yield $a;
    }
}

$out = [];

foreach (fibonacci(10) as $fib) {
    $out[] = $fib;
}

echo implode(', ', $out) . "\n";

/*
Output: 1, 1, 2, 3, 5, 8, 13, 21, 34, 55
*/
```

### Creating a custom version of PHP `yield`

This is my own version using the library parallel and channels (probably uses yield internally).

```php
<?php

class MyGenerator implements Iterator
{
    private $chan;
    private $current;
    private $iteratorFn;
    private $runtime;
    private $key = -1;
    private $valid = true;

    public function __construct($iteratorFn)
    {
        $this->iteratorFn = $iteratorFn;
        $this->runtime = new \parallel\Runtime();
        $channel = new \parallel\Channel();

        $this->runtime->run(function() use ($iteratorFn, $channel) {
            $iteratorFn(function ($val) use ($channel) {
                $channel->send($val);
            });
            $channel->close();
        });

        $this->chan = $channel;
        $this->next();
    }

    public function current()
    {
        return $this->current;
    }

    public function next()
    {
        try {
            ++$this->key;
            $val = $this->chan->recv();
            $this->current = $val;
        } catch (\parallel\Channel\Error\Closed $e) {
            $this->valid = false;
        }
        return $this->current;
    }

    public function key() {return $this->key;}
    public function valid() {return $this->valid;}
    public function rewind() {}
}


function fibonacci($N)
{
    return new MyGenerator(function ($yield) use ($N) {
        $a = 0;
        $b = 1;
        for ($i = 0; $i < $N; $i++) {
            $aux = $b;
            $b = $a + $b;
            $a = $aux;
            $yield($a);
        }
    });
}

$out = [];

foreach (fibonacci(10) as $fib) {
    $out[] = $fib;
}

echo implode(', ', $out) . "\n";
```

### Performance comparison: PHP vs Custom

#### Tested code

```php
for ($i = 0; $i < 1000; ++$i) {
    foreach (fibonacci(100) as $fib) {
        $out[] = $fib;
    }
}
```

#### `yield` version

```
real    0m0,083s
user    0m0,059s
sys     0m0,023s
```

#### `MyGenerator` version

```
real    0m2,138s
user    0m1,426s
sys     0m1,363s
```

So, it's aproximately 26 times slower :-)
