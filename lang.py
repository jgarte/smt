




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
# import inspect
# import re
import rply
from functools import reduce


OPEN = r"\["
CLOSE = r"\]"


########################################## Lexer
srclexgen = rply.LexerGenerator()
srclexgen.add("TOPLEVEL", r"{0}.*{1}".format(OPEN, CLOSE))
srclexgen.ignore(r"\s+")
srclexer = srclexgen.build()



lg = rply.LexerGenerator()

NUMPATT = r"[\-\+]?\d+(?:\.\d+)?"
# print(NUMPATT)
TOKENS = (
    # ("STREAM", r"({0})\s*".format(NUMPATT)),
    # ("NUMBER", NUMPATT),
    ("OPEN", OPEN),
    ("CLOSE",CLOSE),
    # ("INC",r"inc\s+"),
    ("BINOP", r"[\+\*\-\/]"),
    ("OPERANDS", r"{0}(?:\s{1})*".format(NUMPATT, NUMPATT))
    )

for tok, patt in TOKENS:
    lg.add(tok, patt)

# for k, v in TOKENS.items():
    # lg.add(k, v)

lg.ignore(r"\s+")

# Build the lexer
lexer = lg.build()
# print([r.name for r in lexer.rules])

# for t in lexer.lex("+ 8123873.878 34 0 0.23"):
    # print(t,)

######################################### Parser
pg = rply.ParserGenerator([x[0] for x in TOKENS])

"""
[! 3/4 [timesig 3 4] [toplvl yes]]
[! 3/4copy 3/4 [x 10] [y 10]]
[! sol [clef treble]]
[staff [content sol 3/4 [note fis 4 [headcolor red]] [note ges 4] [note c 4] [barline end]]
       [width 20] [toplvl yes]]
       
"""
# @pg.production("stat : symbol")
# def symbol(p):
    # print(p)
    # return p

# @pg.production("symbol : EMPTY_STREAM")
# def expr_empty(p): return []

# @pg.production("symbol : NUMBER_STREAM")
# def _number_stream(p):
    # print("NS", p)

# @pg.production("symbol : NUMBER")
# def _number(p):
    # print(dir(p[0]), p[0])
    # return float(p[0].value)

# @pg.production("symbol : OPERANDS")
# def _operands(expr):
    # print(expr)

# @pg.production("symbol : OPERATOR")
# def _operator(expr):
    # print(expr)
    # return {
        # "+": None
    # }[expr]

@pg.production("symbol : OPEN BINOP OPERANDS CLOSE")
def _operation(expr):
    op = expr[1].value
    try:
        # All nums? Math
        operands = [float(e) for e in expr[2].value.split()]
        if op == "+":
            return sum(operands)
        elif op == "*":
            return reduce(lambda x, y: x*y, operands)
        elif op == "-":
            return reduce(lambda x, y: x-y, operands)
        elif op == "/":
            return reduce(lambda x, y: x/y, operands)
        else:
            raise NotImplementedError
    except ValueError:
        pass


parser = pg.build()
with open("./etude~", "r") as src:
    s = src.read()
    # print(s)
    # l = lexer.lex(s)
    l = srclexer.lex(s)
    for toplvl_tok in l:
        L = lexer.lex(toplvl_tok.value)
        # print(list(L))
        p = parser.parse(L)
        print(p)
