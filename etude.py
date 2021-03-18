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
        note.addcont(E.MChar(name={
            "w": "noteheads.s0",
            "h": "noteheads.s1",
            "q": "noteheads.s2"
        }[note.dur]))
    elif isinstance(note.dur, (float, int)):
        note.addcont(E.MChar(name={
            1: "noteheads.s0",
            .5: "noteheads.s1",
            .25: "noteheads.s2"
        }[note.dur]))
# ~ Deduces the notehead symbol from note's duration.
E.r(1, (E.Note,), ["treble"], notehead)
E.r(2, (E.Note,), ["treble"], lambda x: x.addcont(E.MChar(name="clefs.F")))
E.r(3, (E.HForm,), ["horizontal"], lambda h: h._lineup())


print(E._ruletable)
print(E._ruletargets)
print(E._ruledomains)
cnt = [E.Note(dur="q"), E.Note(dur=1), E.Note(dur=.25), E.Note(dur="h")]
h = E.HForm(content=cnt)
h.render()


"""
MNSD
music typesetter
Music Notation Semantics
me
"""
