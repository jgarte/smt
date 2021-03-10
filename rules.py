"""
attribute (type_of_objs* or all) (domains or all) order_or_default_order desc
r("smt", (HorizontalForm, Note, Accidental), ("treble","bass"), -1, "Rule Description")
clause(-1, tuple)
clause(-1, str,)
clause(-1, int,)
"""

ruletable = {2:3,4:5,1:2}

def apply_rules(score_objs):
    for order, ruledict in sorted(ruletable.items()):
        targs =  
