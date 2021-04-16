from random import randint, choice
from score import *


def make_notehead(note):
    # setter for head? to append automatically
    if isinstance(note.duration, str):
        note.head_punch = NGN.Char(name={
            "w": "noteheads.s0",
            "h": "noteheads.s1",
            "q": "noteheads.s2"
        }[note.duration])
    elif isinstance(note.duration, (float, int)):
        note.head_punch = NGN.Char(name={
            1: "noteheads.s0",
            .5: "noteheads.s1",
            .25: "noteheads.s2"
        }[note.duration],
        )
        
def headcolor(n):
    n.head_punch.color = NGN.SW.utils.rgb(50,0,100,"%")
    # n.head_punch.x += 20
    n.append(NGN.Char(name="accidentals.flat",opacity=.5))
    

def longer(s):
    print("Longer",s.id)
    # s.length += randint(0, 51)
    NGN.cmn.add(headcolor, isnote)
    print(len(NGN.cmn))

def reden(stm):
    stm.color=NGN.SW.utils.rgb(100,0,0,"%")
    # stm.length += 10
    NGN.cmn.add(longer, isstem)
    #rule applied, appliedto=true

def isstem(o): return isinstance(o, Stem)
def setstem(self):
    self.stem_graver = Stem(length=10,thickness=5,opacity=.2) #taze , appliedto =false
    NGN.cmn.add(reden, isstem)
    


def notehead_vertical_pos(note):
    if isinstance(note.pitch, list):
        p = note.pitch[0]
        okt = note.pitch[1]
        note.headsymbol.y = ((note.fixbottom - {"c":-STAFF_SPACE, "d":-(.5 * STAFF_SPACE)}[p]) + ((4 - okt) * 7/8 * note.FIXHEIGHT))

        
def make_accidental_char(accobj):
    accobj.punch = NGN.Char(name="accidentals.sharp")

def make_clef_char(clefobj):
    clefobj.punch = NGN.Char(name={"treble":"clefs.G", "g": "clefs.G",
    "bass":"clefs.F", "alto":"clefs.C"}[clefobj.pitch])


def decide_unit_dur(dur_counts):
    # return list(sorted(dur_counts.items()))[1][1]
    return list(sorted(dur_counts, key=lambda l:l[0]))[0][1]

punct_units = {1:7, .5: 5, .25: 3.5, 1/8: 2.5, 1/16: 2}

def ufactor(udur, dur2):
    return punct_units[dur2] / punct_units[udur]
    
def compute_perf_punct(clocks, w):
    # notes=list(filter(lambda x:isinstance(x, Note), clocks))
    durs=list(map(lambda x:x.duration, clocks))
    dur_counts = []
    for d in set(durs):
        # dur_counts[durs.count(d)] =d
        # dur_counts[d] =durs.count(d)
        dur_counts.append((durs.count(d), d))
    udur=decide_unit_dur(dur_counts)
    uw=w / sum([x[0] * ufactor(udur, x[1]) for x in dur_counts])
    perfwidths = []
    for x in clocks:
        space = ((uw * ufactor(udur, x.duration)) - x.width)
        perfwidths.append(space)
        # x.width += ((uw * ufactor(udur, x.duration)) - x.width)
    return perfwidths

def right_guard(obj):
    return {Note: 10, Clef:10, Accidental: 1}[type(obj)]

def f(h):
    # print([(a.x, a.left, a.width) for a in h.content])
    clkchunks=clock_chunks(h.content)
    # print(clkchunks)
    clocks = list(map(lambda l:l[0], clkchunks))
    perfwidths = compute_perf_punct(clocks, h.width)
    if allclocks(h):
        for C, w in zip(h.content, perfwidths):
            C.width += w
            C.width_locked = True
    else:
        print("-------nonclocks")
        for c,w in zip(clkchunks, perfwidths):
            clock = c[0]
            nonclocks = c[1:]
            s=sum(map(lambda x:x.width + right_guard(x), nonclocks))
            if s < w:
                # add rest of perfect width - sum of nonclocks
                clock.width += (w - s)
                clock.width_locked = True
                for a in nonclocks:
                    a.width += right_guard(a)
                    a.width_locked = 1
    # print([(a.id, a.x) for a in h.content])


def noteandtrebe(x): return isinstance(x, Note) and x.domain == "treble"
NGN.cmn.add(make_notehead, noteandtrebe)
def isacc(x): return isinstance(x, Accidental)
NGN.cmn.add(make_accidental_char, isacc)
def isnote(x): return isinstance(x,Note)
NGN.cmn.add(setstem, isnote)

def greenhead(x): x.head_punch.color = NGN.SW.utils.rgb(0,0,100,"%")
NGN.cmn.add(greenhead, noteandtrebe)


def ish(x): return isinstance(x, NGN.HForm)
NGN.cmn.add(f, ish)

# 680.3149 pxl
gemischt=[
Note(domain="treble", duration=1, pitch=["c",4]),
Accidental(pitch=["c", 4],domain="treble"),
Accidental(domain="treble"), 
# Clef(pitch="g",domain="treble"),
Accidental(domain="treble"),
Note(pitch=["d",4],domain="treble", duration=.5),
Note(pitch=["d",4],domain="treble", duration=.25),
# Clef(domain="treble",pitch="bass"),
Accidental(domain="treble",pitch=["d",4])
]


# s=SForm(width=5,width_locked=0,x=50)
# s.append(Stem(length=10,thickness=30))
# h=HForm(content=[s],width=mmtopx(20),x=40,y=200, canvas_opacity=.2, width_locked=0)

# print(NGN.mmtopx(100))
h=NGN.HForm(content=gemischt,width=NGN.mmtopx(100),x=40,y=200, canvas_opacity=.2, width_locked=True,
id_="top")
NGN.render(h,)
# print(NGN.cmn.rules.keys())
