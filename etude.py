import engine as e




n = e.Note(domain="treble",_id="Note")
        
f=e.SForm(_id="SF", content=[n], canvas_color=e.rgb(0,0,100,"%"))


def head(note):
    headsym = {1: "noteheads.s0", 0.5: "noteheads.s1", .25: "noteheads.s2"}[note.dur]
    note.addcont(e.MChar(headsym, domain="head"))
    note.addcont(e.MChar("clefs.C", domain="c"))

def foo(self):
    # ~ print(self.color)
    self.color = e.rgb(100,0,0,"%")
def shiftx(o):
    o.x = 10



e.rule((e.Note,), ("treble",), head)
e.rule((e.MChar,),("head",), shiftx)
e.rule((e.MChar,), ("c",), foo)
f.render()#calls packsvglst
# ~ print(f.id, f.y, f.x)
# ~ for i in f.content:
    # ~ print(i.id, i.y,i.content[0].id,i.content[0].y)
    # ~ print(i.id, i.x,i.content[0].id,i.content[0].x)
