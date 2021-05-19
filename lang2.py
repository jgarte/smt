"""
op atom atom atom atom atom -> unamb


\n linebreak unambs amb situations.

Ein op wird bis zum \n auf die args angewendet.

Atoms = unambigouse
Expressions = ambigouse
+ 1 2 3 4 5 * 2 3 7

+ 1 2 3 4 5 7 * 2 3
+ 1 2 3 4 5\n
    * 2 3\n
    7
Note(pitch="C4", dur=3+4+1*.5)
Note Dur * .5 + 3 4 1
Note
 Dur
  Dur MyNote

"""
import re
from functools import reduce
class Exp: pass
class Line:
    def __init__(self, op, params):
        self.op  = op
        self.params = params

funcenv = {
    "+": sum,
    "*": lambda args: reduce(lambda x, y: x * y, args)
    }
# p=re.compile(r"[*+][\s\d]*")
TOPLEVEL_PATT = re.compile(r"(^[^\s]\w*(?:\n^\s+\w*)*)", re.M)
LEADING_SPACE_PATT = re.compile(r"^\s*")
OPERATORS_PATT = re.compile(r"[*+][\w\s]*")
def count_leading_spaces(S):
    M = LEADING_SPACE_PATT.search(S)
    return 0 if not M else M.end()

s="""
+ 1 1 1 1 1 1 + 1 2 * 2 2
"""
def resolve_token(t):
    try:
        return int(t)
    except ValueError:
        try:
            return float(t)
        except ValueError:
            pass
        
def evalexp(x, ready=None):
    fn, *args = x.split()
    A = [resolve_token(a) for a in args]
    if ready:
        return funcenv[fn](A+[ready])
    else:
        return funcenv[fn](A)
def evalline(line):
    last_val=None
    for i, x in enumerate(reversed(line)):
        if i==0:
            last_val = evalexp(x)
        else:
            last_val = evalexp(x, last_val)
    return last_val
    
    
l =OPERATORS_PATT.findall(s)

print(evalline(l))
# for m in TOPLEVEL_PATT.findall(s):
    # splitted = m.split("\n")
    # print(splitted[0])
    # # for x in m.split("\n"):
        # # print(count_leading_spaces(x), x)
    
def toplevels(src):
    with open(src, "r") as s:
        return TOPLEVEL_PATT.findall(s.read())
    

# with open("./x", "r") as x:
    # print(p.findall(x.read()))

def build_lineop():
    L = []
    op = 0
"""
(+ 1 2 (* 3 4 (* 5 (+ 1 6))))
"""

