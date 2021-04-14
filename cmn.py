from random import randint, choice
from score import *


def make_notehead(note):
    # setter for head? to append automatically
    if isinstance(note.duration, str):
        note.head_punch = Char(name={
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

def setstem(self):
    self.stem_graver = Stem(length=10,thickness=1,x=.5,endxr=2)
    
    

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
        print("-------")
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

cmn.add(make_notehead, (Note,), ["treble"])
cmn.add(make_accidental_char, (Accidental,), ["treble", "bass"])
cmn.add(setstem, (Note,),["treble"])
cmn.add(f, (NGN.HForm,), ["horizontal"])

# def x(self): self._svg_list.append(SW.shapes.Rect(insert=(self.stem.left, self.stem.bottom),size=(5,5),fill=SW.utils.rgb(100,100,0,"%")))
# def xx(self): self._svg_list.append(SW.shapes.Rect(insert=(self.head.right, self.head.top),size=(2,5),fill=SW.utils.rgb(100,0,0,"%")))
# cmn.add(x, (Note,),["treble"])
# cmn.add(xx, (Note,),["treble"])



def reden(o): o.color=SW.utils.rgb(randint(0,100),0,0,"%")
# cmn.add(reden, (Stem,),["d"])
# print(cmn.domains)


# 680.3149 pxl
gemischt=[
Note(domain="treble", duration=1, pitch=["c",4]),
Accidental(pitch=["c", 4],domain="treble"),
Accidental(domain="bass"), 
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
print(NGN.mmtopx(100))
h=NGN.HForm(ruletable=cmn, content=gemischt,width=NGN.mmtopx(100),x=40,y=200, canvas_opacity=.2, width_locked=True)
NGN.render(h,)
