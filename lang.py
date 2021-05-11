




"""

[note [pitch ]]





[cond [[= 2 3] [print hello world!]]
      true [print 2 was not = to [+ 3 4]]]

[[function 123]] => 123

setting:
[= a 2]

[comment Folgendes ist immer yes!]
[ja [= 2 3] [ja] [ja] [< 3 4 5]]

[defrule cmn
  
  [comment predicate können soviele sein wie man will!]
  [comment und können alle in ,,,,]
  [true [< [height %] 100]
        [= [farbe %] rot]
        [false [= [farbe [stemGraver %]] rot]]]

  [comment Und hier kommt action!]
  [set [farbe [stemGraver %] grün]]
  
  [defrule cmn pred funcs [aux true]]
  ]



Wir brauchen auch eine Konsole zum printen

[print Hello world, welcome to the SMTPad, a text-editor for 
Semantic Music Typesetting!]
[print
 [pitch [note [pitch 60]]]
]

[Function [a b c]
  [loop x in [range 10 21]
     [print [+ a b c]]]]

[defrule [note clef hform accidental]
 	 [treble bass alto]
	 [function [self]
	    comment line, dont do this: [inc [x self]] 
instead use the set operator
	    [assign [x self] [* [x self] 10]]
	 [function [self]
	   [set [color self] green]]
	 [function [self parent]
	   [set [xscale parent] [* 3 4 .5 2]]]
]]

@ = Object to which rule must be applied!
@color = [color object]
@0color = [color [at 0 [content object]]]
@-1color = [color [ancestors object]]
[defrule [set @color [list [random 0 101] 0 0]]]


A named function:

[set fun [function [x y] [print [* x y]]]]
[fun 3 4] => 12
vs. anonymus function:

[function [x y] a doc string? [print [list x y]]]

[[function [a b] [* a b]] 3 4] => 12

[procedure make_note [p] [note [pitch p] [duration 1] [id foo]]
[line [toplevel yes] [make_note c4]]

comment whole line, aber das wird trotzdem gemach [+ 2 1]
[print [getby pitch c4] 
[getby id 
foo]
]



[fun FoBar]


"""
from functools import reduce
import math
import operator as op
from score import *

SCOREOBJS = {
    "note": Note, 
}
OPEN = "["
CLOSE = "]"

def parse(program):
    "Read a Scheme expression from a string."
    return tokens_to_list(program)

def tokens_to_list(tokens):
    "Read an expression from a sequence of tokens."
    if len(tokens) == 0:
        raise SyntaxError('unexpected EOF')
    token = tokens.pop(0)
    if token == OPEN:
        L = []
        while tokens[0] != CLOSE:
            L.append(tokens_to_list(tokens))
        tokens.pop(0) # pop off ')'
        # print(tokens)
        return L
        # whole.append(L)
    elif token == CLOSE:
        raise SyntaxError('unexpected )')
    else:
        return atom(token)

def atom(token):
    "Numbers become numbers; every other token is a symbol."
    try: return int(token)
    except ValueError:
        try: return float(token)
        except ValueError:
            return token


def standard_env():
    "An environment with some Scheme standard procedures."
    env = {}
    # env.update(vars(math)) # sin, cos, sqrt, pi, ...
    env.update({
        # '+':op.add, '-':op.sub, '*':op.mul, '/':op.truediv, 
        '>':op.gt, '<':op.lt, '>=':op.ge, '<=':op.le, '=':op.eq,
        'list': lambda *args: list(args),
        "+": lambda *args: sum(args),
        "*": lambda *args: reduce(lambda x, y: x*y, args)
    })
    return env

global_env = standard_env()

def eval(x, env=global_env):
    "Evaluate an expression in an environment."
    if isinstance(x, (int, float)):      # constant number
        return x                
    elif x[0] == 'if':               # conditional
        (_, test, conseq, alt) = x
        exp = (conseq if eval(test, env) else alt)
        return eval(exp, env)
    elif x[0] == 'set':           # definition
        (_, symbol, exp) = x
        env[symbol] = eval(exp, env)
    elif isinstance(x, list):
        # SMT zeug
        if x[0] in SCOREOBJS:
            return SCOREOBJS[x[0]](**dict([[a[0], eval(a[1])] for a in x[1:]]))
        else: #Lispy
            proc = eval(x[0], env)
            args = [eval(arg, env) for arg in x[1:]]
            return proc(*args)
    else:
        return env[x]
def tokenize_source(src):
    return src.replace(OPEN, f" {OPEN} ").replace(CLOSE, f" {CLOSE} ").split()
def index_open_close(tokens):
    L = []
    i = 0
    for tok in tokens:
        if tok == "[":
            L.append((tok, i))
            i += 1
        elif tok == "]":
            i -= 1
            L.append((tok, i))
        else:
            L.append(tok)
    return L

def toplevel_tokens(indexed):
    L = []
    toplevel=[]
    for tok in indexed:
        if isinstance(tok, tuple):
            if tok[0] == "[" and tok[1]==0:
                toplevel.append(tok[0])
            elif tok[0]=="]" and tok[1]==0:
                toplevel.append(tok[0])
                L.append(toplevel)
                toplevel=[]
            else:
                toplevel.append(tok[0])
        else:
            toplevel.append(tok)
    return L

if __name__ == "__main__":
    s="[note]"
    i=index_open_close(tokenize_source(s))
    for tl in toplevel_tokens(i):
        print(parse(tl))
