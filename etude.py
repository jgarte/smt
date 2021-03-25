from random import randint, choice
import engine as E


def notehead(note):
    if isinstance(note.dur, str):
        note.append(E.Char(name={
            "w": "noteheads.s0",
            "h": "noteheads.s1",
            "q": "noteheads.s2"
        }[note.dur]))
    elif isinstance(note.dur, (float, int)):
        note.append(E.Char(name={
            1: "noteheads.s0",
            .5: "noteheads.s1",
            .25: "noteheads.s2"
        }[note.dur]))

def clock_heads(lst):
    indices = []
    for i in len(lst):
        if isinstance(lst[i], E.Note):
            indices.append(i)
    L =[]
    for s,e in zip(indices[:-1], indices[1:]):
        L.append(lst[s:e])
    return L

def decide_unit(dur_counts):
    return list(sorted(dur_counts.items()))[1]

punct_units = {1:7, .5: 5, .25: 3.5, 1/8: 2.5, 1/16: 2}

def ufactor(udur dur2):
    return punct_units[dur2] / punct_units[udur]
    
def compute_perf_punct(cnt, w):
    clkheads=clock_heads(cnt)
    notes=filter(lambda x:isinstance(x, E.Note), cnt)
    durs=list(map(lambda x:x.dur, notes))
    dur_counts = {}
    for d in set(durs):
        dur_counts[durs.count(d)] =d
    udur=decide_unit(dur_counts)
    uw=w / sum([x[0] * ufactor(udur, x[1]) for x in dur_counts.items()])
    

def punct(h)


E.r(1, (E.Note,), ["treble"], notehead)
E.r(2, (E.HForm,), ["horizontal"], punct)

h=E.HForm(content=[E.Note(domain="treble",dur=choice((1,.5,.25))) for _ in range(10)])
