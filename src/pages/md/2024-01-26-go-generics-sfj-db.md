---
title: "Go Generics: Single file JSON DB"
excerpt: "Storing your data in a single json file can be useful when there isn't much state that needs to be tracked. In this post we leverage Go's generics to implement a simple JSON DB."
author: "Miguel Liezun"
tags: markdown,parser,blog
---

# Go Generics: Single file JSON DB

Let's start with an example use case: you have a multitenant web server that serves pages for various customers, you can know how to which page to serve based on `Host` header in the request.

You can track each site in a struct like this:

```go
type Site struct {
    Name    string  `json:"name"`
    Host    string  `json:"host"`
}
```

Your `sites.json` file could be something like this:

```json
{
    "www.example.com": {
        "name": "Example",
        "host": "www.example.com",
    }
}
```

Which can be opened as a db:

```go
sitesdb, err := sfjdb.Open[map[string]Site]("./sites.json")
```

Then you can simply get the content of the json file and validate requests:

```go
func handle(w http.ResponseWriter, req *http.Request) {
    sites := sitesdb.View()
    host := req.Header["Host"][0]
    if site, ok := sites[host]; ok {
        // Render sites that are stored in DB
        renderSite(w, req, site)
    } else {
        w.WriteHeader(404)
    }
}
```

## Implementation

Thanks to Go generics and built-in json Marshaling/Unmarshaling this is quite easy to build:

```go
type DB[T any] struct {
	rw       sync.RWMutex
	data     T
	filepath string
}
```

We have a `DB` struct to keep track of the file, data and a `RW` mutex.

Then we can easily read data from a local file:

```go
// Load loads data from file.
func (db *DB[T]) Load() error {
	db.rw.Lock()
	defer db.rw.Unlock()
	content, err := os.ReadFile(db.filepath)
	if err != nil {
		return err
	}
	return json.Unmarshal(content, &db.data)
}
```

Each time we use the data in the DB we make a copy, to avoid modifying some attributes via pointers by mistake.

```go
func objcopy[T any](obj T) *T {
	data, err := json.Marshal(obj)
	if err != nil {
		panic(err)
	}
	newobj := new(T)
	if err := json.Unmarshal(data, newobj); err != nil {
		panic(err)
	}
	return newobj
}


// View returns a copy of the data.
func (db *DB[T]) View() T {
	db.rw.RLock()
	defer db.rw.RUnlock()
	return *objcopy(db.data)
}
```

We can also save a new state in case we modified something (e.g. added a new site to our list).

```go
// Save saves a copy of the data as plain json in the file.
func (db *DB[T]) Save(data T) error {
	db.rw.Lock()
	defer db.rw.Unlock()
	db.data = *objcopy[T](data)
	content, err := json.Marshal(db.data)
	if err != nil {
		return err
	}
	return WriteFile(db.filepath, content, 0644)
}
```

You can get the `WriteFile` function [here](https://github.com/tailscale/tailscale/blob/main/atomicfile/atomicfile.go).

This function writes the file atomically, which means is sucessfully written or not written at all.


Finally we have to implement `Open` to instantiate our DB:

```go
// Open opens a json file as a database.
func Open[T any](filepath string) (db *DB[T], err error) {
	db = &DB[T]{filepath: filepath}
	if err := db.Load(); err != nil {
		return nil, err
	}
	return db, nil
}
```

## In praise of Go generics

At the beginning I was a little sad about generics, go the simple language was at end becoming a huge complex beast. But overall if you don't over-abuse generics it feels natural and easy to use/understand.

This still feels like the good old Go, but just a bit more power in the right way.

If you wish to use this in your project you can just import it from [https://github.com/mliezun/sfj-db](https://github.com/mliezun/sfj-db).
