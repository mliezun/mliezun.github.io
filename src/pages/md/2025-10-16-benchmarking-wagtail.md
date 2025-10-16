---
title: "Benchmarking Wagtail CMS Across Python Versions"
excerpt: "I spent some time benchmarking Wagtail CMS across different Python versions to see how performance varies. The results are pretty interesting - Python 3.11 comes out on top with some solid improvements over 3.10."
author: "Miguel Liezun"
tags: python,benchmarking,performance,wagtail,cms
image: /assets/images/wagtail-benchmark/rps_comparison.png
---

# Benchmarking Wagtail CMS Across Python Versions

**Testing real-world performance across 8 different Python versions**

*Published: October 16, 2025*

## Introduction

I've been curious about how different Python versions perform in real-world web applications. Python keeps getting faster with each release, but I wanted to see how much of a difference it actually makes when running a real application under load.

So I decided to benchmark **Wagtail CMS**—a Django-based content management system, tested across 8 different Python versions. This is the first in what I hope will be a series of benchmarks testing different Python web applications.

Here's what I tested:
- **Python 3.10** (our baseline)
- **Python 3.11** 
- **Python 3.12**
- **Python 3.13**
- **Python 3.13t** (free-threaded, GIL disabled)
- **Python 3.14**
- **Python 3.14-tailcall** (experimental tailcall optimization)
- **Python 3.14t** (free-threaded, GIL disabled)

The results were pretty interesting! You can check out the full benchmark setup and results at [https://github.com/mliezun/python-web-benchmarks](https://github.com/mliezun/python-web-benchmarks).

## How I Set Up the Tests

### The Setup
I wanted to keep things realistic, so I used:
- **Wagtail CMS 6.3** with Django 5.1.4 (a real production setup)
- **Gunicorn 21.2.0** as the WSGI server
- **SQLite** with actual content (15+ blog posts, multiple pages)
- **Apache Bench (ab)** for load testing
- **Docker** to keep everything isolated and reproducible

For the experimental Python versions, I used custom Docker images:
- `ghcr.io/mliezun/python-web-benchmarks/python-freethreaded:3.14t-slim-20251015`
- `ghcr.io/mliezun/python-web-benchmarks/python-freethreaded:3.13t-slim-20251015`  
- `ghcr.io/mliezun/python-web-benchmarks/python-freethreaded:3.14-tailcall-slim-20251015`

### Test Scenarios
I ran three scenarios that you'd actually encounter in real usage:

1. **Homepage Load**: Full page with navigation, sections, and dynamic content
2. **Admin Login**: Authentication and admin interface access  
3. **Blog Browsing**: Listing and viewing blog posts

Each scenario was tested with **1, 5, 10, and 20 concurrent users** to see how things scale.

### What I Measured
- **Requests per Second (RPS)**: How many requests we can handle
- **Response Time**: Average, p50, p95, and p99 percentiles
- **CPU Usage**: How hard the server was working
- **Memory Usage**: RAM consumption during tests

## The Results

### Overall Throughput Performance

![RPS Comparison](/assets/images/wagtail-benchmark/rps_comparison.png)

Here's how many requests per second each Python version can handle. Higher is better, obviously.

### Response Time Analysis

![Response Time Comparison](/assets/images/wagtail-benchmark/response_time_comparison.png)

This shows how response times change as we add more concurrent users. Lower is better here.

### Relative Performance Improvements

![Performance Gains](/assets/images/wagtail-benchmark/performance_gains.png)

This is probably the most interesting chart - it shows how much faster each version is compared to Python 3.10 (our baseline). Positive numbers mean it's faster.

### Resource Utilization

![Resource Usage](/assets/images/wagtail-benchmark/resource_usage.png)

CPU and memory usage is important for capacity planning. You want good performance without burning through resources.

## What I Found

### 🏆 Python 3.11 is the Winner

**Python 3.11 came out on top** with about 3.2% better performance than Python 3.10 on average. That might not sound like much, but when you're handling thousands of requests per day, it adds up.

### The Big Picture

1. **Experimental versions are interesting**: Python 3.14t (free-threaded) shows some promising results for concurrent workloads, but I'd be careful about using it in production just yet.

2. **All versions scale well**: Every version handled 20 concurrent users without breaking a sweat. The newer versions just do it slightly better.

3. **Memory usage is consistent**: All versions used roughly the same amount of RAM (~300-360 MB), so upgrading won't cost you more in memory.

4. **Everything was stable**: Zero errors across all tests. All versions are production-ready.

## My Recommendations

### For Production

**Go with Python 3.11** if you want the best performance. It's stable, fast, and has been around long enough that most packages support it well.

**Python 3.12** is also a solid choice if you want something newer but still conservative.

I'd hold off on the experimental versions (3.14t, 3.14-tailcall) for production use until they're more mature.

### If You're Upgrading

If you're currently on Python 3.10 or earlier, here's what I'd suggest:

**Important note**: Python 3.10 reaches end-of-life on **October 31, 2026** according to the [Python Developer's Guide](https://devguide.python.org/versions/). After that date, it will only receive security fixes, so you'll want to plan your upgrade well before then.

1. **Test everything**: Run your full test suite on the target version first
2. **Check your dependencies**: Make sure all your packages support the new version  
3. **Benchmark your specific app**: My results are for Wagtail - your mileage may vary
4. **Deploy carefully**: Use canary deployments or blue-green strategies

The good news is that memory usage is pretty consistent across versions, so you won't need to resize your servers.

## Wrapping Up

So what did I learn from all this testing?

**Python version upgrades are worth it.** You get measurable performance improvements without needing more resources. Python 3.11 is the sweet spot right now - fast, stable, and well-supported.

The experimental versions are definitely interesting to watch. The free-threaded versions (3.13t, 3.14t) could be a game-changer for certain workloads, but I'd wait until they're more mature before using them in production.

I'm planning to benchmark more Python web applications in the future - maybe Django REST Framework, FastAPI, or even some data processing workloads. If you have suggestions for what to test next, let me know!

You can find all the benchmark code, results, and setup instructions at [https://github.com/mliezun/python-web-benchmarks](https://github.com/mliezun/python-web-benchmarks). Feel free to run your own tests or contribute to the project.
