
import tempfile
import xml.etree.ElementTree as ET
import subprocess as sp


##### Font
class Bbox:
    def __init__(self, x, y, left, right, top, bottom, width, height):
        self.x = x
        self.y = y
        self.left = left
        self.right = right
        self.top = top
        self.bottom = bottom
        self.width = width
        self.height = height
class Glyph:
    def __init__(self, name, bbox, pathd):
        self.name = name
        self.bbox = bbox
        self.pathd = pathd

__fontdicts = {}
font = "Haydn"
__staff_height_reference_glyph = "clefs.c"

def fontdict(fontname): return __fontdicts[fontname]
def glyphs(fontname): return fontdict(fontname).keys()
def glyph(name, fontname): return fontdict(fontname)[name]

def instfont(fontname, srcpath, shrg=__staff_height_reference_glyph):
    """"""
    glyph_pathd = {}
    for E in ET.parse(srcpath).iter():
        if "glyph-name" in E.attrib: # An identified glyph?
            try:
                glyph_pathd[E.attrib["glyph-name"]] = E.attrib["d"]
            except KeyError: # E.g. space glyph has no pathd in haydn!
                glyph_pathd[E.attrib["glyph-name"]] = "" # An empty string as pathd?????
    temp_bbox_file = tempfile.NamedTemporaryFile(mode="r")
    sp.run(["/usr/bin/fontforge", "-script", 
            "/home/amir/Work/Python/me/fontinstprep.ff", 
            srcpath, temp_bbox_file.name])
    # ~ Register glyphs and their bboxes
    D = {}
    for ln in temp_bbox_file:
        if not(ln.isspace()): # Auf linien mit NUR space verzichten
            name, minx, miny, maxx, maxy, w, h = ln.strip().split(" ")
            D[name] = {
            "d": glyph_pathd[name], "x": minx, "y": miny,
            "left": minx, "right": maxx,
            "top": miny, "bottom": maxy,
            "width": w, "height": h
            }
    # ~ Closing Neccessary?
    temp_bbox_file.close()
    __fontdicts[fontname] = D

# ~ Iinstalled fonts
instfont(font, "/home/amir/haydn/svg/haydn-11.svg")







##### Rastral
__PXPERMM = 3.7795275591 # Pixel per mm

def mmtopx(mm): return mm * __PXPERMM
def chlapik_staff_space(rastral):
    return {
    2: mmtopx(1.88), 3: mmtopx(1.755), 4: mmtopx(1.6),
    5: mmtopx(1.532), 6: mmtopx(1.4), 7: mmtopx(1.19),
    8: mmtopx(1.02)}[rastral]

space = chlapik_staff_space(2)
scale = 1
        
# ~ __scale = 

meid_counter = 0
meid_name = "smtobj"
def rndid():
    global meid_counter
    _id = meid_name + str(meid_counter)
    meid_counter += 1
    return _id

class MeObj:
    def __init__(self, ancestors=[], _id=rndid(), svglst=[], domain=None):
        self.ancestors = ancestors
        self.id = _id
        self.svglst = svglst
        self.domain = domain

class Canvas(MeObj):
    def __init__(self, font, absx, absy, offx=0, offy=0,
    xscale=scale, yscale=scale, *args):
        super().__init__(*args)
        self.font = font
        self.absx = absx
        self.absy = absy
        self.offx = offx
        

class MChar(MeObj):
    def __init__(self, ):
        super().__init__(_id)

class Form(MeObj):
    def __init__(self, _id, content=()):
        super().__init__(_id)
        self.content = content

        
def __descendants(obj, N, D):
    """"""
    if isinstance(obj, Form):
        if not(N in D): D[N] = []
        # need objs themselves
        for child in obj.content:
            D[N].append(child)
        for child in obj.content:
            __descendants(child, N+1, D)
    return D
    
def descendants(obj, lastgen_first=True):
    D = []
    for _, gen in sorted(__descendants(obj, 0, {}).items(), reverse=lastgen_first):
        D.extend(gen)
    return D

# ~ f =Form("f1", 
        # ~ content=[MChar("m1"),
                # ~ Form("form", content=[MChar("mchar"), 
                                    # ~ Form("formX", content=[MChar("mcharYY")])]),
                # ~ MChar("m2"), 
                # ~ MChar("mc"),
                # ~ Form("f2", content=[MChar("m3"),
                                    # ~ MChar("m4"),
                                    # ~ Form("f3", content=[MChar("M5"),
                                                        # ~ Form("FF", content=([MChar("MM"+str(i)) for i in range(5)]))])])])

# ~ for x in descendants(f):
    # ~ print(x.id)
