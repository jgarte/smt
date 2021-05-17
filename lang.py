
"""
[AddRule cmn pred]
[Is $ Note]

This is a comment,
so write any thing you
like here, and it will all thrown away for you!
[Define cmn ]
[! Here is an inline comment
which can be multiple lines
and etc.]


[TimeSig [Num 3] [Denom 4]]

(set (timesig (num 3) (denom 5)))
(num )

"""
import re
from functools import reduce
from score import *
# import score

# S.E.cmn.unsafeadd(settime,istime,"Set Time...",)
LBRACKET = "("
RBRACKET = ")"

SMTCONS = {x.__name__.lower() for x in (
        E.SForm, E.HForm, E.VForm, E.MChar,
        Note, SimpleTimeSig
    )
}

TYPENV = {t.__name__.lower(): t for t in (
        list, int, float, str,
        E.SForm, E.HForm, E.VForm, E.MChar
    )
}

def attrgetter(attr_name): 
    return lambda inst: getattr(inst, attr_name)

def make_env(*others):
    D = dict(
    )
    D = {
        'list': lambda *args: list(args),
        "+": lambda *args: reduce(lambda x, y: x + y, args),
        "*": lambda *args: reduce(lambda x, y: x * y, args),
        "=": lambda *args: args.count(args[0]) == len(args),
        "print": print,
        # Boolean
        "true": True, "false": False,
        # SMT
        "pitch": lambda pitchobj: getattr(pitchobj, "pitch"),
        # TimeSig
        "num": lambda ts: getattr(ts, "num")
    }
    if others:
        for other in others:
            D.update(other)
    return D
    

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
    if isinstance(exp, (int, float)):
        return exp
    
    elif isinstance(exp, list):
        car = exp[0]
        cdr = exp[1:]
        
        if car == "case":
            for pred, x in cdr:
                if evalexp(pred, env):
                    return evalexp(x, env)
            return False
        
        elif car == "and":
            return all([evalexp(a, env) for a in cdr])
            
        # Setter defining variabls
        elif car == 'set':
            var, val = cdr
            env[var] = evalexp(val, env)
                
        # Comment
        elif car == '!': pass
        
        elif car == "Inc": 
            curr = evalexp(exp[1], env)
            print("??????????????")
        
        elif car == "is":
            thing = cdr[0]
            type = cdr[1]
            return isinstance(evalexp(thing, env), TYPENV[type])
        
        # init = [Function [x y] [* x y] [+ x y]]
        # call = F(x, y)
        elif car == "fn":
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
            
        # A SMT constructor (the class and it's attributes)
        elif car in SMTCONS:
            return SMTCONS[car](**dict([(a[0], evalexp(a[1], env)) for a in cdr]))
        else:
            raise NameError(f"{exp}")
    # A string
    elif exp.startswith("\"") and exp.endswith("\""):
        return exp[1:-1]
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
            tokens.extend(src[x[0]:x[1]].replace(LBRACKET, f" {LBRACKET} ").replace(RBRACKET, f" {RBRACKET} ").split())
    return tokens
    # return src.replace(LBRACKET, f" {LBRACKET} ").replace(RBRACKET, f" {RBRACKET} ").split()

def index_tokens(tokens):
    """
    Mark openings and closings of lists, eg [[]] ->
    [open0, open1, close1, close0]
    """
    L = []
    i = 0
    x = []
    for tok in tokens:
        if tok == LBRACKET:
            L.append((tok, i))
            i += 1
        elif tok == RBRACKET:
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
            if tok[0] == RBRACKET and tok[1] == 0:
                TL.append(L)
                L = []
            # Track if it's a bracket token.
            last_bracket = tok
        else:
            if not last_bracket == (RBRACKET, 0): # not a comment
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
    
    (print (simpletimesig))
    

    """
    i=index_tokens(tokenize_source(s))
    # print(read_from_tokens(tokenize_source(s)))
    # print(i)
    # print(listify(i,[]))
    # print(toplevel_exprs(i))
    
    # print([listify(t, []) for t in toplevel_exprs(index_tokens(tokenize_source(s)))])
    # t =toplevel_exprs(i)[0]
    # print(read_from_tokens(t))
    env = make_env()
    # print(toplevel_exprs(i))
    for e in toplevel_exprs(i):
        # print(">>",e,read_from_tokens(e))
        evalexp(read_from_tokens(e), env)
        
