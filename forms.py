
class SmtObj:
    def __init__(self, _id):
        self.id = _id
class MChar(SmtObj):
    def __init__(self, _id):
        super().__init__(_id)

class Form(SmtObj):
    def __init__(self, _id, content=()):
        super().__init__(_id)
        self.content = content

        
def __descendants(obj, gen, D):
    """"""
    if isinstance(obj, Form):
        if gen in D:
            D[gen].extend(obj.content.copy())
        else:
            D[gen] = obj.content.copy()
        # ~ D.append([gen, obj.content])
        for child in obj.content:
            __descendants(child, gen+1, D)
    return D
    
def descendants(obj, lastgen_first=True):
    desc = __descendants(obj, 0, {})
    D = []
    for gen in sorted(desc.keys(), reverse=lastgen_first):
        D.extend(desc[gen])
    return D


# ~ f =Form("f1", 
        # ~ content=[MChar("m1"),
                # ~ Form("form", content=[MChar("mchar"), 
                                    # ~ Form("formX", content=[MChar("mcharYY")])]),
                # ~ MChar("m2"), 
                # ~ MChar("mc"),
                # ~ Form("f2", content=[MChar("m3"),
                                    # ~ MChar("m4"),
                                    # ~ Form("f3", content=[MChar("M5"),
                                                        # ~ Form("FF", content=([MChar("MM"+str(i)) for i in range(5)]))])])])


# ~ d = descendants(f)
d = __descendants(f, 0, {})
# ~ print(list(map(lambda x:x.id, d)))
