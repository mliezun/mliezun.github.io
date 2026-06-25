---
title: "What happened in December 2025 or how I got a 40x speedup?"
excerpt: "I'm quite late to the discussion, but everyone has been saying that they have not written code since December. What happened? The release of Gemini 3 Pro, GPT-5.1 and Claude Opus 4.5 was a game changer. It was the first time that models were 'smart enough' to accomplish complex tasks."
author: "Miguel Liezun"
tags: rust,ai,speedup
image: /assets/images/rust-and-gemini.png
ai-assisted: false
---

# What happened in December 2025 or how I got a 40x speedup?

![Rust and Gemini](/assets/images/rust-and-gemini.png)

I'm quite late to the discussion, but everyone has been saying that they have not written code since December.

## What happened?

In November 2025 the release of Gemini 3 Pro, GPT-5.1 and Claude Opus 4.5 was a game changer. It was the first time that models were "smart enough" to accomplish complex tasks.

Since around August 2024 I tried using Agentic coding (via Cursor) to improve the performance of [Grotsky](https://github.com/mliezun/grotsky), a toy programming language whose interpreter is written in Rust.

I didn't get much improvements until November/December 2025.

In that period of 15 months I tried putting the following prompt through different models in several occasions.

```md
This project is called Grotsky a toy programming language whose interpreter is written in Rust.

To compile test and run benchmarks do:
<list-of-commands>

I want to optimize performance, since the current interpreter is very slow.

Setup a cpu profiler to analyze where the time is spent in the Rust code.

Optimize the code based on the profiling result.

Each time you modify the code compile, run tests and benchmarks to confirm the speedup.

Keep iterating while there's still room for improvement.
```

As you can see it was a very high level prompt where I didn't give it any instructions or guidance about the underlying codebase or how to integrate the profiler itself.

Until November 2025 I would always hit a roadblock with this approach, where the model would not be able to figure out how to integrate the profiler or it would change the codebase in a way that broke all the tests and not be able to recover.

But between November 30th and December 1st, armed with Cursor and Gemini 3 Pro, I finally got it working:

[https://github.com/mliezun/grotsky/pull/9](https://github.com/mliezun/grotsky/pull/9)

As you can see in the PR description:

```md
Integration Test:
    Master total time: 145.849s (test output) / 140.96s (user cpu)
    Optimized total time: 4.737s (test output) / 3.58s (user cpu)
    Speedup (test time): 145.849 / 4.737 = 30.78x
    **Speedup (user cpu): 140.96 / 3.58 = 39.37x**
```

That's basically a 40x speedup. "User cpu" means the time that the program is actually running.


The program used for integration testing, is this blog's engine, which is indeed written in Grotsky. The program takes plain markdown files and turns them into HTML.


This is a testament of how poorly I had written the interpreter. There was a lot of low hanging fruit to be optimized. But it was also the first time when I experienced how a powerful LLM with a tight agentic loop would actually compound and produce a virtuous result.

You could say that this was the point the LLMs surpassed human (me) abilities.

## What was the optimization?

Basically the codebase was infested with `.clone()`, which was copying memory and generating delays each time it was called, the AI model was smart enough to figure out how to get rid of that while complying with Rust's borrow checker and passing all conformance tests.

---

This blogpost was rendered by that optimized code.
