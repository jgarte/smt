




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
    "Note": Note, 
}

OPEN = "["
CLOSE = "]"



def env():
    "An environment with some Scheme standard procedures."
    env = {}
    # env.update(vars(math)) # sin, cos, sqrt, pi, ...
    env.update({
        '>':op.gt, '<':op.lt, '>=':op.ge, '<=':op.le, '=':op.eq,
        'List': lambda *args: list(args),
        "+": lambda *args: sum(args),
        "*": lambda *args: reduce(lambda x, y: x*y, args),
        "print": print,
        'int': int, 'float': float,
        # SMT object getters
        "Pitch": lambda obj: getattr(obj, "pitch")
    })
    return env

global_env = env()

def eval(x, env=global_env):
    """
    function ???
    """
    if isinstance(x, (int, float)):      # constant number
        return x
    elif isinstance(x, list):
        if x[0] == 'if':               # conditional
            (_, test, conseq, alt) = x
            exp = (conseq if eval(test, env) else alt)
            return eval(exp, env)
        # Setter & Getter, defining variabls
        elif x[0] == '!':
            (_, var, exp) = x
            val = eval(exp, env)
            env[var] = val
            return var
        elif x[0] == "?":
            (_, objname, attr) = x
            return getattr(env[objname], attr.lower())
        elif x[0] == 'comment': pass
        elif x[0] == "is?":
            # [is? x type1 type2 type3]
            thing = x[1]
            types = x[2:]
            return isinstance(eval(thing), tuple([eval(type) for type in types]))
        elif x[0] == "function":
            raise NotImplementedError
        # In env named functions call
        elif x[0] in env:
            op = eval(x[0], env)
            args = [eval(arg, env) for arg in x[1:]]
            return op(*args)
        # Create SMT objects
        elif x[0] in SCOREOBJS:
            # I wanted Attrs be camelcase 
            attrs = [(a[0].lower(), eval(a[1])) for a in x[1:]]
            return SCOREOBJS[x[0]](**dict(attrs))
        else:
            raise NameError(f"Unknown operator {x[0]}")
    else:
        return env[x]


def tokenize_source(src):
    return src.replace(OPEN, f" {OPEN} ").replace(CLOSE, f" {CLOSE} ").split()

def index_tokens(tokens):
    """
    Mark openings and closings of lists, eg [[]] ->
    [open0, open1, close1, close0]
    """
    L = []
    i = 0
    for tok in tokens:
        if tok == OPEN:
            L.append((tok, i))
            i += 1
        elif tok == CLOSE:
            i -= 1
            L.append((tok, i))
        else:
            L.append(tok)
    return L

def listify(toks, L=None):
    if toks:        
        tok = toks[0]
        if isinstance(tok, tuple):
            if tok[0] == OPEN:
                if L is None:
                    return listify(toks[1:], [])
                else:
                    L.append(listify(toks[1:], []))
            else: # Discard CLOSE
                return listify(toks[1:], L)
        else:
            # The token I care about!
            try: L.append(atom(tok))
            # Random texts flying around, I don't care about them!
            except AttributeError: pass
            return listify(toks[1:], L)
    return L

def atom(tok):
    try: return int(tok)
    except ValueError:
        try: return float(tok)
        except ValueError: return tok

def toplevels(indexed_tokens):
    "Returns a list of all top-level lists."
    TL = []
    L = []
    for tok in indexed_tokens:
        L.append(tok)
        if isinstance(tok, tuple):
            if tok[0] == CLOSE and tok[1] == 0:
                TL.append(L)
                L = []
    return TL
        

if __name__ == "__main__":
    s="""
    [is? 7.34 int float]
    """
    i=index_tokens(tokenize_source(s))
    # print(i)
    # print(listify(i,[]))
    # print(toplevels(i))
    
    # print([listify(t, []) for t in toplevels(index_tokens(tokenize_source(s)))])
    
    # print(toplevels(i))
    
    for tl in toplevels(i):
        # print(tl)
        # l=
        # listify(tl)
        print(eval(listify(tl)))
        # print(tl)
        # print(eval(l))
