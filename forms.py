
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

        
def __descendants(obj, N, D):
    """"""
    if isinstance(obj, Form):
        if N in D:
            D[N].extend(obj.content)
        else:
            D[N] = obj.content
        for child in obj.content:
            __descendants(child, N+1, D)
    return D
    
def descendants(obj, lastgen_first=True):
    D = []
    for _, gen in sorted(__descendants(obj, 0, {}).items(), reverse=lastgen_first):
        D.extend(gen)
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

