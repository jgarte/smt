from random import randint, choice
import engine as E

""".smt File
[unknownName knownExpression] is an assignment.
[knownName knownExpression] ?
[myNote [note
            [domain treble]
            [color [rgb 100 10 20]]
            [absx 100] [absy 100]]]
[sform [content myNote]]
[render sform]
; Here we bind Python code
[py def double(x): return x * 2]
[double 4]
[page1 [page [title [bold Douxe [size [cm 10] Notation]] pour Piano]]]
Syntax known Names:
[SIZE Type:Number Type:String] Returns a new String with the size Number.  
[BOLD Type:String] Returns a new String in bold.

[RGB Type:Number Type:Number Type:Number] Returns an RGB Object for use as the value for the COLOR attribute.
[COLOR red] Designates the attribute color to be the string value red.
[LOOP variable Type:Sequence|[RANGE Type:Integer Type:Integer]]
"""


def notehead(note):
    if isinstance(note.dur, str):
        note.head = E.Char(name={
            "w": "noteheads.s0",
            "h": "noteheads.s1",
            "q": "noteheads.s2"
        }[note.dur])
    elif isinstance(note.dur, (float, int)):
        note.head = E.Char(name={
            1: "noteheads.s0",
            .5: "noteheads.s1",
            .25: "noteheads.s2"
        }[note.dur])
    note.head.y += randint(-100, 100)
    # note.head.x = 50
    note.append(note.head)

def clock_heads(lst):
    indices = []
    for i in range(len(lst)):
        if isinstance(lst[i], E.Note):
            indices.append(i)
    L =[]
    for s,e in zip(indices[:-1], indices[1:]):
        L.append(lst[s:e])
    return L

def decide_unit_dur(dur_counts):
    # return list(sorted(dur_counts.items()))[1][1]
    return list(sorted(dur_counts, key=lambda l:l[0]))[0][1]

punct_units = {1:7, .5: 5, .25: 3.5, 1/8: 2.5, 1/16: 2}

def ufactor(udur, dur2):
    return punct_units[dur2] / punct_units[udur]
    
def compute_perf_punct(cnt, w):
    clkheads=clock_heads(cnt)
    # print(clkheads)
    notes=list(filter(lambda x:isinstance(x, E.Note), cnt))
    durs=list(map(lambda x:x.dur, notes))
    dur_counts = []
    for d in set(durs):
        # dur_counts[durs.count(d)] =d
        # dur_counts[d] =durs.count(d)
        dur_counts.append((durs.count(d), d))
    udur=decide_unit_dur(dur_counts)
    uw=w / sum([x[0] * ufactor(udur, x[1]) for x in dur_counts])
    for x in notes:
        x.width += ((uw * ufactor(udur, x.dur)) - x.width)
        # print(x.content[0].width, x.width)
        # print("======")
def f(h):
    compute_perf_punct(h.content, h.width)
    h._lineup()
    # print("AAA", h.FIXBOTTOM)

E.r(1, (E.Note,), ["treble"], notehead)
E.r(2, (E.HForm,), ["horizontal"], f)



# print(E.mmtopxl(100))
# 680.3149 pxl
notes=[E.Note(spn="F2",dur=choice((1,.5,.25)),  domain="treble", canvas_color=E.rgb(randint(0, 100), randint(50, 100), randint(50, 100), "%")) for _ in range(5)]
# print(notes[0].width, notes[0].content[0].width)
# print(list(map(lambda n:n.x, notes[0].content)))
# print(notes[0].width)
h=E.HForm(content=notes,abswidth=E.mmtopxl(100))
# print(list(map(lambda n:n._fixtop, notes)))
h.render()
    
# a=E.SForm(xoff=20, content=[E.Char("clefs.F", xoff=50)])
# b=E.HForm(absy=100, content=[a])
# b.render()

