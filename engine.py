
import tempfile
import xml.etree.ElementTree as ET
import subprocess as sp
import svgwrite

##### Font
__fontdicts = {}
font = "Haydn"
STAFF_HEIGHT_REFERENCE_GLYPH = "clefs.C"

def fontdict(fontname): return __fontdicts[fontname]
def glyphs(fontname): return fontdict(fontname).keys()
def glyph(name, fontname): 
    """Returns glyph's dictionary"""
    return fontdict(fontname)[name]

def instfont(fontname, srcpath, shrg=STAFF_HEIGHT_REFERENCE_GLYPH):
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
            # ~ Create glyph's dict
            D[name] = {
            "d": glyph_pathd[name],
            "x": float(minx), "y": float(miny),
            "left": float(minx), "right": float(maxx),
            "top": float(miny), "bottom": float(maxy),
            "width": float(w), "height": float(h)
            }
    # ~ Closing Neccessary?
    temp_bbox_file.close()
    __fontdicts[fontname] = D

# ~ Iinstalled fonts
instfont("Haydn", "/home/amir/haydn/svg/haydn-11.svg")



##### Rastral, Dimensions, Margins
__PXPERMM = 3.7795275591 # Pixel per mm

def mmtopx(mm): return mm * __PXPERMM
def chlapik_staff_space(rastral):
    return {
    2: mmtopx(1.88), 3: mmtopx(1.755), 4: mmtopx(1.6),
    5: mmtopx(1.532), 6: mmtopx(1.4), 7: mmtopx(1.19),
    8: mmtopx(1.02)}[rastral]

space = chlapik_staff_space(2)
scale = 1
def _scale():
    return scale * ((4 * space) / glyph("clefs.C", "Haydn")["height"])
def toplevel_scale(R): return R * _scale()

_LEFT_MARGIN = mmtopx(36)
_TOP_MARGIN = mmtopx(56)


##### Score Objects

class MeObj:
    _meid_count = -1
    _meid_name = "ME"
    def __init__(self, _id=None, domain=None):
        self.ancestors = []
        self.id = self.allocid(_id)
        self._svglst = []
        self.domain = domain
    def allocid(self, _id):
        if not(_id):
            MeObj._meid_count += 1
            return MeObj._meid_name + str(MeObj._meid_count)
        else: return _id

# ~ Canvas, Origin's Circle, Origin's Cross, Origin's Circle Contour
mchar_cnv = __mchar_orgcrcl = __mchar_orgcrs = __mchar_orgcrcl_cntr = "deeppink"
__sform_cnv = __sform_orgcrcl = __sform_orgcrs = __sform_orgcrcl_cntr = "tomato"
__hform_cnv = __hform_orgcrcl = __hform_orgcrs = __hform_orgcrcl_cntr = "green"
__vform_cnv = __vform_orgcrcl = __vform_orgcrs = __vform_orgcrcl_cntr = "blue"
__orgcrs_len = 20
__orgcrcl_r = 4
__orgcrcl_opac = 0.3
__orgln_thickness = 0.06
pgw = mmtopx(210)
pgh =mmtopx(297)

class Canvas(MeObj):
    def __init__(self, canvas_color,
    absx=None, absy=None, toplevel=False, font=font, canvas_opacity=0.3,
    xoff=0, yoff=0, xscale=scale, yscale=scale, canvas_visible=True,
    **kwargs):
        super().__init__(**kwargs)
        self.font = font
        self.canvas_color = canvas_color
        self.canvas_opacity = canvas_opacity
        self.xoff = xoff
        self.yoff = yoff
        self.xscale = xscale
        self.yscale = yscale
        self.toplevel = toplevel
        self.absx = _LEFT_MARGIN if self.toplevel and not(absx) else absx
        self.absy = _TOP_MARGIN if self.toplevel and not(absy) else absy
        self.canvas_visible = canvas_visible
        # ~ We need xy at init-time, just make absx 0 above??????
        self._x = (self.absx or 0) + self.xoff
        self._y = (self.absy or 0) + self.yoff
    def _bbox_rect(self): 
        return svgwrite.shapes.Rect(
        insert=(self.left, self.top),
        size=(self.width, self.height), fill=self.canvas_color,
        fill_opacity=self.canvas_opacity
        )
    # ~ A canvas can be a page??
    def render(self):
        D = svgwrite.drawing.Drawing(filename="/tmp/me.svg", size=(pgw,pgh),debug=True)
        self._pack_svglst()
        for elem in self._svglst:
            D.add(elem)
        D.save(pretty=True)


class MChar(Canvas):
    def __init__(self, name, **kwargs):
        super().__init__(mchar_cnv, **kwargs)
        self.name = name
        self._left = self.compute_leftmost()
        self._right = self.compute_rightmost()
        self._width = self.compute_width()
        self._top = self.compute_topmost()
        self._bottom = self.compute_bottommost()
        self._height = self.compute_height()
    # ~ Horizontals
    @property
    def x(self): return self._x
    @property
    def left(self): return self._left
    @property
    def right(self): return self._right
    @property
    def width(self): return self._width
    @x.setter
    def x(self, newx):
        dx = newx - self.x
        self._left += dx
        self._right += dx
        self._x += dx
        for A in reversed(self.ancestors): # An ancestor IS a Form.
            A._left = A.compute_leftmost()
            A._right = A.compute_rightmost()
            A._width = A.compute_width()
    # ~ Verticals
    @property
    def y(self): return self._y
    @property
    def top(self): return self._top
    @property
    def bottom(self): return self._bottom
    @property
    def height(self): return self._height
    @y.setter
    def y(self, newy): pass
    def compute_leftmost(self):
        return self.x + toplevel_scale(glyph(self.name, self.font)["left"])
    def compute_rightmost(self):
        return self.x + toplevel_scale(glyph(self.name, self.font)["right"])
    def compute_width(self):
        return toplevel_scale(glyph(self.name, self.font)["width"])
    def compute_topmost(self):
        return self.y + toplevel_scale(glyph(self.name, self.font)["top"])
    def compute_bottommost(self):
        return self.y + toplevel_scale(glyph(self.name, self.font)["bottom"])
    def compute_height(self):
        return toplevel_scale(glyph(self.name, self.font)["height"])
    def _pack_svglst(self):
        # ~ Add the music character
        self._svglst.append(
        svgwrite.path.Path(d=glyph(self.name, self.font)["d"],
        id_=self.id, fill="black", fill_opacity=1,
        transform="translate({0} {1}) scale(1 -1) scale({2} {3})".format(
        self.x, self.y, self.xscale*_scale(), self.yscale*_scale())))
        # ~ Add bbox rect
        self._svglst.append(self._bbox_rect())

def __descendants(obj, N, D):
    """"""
    if isinstance(obj, _Form) and obj.content:
        if not(N in D): 
            D[N] = obj.content
        else:
            D[N].extend(obj.content)
        # need objs themselves
        # ~ for child in obj.content:
            # ~ D[N].append(child)
        for child in obj.content:
            __descendants(child, N+1, D)
    return D
    
def descendants(obj, lastgen_first=True):
    D = []
    for _, gen in sorted(__descendants(obj, 0, {}).items(), reverse=lastgen_first):
        D.extend(gen)
    return D

class _Form(Canvas):
    def __init__(self, content=None, uwidth=None, **kwargs):
        super().__init__(svgwrite.utils.rgb(1, 0, 0), **kwargs)
        self.content = content if content else []
        self.FIXTOP = self.y + toplevel_scale(glyph(STAFF_HEIGHT_REFERENCE_GLYPH, self.font)["top"])
        self.FIXBOTTOM = self.y + toplevel_scale(glyph(STAFF_HEIGHT_REFERENCE_GLYPH, self.font)["bottom"])
        self.FIXHEIGHT = toplevel_scale(glyph(STAFF_HEIGHT_REFERENCE_GLYPH, self.font)["height"])
        self.uwidth = uwidth
        for d in descendants(self, False):
            d.ancestors.insert(0, self) # Need smteq??
        for C in self.content:
            if not(C.absx):
                # ~ Call child's setter
                C.x += self.x
            if not(C.absy):
                C.y += self.y
    # ~ Horizontal Attributes
    @property
    def x(self): return self._x
    @property
    def left(self): return self._left
    @property
    def right(self): return self._right
    @property
    def width(self): return self._width
    @x.setter
    def x(self, newx):
        dx = newx - self.x
        self._left += dx
        self._right += dx
        self._x += dx
        for d in descendants(self, False):
            d._x += dx
            d._left += dx
            d._right += dx
        for a in reversed(self.ancestors):
            a._left = a.compute_leftmost()
            a._right = a.compute_rightmost()
            a._width = a.compute_width()
    # ~ Vertical Attributes
    @property
    def y(self): return self._y
    @property
    def top(self): return self._top
    @property
    def bottom(self): return self._bottom
    @property
    def height(self): return self._height
    @y.setter
    def y(self, newy): pass
    def compute_leftmost(self):
        return min([self.x] + list(map(lambda c: c.left, self.content)))
    def compute_rightmost(self):
        return max([self.x] + list(map(lambda c: c.right, self.content)))
    def compute_width(self): return self.right - self.left
    def compute_topmost(self):
        return min([self.FIXTOP] + list(map(lambda C: C.top, self.content)))
    def compute_bottommost(self):
        return max([self.FIXBOTTOM] + list(map(lambda C: C.bottom, self.content)))
    def compute_height(self): return self.bottom - self.top
    def _pack_svglst(self):
        # ~ Add content
        for C in self.content:
            C.xscale *= self.xscale
            C.yscale *= self.yscale
            C._pack_svglst() # Recursively gather svg elements
            self._svglst.extend(C._svglst)
        # ~ Bbox
        if self.canvas_visible:
            self._svglst.append(self._bbox_rect())

class SForm(_Form):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.domain = "stacked"
        self._left = self.compute_leftmost()
        self._right = self.compute_rightmost()
        self._width = self.compute_width()
        self._top = self.compute_topmost()
        self._bottom = self.compute_bottommost()
        self._height = self.compute_height()

class HForm(_Form):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.domain = "horizontal"
        # ~ First Lineup!
        self._left = self.compute_leftmost()
        self._right = self.compute_rightmost()
        self._width = self.compute_width()
        self._top = self.compute_topmost()
        self._bottom = self.compute_bottommost()
        self._height = self.compute_height()

f=SForm(toplevel=True, _id="FRM",content=[MChar("clefs.C",_id="m1"), 
MChar("clefs.G",_id="m2"),
MChar("clefs.F",_id="m3"),
 HForm(content=[MChar("clefs.G",_id="m4")],_id="frm")])
 
f.render()


    
    
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
