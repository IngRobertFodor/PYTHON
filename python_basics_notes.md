# 🐍 Python Basics – Notes

> Personal notes, like underlined parts of a textbook. To be expanded over time.

---

## 📑 Contents
1. [Basics](#basics)
2. [Data Types](#data-types)
3. [Conditionals](#conditionals)
4. [Loops](#loops)
5. [Lists](#lists)
6. [Tuples](#tuples)
7. [Sets](#sets)
8. [Dictionaries](#dictionaries)
---

## Basics

**`print()`** — outputs text/values to the screen. Can take multiple values, separated by commas.

```python
print("Hello, world!")
print("Age:", 25)          # multiple values -> "Age: 25"
```

**`end=` parameter** — by default `print()` adds a newline (`\n`) after each call. You can change that with `end=`.

```python
print("Hello", end="")   # no newline – stays on the same line
print("World")
```
Output:
```
HelloWorld
```

```python
print("Hello", end="\n")   # explicit newline – this is the default behavior
print("World")
```
Output:
```
Hello
World
```

**Comments** — ignored by Python, used to explain code. `#` for a single line, `'''` or `"""` for multi-line.

```python
# this is a single-line comment
x = 5   # can also go at the end of a line

"""
This is a
multi-line comment
"""
```

**Indentation** — Python uses indentation (spaces) instead of `{}` to define code blocks (inside `if`, loops, functions...). Consistent indentation is **required**, not just style.

```python
if True:
    print("indented – part of the if block")
print("not indented – runs regardless")
```

**`=` vs `==`**

| Operator | Meaning | Example |
|---|---|---|
| `=` | **assignment** – stores a value in a variable | `x = 5` |
| `==` | **comparison** – checks if two values are equal, returns `True`/`False` | `x == 5` |

```python
x = 5        # assign 5 to x
print(x == 5)   # True  – comparison
print(x == 6)   # False
```

> 💡 A very common beginner mistake is writing `if x = 5:` instead of `if x == 5:` — Python will raise a `SyntaxError` for that, which helps catch it.

---

## Data Types

Python is dynamically typed – a variable's type is determined automatically from its value.

| Type | Example | Description |
|---|---|---|
| `int` | `5` | integer number |
| `float` | `3.14` | decimal number |
| `str` | `"hello"` | text (string) |
| `bool` | `True` / `False` | boolean value |
| `list` | `[1, 2, 3]` | list (mutable) |
| `tuple` | `(1, 2, 3)` | tuple (immutable) |
| `set` | `{1, 2, 3}` | set (unique elements) |
| `dict` | `{"a": 1}` | dictionary (key–value) |
| `NoneType` | `None` | represents "no value" / "nothing" |

```python
x = 5
print(type(x))   # <class 'int'>

y = "text"
print(type(y))   # <class 'str'>
```

**Type conversion:**
```python
int("5")      # 5
str(5)        # "5"
float("3.2")  # 3.2
bool(0)       # False
```

### Adding strings (concatenation)

**Theory:** Strings are joined with `+`. Only `str` + `str` works — numbers must be converted with `str()` first, or use an f-string instead.

```python
first = "John"
last = "Smith"
full = first + " " + last
print(full)   # John Smith

age = 30
# print("Age: " + age)        # TypeError – can't add str + int
print("Age: " + str(age))     # Age: 30   – convert first
print(f"Age: {age}")          # Age: 30   – f-string is usually cleaner
```

> 💡 `*` also works on strings for repetition: `"ab" * 3` → `"ababab"`.

### Escape characters

**Theory:** Special characters inside a string, written with a backslash `\`. Most common: `\n` (new line) and `\t` (tab).

```python
print("Line 1\nLine 2")
# Line 1
# Line 2

print("Name:\tJohn")
# Name:    John
```

> 💡 To print a literal backslash or quote, escape it too: `\\` or `\"`.

---

## Conditionals

**Theory:** `if / elif / else` – run code based on whether a condition is met. `elif` (short for "else if") lets you test multiple conditions in sequence without nesting separate `if` statements — you can chain as many `elif` blocks as needed between `if` and `else`.

```python
score = 75

if score >= 90:
    print("A")
elif score >= 80:
    print("B")
elif score >= 70:
    print("C")
else:
    print("F")
```

Python checks conditions top to bottom and stops at the **first** one that's `True` (here `75 >= 70` → prints `C`; the remaining `elif`/`else` are never even checked).

```python
age = 18

if age < 18:
    print("Minor")
elif age == 18:
    print("Just became an adult")
else:
    print("Adult")
```

> 💡 **Evaluation order:** Python checks conditions top to bottom and runs **only the first one that is `True`** — the rest are skipped entirely. `else` only runs if *none* of the above matched.

**Comparison operators:** `==`, `!=`, `<`, `>`, `<=`, `>=`

**Logical operators:** `and`, `or`, `not`

| Operator | Result is `True` when... |
|---|---|
| `and` | **both** conditions are `True` |
| `or` | **at least one** condition is `True` |
| `not` | **flips** the value (`True` → `False` and vice versa) |

```python
print(True and False)   # False – both must be True
print(True or False)    # True  – only one needs to be True
print(not True)         # False – flipped
```

> 💡 Priority: `not` is evaluated first, then `and`, then `or`. When unsure, use parentheses `()` for clarity.

```python
age = 20
has_license = True

if age >= 18 and has_license:
    print("Can drive a car")
```

**Shorthand (ternary):**
```python
status = "adult" if age >= 18 else "minor"
```

**Chained comparisons:** Python lets you chain conditions instead of using `and`.
```python
x = 5
print(0 < x < 10)   # True   – same as: 0 < x and x < 10
```

---

## Loops

**Theory:** Repeat a block of code. `for` loops over items of a collection (or a range); `while` repeats as long as a condition is `True`.

### `for` loop

```python
fruits = ["apple", "pear", "banana"]

for fruit in fruits:
    print(fruit)
```

```python
for i in range(5):        # 0, 1, 2, 3, 4
    print(i)

for i in range(2, 10, 2): # start, stop, step -> 2, 4, 6, 8
    print(i)
```

**`enumerate()`** – get both index and value:
```python
for i, fruit in enumerate(fruits):
    print(i, fruit)   # 0 apple / 1 pear / 2 banana
```

### `while` loop

```python
count = 0
while count < 3:
    print(count)
    count += 1
```

### Loop control

| Keyword | Description | Example |
|---|---|---|
| `break` | **stops the loop entirely** – jumps out of it, nothing after it in the loop runs again | stop searching once found |
| `continue` | **skips only the rest of the current iteration** – the loop keeps going with the next value | skip an item, keep looping |
| `else` | runs after the loop finishes normally (no `break`) | often used with search loops |

```python
for i in range(5):
    if i == 3:
        break          # loop stops completely at 3
    print(i)
# output: 0 1 2

for i in range(5):
    if i == 3:
        continue       # only skips printing 3, loop continues
    print(i)
# output: 0 1 2 4
```

> 💡 `break` = "stop, exit the loop". `continue` = "skip this one, but keep going".

**List/dict/set comprehensions** are a compact way to build collections using a loop in one line — you'll see this exact pattern (`for x in range(5)`) again in the [Lists](#lists) chapter.

---

## Lists

**Theory:** An ordered, **mutable** collection of items. Can hold different types. Written with `[]`.

```python
fruits = ["apple", "pear", "banana"]
print(fruits[0])      # apple
fruits[1] = "lemon"    # change an item
print(fruits)          # ['apple', 'lemon', 'banana']
```

### List methods

| Method | Description | Example |
|---|---|---|
| `.append(x)` | adds an item to the end | `fruits.append("pear")` |
| `.insert(i, x)` | inserts an item at index `i` | `fruits.insert(0, "melon")` |
| `.remove(x)` | removes the first matching value | `fruits.remove("banana")` |
| `.pop(i)` | removes and returns item at index (default last) | `fruits.pop()` |
| `.sort()` | sorts the list (in-place) | `fruits.sort()` |
| `.reverse()` | reverses the order | `fruits.reverse()` |
| `.index(x)` | returns the index of the first match | `fruits.index("apple")` |
| `.count(x)` | counts occurrences of a value | `fruits.count("apple")` |
| `.extend(list2)` | adds items from another list | `fruits.extend(["kiwi"])` |
| `.copy()` | returns a shallow copy of the list | `fruits.copy()` |
| `.clear()` | empties the list | `fruits.clear()` |

### Useful built-in functions

**Theory:** These are not list *methods* (not called with a dot) – they're built-in functions that take a list (or other iterable) as an argument. Also work on tuples and sets.

```python
numbers = [4, 2, 7, 1]

print(len(numbers))   # 4   – number of items
print(sum(numbers))   # 14  – sum of items
print(min(numbers))   # 1   – smallest item
print(max(numbers))   # 7   – largest item
```

> 💡 `some_list.count(value)` (a method, counts a specific value) is different from `len(some_list)` (a function, counts *all* items).

### `sort()` vs `sorted()`

**Theory:** `.sort()` is a list method – sorts the list **in-place** (changes the original, returns `None`). `sorted()` is a built-in function – works on any iterable and **returns a new sorted list**, leaving the original unchanged.

```python
numbers = [3, 1, 2]

numbers.sort()
print(numbers)   # [1, 2, 3]  – original changed

numbers2 = [3, 1, 2]
result = sorted(numbers2)
print(result)     # [1, 2, 3]  – new list
print(numbers2)   # [3, 1, 2]  – original unchanged
```

> 💡 Use `.sort()` when you don't need the original order anymore. Use `sorted()` when you need to keep the original list intact, or when sorting something other than a list (e.g. a tuple or dict keys). Both accept `reverse=True` and `key=...`.

**Slicing:**
```python
numbers = [0, 1, 2, 3, 4, 5]
print(numbers[1:4])   # [1, 2, 3]
print(numbers[::-1])  # [5, 4, 3, 2, 1, 0]  – reversed
```

**List comprehension (shorthand syntax):**
```python
squares = [x**2 for x in range(5)]
print(squares)   # [0, 1, 4, 9, 16]
```

### Membership operator: `in`

**Theory:** Checks if a value exists inside a collection (list, tuple, set, dict, string). Returns `True` / `False`. Opposite: `not in`.

```python
fruits = ["apple", "pear", "banana"]

print("apple" in fruits)       # True
print("kiwi" in fruits)        # False
print("kiwi" not in fruits)    # True
```

```python
# also works with other types
print("a" in "banana")         # True   – substring check
print(3 in (1, 2, 3))          # True   – tuple
print(3 in {1, 2, 3})          # True   – set
print("name" in {"name": "John"})   # True  – checks dict keys
```

> 💡 Often used inside `if` statements: `if "apple" in fruits:`

### ⚠️ Never modify a list while iterating over it

**Theory:** Changing a list's size (adding/removing items) *while* looping over it directly can skip items or cause bugs, because the loop tracks the list by index/position, and that position shifts as items are added/removed.

```python
numbers = [1, 2, 3, 4, 5]

# ❌ Wrong – modifying while iterating
for n in numbers:
    if n % 2 == 0:
        numbers.remove(n)   # skips items! result: [1, 3, 5] but not by design
```

```python
# ✅ Correct – iterate over a copy instead
numbers = [1, 2, 3, 4, 5]
for n in numbers.copy():     # .copy() makes a copy
    if n % 2 == 0:
        numbers.remove(n)
print(numbers)   # [1, 3, 5]
```

```python
# ✅ Or, even better – build a new list instead of mutating
numbers = [1, 2, 3, 4, 5]
numbers = [n for n in numbers if n % 2 != 0]
print(numbers)   # [1, 3, 5]
```

---

## Tuples

**Theory:** Like a list, but **immutable** – cannot be changed after creation. Written with `()`. Used for data that shouldn't change (coordinates, dates).

```python
coordinates = (10, 20)
print(coordinates[0])   # 10
# coordinates[0] = 5   -> TypeError, cannot be changed
```

### Tuple methods

| Method | Description | Example |
|---|---|---|
| `.count(x)` | counts occurrences of a value | `coordinates.count(10)` |
| `.index(x)` | returns the index of the first match | `coordinates.index(20)` |

**Unpacking:**
```python
x, y = coordinates
print(x, y)   # 10 20
```

> 💡 It's worth using a tuple instead of a list when you want to signal the data shouldn't change, or when you need a lighter/faster structure.

---

## Sets

**Theory:** An unordered collection of **unique** items. Written with `{}`. Useful for removing duplicates and doing set-math operations.

```python
a = {1, 2, 3, 3, 2}
print(a)   # {1, 2, 3} – duplicates removed
```

### Set methods

| Method | Description | Example |
|---|---|---|
| `.add(x)` | adds an item | `a.add(4)` |
| `.remove(x)` | removes an item (error if missing) | `a.remove(2)` |
| `.discard(x)` | removes an item (no error) | `a.discard(10)` |
| `.union(b)` | union of sets | `a.union(b)` or `a \| b` |
| `.intersection(b)` | intersection of sets | `a.intersection(b)` or `a & b` |
| `.difference(b)` | difference of sets | `a.difference(b)` or `a - b` |
| `.clear()` | empties the set | `a.clear()` |
| `.issubset(b)` | checks if `a` is entirely contained in `b` | `a.issubset(b)` |
| `.issuperset(b)` | checks if `a` entirely contains `b` | `a.issuperset(b)` |
| `.isdisjoint(b)` | checks if the sets have no common items | `a.isdisjoint(b)` |

```python
a = {1, 2, 3}
b = {2, 3, 4}
print(a | b)   # {1, 2, 3, 4}
print(a & b)   # {2, 3}
print(a - b)   # {1}

print({1, 2}.issubset(a))   # True
print(a.isdisjoint({9, 10}))  # True – no items in common
```

---

## Dictionaries

**Theory:** A collection of **key : value** pairs. Mutable, keys are unique. Written with `{}`.

```python
person = {"name": "John", "age": 30}
print(person["name"])   # John
person["age"] = 31       # change a value
```

### Dict methods

| Method | Description | Example |
|---|---|---|
| `.get(k)` | returns the value (no error if key is missing) | `person.get("name")` |
| `.keys()` | returns all keys | `person.keys()` |
| `.values()` | returns all values | `person.values()` |
| `.items()` | returns key-value pairs | `person.items()` |
| `.update(d2)` | adds/overwrites values from another dict | `person.update({"age": 32})` |
| `.pop(k)` | removes a key and returns its value | `person.pop("age")` |
| `.setdefault(k, v)` | returns the value, sets it if missing | `person.setdefault("city", "NY")` |

```python
for key, value in person.items():
    print(key, "->", value)
```

---

## 🔜 To add later
- [ ] Functions
- [ ] Exceptions (try/except)
- [ ] Classes / OOP
- [ ] Modules and imports
- [ ] Dict/set comprehensions