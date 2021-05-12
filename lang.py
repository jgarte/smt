




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

SMTCONS = {
    "Note": Note, 
}
TYPENV = {
    "List": list, "Integer": int, "Float": float,
    "Note": Note
}

# Everything which can be expressed as a function comes here,
# plus variables
ENV = {
    # '>':op.gt, '<':op.lt, '>=':op.ge, '<=':op.le, '=':op.eq,
    'List': lambda *args: list(args),
    "+": lambda *args: sum(args),
    "*": lambda *args: reduce(lambda x, y: x*y, args),
    "=": lambda *args: len(set(args)) == 1,
    "Print": print,
    # Boolean
    "True": True, "False": False,
    # SMT objects
    "Pitch": lambda pitchobj: getattr(pitchobj, "pitch"),
}

OPEN = "["
CLOSE = "]"


def evalexp(x, env=ENV):
    """
    function ???
    """
    if isinstance(x, (int, float)):      # constant number
        return x
    elif isinstance(x, list):
        
        if x[0] == "Case":
            for pred, expr in x[1:]:
                if evalexp(pred): return evalexp(expr)
            return False
        
        # if x[0] == 'If':               # conditional
            # (_, test, conseq, alt) = x
            # exp = (conseq if evalexp(test, env) else alt)
            # return evalexp(exp, env)
        
        # Setter & Getter, defining variabls
        elif x[0] == 'Set':
            # (set x 34) -> variable
            # (set y x)
            (_, var, exp) = x
            env[var] = evalexp(exp, env)
        
        elif x[0] == "get":
            # (get note pitch)
            (_, objname, attr) = x
            return getattr(env[objname], attr)
        
        elif x[0] == 'Comment': pass
        
        elif x[0] == "Is":
            # [is? x type1 type2 type3]
            thing = x[1]
            types = x[2:]
            return isinstance(evalexp(thing), tuple([TYPENV[type_] for type_ in types]))
        
        elif x[0] == "function":
            raise NotImplementedError
        
        # elif x[0] in env:
        
        # elif isinstance(x[0], str): # A named function
            # op = env[x[0]]
            # args = [evalexp(arg, env) for arg in x[1:]]
            # return op(*args)
        
        
        # Function call
        elif isinstance(x[0], list) or x[0] in env:
            op = evalexp(x[0])
            args = [evalexp(arg, env) for arg in x[1:]]
            return op(*args)
        
        # Create SMT objects
        elif x[0] in SMTCONS:
            # print(x)
            return SMTCONS[x[0]](**dict([(a[0], evalexp(a[1])) for a in x[1:]]))
        # # In env saved names
        # elif :
            # op = evalexp(x[0], env)
            # args = [evalexp(arg, env) for arg in x[1:]]
            # return op(*args)
        
        
        else:
            raise NameError(f"{x}")
        
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

def toplevels(indexed_tokens):
    "Returns a list of all top-level lists."
    TL = []
    L = []
    for tok in indexed_tokens:
        # L.append(tok)
        # if isinstance(tok, tuple):
            # if tok[0] == CLOSE and tok[1] == 0:
                # TL.append(L)
                # L = []
        if isinstance(tok, tuple):
            L.append(tok[0])
            if tok[0] == CLOSE and tok[1] == 0:
                TL.append(L)
                L = []
        else:
            L.append(tok)
    return TL


def read_from_tokens(tokens):
    "Read an expression from a sequence of tokens."
    if len(tokens) == 0:
        raise SyntaxError('unexpected EOF')
    token = tokens.pop(0)
    if token == OPEN:
        L = []
        while tokens[0] != CLOSE:
            L.append(read_from_tokens(tokens))
        tokens.pop(0) # pop off ')'
        return L
    elif token == CLOSE:
        raise SyntaxError('unexpected )')
    else:
        return atom(token)


def atom(tok):
    try: return int(tok)
    except ValueError:
        try: return float(tok)
        except ValueError: return tok

        

if __name__ == "__main__":
    s="""
    [Print
    [Case [False 3]
        [False 8]
        [[= [[Case [False *]
                    [True +]] 2 3] 5] [* 2 10]]
        ]]
    """
    i=index_tokens(tokenize_source(s))
    # print(read_from_tokens(tokenize_source(s)))
    # print(i)
    # print(listify(i,[]))
    # print(toplevels(i))
    
    # print([listify(t, []) for t in toplevels(index_tokens(tokenize_source(s)))])
    # t =toplevels(i)[0]
    # print(read_from_tokens(t))
    
    for tl in toplevels(i):
        # print(tl)
        # l=
        # listify(tl)
        evalexp(read_from_tokens(tl))
        
