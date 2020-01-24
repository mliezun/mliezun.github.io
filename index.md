---
layout: default
title: Blog
---

<div class="posts">
  {% for post in site.posts %}
    <div class="post_info">
      <h3 style="margin-bottom: 10px"><a href="{{ post.url }}">{{ post.title }}</a></h3>
      <small>{{ post.date | date_to_long_string: "ordinal" }}</small>
      <p>{{ post.excerpt }}</p>
    </div>
  {% endfor %}
</div>
