### The Enduring Simplicity of C

I recently came across a video by Salvatore Sanfilippo, the creator of Redis, titled "Why I use C and not Rust". It made me stop and think about the constant push for newer, "safer" programming languages.

Watch the video [here](https://www.youtube.com/watch?v=5SLsH755XAA).

The gist of his argument is that while C has well-known memory safety issues, the modern alternatives, particularly Rust, come with their own significant costs. This isn't just about nostalgia for an older language; it's a pragmatic choice based on a different set of values.

His points really resonated with me:

- **Safety has a complexity cost.** Rust's main selling point is memory safety, but this safety net makes certain things, like a doubly linked list, much more complex to implement. Sanfilippo argues that he'd rather have the directness and simplicity of C and manage the risks with good practices and tools like Valgrind.
- **The curse of hyper-dependencies.** He makes a fascinating point that C's lack of a built-in package manager is a feature, not a bug. In ecosystems like Rust or Node.js, it's incredibly easy to accumulate massive dependency trees for simple projects. C forces you to be more deliberate.
- **The need for speed.** The feedback loop in programming is critical. Sanfilippo notes that C compiles in seconds (or fractions of a second), while Rust is known for "biblical" compilation times. He argues that waiting for the compiler kills productivity and flow.
- **AI understands C better.** This was the most surprising insight. Because of C's simple semantics and the sheer volume of C code in the world, LLMs are currently much better at reasoning about and generating C code than Rust. In an age where AI is becoming a co-pilot, this is a huge practical advantage.

It's not about being against progress. It's a realization that the "new and safe" way isn't always the "better" way. In engineering we always face compromise and deciding which language to use is just one of those cases.

Personally, I like both languages, I'm more fond of C because of its simplicity, but the Rust toolchain and community pushing it forward makes it really easy to start a project and get everything you need to start building.

A system level programmer like Salvatore might pick C because he has the need to build an object system perfectly tailored for his application. But I mostly spend time writing Python for APIs and glue code, I would pick up Rust when I'm in the need for a little more speed because it's faster than an interpreted language.
