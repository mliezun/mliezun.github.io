---
title: "From Script to Binary, Creating single executables with Grotsky"
excerpt: "Recently I added the possibility to embed compiled scripts to Grotsky, this makes it super easy to generate single executables that can be easily distributed."
author: "Miguel Liezun"
tags: grotsky,binary,script,compile,embed,executable
---

# From Script to Binary, Creating single executables with Grotsky

Recently I added the possibility to embed compiled scripts to Grotsky, this makes it super easy to generate single executables that can be easily distributed.

Using the release [v0.0.13](https://github.com/mliezun/grotsky/releases/tag/v0.0.13) of Grotsky, a toy programming language that I've been developing for a while, you can compile scripts into bytecode and embed them into a single binary that can be easily distributed.

For now, it's only possible to embed a single script, so if your script needs to import something it won't work.

## How embedding works

Grotsky by default generates a magic pattern at compile time. It's 512 bytes and is stored as a static variable.

To generate that pattern we use the [const-random](https://crates.io/crates/const-random) crate.

We use that to define a marker and identify if the Grotsky binary is running in embedded mode or not.

```rust
#[repr(C)]
struct Marker {
    magic_pattern: [u8; 512],
    is_embedded: u8,
}

const fn new_marker() -> Marker {
    Marker{
        magic_pattern: const_random!([u8; 512]),
        is_embedded: 0,
    }
}

static EMBEDDED_MARKER: Marker = new_marker();
```

Then we can use a very hacky trick to take a compiled script and generate an single executable with the embedded bytecode.

```rust
pub fn embed_file(compiled_script: String, output_binary: String) {
    // Get the path of the current executable (Grotsky interpreter)
    let exe_path = env::current_exe().unwrap();
    let mut exe_contents = read(exe_path).unwrap();
    let pattern = &amp;EMBEDDED_MARKER.magic_pattern;

    // Find the magic pattern inside the executable. Given that is a static
    // variable with a value defined at compile time, it has to be stored in
    // the binary, we can find it and switch the `is_embedded` flag.
    if let Some(pos) = find_position(&amp;exe_contents, pattern) {
        // We defined the Marker struct with a C representation
        // which means that right after the magic PATH we have a byte
        // that indicates if the interpreter is running in embedded mode or not.
        exe_contents[pos+512] = 1;

        // We add the magic pattern at the end of the executable again.
        // As a stop mark that right after that the bytecode will come.
        for i in 0..512 {
            exe_contents.push(pattern[i]);
        }

        // Now we read the compiled code and add it to the end of the new executable.
        let mut compiled_content = read(compiled_script).unwrap();
        exe_contents.append(&amp;mut compiled_content);

        // We write a single file with the bytecode concatenated at the end.
        write(output_binary, exe_contents).unwrap();
    }
}

// Function to find the position of magic pattern in a stream of bytes
fn find_position(haystack: &amp;Vec<u8>, needle: &amp;[u8; 512]) -> Option<usize> {
    if haystack.len() < needle.len() {
        return None;
    }
    for i in 0..=haystack.len() - needle.len() {
        if &amp;haystack[i..i + needle.len()] == needle.as_ref() {
            return Some(i);
        }
    }
    None
}
```

We're using the magic pattern as a stop mark. Our resulting binary will have the same magic pattern twice.
First is the original that gets loaded as a global static variable. The second one is almost at the end of
the file and indicates the beginning of the embedded bytecode.

We also need a function to detect if we're running under "embedded" mode. In that case the interpreter should only
read the embedded bytecode and execute it.

```rust
pub fn is_embedded() -> bool {
    let embedded_indicator = &amp;EMBEDDED_MARKER.is_embedded as *const u8;
    unsafe {
        // Need to perform this trick to read the actual memory location.
        // Otherwise during compilation Rust does static analysis and assumes
        // this function always returns the same value.
        return ptr::read_volatile(embedded_indicator) != 0;
    }
}
```

We change the value without the Rust compiler ever knowing, so we do a volatile read of the pointer to make sure
we actually load the value from memory.

Otherwise the Rust compiler assumes that this always returns 0, because it is hardcoded in the `new_marker` function
and is never changed in the codebase.

Now we can proceed to run in "embedded" mode.

```rust
pub fn execute_embedded() {
    // Get path of current executable
    let exe_path = env::current_exe().unwrap();
    interpreter::set_absolute_path(exe_path.clone().to_str().unwrap().to_string());

    let exe_contents = read(exe_path).unwrap();
    let pattern = &amp;EMBEDDED_MARKER.magic_pattern;

    // The offset is 512 because that's the size of the magic pattern
    let offset: usize = 512;

    // Find first match (original)
    let first_match = find_position(&amp;exe_contents, pattern).unwrap();

    // We try to find the second mark by reading what comes after the first one
    let remaining = &amp;exe_contents[first_match+offset..].to_vec();
    let pos = find_position(remaining, pattern).unwrap();

    // The bytecode is located right after the second mark
    let compiled_content = &amp;remaining[pos+offset..];
    
    // Run interpreter from bytecode
    if !interpreter::run_interpreter_from_bytecode(&amp;compiled_content) {
        println!("Could not read embedded script");
        exit(1);
    }
}
```

With all those function only thing I need to do is add an if-statement to the `main` function in the Rust project
to check if we're on embedded mode and proceed accordingly.

```rust
fn main() {
    if embed::is_embedded() {
        embed::execute_embedded();
        return;
    }
    // Continue executing normally
    // ...
}
```

That's it. That's all that takes to implement single binaries with Grotsky.
Continue reading to see an example of how to actually use this feature.

## Embedding example: Make your own Grep

Let's try to reproduce a simple version of the well-known Unix tool `grep`.

Store the following script in a file called `grep.gr`:

```js
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
```

Then it can be used like this:

```
$ cat file.txt | ./grotsky grep.gr pattern
```

And it will print all lines that match the "pattern".

We can also package it as a single binary by doing the following commands.

```
$ ./grotsky compile grep.gr
$ ./grotksy embed grep.grc
```

Now we should have a `grep.exe` in our directory. And we can use it:

```
$ chmod +x grep.exe
$ cat file.txt | ./grep.exe pattern
```

Should work the same as the previous example.
