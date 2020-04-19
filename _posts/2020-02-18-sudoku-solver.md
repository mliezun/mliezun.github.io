---
layout: post
title: "Sudoku Solver"
excerpt: "Iterative + recursive sudoku solver using python magic methods."
author: "Miguel Liezun"
tags: sudoku,python,solver
---

# Sudoku Solver

I wanted to make my own sudoku solver to challenge myself.

Im not a sudoku player so my approach is a brute force scan of possible combinations sort-of.

I just know the basic rules:

- Numbers 1-9 are allowed.
- Numbers in the same row cannot be repeated.
- Numbers in the same column cannot be repeated.
- Numbers in the 3x3 square cannot be repeated.

The first thing i did was to build a some classes that calculates the possible values a cell can have if it's empty, based on the constraints.

I came up with 3 classes:

- `Board` that stores the entire board.
- `BoardSlice` that stores a slice of a board. An object of this type is returned when a `Board` is sliced (method `__getitem__`).
- `Cell` that stores the value of a single cell and calculates all possible values a cell can take.

The class `Cell` receives a board, the coordinates on the board, and the value that holds. Also has the method options that uses python `set` data structure to calculate the posibilites.

If you look at the following snippet you can see that the method `options`
generates the sets: `options` that contains all possible options (1-9), `row` that contains all the numbers that are in the same row, `column` that contains all the numbers that are in the same column and `square` that contains all the numbers that are in the same 3x3 square. The return value is `options` without all the used values.

```python
class Cell:
    def __init__(self, b, i, j, value):
        self.b = b
        self.value = value
        self.i = i
        self.j = j

    def options(self):
        if self.value != 0:
            return {self.value}
        options = set(range(1, 10))
        row = set(map(lambda x: x.value, self.b[self.i]))
        column = set(map(lambda x: x.value, self.b[:][self.j]))
        def to_square(k): return slice((k // 3) * 3, (k // 3) * 3 + 3)
        square = set(
            map(lambda x: x.value,
                self.b[to_square(self.i)][to_square(self.j)]))
        return options - row - column - square - {0}
```

To make easier the implementation of the square I used the class `BoardSlice` that contains a slice of a board and implements the magic method `__getitem__`.

```python
class BoardSlice:
    def __init__(self, board_slice):
        self.board_slice = board_slice

    def __getitem__(self, items):
        if type(items) == slice:
            return (el for row in self.board_slice for el in row[items])
        if type(items) == int:
            return (row[items] for row in self.board_slice)
        raise KeyError
```

The base class: `Board` contains the board and a copy method that copies all the values and creates a new `Board` object. This is necessary to avoid messing with object references and have a clean object when needed.

```python
class Board:
    def __init__(self, board):
        self.board = [[Cell(self, i, j, value)
                       for (j, value) in enumerate(row)] for (i, row) in enumerate(board)]

    def copy(self):
        return Board(((cell.value for cell in row) for row in self.board))

    def __getitem__(self, items):
        if type(items) == int:
            return self.board[items]
        if type(items) == slice:
            return BoardSlice(self.board[items])
        raise KeyError

    def __repr__(self):
        return repr(self.board)
```

With these tools the next step is to solve the problem!

My idea was to generate a mixed iterative-recursive algorithm.

The first pass will be iterative, and if needed, the second pass will be recursive.

#### Iterative pass

Iterates over the whole board and calculates the options that each cell can have. If a cell has only one option set that option on the cell and set a flag to repeat the iterative pass, if has 0 options return `None` meaning that the board has no solutions, and if has more than one option store the options for the recursive pass.

If the loop ends and we found that no cell has more than one option then we solved the board!

The idea of this first step is to solve an _easy_ board quickly.

#### Recursive pass

If the iterative pass ends and we found that a cell has more than one option then we try all that options and call solve again!

If solve returns a board that means we've found the solution!

If solve returns None (back at the iterative passs) we have to try with another options.

#### BoardSolver

The class is pretty straightforward.

```python
class SudokuSolver:
    @staticmethod
    def solve(board):
        b = board.copy()
        # First pass: Iterative
        board_map = {}
        exhaust = False
        while not exhaust:
            exhaust = True
            for i in range(9):
                for j in range(9):
                    cell = b[i][j]
                    if cell.value == 0:
                        options = cell.options()
                        if len(options) == 1:
                            cell.value = options.pop()
                            exhaust = False
                        elif len(options) == 0:
                            return None
                        elif len(board_map) == 0:
                            board_map[(i, j)] = options

        # Second pass: Recursive
        for ((i, j), options) in board_map.items():
            for op in options:
                b[i][j].value = op
                solved = SudokuSolver.solve(b)
                if solved:
                    return solved
            return None

        return b
```

#### Conclusions

Actually my implementation is not a brute force algorithm, is a search algorithm, that searches the path to solving a board. Because it doesn't try all values on all cells nonsensically, it rather tries _some_ options for a given cell and advances to the next option as _soon_ as it detects that it's not the correct path.

### Source

Take a look at the [source code](https://github.com/mliezun/sudoku-solver).
