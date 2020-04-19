---
layout: post
title: "Writing your own C malloc and free"
excerpt: "Challenge for writing your own implementation of malloc and free."
author: "Miguel Liezun"
tags: malloc,free,tutorial
---

# Writing your own C malloc and free

## Challenge

This challenge comes from the book Crafting Interpreters by Bob Nystrom. And can be found in [Chapter 14 - Challenge 3](http://www.craftinginterpreters.com/chunks-of-bytecode.html#challenges).

The challenge goes:

> You are allowed to call malloc() once, at the beginning of the interpreter’s execution, to allocate a single big block of memory which your reallocate() function has access to. It parcels out blobs of memory from that single region, your own personal heap. It’s your job to define how it does that.

## Solution

As stated in the challenge I'll be using a big chunk of _contiguous_ memory. The main idea of my solution is to store the blocks of memory in the array prepending a header with metadata.

```
 _______________________________________________
|head_0|block_0 ... |head_1|block_1    ...      |
 ¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯
```

The structure of the header is pretty similar to that of a linked list.

```c
struct block_meta
{
    size_t size;
    struct block_meta *next;
    int free;
};

#define META_SIZE sizeof(struct block_meta)
```

It stores the size of the block, a pointer to the next block and a flag to mark wether it's free or not.

Then, a function to traverse the list of blocks and find if there is any freed block is needed:

```c
void *first_block = NULL;

struct block_meta *find_free_block(struct block_meta **last, size_t size)
{
    struct block_meta *current = first_block;
    while (current && !(current->free && current->size >= size))
    {
        *last = current;
        current = current->next;
    }
    return current;
}
```

This function receives a double pointer to a block_meta struct called `last` that at the end of the execution should be pointing to the last node of the list and a size_t variable that indicates the minimum size that the block needs to be.

#### Memory initialization

Two functions are needed to handle the big chunk of memory, one to initialize and the other to free it.

```c
void initMemory();
void freeMemory();
```

To implement `initMemory` I've decided that I would ask for the maximum amount of memory that I could get from the OS.

```c
#define MINREQ 0x20000

// Big block of memory
void *memory = NULL;
// Position where the last block ends
size_t endpos = 0;

void initMemory()
{
    size_t required = PTRDIFF_MAX;
    while (memory == NULL)
    {
        memory = malloc(required);
        if (required < MINREQ)
        {
            if (memory)
            {
                free(memory);
            }
            printf("Cannot allocate enough memory\n");
            exit(ENOMEM);
        }
        required >>= 1;
    }
}

void freeMemory()
{
    free(memory);
}
```

As you can see, `initMemory` starts trying to allocate the maximum amount a memory allowed, and starts to divide that amount by 2 every time the allocation fails. If there isn't at least 128KB of memory available the program crashes with ENOMEM.

Now that we have our chunk of memory ready to go, we can start to start giving blocks away.

```c
struct block_meta *request_block(size_t size)
{
    struct block_meta *last = NULL;
    struct block_meta *block = find_free_block(&last, size);
    if (block)
    {
        block->free = 0;
        return block;
    }
    // Append new block to list
    block = memory + endpos;
    endpos += META_SIZE + size;
    if (last)
    {
        last->next = block;
    }
    else
    {
        first_block = block;
    }
    block->free = 0;
    block->next = NULL;
    block->size = size;
    return block;
}
```

How `request_block` works:

1. Tries to find a free block with enough space. If there is one, it is set as occupied and returns that block.
2. If there isn't a free block available. It adds a new block with enough space at the end of `memory` (the big chunk).
3. If this is the first call, points the head of the list to the recently created block, else point the last node to the block.
4. Set the new block as occupied, set the size and next to null. Then return the new block.

With this function, implementing `malloc` and `free` is pretty easy:

```c
void *my_malloc(size_t size)
{
    struct block_meta *block = request_block(size);
    return block + 1;
}

void my_free(void *ptr)
{
    struct block_meta *block = ptr - META_SIZE;
    block->free = 1;
}
```

To finish the challenge, I have to implement realloc, that is a little bit more tricky.

```c
void *my_realloc(void *ptr, size_t size)
{
    if (!ptr)
    {
        return my_malloc(size);
    }
    struct block_meta *block = ptr - META_SIZE;
    if (block->size >= size)
    {
        return block + 1;
    }
    uint8_t *newptr = my_malloc(size);
    size_t i;
    for (i = 0; i < (block->size < size ? block->size : size); i++)
    {
        newptr[i] = ((uint8_t *)ptr)[i];
    }
    block->free = 1;
    return newptr;
}
```

How realloc works:

- If the pointer to reallocate is null, works just like malloc.
- If the given size is bigger than the prior size, it allocates a bigger block and copies all data from the original block to the new block.
- If the given size is smaller than the prior size, it allocates a smaller block and copies just the data that fits into the smaller block.

## New challenge

In my implementation I used a linked list where each node holds a pointer to the next, but given that I have control over the _entire_ memory this actualy isn't necessary.

My challenge to you is that you remove the pointer to next from the `block_meta` struct.

## Resources

- https://danluu.com/malloc-tutorial/
- http://www.craftinginterpreters.com/chunks-of-bytecode.html
