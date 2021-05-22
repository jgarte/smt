
import re
from functools import reduce



s="""
+ 2
 show + 1 1 * 3 2 
       -10
"""
def show(thing):
    print(thing)
    return thing

builtins_env = {
    "*": lambda *args: reduce(lambda x, y: x*y, args),
    "+": lambda *args: sum(args),
    "show": show
}

class Token:
    def __init__(self, label, start, end, line):
        self.label = label
        self.start = start
        self.end = end
        self.line = line
        self.allocated = False
        self.value = None
    
    def __repr__(self):
        return f"{self.label}"

def resolve_token(t):
    try:
        return int(t.label)
    except ValueError:
        try:
            return float(t.label)
        except ValueError:
            try:
                return builtins_env[t.label]
            except KeyError:
                pass

def set_token_value_ip(t):
    try:
        t.value = int(t.label)
    except ValueError:
        try:
            t.value = float(t.label)
        except ValueError:
            try:
                t.value = builtins_env[t.label]
            except KeyError:
                pass

    

def tokisfun(t): return t.label in builtins_env

def lines(src): return src.strip().splitlines()

# decimal numbers
DECPATT = r"[+-]?((\d+(\.\d*)?)|(\.\d+))"

def tokenize_source(src):
    toks = []
    for i, line in enumerate(lines(src)):
        for match in re.finditer(r"([*+]|\w+|{})".format(DECPATT), line):    
            toks.append(Token(label=match.group(), start=match.start(), end=match.end(), line=i)
            )
    return toks

def tokensatline(line, toks):
    return [t for t in toks if t.line == line]



def linekws(linetoks):
    """Returns a list of kw tokens at current line."""
    return [t for t in linetoks if tokisfun(t)]

def is_atomic_subordinate(tok, kw):
    """Is token inside of the kw's block, eg an arg etc
    """
    return (not tokisfun(tok)) and tok.start > kw.start and \
    tok.line >= kw.line and (not tok.allocated)

def allocate_atomics(toks):
    """
    [operator . . . . . . . .]
    """
    L = []
    maxline = max(toks, key=lambda t: t.line).line
    for i in range(maxline, -1, -1):
        kwtoks = linekws(tokensatline(i, toks))
        if kwtoks:
            for kw in sorted(kwtoks, key=lambda t: t.start, reverse=True):
                set_token_value_ip(kw)
                x=[kw]
                for a in [t for t in toks if is_atomic_subordinate(t, kw)]:
                    a.allocated = True
                    set_token_value_ip(a)
                    # x.append(resolve_token(a))
                    # resolve_token(a)
                    x.append(a)
                L.append(x)
    return L

def ast(atomic_lists):
    while len(atomic_lists) > 1:
        lst = atomic_lists.pop(0)
        for x in atomic_lists:
            if x[0].start < lst[0].start and x[0].line <= lst[0].line:
                x.append(lst)
                break
    return atomic_lists[0]


def evalexp(x):
    try: # a token obj?
        return x.value
    except AttributeError: # a list?
        try:
            fn, *args = x
            return evalexp(fn)(*[evalexp(a) for a in args])
        except KeyError:
            pass

toks = tokenize_source(s)
print(evalexp(ast(allocate_atomics(tokenize_source(s)))))
# for x in allocate_atomics(tokenize_source(s)):
    # print([a.label for a in x])
