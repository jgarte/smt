
"""


"""
import re
from functools import reduce
from score import *


# S.E.cmn.unsafeadd(settime,istime,"Set Time...",)
LPAR = "("
RPAR = ")"

SMTCONS = {x.__name__.lower(): x for x in (
        E.SForm, E.HForm, E.VForm, E.MChar,
        Note, SimpleTimeSig, Clef
    )
}

TYPENV = {t.__name__.lower(): t for t in (
        list, int, float, str,
        E.SForm, E.HForm, E.VForm, E.MChar,
        Note, Clef
    )
}

def attrgetter(attr_name): 
    return lambda inst: getattr(inst, attr_name)

# Put things here which shouldn't be evalulated (evaluation needs env)!
def make_env(*others):
    # These names have priority over object's methods
    D = {
        'list': lambda *args: list(args),
        "+": lambda *args: reduce(lambda x, y: x + y, args),
        "*": lambda *args: reduce(lambda x, y: x * y, args),
        "=": lambda *args: args.count(args[0]) == len(args),
        "?": print,
        "t": True, "f": False,
        "render": E.render, "rt": E._RT
    }
    if others:
        for other in others:
            D.update(other)
    return D
    

class _Function:
    def __init__(self, params, body):
        self.params = params
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
    (def rt t/f
      (! (pitch @) "C#4"))
    """
    if isinstance(exp, (int, float)): return exp
    
    elif isinstance(exp, list):
        car = exp[0]
        cdr = exp[1:]
        if car == "case":
            for pred, x in cdr:
                if evalexp(pred, env):
                    return evalexp(x, env)
            return False
        elif car == "def": # defining rules
            rt, pred, *body = cdr
        elif car == "and":
            return all([evalexp(a, env) for a in cdr])
        # Setter defining variabls
        elif car == '!':
            thing, val = cdr
            if isinstance(thing, list):
                name, obj = thing
                setattr(evalexp(obj, env), name, evalexp(val, env))
            elif isinstance(thing, str): # a symbol
                env[thing] = evalexp(val, env)
            else:
                raise SyntaxError
                
        # Comment
        elif car == '~': pass
        
        elif car == "Inc": 
            curr = evalexp(exp[1], env)
            print("??????????????")
        
        elif car == "is?":
            thing = cdr[0]
            type_ = cdr[1]
            return isinstance(evalexp(thing, env), TYPENV[type_])
        
        # Function definition
        elif car == "fn":
            if isinstance(cdr[0], str): # Named function
                pass
            else: # anonymus function
                params = cdr[0]
                body = cdr[1:]
                return _Function(params, body)
        
        # Anonymus function call
        elif isinstance(car, list):
            op = evalexp(car, env)
            args = [evalexp(arg, env) for arg in cdr]
            return op(*args)
        # Named function call
        elif car in env:
            op = env[car]
            args = [evalexp(arg, env) for arg in cdr]
            return op(*args)
            
        # A SMT constructor (the class and it's attributes)
        elif car in SMTCONS:
            # att[0] = att name, att[1] = att value
            return SMTCONS[car](**dict([(att[0], evalexp(att[1], env)) for att in cdr]))
        else:
            # The last resort: try to resolve car as an
            # attribute or a method of an object (which must come at cdr[0])
            obj = cdr[0]
            args = cdr[1:]
            try:
                # A method? then call it, if car not an attribute at all,
                # let's have an AttributeError!
                return getattr(evalexp(obj, env), car)(*args)
            except TypeError: # Menas car is an attr, but not callable!
                return getattr(evalexp(obj, env), car)
    # A string
    elif exp.startswith("\"") and exp.endswith("\""):
        return exp[1:-1]
    # Should be a variable
    else:
        return env[exp]

# Allow anything between double quotes except with double quote itself!
STRPATT = re.compile(r'"[^"]*"')
def tokenize_source(src):
    """
    """
    src = src.strip()
    str_matches = list(STRPATT.finditer(src))
    spans = [m.span() for m in str_matches]
    indices = [0] + [i for s in spans for i in s] + [len(src)]
    tokens = []
    for x in list(zip(indices[:-1], indices[1:])):
        if x in spans: # str match?
            tokens.append(src[x[0]:x[1]])
        else:
            tokens.extend(src[x[0]:x[1]].replace(LPAR, f" {LPAR} ").replace(RPAR, f" {RPAR} ").split())
    return tokens
    # return src.replace(LPAR, f" {LPAR} ").replace(RPAR, f" {RPAR} ").split()

def index_tokens(tokens):
    """
    Mark openings and closings of lists, eg [[]] ->
    [open0, open1, close1, close0]
    """
    L = []
    i = 0
    x = []
    for tok in tokens:
        if tok == LPAR:
            L.append((tok, i))
            i += 1
        elif tok == RPAR:
            i -= 1
            L.append((tok, i))            
        else:
            L.append(tok)
    # print(x)
    return L

def toplevel_exprs(indexed_tokens):
    TL = []
    L = []
    # Track last bracket, we trash anything
    # which comes AFTER the last toplevel closing bracket (ie (']', 0)).
    # These are considered as toplevel comments!
    last_bracket = None
    for tok in indexed_tokens:
        if isinstance(tok, tuple):
            L.append(tok[0])
            if tok[0] == RPAR and tok[1] == 0:
                TL.append(L)
                L = []
            # Track if it's a bracket token.
            last_bracket = tok
        else:
            if not last_bracket == (RPAR, 0): # not a comment
                L.append(tok)
    return TL


def read_from_tokens(tokens):
    "Read an expression from a sequence of tokens."
    if len(tokens) == 0:
        raise SyntaxError('unexpected EOF')
    token = tokens.pop(0)
    if token == LPAR:
        L = []
        while tokens[0] != RPAR:
            L.append(read_from_tokens(tokens))
        tokens.pop(0) # pop off ')'
        return L
    elif token == RPAR:
        raise SyntaxError(f'unexpected {RPAR}')
    else:
        return atom(token)


def atom(tok):
    try: return int(tok)
    except ValueError:
        try: return float(tok)
        except ValueError: return tok

        

if __name__ == "__main__":
    s="""
    Func Atom Atom
        Func Atom Atom
    Defn
        Foo args+
        ->
            Fn x
                x * 10
            args
    Defn Foo N
        If
            N = 0
            1
        Else
            N * Foo N-1
    
    Set y 10
    Call
        *
        10 10
    *
        10 10
    Call
        Fn
            x\sy\sz\n
            +\sx\sy\sz
        1 2 3
    
    Fn x y x
    
    Fn
        x \n
        x
    
    Note
      Pitch
       "C#4"
      Dur
    Set n Note Pitch 3 Dur 4
    Note
        Pitch
            Conc "C#4" Color 
        Dur
            + 2 3 4 5
                * 3 4
                    4 5 6
    Staff
        Cont
            Clef
                Name "Sol"
            Time
                num 
                    3
                denom
                    4
            note
                pitch "C#4"
                dur 4
            note
                pitch 60
                dur 4
            rest
                dur 4
    (? (& t t t t (= 2 2 2.0009) 0.2))
    """
    i=index_tokens(tokenize_source(s))
    # print(read_from_tokens(tokenize_source(s)))
    # print(i)
    # print(listify(i,[]))
    # print(toplevel_exprs(i))
    
    # print([listify(t, []) for t in toplevel_exprs(index_tokens(tokenize_source(s)))])
    # t =toplevel_exprs(i)[0]
    # print(read_from_tokens(t))
    envt = make_env()
    for e in toplevel_exprs(i):
        # print(read_from_tokens(e))
        evalexp(read_from_tokens(e), envt)
        
