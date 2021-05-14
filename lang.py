




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


# S.E.cmn.unsafeadd(settime,istime,"Set Time...",)

SMTCONS = {
    "Note": Note, "MChar": E.MChar, "SimpleTimeSig": SimpleTimeSig
}

TYPENV = {
    "List": list, "Num": (int, float),
    "Note": Note
}

    

def make_env(*others):
    D = {
        'List': lambda *args: list(args),
        "+": lambda *args: reduce(lambda x,y: x+y, args),
        "*": lambda *args: reduce(lambda x, y: x*y, args),
        "=": lambda *args: args.count(args[0]) == len(args),
        "Print": print,
        # Boolean
        "True": True, "False": False,
        # SMT objects
        "Pitch": lambda pitchobj: getattr(pitchobj, "pitch"),
    }
    if others:
        for other in others:
            D.update(other)
    return D
    

LBRACKET = "["
RBRACKET = "]"

class _Function:
    def __init__(self, params, body):
        self.params = params #["a","b"]
        self.body = body
        self.env = make_env()
    
    def __call__(self, *args):
        assert len(self.params) == len(args)
        self.env.update(zip(self.params, args))
        for exp in self.body[:-1]: # Side effects
            evalexp(exp, self.env)
        return evalexp(self.body[-1], self.env)
        


def evalexp(x, env):
    """
    function ???
    """
    if isinstance(x, (int, float)): return x
    elif isinstance(x, list):
        
        if x[0] == "Case":
            for pred, expr in x[1:]:
                if evalexp(pred, env): return evalexp(expr, env)
            return False
        
        # Setter defining variabls
        elif x[0] == 'Set':
            # (set x 34) -> variable
            # (set y x)
            (_, var, exp) = x
            env[var] = evalexp(exp, env)
                
        # Comment
        elif x[0] == 'Comment': pass
        
        elif x[0] == "Inc": 
            curr = evalexp(x[1], env)
            print("??????????????")
        
        elif x[0] == "Is":
            thing = x[1]
            type_ = x[2]
            return isinstance(evalexp(thing, env), TYPENV[type_])
        
        # init = [Function [x y] [* x y] [+ x y]]
        # call = F(x, y)
        elif x[0] == "Function":
            if isinstance(x[1], str): # Named function
                pass
            else: # anonymus function
                params = x[1]
                body = x[2:]
                return _Function(params, body)
        
        # Function call
        elif isinstance(x[0], list):
            op = evalexp(x[0], env)
            args = [evalexp(arg, env) for arg in x[1:]]
            return op(*args)
        
        elif x[0] in env:
            op = env[x[0]]
            args = [evalexp(arg, env) for arg in x[1:]]
            return op(*args)
            
        
        # Create SMT objects
        elif x[0] in SMTCONS:
            attrs = [(a[0].lower(), evalexp(a[1], env)) for a in x[1:]]
            return SMTCONS[x[0]](**dict(attrs))
        # # In env saved names
        # elif :
            # op = evalexp(x[0], env)
            # args = [evalexp(arg, env) for arg in x[1:]]
            # return op(*args)
        
        else:
            raise NameError(f"{x}")
    elif x.startswith(("\"", "\'")): return x[1:-1]
    else:
        return env[x]


def tokenize_source(src):
    return src.replace(LBRACKET, f" {LBRACKET} ").replace(RBRACKET, f" {RBRACKET} ").split()

def index_tokens(tokens):
    """
    Mark openings and closings of lists, eg [[]] ->
    [open0, open1, close1, close0]
    """
    L = []
    i = 0
    for tok in tokens:
        if tok == LBRACKET:
            L.append((tok, i))
            i += 1
        elif tok == RBRACKET:
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
            # if tok[0] == RBRACKET and tok[1] == 0:
                # TL.append(L)
                # L = []
        if isinstance(tok, tuple):
            L.append(tok[0])
            if tok[0] == RBRACKET and tok[1] == 0:
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
    if token == LBRACKET:
        L = []
        while tokens[0] != RBRACKET:
            L.append(read_from_tokens(tokens))
        tokens.pop(0) # pop off ')'
        return L
    elif token == RBRACKET:
        raise SyntaxError(f'unexpected {RBRACKET}')
    else:
        return atom(token)


def atom(tok):
    try: return int(tok)
    except ValueError:
        try: return float(tok)
        except ValueError: return tok

        

if __name__ == "__main__":
    s="""
    [Print [* [[Function [] 3]] 10]]

    """
    i=index_tokens(tokenize_source(s))
    # print(read_from_tokens(tokenize_source(s)))
    # print(i)
    # print(listify(i,[]))
    # print(toplevels(i))
    
    # print([listify(t, []) for t in toplevels(index_tokens(tokenize_source(s)))])
    # t =toplevels(i)[0]
    # print(read_from_tokens(t))
    e = make_env()
    for tl in toplevels(i):
        # print(read_from_tokens(tl))
        # print(tl)
        evalexp(read_from_tokens(tl), e)
        
