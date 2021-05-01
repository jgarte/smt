"""

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
from score import *


lg = rply.LexerGenerator()

# lg.add('NUMBER', r'\d+')
lg.add('NUMBER', r'[\d\s]+')
lg.add('PLUS', r'\+')
lg.add('OPEN', r'\[')
lg.add('CLOSE', r'\]')

lg.ignore('\s+')

lexer = lg.build()


class Number(rply.token.BaseBox):
    def __init__(self, value):
        self.value = value
    def eval(self):
        return self.value
class Numbers(rply.token.BaseBox):
    def __init__(self, *value):
        self.value = value
    def eval(self):
        return self.value

# class Prefix(rply.token.BaseBox):
    # def __init__(self, cdr):
        # # self.left = left
        # self.cdr = cdr

class Add(rply.token.BaseBox):
   def __init__(self, cdr):
      self.cdr =cdr
   def eval(self):
      # print("CDR",self.cdr)
      return sum(self.cdr[0].eval())
      # return self.cdr.eval()+.2


pg = rply.ParserGenerator(
    # A list of all token names, accepted by the parser.
    ['NUMBER', 'OPEN', 'CLOSE',
     'PLUS'
    ],
    # A list of precedence rules with ascending precedence, to
    # disambiguate ambiguous production rules.
    # precedence=[
        # ('left', ['PLUS', 'MINUS']),
        # ('left', ['MUL', 'DIV'])
    # ]
)

@pg.production('expression : NUMBER')
def expression_number_____(p):
    # p is a list of the pieces matched by the right hand side of the
    # rule
    # print("---------",p[0].getstr().split(" "))
    # print("==========",Number([int(x) for x in p[0].getstr().split(" ")]).eval())
    return(Number([int(x) for x in p[0].getstr().split(" ")]))
    # return Number(int(p[0].getstr()))

# @pg.production('expression : OPEN expression CLOSE')
# def expression_parens(p):
   # print(">>>>", p)
   # return p[1]

@pg.production('expression : OPEN PLUS expression CLOSE')
# @pg.production('expression : expression MINUS expression')
# @pg.production('expression : expression MUL expression')
# @pg.production('expression : expression DIV expression')
def expression_binop(p):
    # left = p[0]
    # right = p[2]
   # print(">>",p[1].gettokentype())
   if p[1].gettokentype() == 'PLUS':
      return Add(p[2:-1])
   else:
      raise AssertionError('Oops, this should not be possible!')

parser = pg.build()

print(parser.parse(lexer.lex('[+ 102 3 45]')).eval())


















smtobjs = {
   "hform": HForm, "sform": SForm, "vform": VForm, "char": Char,
   "note": Note
}
smt_pubattrs = {
   "note": [x for x in dir(Note) if not x.startswith("_") and not callable(x)] 
}




# print(pubattrs["note"], not callable(Note.addsvg))
# print([x for x in dir(Note) if not x.startswith("_") and not inspect.isfunction(x)])
# pattern = "\[[\w]\]"
# print(re.fullmatch(pattern, "[note [pitch [+1 3]]]"))
