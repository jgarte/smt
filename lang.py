
"""
[AddRule cmn pred]
[Is $ Note]
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
        

def evalexp(exp, env):
    """
    """
    if isinstance(exp, (int, float)): return exp
    elif isinstance(exp, list):
        
        car = exp[0]
        cdr = exp[1:]
        
        if car == "Case":
            for pred, x in cdr:
                if evalexp(pred, env): return evalexp(x, env)
            return False
        
        elif car == "And":
            return all([evalexp(a, env) for a in cdr])
            
        # Setter defining variabls
        elif car == 'Set':
            var, val = cdr
            env[var] = evalexp(val, env)
            
                
        # Comment
        elif car == 'Comment': pass
        
        elif car == "Inc": 
            curr = evalexp(exp[1], env)
            print("??????????????")
        
        elif car == "Is":
            thing = cdr[0]
            type = cdr[1]
            return isinstance(evalexp(thing, env), TYPENV[type])
        
        # init = [Function [x y] [* x y] [+ x y]]
        # call = F(x, y)
        elif car == "Function":
            if isinstance(cdr[0], str): # Named function
                pass
            else: # anonymus function
                params = cdr[0]
                body = cdr[1:]
                return _Function(params, body)
        
        # Function call
        elif isinstance(car, list):
            op = evalexp(car, env)
            args = [evalexp(arg, env) for arg in cdr]
            return op(*args)
        
        elif car in env:
            op = env[car]
            args = [evalexp(arg, env) for arg in cdr]
            return op(*args)
            
        
        # Create SMT objects
        elif car in SMTCONS:
            attrs = [(a[0].lower(), evalexp(a[1], env)) for a in cdr]
            return SMTCONS[car](**dict(attrs))
        # # In env saved names
        # elif :
            # op = evalexp(x[0], env)
            # args = [evalexp(arg, env) for arg in x[1:]]
            # return op(*args)
        
        else:
            raise NameError(f"{exp}")
    elif exp.startswith(("\"", "\'")): return exp[1:-1]
    else:
        return env[exp]


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
    [Print [And True  [= 2 2.0 [+ 1 1]]
    [[Function [x y] [= x y]] 2 20]
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
    e = make_env()
    for tl in toplevels(i):
        # print(read_from_tokens(tl))
        # print(tl)
        evalexp(read_from_tokens(tl), e)
        
