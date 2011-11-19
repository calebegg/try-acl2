Lesson 1. Lisp
--------------
ACL2 uses a subset of the Lisp programming language. Lisp syntax is one of the simplest ones of any programming language. However, it is different from most other languages, so let's take a moment to get acquainted with it.

First of all, every operation in Lisp is a function. Even very basic mathematical operations, such as addition. Secondly, functions are called in a different way than they are in mathematics or in most other languages. While in most languages, you might write `f(x, y)`, in Lisp, you write `(f x y)`.

The addition function is called `+`. Try adding two numbers now: `(+ 1 2)`

*Tip: You can click on any code you see in this tutorial to insert it at the prompt.*

Lesson 1. Lisp
--------------
'Lisp' is short for 'list processing'. Lists, specifically [linked lists](http://en.wikipedia.org/wiki/Linked_list), are a fundamental part of how Lisp represents and manipulates data. The function used to create a list is called, appropriately, `list`. Try creating a list: `(list 8 6 7 5 3 0 9)`

Lesson 1. Lisp
--------------
You can use the single quote mark as a type of shorthand for creating lists. Unlike with `(list ...)`, the single quote marker also "quotes" the items inside of it. While `(list 1 2 (+ 1 2))` would be the same as `(list 1 2 3)`, `'(1 2 (+ 1 2))` is the same as `(list 1 2 (list '+ 1 2))`.

The single quoted + sign, `'+` is called a "symbol". You can use the single quote to create a symbol out of any simple sequence of characters, such as `'not-found`, `'valid`, or `'1+1.

`append` concatenates two (or more) lists together. Try: `(append '(1 2 3) '(4 5 6))`

Lesson 1. Lisp
--------------
There are two more basic types of values in ACL2 that are important: strings and booleans. Strings are double quoted, `"like this"`. The two boolean values are `t` (for true) and `nil` (for false). Actually, any value (except `nil`) is considered to be true for boolean tests. Use `t` if no other value makes more sense.

The primary use for boolean functions and values is to branch using the `(if ...)` function.


Usage:
    (if test if-true if-false)

Try it now with one of the simple boolean values: `(if t "True" "False")`

Lesson 1. Lisp
--------------
Of course, `(if ...)` doesn't do much good in this form. You'll almost always call (if ...) with a function call for the second parameter. Some functions that return boolean values:

    (< a b) (> a b) (<= a b) (>= a b) (= a b) (/= a b)
These are the six equality and inequality tests. They should be familiar to you. The final one is 'not equal'; the slash is meant to signify the crossed out equal sign of mathematics.

    (integerp x) (rationalp x) (acl2-numberp x) (complex-rationalp x) (natp x) 
These functions recognize (return `t`) some of the different types of numbers available in ACL2. The terminal '`p`' is a common idiom from Lisp and means "predicate". You can imagine it as a sort of question mark; `(natp i)` means "Is `i` an natural number?".

Try this: `(if (= (+ 1 3) (+ 5 2 -3)) "Equal" "Not equal")`

Lesson 1. Lisp
--------------
    (endp xs) (listp xs) (true-listp xs) (equal xs ys)
These functions relate to lists. `(endp xs)` checks to see if `xs` is an empty list (if we are "at the end" of the list, a phrasing that makes sense if you think about these functions as they are used recursively). `(listp xs)` is a recognizer for lists. `(true-listp xs)` is a stronger recognizer for lists that checks to see if the marker used for the empty list is `nil`, as it is in the system-created lists. Most ACL2 functions require (or only work with) "true" lists, like the ones you can construct with `(list ...)`. `(equal ...)` tests the equality of lists (or more simple elements). `(= ...)` only works for numbers.

As a side note, I often use `xs` (or `ys`, `zs`, etc), pronounced like English plurals ("exes", "whys", "zees"), for lists and `x`, `y`, etc. for numbers or simple values. This is just a convention, not a part of Lisp.

This time, try: `(true-listp '(a b c))` to verify what I asserted earlier.

Lesson 1. Lisp
--------------
By now, if you're an experienced programmer, you're probably expecting a way to assign variables. However, one of the important parts of how ACL2 differs from regular Common Lisp is that it does not allow variables to be modified in place. In essence, it doesn't allow variables at all; only constants and aliases.

Instead, to produce meaningful or complex programs, you'll need to modify and return variables by creating new ones. This may seem unusual and may take some time to get accustomed to if you've never used an applicative programming language, but once you get the hang of it, it's pretty easy.

Lets start with aliases. They are a good way to "save" the results of a complex computation and use it more than once, so you don't have to redo expensive operations. Aliasing is done with the `let` function.

    (let ((alias1 value1) (alias2 value2) ...) body)
where the aliases are symbols (made up of letters, numbers, and/or some symbols) and the values are either literal values, or, more often, function calls.

Try this: `(let ((xs (append '(1 2 3) '(4 5 6)))) (and (listp xs) (true-listp xs)))`

Lesson 1. Lisp
--------------
In the previous example, I snuck in an extra simple function: `(and ...)`. It does what you'd expect from boolean algebra, and you can also use `(or ...)`, `(not ...)`, `(implies p q)`, etc.

There's one final important built-in function that I'd like to introduce. To compute the length of a list, use (len xs): `(len '(1 2 3 4))`.

Lesson 2. Functions
--------------
Now that you've got a basic understanding of some of the built-in functions of lisp, let's move on to defining new ones. The function you use to define new functions is `defun`:

    (defun name (param1 param2 ...) body)

Try adding this function that squares numbers: `(defun square (x) (* x x))`.

Lesson 2. Functions
--------------
An important thing happened here: in addition to just adding the new function, ACL2 did something interesting: it proved that no matter what input you give to your new function, it will, eventually, complete. It won't loop or call itself forever. Now, that's not too surprising, given how simple `(square ...)` is. But it can be quite a task for complex functions.

Try out your new function now by squaring some of the types of numbers that ACL2 supports.

Lesson 2. Functions
--------------
Next, we're going to enter a recursive function; `factorial`. The factorial of a natural number is the product of the number and all the natural numbers below it. In other words, `(factorial n)` = `(* n (factorial (- n 1)))`. As a special case (called the "base case"), `(factorial 0)` = 1. A naive (but wrong) approach might be this:

    (defun factorial-wrong (n)
      (if (= n 0)
          1
          (* n (factorial-wrong (- n 1)))))

You can try adding this to ACL2, but it won't work. To see what's wrong, imagine calling factorial on the (perfectly valid) ACL2 number `-1`.

    (factorial -1)
    (* -1 (factorial -2))
    (* -1 (* -2 (factorial -3)))
    ...

Uh oh. You can clearly see that this will never terminate. ACL2 functions are 'total', meaning that they must be able to accept any object of any type and return *something* in a finite amount of time, even if it's not necessarily a useful response. Keep this in mind as you define ACL2 functions.

When defining functions like `factorial` that recurse "towards" 0 and where you only care about natural numbers, use the function `zp` (the "zero predicate"). `(zp n)` is `t` when n is zero. But it's also `t` if n is *not* a natural number. So it returns the "base case" if n is something weird, like a list or a complex number. Try this definition of `factorial`:

    (defun factorial (n)
      (if (zp n)
          1
          (* n (factorial (- n 1)))))

Lesson 2. Functions
--------------------
You'll notice that `(factorial (list 1 2 3))` returns `1`, an inapplicable answer. This is a little messy, but fine. Later, you can add `:guard`s to functions to ensure that users don't execute them on irrelevant values. (The prover, on the other hand, ignores guards, so it's best to do the same for now).

Now let's try defining a function on lists; `rev`, which reverses the list you give it. The base case for `rev` is the empty list, the reverse of which is just the empty list. For the general case, the reversed list is just the reversed "rest" of the list with the "first" element at the end, like so:

    (defun rev (xs)
      (if (endp xs)
          nil
          (append (rev (rest xs)) (list (first xs)))))

Lesson 3. Theorems
-----------------
Of course, proving that functions terminate is only a small part of proving that they work. ACL2 also lets you prove arbitrary theorems about functions. We will start out using the `(thm ...)` function to do this. Try the following pretty obvious theorem: If a number is a natural number, that number is also an integer; `(thm (implies (natp i) (integerp i)))`

This tutorial is a work in progress
-----------------------------------
Feel free to email any comments you have to me at calebegg@gmail.com, and come back for more later.

<!--
  (thm (= (+ a b) (+ b a)))
  (thm (= (* a 2) (+ a a)))
  (thm (> (factorial n) 0))
  (equal ...)
  (thm (equal (append (append xs ys) zs) (append xs (append ys zs))))
  (defthm name ...)
  :rewrite rules
3. Harder theorems
  (defun rev ...)
  (defthm rev-rev ...)
  (defun exp (b n) ...)
  (defun rp (b n) ...)
  (defthm rp-equals-exp ...)
  (defun orderedp (xs) ...)
  (defun partial-sums (xs running) ...)
  (defthm partial-sums-ordered (orderedp (partial-sums xs 0)))
4. Tail recursion
  (defun fact-tail (n r) ...)
  (defun sum (xs) ...)
  (defthm xs-over-append ...)
  (defun running-sum (xs r) ...)
  (defthm sum=rumming-sum ...)
5. Sorting
  (defun insert (x xs) ...)
  (defthm (implies (orderedp xs)) (orderedp (insert x xs)))
  (defun isort (xs) ...)
  (defthm (orderedp (isort xs)))
  (defun split (xs) ...)
  (defthm split-halves-list ...)
  (defun merge (xs ys) ...)
  (defthm (implies (and (orderedp xs) (orderedp ys)) (orderedp (merge xs ys))))
  Qsort
6. I/O
-->
