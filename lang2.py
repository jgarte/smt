
import re

"""
+
  2 3 4
  *
    10 10 + 
            20 20
            30 30
fn
  p1
    p2
  + p1 p2
  * p1 p2
  + p1 * p2 100

  
arglose fn?

call
  fn
    append list 2 3 4
        list 1 2 3

-> ([2,3,4], [1,2,3])

call
  fn
    p1 p2
      p3
    append list 2 3 4
           list p1 p2 p3
  1 2 3
-> [2,3,4,1,2,3]

defn name
  p1 p2
     p3 p4
     p5 p6
  + p1 p2 p3 p4 p5 p6

name 3 + 5 6
         4 5

case
  = * 10 10 10
    + 10 2 - 9 8
             23
  print "Hello you?"
  true
  print "No!"
"""









s="""
+ 1 2 3 4
  * 3 4 5 + 6 7
  8 9 10 1112 0
"""
# Blocks at specific indentation levels!!!!!!!!!!!!!!!!!!!!111111
kwenv = {
    "*": None,
    "+": None
}
def iskw(s): return s in kwenv
def lines(src): return src.strip().splitlines()
def tokenize_source(src):
    toks = []
    idx = 0
    for i, line in enumerate(lines(src)):
        for match in re.finditer("[*+\w\d]+", line):
            toks.append({
                "str": match.group(), "start": match.start(),
                "end": match.end(), "line": i, "idx": idx,
                "alloced": False
            })
            idx += 1
    return toks

def tokensatline(line, toks):
    return [t for t in toks if t["line"] == line]

def kwatline(line, tokens):
    return [t for t in tokens if iskw(t["token"]) and t["line"] == line]

toks = tokenize_source(s)


def linekws(linetoks):
    """Returns a list of kw tokens at current line."""
    return [t for t in linetoks if iskw(t["str"])]

def isinblock(tok, kw):
    """Is token inside of the kw's block?
    
    """
    return (not iskw(tok["str"])) and tok["start"] > kw["start"] and \
    tok["line"] >= kw["line"] and (not tok["alloced"])

def allocate_literals(toks):
    L = []
    maxline = max(toks, key=lambda t: t["line"])["line"]
    for i in range(maxline, -1, -1):
        kwtoks = linekws(tokensatline(i, toks))
        if kwtoks:
            for kw in sorted(kwtoks, key=lambda t: t["start"], reverse=True):
                x=[kw]
                for a in [t for t in toks if isinblock(t, kw)]:
                    x.append(a)
                    a["alloced"] = True
                L.append(x)
    return L

for b in allocate_literals(toks):
    print([x["str"] for x in b])

# for b in blocks(toks):
    # print([t["token"] for t in b])

# for t in toks:
    # print(t, iskw(t["str"]))

# print(kwatline(0, spans))












