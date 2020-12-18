---
layout: post
title: "Grotsky Part 4: Writing a service to get your public IP"
excerpt: "Part 4 of building my own laguage series. This time I write and deploy a service to Heroku that let's your retrieve your pulbic IP."
author: "Miguel Liezun"
tags: grotsky,service,http,heroku,ip
---

# Writing a service to get your public IP

[Grotsky](https://github.com/mliezun/grotsky) (my toy programming language) finally can be used to make something useful.

In this post I want to show you how I made a service that let's your retrieve your public IP as a response to a HTTP Request.

## Show me the code

Let's start by building the http request handler.

The service will be deployed to heroku. Heroku passes the port that the http server has to listen as an environment variable named `PORT`.

#### Let's get the server up and running

```
let listen = ":8092"
let port = env.get("PORT")
if port != "" {
    listen = ":" + port
}

io.println("Listen " + listen)
http.listen(listen)
```

We listen by default at the port 8092 and if the environment variable is given we change it.

Then we print what is the port and start the server with `http.listen`. That blocks the execution and starts the server.

Grotsky interpreter is written in Go, and uses Go's standard http server. Each requests is handled by a goroutine, but because Grotsky is single threaded only one goroutine executes at any given point in time. 

When a request is received the goroutine has to hold the GIL (Global Interrupt Lock) to be able to give control to the interpreter.

#### Now lets add some code to handle requests

```
fn getIP(rq, rs) {
    io.println("Request from --> " + rq.address)
    rs.write(200, rq.address)
}

http.handler("/", getIP)

let listen = ":8092"
let port = env.get("PORT")
if port != "" {
    listen = ":" + port
}

io.println("Listen " + listen)
http.listen(listen)
```

Now we have something interesting to try out!

What we've done is to log and write back as response the address of the device that is doing the request.

To try it out you need to download grotsky.

```bash
$ go get github.com/mliezun/grotsky/cmd/grotsky
```

Save the Grotsky code under a filed called `getip.g` and the execute it using the grotsky interpreter:

```bash
$ go run $(go env GOPATH)/src/github.com/mliezun/grotsky/cmd/grotsky getip.g
```

Output:
```
Listen :8092
```

Now you can make a request to see if it is working

```bash
$ curl localhost:8092
```

Output:
```
[::1]:43464
```

We see that the address contains the port we want to split it and show just the IP.


#### Let's write a couple functions to do that

```
fn findReversed(string, char) {
    for let i = string.length-1; i > -1; i = i - 1 {
        if string[i] == char {
            return i
        }
    }
    return -1
}

fn parseIP(address) {
    let ix = findReversed(address, ":")
    return address[:ix]
}
```

The function `findReversed` finds the first index where `char` appears in `string` starting from the end.

The function `parseIP` uses `findReversed` to obtain the index where ":" splits the IP and the PORT and uses that index to return just the IP address.

#### Now we can send just the IP address

```
fn getIP(rq, rs) {
    let address = parseIP(rq.address)
    io.println("Request from --> " + address)
    rs.write(200, address)
}
```

Add the two functions at the beginning of the file and modify the getIP function.

Restart the server and now if you make a request you should get just the IP.

```
$ curl localhost:8092
[::1]
```

Voila!


#### We have just one last issue: Proxies!

Our service will probably sit behind a proxy, so we need to read the address from a special header `X-Forwarded-For`.

Let's implement that!

```
fn getIP(rq, rs) {
    let address = parseIP(rq.address)
    let forwarded = rq.headers["X-Forwarded-For"]
    if forwarded != nil {
        address = forwarded[0]
    }
    io.println("Request from --> " + address)
    rs.write(200, address)
}
```

We read the header from the request and if `X-Forwarded-For` is present we sent that as a response to the user.

#### Our work is complete. Let's try it!

```
$ curl localhost:8092 -H 'X-Forwarded-For: 8.8.8.8'
8.8.8.8

$ curl localhost:8092
[::1]
```

Well done. Now you can deploy it to Heroku (that's up to you) or any other cloud platform.

I have my own version running under: https://peaceful-lowlands-45821.herokuapp.com/


#### Try it from your command line

```bash
$ curl https://peaceful-lowlands-45821.herokuapp.com/
```

