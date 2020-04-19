---
layout: post
title: "Executing python code from MySQL Server"
excerpt: "Evaluate python expressions inside MySQL using a UDF that binds to python interpreter."
author: "Miguel Liezun"
tags: python,c++,mysql,udf
---

# Executing python code from MySQL Server

## Trying `py_eval`

#### Generate a list of integers from 0 to 10

```sql
> select py_eval('[i for i in range(10)]') list;
+--------------------------------+
| list                           |
+--------------------------------+
| [0, 1, 2, 3, 4, 5, 6, 7, 8, 9] |
+--------------------------------+
```

#### Generate a dictionary (json object) from a list of dicts

```sql
> select replace(py_eval('{ str(user["id"]) : user for user in [{"id": 33, "name": "John"}, {"id": 44, "name": "George"}] }'), "'", '"') dict;
+------------------------------------------------------------------------+
| dict                                                                   |
+------------------------------------------------------------------------+
| {"33": {"id": 33, "name": "John"}, "44": {"id": 44, "name": "George"}} |
+------------------------------------------------------------------------+
```

Replace is needed here, because python uses single quotes for dictionaries.

#### Make a function that receives a json array and a key and sorts the array by key

```sql
DROP function IF EXISTS `sort_by_key`;
DELIMITER $$
CREATE FUNCTION `sort_by_key` (arr json, k text)
RETURNS json
BEGIN
    RETURN replace(py_eval(CONCAT("sorted(", arr, ", key=lambda e: e['", k, "'])")), "'", '"');
END$$
DELIMITER ;
```

Test

```sql
> select sort_by_key('[{"a":2}, {"a":1}, {"a": 722}, {"a": 0}]', 'a') sorted;
+--------------------------------------------+
| sorted                                     |
+--------------------------------------------+
| [{"a": 0}, {"a": 1}, {"a": 2}, {"a": 722}] |
+--------------------------------------------+
```

## How to write a MySQL UDF

There is a pretty good guide at the [MySQL 8.0 Reference Manual](https://dev.mysql.com/doc/refman/8.0/en/adding-udf.html). I'll give you a brief explanation so you can start quickly, but reading the full guide is highly recomended.

MySQL's UDFs are written in C++ and need to follow certain conventions so they can be recognized as such.

In our case, we want our MySQL function to be called `py_eval`, so we have to define the following C++ functions:

- py_eval_init or py_eval_deinit
- py_eval

**py_eval_init**: (Optional) Initializes memory and data structures for the function execution.

**py_eval**: Executes the actual function, in our case evaluates a python expression.

**py_eval_deinit**: (Optional) If any memory was allocated in the init function, this is the place where we free it.

For `py_eval` we only need **py_eval_init** and **py_eval**.

### Functions signatures

```c
bool py_eval_init(UDF_INIT *initid, UDF_ARGS *args,
                             char *message);

char *py_eval(UDF_INIT *, UDF_ARGS *args, char *result,
                         unsigned long *res_length, unsigned char *null_value,
                         unsigned char *);
```

These are the standard definitions for MySQL functions that return string, as is the case of `py_eval`. To be able to declare this functions, you need to have the definition of `UDF_INIT` and `UDF_ARGS`, you can find that at the source code of mysql server -> [right here](https://github.com/mysql/mysql-server/blob/8.0/include/mysql/udf_registration_types.h).

## Evaluating python expression

For evaluating python expression, we'll be using [pybind11](https://github.com/pybind/pybind11). That gives us the ability to directly access the python interpreter and execute code.

#### Example

Make sure you have `g++` installed. Try executing: `g++ --help`. And some version of python running of your system, for this tutorial I'll be using version _3.8_.

```bash
$ mkdir py_eval && cd py_eval
$ git clone https://github.com/pybind/pybind11
```

Create a new file called `main.cpp` with the following content:

```c
#include "pybind11/include/pybind11/embed.h"
#include "pybind11/include/pybind11/eval.h"
#include <iostream>

namespace py = pybind11;

py::scoped_interpreter guard{}; // We need this to keep the interpreter alive

int main(void) {
    auto obj = py::eval("[i for i in range(10)]");
    std::cout << std::string(py::str(obj)) << std::endl;
}
```

To run the example we have to compile the file.

First, we need the compilation flags.

```bash
$ pkg-config python-3.8 --libs --cflags
-I/usr/include/python3.8
```

Then, we can compile and run our code with the following.

```bash
$ g++ main.cpp -I/usr/include/python3.8 -lpython3.8
$ ./a.out
[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
```

## Putting all together

Download udf types to the project folder.

```bash
$ wget https://raw.githubusercontent.com/mysql/mysql-server/8.0/include/mysql/udf_registration_types.h
```

Create a new file called `py_eval.cpp`, with the following content:

```c++
#include "pybind11/include/pybind11/embed.h"
#include "pybind11/include/pybind11/eval.h"
#include "udf_registration_types.h"
#include <string.h>

namespace py = pybind11;

py::scoped_interpreter guard{}; // We need this to keep the interpreter alive

extern "C" bool py_eval_init(UDF_INIT *initid, UDF_ARGS *args,
                             char *message)
{
    // Here we can check if we received one argument
    if (args->arg_count != 1)
    {
        // The function returns true if there is an error,
        // the error message is copied to the message arg.
        strcpy(message, "py_eval must have one argument");
        return true;
    }
    // Cast the passed argument to string
    args->arg_type[0] = STRING_RESULT;
    initid->maybe_null = true; /* The result may be null */
    return false;
}

extern "C" char *py_eval(UDF_INIT *, UDF_ARGS *args, char *result,
                         unsigned long *res_length, unsigned char *null_value,
                         unsigned char *)
{
    // Evaluate the argument as a python expression
    auto obj = py::eval(args->args[0]);
    // Cast the result to std::string
    std::string res_str = std::string(py::str(obj));

    // Copy the output string from py::eval to the result argument
    strcpy(result, res_str.c_str());

    // Set the length of the result string
    *res_length = res_str.length();

    return result;
}
```

Then, we have to compile the project as a shared library, and move it to the plugin folder of mysql (in your case, it could be located in some other directory).

```bash
$ g++ -I/usr/include/python3.8 -lpython3.8 -shared -fPIC -o py_eval.so py_eval.cpp
$ sudo cp py_eval.so /usr/lib/mysql/plugin/
```

Now, it's time to try it from mysql.

First, connect to your server as root.

```bash
$ sudo mysql -uroot
```

Create and test the function.

```sql
> create function py_eval returns string soname 'py_eval.so';
Query OK, 0 rows affected (0.029 sec)

> select py_eval('[i for i in range(10)]') list;
+--------------------------------+
| list                           |
+--------------------------------+
| [0, 1, 2, 3, 4, 5, 6, 7, 8, 9] |
+--------------------------------+
1 row in set (0.001 sec)
```

## Future

There is a lot to do, for example there is no error control on the function execution. The python expression that we are trying to evaluate could fail causing a server reboot. Also, there is some extra work to do to be able to use `import`. And there are many concerns regarding concurrency issues.

If you want to contribute to improve execution of python code on mysql server, please go to my [github project](https://github.com/mliezun/mysql-python) and make a PR.

I hope you enjoyed this tutorial and come back soon for more.
