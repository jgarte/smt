from random import randint, choice
from score import *


def make_notehead(note):
    # setter for head? to append automatically
    if isinstance(note.duration, str):
        note.head_punch = e.Char(name={
            "w": "noteheads.s0",
            "h": "noteheads.s1",
            "q": "noteheads.s2"
        }[note.duration])
    elif isinstance(note.duration, (float, int)):
        note.head_punch = e.Char(name={
            1: "noteheads.s0",
            .5: "noteheads.s1",
            .25: "noteheads.s2"
        }[note.duration],
        )
        
def headcolor(n):
    n.head_punch.color = e.SW.utils.rgb(50,0,100,"%")
    # n.head_punch.x += 20
    n.append(e.Char(name="accidentals.flat",opacity=.5))
    # print(len(e.cmn))
    

def longer(s):
    # s.length += randint(0, 51)
    e.cmn.add(headcolor, isnote)

def reden(stm):
    stm.color=e.SW.utils.rgb(100,0,0,"%")
    # stm.length += 10
    e.cmn.add(longer, isstem)
    #rule applied, appliedto=true

def isstem(o): return isinstance(o, Stem)
def setstem(self):
    if self.duration in (.25, .5):
        s=Stem(length=13,thickness=10,x=self.x+5)
        self.stem_graver = s #taze , appliedto =false
        print(s,s._x_locked, s._y_locked)
        # e.cmn.add(rutchS, isstem)
def rutchS(s): s.x += .5
    


def notehead_vertical_pos(note):
    if isinstance(note.pitch, list):
        p = note.pitch[0]
        okt = note.pitch[1]
        note.headsymbol.y = ((note.fixbottom - {"c":-STAFF_SPACE, "d":-(.5 * STAFF_SPACE)}[p]) + ((4 - okt) * 7/8 * note.FIXHEIGHT))

        
def make_accidental_char(accobj):
    accobj.punch = e.Char(name="accidentals.sharp")

def setclef(clefobj):
    clefobj.punch = e.Char(name={"g": "clefs.G",
    "f":"clefs.F", "c":"clefs.C"}[clefobj.pitch])


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
        # a space is excluding the own width of the clock (it's own char width)
        space = ((uw * ufactor(udur, x.duration)) - x.width)
        perfwidths.append(space)
        # x.width += ((uw * ufactor(udur, x.duration)) - x.width)
    return perfwidths

def right_guard(obj):
    return {Note: 2, Clef:3, Accidental: 2,}[type(obj)]
def first_clock_idx(l):
    for i,x in enumerate(l):
        if isinstance(x, Clock):
            return i
def punctuate_line(h):
    first_clock_idx_ = first_clock_idx(h.content)
    startings=h.content[0:first_clock_idx_]
    for starting in startings:
        starting.width += right_guard(starting)
    clkchunks=clock_chunks(h.content[first_clock_idx_:])
    # print(clkchunks)
    clocks = list(map(lambda l:l[0], clkchunks))
    perfwidths = compute_perf_punct(clocks, h.width - sum([x.width for x in startings]))
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
                    # dont need to lock this width, since it's not touched
                    # by setstem: setstem only impacts it's papa: the NOTE object
                    # a.width_locked = 0


def noteandtrebe(x): return isinstance(x, Note) and x.domain == "treble"
def isacc(x): return isinstance(x, Accidental)
def isnote(x): return isinstance(x,Note)

def greenhead(x): x.head_punch.color = e.SW.utils.rgb(0,0,100,"%")
def reden(x): 
    print(x.id, x.content)
    x.content[0].color = e.SW.utils.rgb(100,0,0,"%")
def S(x): return x.id == "S"
def isline(x): return isinstance(x, Line)
def ish(x): return isinstance(x, e.HForm)
def isclef(x): return isinstance(x, Clef)
def opachead(n): n.head_punch.opacity = .3

e.cmn.add(make_notehead, noteandtrebe)
e.cmn.add(make_accidental_char, isacc)
# e.cmn.add(greenhead, noteandtrebe)
e.cmn.add(setstem, isnote)
e.cmn.add(setclef, isclef)
e.cmn.add(opachead, isnote)

e.cmn.add(punctuate_line, isline)

def addstaff(n):
    for i in range(5):
        l=e.HLineSegment(length=n.width, thickness=1, endxr=0, y=i*e.STAFF_SPACE + n.top)
        n.append(l)
        # n.append(e.HLineSegment(length=n.width, thickness=1, endxr=0))

e.cmn.add(addstaff, isnote)



# 680.3149 pxl
# gemischt=[
# Note(domain="treble", duration=1, pitch=["c",4]),
# Accidental(pitch=["c", 4],domain="treble",),
# Accidental(domain="treble"), 
# # Clef(pitch="g",domain="treble"),
# Accidental(domain="treble"),
# Note(pitch=["d",4],domain="treble", duration=.5),
# Note(pitch=["d",4],domain="treble", duration=.25),
# # Clef(domain="treble",pitch="bass"),
# Accidental(domain="treble",pitch=["d",4])
# ]

class Line(e.HForm):
    def __init__(self, *objs, **kw):
        e.HForm.__init__(self, content=objs, **kw)
# s=SForm(width=5,width_locked=0,x=50)
# s.append(Stem(length=10,thickness=30))
# h=HForm(content=[s],width=mmtopx(20),x=40,y=200, canvas_opacity=.2, width_locked=0)
if __name__=="__main__":
    print(e.mmtopx(100))
# e.render(Line(
# Clef(pitch="g"),
# Clef(pitch="f"),
# Clef(pitch="c"),
# Note(domain="treble", duration=.25, pitch=["c",4]), 
# Note(domain="treble", duration=1, pitch=["c",4]), 
# Note(domain="treble", duration=.25, pitch=["c",4]), 
# Note(domain="treble", duration=.5, pitch=["c",4]), 
# Note(domain="treble", duration=1, pitch=["c",4]), 
# Note(domain="treble", duration=.5, pitch=["c",4]), 
# Note(domain="treble", duration=.25, pitch=["c",4]), 

# width=e.mmtopx(70),x=20,y=20, width_locked=True))

# h=e.HForm(content=gemischt,width=e.mmtopx(100),x=40,y=200, canvas_opacity=.2, width_locked=True,id_="top")
# e.render(h,)
