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
def notehead(note):
    if isinstance(note.dur, str):
        note.addcont(E.Char(name={
            "w": "noteheads.s0",
            "h": "noteheads.s1",
            "q": "noteheads.s2"
        }[note.dur]))
    elif isinstance(note.dur, (float, int)):
        note.addcont(E.Char(name={
            1: "noteheads.s0",
            .5: "noteheads.s1",
            .25: "noteheads.s2"
        }[note.dur]))
# ~ Deduces the notehead symbol from note's duration.
# E.r(1, (E.Note,), ["treble"], notehead)
# E.r(2, (E.Note,), ["treble"], lambda x: x.append(E.Char(name="clefs.F")))
"""
Music Notation Semantics Descriptor
"""
def f(x):
    x.content[1].left += 5
    x.content[2].left += 0

# E.r(2.3, (E.HForm,), ("horizontal",), f)
# E.r(4, (E.HForm,), ("horizontal",), f)


def reline(self):
    # h.content[0]._needs_hlineup=True
    self.content[1].x += 10
    self.content[2].x += 3

E.r(3, (E.HForm,), ["horizontal"], reline)
# E.r(4, (E.HForm,), ["horizontal"], reline)
# E.r(5, (E.HForm,), ["horizontal"], lambda h: h._lineup())


# print(E._ruletable)
# print(E._ruletargets)
# print(E._ruledomains)
# from random import choice
# E.r(1, (E.HForm,), ("horizontal",), lambda h: h.add(*[E.Char(name="clefs.{}".format(choice(["C","F","G"]))) for _ in range(10)]))
# n1 = E.Note(dur="q", content=[E.Char(name="clefs.F")])
# n2 = E.Note(dur=1, content=[E.Char(name="clefs.G")])
# n3=E.Note(dur=1, content=[E.Char(name="accidentals.sharp")])

h = E.HForm(content=[E.Char(name="clefs.F") for _ in range(4)])
# h=E.HForm(content=[n1, n2,n3])
# h=E.HForm(content=[E.Note(domain="treble") for _ in range(3)])
# h2=E.HForm(content=[E.HForm(content=[E.Note(domain="treble") for _ in range(3)]) for _ in range(2)])
# h2=E.HForm(content=[E.HForm(content=[E.Char(name="clefs.F") for _ in range(2)]) for _ in range(3)])

h.render()
# print(E.Char(name="clefs.C").left)

"""
MNSD
music typesetter
Music Notation Semantics
me
"""
