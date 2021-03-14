"""
rule_typespecifier_attribute (type_of_objs* or all) (domains or all) order_or_default_order desc

r("smt", (HorizontalForm, Note, Accidental), ("treble","bass"), -1, "Rule Description")

clause(-1, tuple, for i in range(10): print(i))
clause(-1, str,)
clause(-1, int,)
"""

_RULETABLE = {}
class rule:
    def __init__(self, order, ruler=isinstance, targs=True, domains=True, table=None):
        self.order = order
        self.ruler = ruler
        self.targs = targs
        self.domains = domains
        self.clauses = {}
        self.table = table or _RULETABLE
        self.table[self.order] = {"targs": targs,
        "domains": domains, "ruler": ruler, "clauses": self.clauses}
    def addclause(self, type_=object, body=None):
        self.clauses[type_] = body or (lambda:None)
def apply(fn, L):
    exec("{}({})".format(fn.__name__, ", ".join([repr(A) for A in L])))
def _argcount(fn): return fn.__code__.co_argcount
def apply_rules(obj):
    """
    Applies rules to OBJ and all it's descendants
    """
    family = [obj] + descendants(obj, False)
    for order in sorted(_RULETABLE):
        ruletab = _RULETABLE[order]
        ruler = ruletab["ruler"] # A string
        targtypes = ruletab["targs"]
        doms = ruletab["domains"]
        # ~ get targs to which rule should be applied
        targobjs = list(filter(lambda O: isinstance(O, targtypes), family))
        domobjs = list(filter(lambda O: O.domain in doms, targobjs))
        for O in domobjs:
            func = ruletab["clauses"][type(getattr(O, ruler)())]
            argcount = _argcount(func)
            if argcount == 0: func()
            elif argcount == 1: func(O)
            else: apply(func, [O] + reversed(O.ancestors[:argcount])) 
        
x=rule(0, targs=(int, str))
y=rule(1, targs=(str,))
def b(x, y, d,f,g,h,j,k,b=4): return x+x+y+y
# ~ x.addclause(type_=int, body=b)
# ~ print(x.clauses[int]("Hello ", "World!"))


print(argcount(b))
