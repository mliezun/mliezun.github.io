---
title: "What's in the future?"
excerpt: ""
author: "Miguel Liezun"
tags: future,plans,predictions,python,web
image: /assets/images/length-of-tasks-log.png
ai-assisted: false
---

# What's in the future?

![Length of tasks log](/assets/images/length-of-tasks-log.png)

Capabilities of AI tools are still advancing rapidly, doubling the length of tasks AI can do every 7 months.

At the end of 2025, we're sitting at around 5 hours. This means that AI tools can now complete tasks that would take a human around 5h and they succeed 50% of the time.

By the end of 2026 this will be close to 20 hours roughly, that's almost equivalent to a human work-week.

But what's more striking is that for Software Engineering this is accelerating at a higher pace.

![Time Horizon SWE](/assets/images/time-horizon-swe.png)

For coding, we're seeing capabilities double in just 70 days!

By extrapolating this trend, discussing this with friends and seeing what people are saying online we can see that the burden of software is less and less coding and increasingly about proper design and verification.

Even Karpathy is saying: [Software 2.0 easily automates what you can verify.](https://x.com/karpathy/status/1990116666194456651)

He's talking about writing software to solve problems that can be verified to be correct or not with a certain grade of accuracy.

For coding in particular this means we need tools to verify the quality of the code written. The better our tools are to formally verify the code the more we can trust our automation to work.

Seeing the landscape of what's out there I think we're missing a tool that has all of the following:

- Ownership of the software process: Design + Implement + Test (like Cursor)
- Hosts the code itself (like Github/Gitlab)
- Runs the code and makes it available (like Vercel)
- Checks that the code is correct and provides guardrails to users (static analysis)
- Is opinionated in what technology should be used (e.g. Python only hosting)
- Provides integration with other services (e.g. easy Stripe integration)
- Open source

The closest we have to this is Lovable, Replit and v0 from Vercel.

But those platforms still rely on external services and are not open source. I think LLMs will work best when we're able to let them handle the full environment were our code lives and making them open source will enable people to trust them and run them on their own.
