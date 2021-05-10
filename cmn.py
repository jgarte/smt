from random import randint, choice
import score as S
import copy 

################ time signature

def istime(x): return isinstance(x, S.SimpleTimeSig)
def settime(ts):
    ts.num_punch=S.E.MChar({3: "three", 4:"four", 5:"five"}.get(ts.num, ".notdef"))
    ts.denom_punch=S.E.MChar({4: "four", 2:"two", 1: "one"}.get(ts.denom, ".notdef"))
    if ts.denom == 1:
        d=ts.denom_punch.parent().width - ts.denom_punch.width
        ts.denom_punch.right = ts.denom_punch.parent().right
        







# Setting noteheads
def make_notehead(note):
    # setter for head? to append automatically
    if isinstance(note.duration, str):
        note.head_punch = S.E.MChar(name={
            "w": "noteheads.s0",
            "h": "noteheads.s1",
            "q": "noteheads.s2",
        }[note.duration])
    # elif isinstance(note.duration, (float, int)):
        # note.head_punch = S.E.MChar(name={
            # 1: "noteheads.s0",
            # .5: "noteheads.s1",
            # .25: "noteheads.s2"
        # }[note.duration],
        # rotate=0)
def isnote(x): return isinstance(x,S.Note)



def isstem(o): return isinstance(o, S.Stem)
def setstem(self):
    if self.duration in (.25, .5, "q", "h", "8"):
        # self.stem_graver = S.E._LineSeg(x2=0, y2=10,thickness=2)
        s=S.Stem(length=15,thickness=1, 
        # color=S.E.SW.utils.rgb(0,50,0,"%"),
        x=self.x+.5, # Eigentlich wenn wir dieses X eingeben, es wird als absolut-X gesehen.
        y=self.head_punch.y,
        endyr=1,endxr=1,rotate=0,
        origin_visible=0)
        self.stem_graver = s #taze , appliedto =false

def notehead_vertical_pos(note):
    if isinstance(note.pitch, list):
        p = note.pitch[0]
        okt = note.pitch[1]
        note.head_punch.y = ((note.fixbottom - {
            "c":-S.E.STAFF_SPACE, 
            "d":-(.5 * S.E.STAFF_SPACE),
            
        }[p]) + ((4 - okt) * 7/8 * note.FIXHEIGHT))


def make_accidental_char(accobj):
    if not accobj.punch:
        accobj.punch = S.E.MChar(name="accidentals.sharp")

def setclef(clefobj):
    clefobj.punch = S.E.MChar(name={"g": "clefs.G", 1:"clefs.C",
    "F":"clefs.F", "f":"clefs.F_change","c":"clefs.C"}[clefobj.pitch],
    rotate=0,)

############################# punctuation

def decide_unit_dur(dur_counts):
    # return list(sorted(dur_counts.items()))[1][1]
    return list(sorted(dur_counts, key=lambda l:l[0]))[0][1]

punct_units = {"w":7, "h": 5, "q": 3.5,"8":3.5, "e": 2.5, "s": 2}

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
    return {S.Note: 2, S.Clef:3, S.Accidental: 2, S.SimpleTimeSig: 5}[type(obj)]
def first_clock_idx(l):
    for i,x in enumerate(l):
        if isinstance(x, S.Clock):
            return i
            
            
def punctsys(h):
    # print("---punct----")
    first_clock_idx_ = first_clock_idx(h.content)
    startings=h.content[0:first_clock_idx_]
    for starting in startings:
        starting.width += right_guard(starting)
    clkchunks=S.clock_chunks(h.content[first_clock_idx_:])
    # print(clkchunks)
    clocks = list(map(lambda l:l[0], clkchunks))
    perfwidths = compute_perf_punct(clocks, h.width - sum([x.width for x in startings]))
    if S.allclocks(h):
        for C, w in zip(h.content, perfwidths):
            C.width += w
            C._width_locked = True
    else:
        for c,w in zip(clkchunks, perfwidths):
            clock = c[0]
            nonclocks = c[1:]
            s=sum([nc.width + right_guard(nc) for nc in nonclocks])
            # s=sum(map(lambda x:x.width + right_guard(x), nonclocks))
            if s <= w:
                # add rest of perfect width - sum of nonclocks
                clock.width += (w - s)
                clock._width_locked = True
                for a in nonclocks:
                    a.width += right_guard(a)
                    # dont need to lock this width, since it's not touched
                    # by setstem: setstem only impacts it's papa: the NOTE object
                    # a._width_locked = 1
    # h._lineup()


def noteandtreble(x): return isinstance(x, S.Note) and x.domain == "treble"
def isacc(x): return isinstance(x, S.Accidental)


def greenhead(x): x.head_punch.color = e.SW.utils.rgb(0,0,100,"%")
def reden(x): 
    print(x.id, x.content)
    x.content[0].color = e.SW.utils.rgb(100,0,0,"%")
def Sid(x): return x.id == "S"
def isline(x): return isinstance(x, System)
def ish(x): return isinstance(x, e.HForm)
def isclef(x): return isinstance(x, S.Clef)
def opachead(n): n.head_punch.opacity = .3

# Rules adding
"""
hook mehrmals überall, 
test
"""
S.E.cmn.unsafeadd(settime,istime,"Set Time...",)
S.E.cmn.unsafeadd(make_notehead, noteandtreble, "make noteheads",)
S.E.cmn.unsafeadd(notehead_vertical_pos, noteandtreble)
S.E.cmn.unsafeadd(make_accidental_char, isacc, "Making Accidental Characters",)
# e.cmn.unsafeadd(greenhead, noteandtreble)
S.E.cmn.unsafeadd(setstem, isnote, "Set stems",)
S.E.cmn.unsafeadd(setclef, isclef, "Make clefs",)
# S.E.cmn.unsafeadd(opachead, isnote)
S.E.cmn.unsafeadd(punctsys, isline, "Punctuate",)


def setbm(l):
    o=[x for x in l.content if isnote(x) and x.duration in ("q","h")] #note mit openbeam
    # c=[x for x in l.content if isnote(x) and x.close_beam][0]
    # d=c.stem_graver.right -o.stem_graver.left
    for a in o:
        a.obeam_graver = S.E.HLineSeg(length=a.width,thickness=5,
        x=a.left,
        y=a.stem_graver.bottom,
        # rotate=45,
        )
    # o.append(S.E.HLineSeg(length=o.width,thickness=5,x=o.left, y=o.stem_graver.bottom))
    # c.append(S.E.HLineSeg(length=o.width,thickness=5,x=o.left, y=o.stem_graver.bottom))


S.E.cmn.unsafeadd(setbm, isline, "Set beams after Noten stehen fest (punctuation)",)


def addstaff(n):
    # s=S.Staff()
    # n.append(s)
    # print(s.y)
    # n.append(S.E.MultiHLineSeg(6, S.E.STAFF_SPACE, n.fixtop))
    # m=S.E.MChar(name="m")
    # n.append(m)
    # n.append(S.E.HLineSeg(length=30, thickness=1, y=n.fixtop))
    # print(m.x, m.y, n.x, n.y)
    # print(n.FIXHEIGHT)
    x=5
    h=n.FIXHEIGHT / (x-1)
    for i in range(x):
        l=S.E.HLineSeg(length=n.width, thickness=1, y=i*h + n.top)
        n.append(l)
        # S.E.cmn.add(rescale, pred(obj, isinstance(obj, int)), "Reset acc xscale.")
        # print(S.E.cmn.rules.keys())

# class pred:
    # def __init__(self, obj, *exprs):
        # self.obj = obj
        # self.exprs = exprs
    # def _replace(self):
        # for e in self.exprs:
            # print(e)
# # pred(isinstance(int), )
    
S.E.cmn.unsafeadd(addstaff, isnote, "Draws stave.")


def skew(staff):
    print(staff.skewx)
    staff.skewx = 50
    print(staff.skewx)
def ishline(x): return isinstance(x,S.E.HLineSeg)
# S.E.cmn.add(skew, isline, "SKEW stave")

def flag(note):
    if note.duration != 1:
        # print(note.stem_graver.y)
        note.append(S.E.MChar(name="flags.d4",y=note.stem_graver.bottom,x=note.x+.5,
        origin_visible=1))
# S.E.cmn.add(flag, isnote, "Flags...")
# print(S.E._glyph_names("haydn-11"))

# def bm(n):
    # if n.stem_graver:
        # n.stem_graver.length -= 10
        # n.append(S.E.HLineSeg(length=10, thickness=5, y=n.stem_graver.bottom, skewy=-0, endxr=1,endyr=.5))


# S.E.cmn.add(bm, isnote, "beams")



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

class System(S.E.HForm):
    def __init__(self, cnt, **kw):
        S.E.HForm.__init__(self, content=cnt, **kw)
# s=SForm(width=5,width_locked=0,x=50)
# s.append(Stem(length=10,thickness=30))
# h=HForm(content=[s],width=mmtopx(20),x=40,y=200, canvas_opacity=.2, width_locked=0)
# F=S.E.RuleTable()
# def note(pitch, dur, **kwargs):
    # return {"type": "note", "pitch":pitch, "dur":dur,**kwargs}
# def sethead(n):
    # print(n["dur"])
    # return S.E.SForm(content=S.E.MChar(n["name"]))
# print(sethead(note(0,1,name="noteheads.s0")))
if __name__=="__main__":
    print(S.E.mmtopx(100))
    s1=System(
        [
        S.Clef(pitch="g"),
        S.SimpleTimeSig(denom=1),
        # # S.Clef(pitch="f"),
        # # S.Clef(pitch="F"),
        # # S.Clef(pitch="F"),
        # # S.Clef(pitch="F"),
        # # S.Clef(pitch="c"),
        S.Note(domain="treble", duration="h", pitch=["c",4]), 
        S.Note(domain="treble", duration="q", pitch=["c",4]), 
        # Wir entscheiden über beam, wie stem einfach in Rules!
        S.Note(domain="treble", duration="h", pitch=["c",4]), 
        S.Note(domain="treble", duration="h", pitch=["d",4]),
        S.Accidental(pitch="c",         ),
        *[S.Note(domain="treble", duration=choice(["q", "h"]), pitch=["c",4]) for _ in range(7)],
        S.Note(domain="treble", duration="w", pitch=["c",4]), 
        S.Note(domain="treble", duration="q", pitch=["c",4]), 
        S.Note(domain="treble", duration="q", pitch=["c",4])],
    width=S.E.mmtopx(100))
    
    s2=System([S.SimpleTimeSig(denom=4),*[S.Note(domain="treble", duration=choice(["q", "h"]), pitch=["c",4]) for _ in range(10)]], width=S.E.mmtopx(100))
    
    # C= S.E.VForm(content=[s1], x=200, y=120)
    # print(C.y,C.fixtop,C.top)
    S.E.render(S.Note(domain="treble", duration="q", pitch=["c",4]))
    
