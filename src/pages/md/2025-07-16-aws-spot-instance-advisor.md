---
title: "AWS Spot instance advisor"
excerpt: "Spot instances are very useful for background jobs where you can afford them to be interrupted and retried. There's a useful tool that AWS provides called Instance Advisor where you can see which instances are more requested and try to avoid them."
author: "Miguel Liezun"
tags: ec2,aws,spot,instances,cloud
---

# AWS Spot instance advisor

Spot instances are very useful for background jobs where you can afford them to be interrupted and retried, in return you usually pay a fraction of the cost, up to a 90% discount on the on-demand price. AWS provides a tool called Instance Advisor where you can see which instances are more requested and try to avoid them.

Let's see a comparison between Graviton 3 and Graviton 4 ARM instances.

m7gd instances are Graviton 3 with local SSD and they get interrupted a lot >20% of the time.

![Graviton 3](/assets/images/aws-spot-instances/m7gd.png)

m8gd are the latest Graviton 4 with local SSD and they get interrupted between 5-20% of the time based on which instance type you choose. This could be due to slower adoption of newly released instances.

![Graviton 4](/assets/images/aws-spot-instances/m8gd.png)


In general it's a good idea to check the frequency of interruption here to optimize your spot instance usage:

[https://aws.amazon.com/ec2/spot/instance-advisor/](https://aws.amazon.com/ec2/spot/instance-advisor/)
