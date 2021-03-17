from random import randint
import engine as E

"""
me-lang me-engine
<hform <id 23> <content <note <spn <f 4>> <duration .5>>
                        <accidental <sharp>>
                        <rest <duration 1>>>>
                        -rest -duration 1
                        -note -spn f 3 1..
"""


def add_notehead(note):
    # ~ if isinstance(note.dur, int):
        # ~ H = E.MChar({1: "noteheads.s0", 0.5: "noteheads.s1"}[note.dur])
    # ~ elif isinstance(note.dur, str):
        # ~ H = E.MChar({"ganze": "noteheads.s0", "halbe": "noteheads.s1", "viertel": "noteheads.s2"}[note.dur])
    note.addcont(E.MChar(domain="clf",name="clefs.C"))
def color(mc): mc.color = E.rgb(*[randint(0, 101) for _ in range(3)],"%")

def draw_stave(mc):
    mc.x = randint(0, 21)
    E.r(3, E.MChar,("clf",),color)

E.r(1, E.Note, ["treble"], add_notehead)
E.r(2, E.Note, "treble", draw_stave)
# ~ E.rule((E.Note,), ("treble",), add_notehead)
# ~ E.rule((E.MChar,), ("clf",), draw_stave)

def getpaths(l):
    L = []
    for x in l:
        if isinstance(x, E.svgwrite.path.Path):
            L.append(x)
    return L

c=[E.Note(dur="viertel", domain="treble") for _ in range(5)]
# ~ Score
h = E.HForm(content=c)
# ~ print(getpaths(h._svglst))
# ~ print(list(map(lambda x:x.id, E.members(h))))
h.render()
# ~ h._apply_rules()
# ~ print(list(map(lambda x:x.id, E.members(h))))
print(E._ruletable)
