


class c:
    def __init__(self):
        self.__x = [0]
    @property
    def x(self): return self.__x
    @x.setter
    def x(self, l):
        print("Setter called ...", l)
        # ~ Here I would probably do more complex stuff
        # ~ before e.g. appending, but this one doesn't get
        # ~ called at all by appending to the list!

C=c()
print(C.x)
C.x.append(1)
print(C.x)
