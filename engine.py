
import tempfile
import xml.etree.ElementTree as ET
import subprocess as sp
import svgwrite
# ~ Alias name
from svgwrite.utils import rgb


############### rule

_ruletable = []
_ruleregistry = []
def rule(targets, domains, *funcs):
    _ruleregistry.append({"T": targets, "D": domains, "F": funcs})

# ~ class rule:
    # ~ def __init__(self, targs=None, domains=None, table=None):
       
        # ~ self.targs = targs or (object,)
        # ~ self.domains = domains or ()
        # ~ self.extensions = []
        # ~ self.table = table or _ruletable
        # ~ self.table.append(self)
       
    # ~ def extend(self, *funcs): self.extensions.extend(funcs)

# ~ def apply(fn, L):
    # ~ exec("{}({})".format(fn.__name__, ", ".join([repr(A) for A in L])))
# ~ def _argcount(fn): return fn.__code__.co_argcount



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
_PXPERMM = 3.7795275591 # Pixel per mm

def mmtopx(mm): return mm * _PXPERMM
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
class _MeObj:
    _meid_count = -1
    _meid_name = "ME"
    def __init__(self, _id=None, domain=None, tst=None):
        self.ancestors = []
        self.id = self.__allocid(_id)
        self._svglst = []
        self.domain = domain
        self._rules_applied = False
        self._tst = tst or []
    def __allocid(self, _id):
        if not(_id):
            _MeObj._meid_count += 1
            return _MeObj._meid_name + str(_MeObj._meid_count)
        else: return _id
    def parent(self): return list(reversed(self.ancestors))[0]
    
# ~ _Canvas, Origin's Circle, Origin's Cross, Origin's Circle Contour
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

def rules_targets():
    T = []
    for rule in _ruleregistry:
        T.extend(rule["T"])
    return T

def rules_domains():
    D= []
    for rule in _ruleregistry:
        D.extend(rule["D"])
    return D
    

def _descendants(obj, N, D):
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
            _descendants(child, N+1, D)
    return D
    
def descendants(obj, lastgen_first=True):
    D = []
    for _, gen in sorted(_descendants(obj, 0, {}).items(), reverse=lastgen_first):
        D.extend(gen)
    return D

def members(obj): return [obj] + descendants(obj, lastgen_first=False)

class _Canvas(_MeObj):
    def __init__(self, absx=None, absy=None, toplevel=False, font=font,
    canvas_opacity=None, xoff=None, yoff=None, xscale=scale, yscale=scale,
    canvas_visible=True, origin_visible=True,
    **kwargs):
        super().__init__(**kwargs)
        self.font = font
        self.canvas_opacity = canvas_opacity or 0.3
        self.canvas_visible = canvas_visible
        self.origin_visible = origin_visible
        self.xoff = xoff or 0
        self.yoff = yoff or 0
        self.xscale = xscale
        self.yscale = yscale
        self.toplevel = toplevel
        self.absx = _LEFT_MARGIN if (self.toplevel and not(absx)) else absx
        self.absy = _TOP_MARGIN if (self.toplevel and not(absy)) else absy
        # ~ We need xy at init-time, just make absx 0 above??????
        self._x = (self.absx or 0) + self.xoff
        self._y = (self.absy or 0) + self.yoff
    def _compute_hsurface(self):
        self._left = self._compute_left()
        self._right = self._compute_right()
        self._width = self._compute_width()
    def _compute_vsurface(self):
        self._top = self._compute_top()
        self._bottom = self._compute_bottom()
        self._height = self._compute_height()
    # ~ A canvas can be a page??
    def render(self):
        D = svgwrite.drawing.Drawing(filename="/tmp/me.svg", size=(pgw,pgh),debug=True)
        self._apply_rules()
        # ~ Form's packsvglst will call packsvglst on descendants recursively
        self._pack_svglst()
        for elem in self._svglst:
            D.add(elem)
        D.save(pretty=True)
    def _apply_rules(self):
        """
        Applies rules to OBJ and all it's descendants. 
        """
        # ~ Each obj will get rules applied to him only ONCE! True or False __rule_applied
        while list(filter(lambda O: not(O._rules_applied), members(self))):
            objs = list(filter(lambda O: not(O._rules_applied), members(self)))
            print("->", objs)
            for obj in objs:
                for rule in list(filter(lambda R: isinstance(obj, R["T"]) and obj.domain in R["D"], _ruleregistry)):
                    for func in rule["F"]: 
                        func(obj)
                obj._rules_applied = True

    
def _bboxelem(obj): 
    return svgwrite.shapes.Rect(
    insert=(obj.left, obj.top),
    size=(obj.width, obj.height), 
    fill=obj.canvas_color,
    fill_opacity=obj.canvas_opacity, 
    id_=obj.id + "BBox"
    )
_ORIGIN_CROSS_LEN = 20
_ORIGIN_CIRCLE_R = 4
_ORIGIN_LINE_THICKNESS = 0.06
def _origelems(obj):
    halfln = _ORIGIN_CROSS_LEN / 2
    return [svgwrite.shapes.Circle(center=(obj.x, obj.y), r=_ORIGIN_CIRCLE_R,
                                    id_=obj.id + "OriginCircle",
                                    stroke=rgb(87, 78, 55), fill="none",
                                    stroke_width=_ORIGIN_LINE_THICKNESS),
            svgwrite.shapes.Line(start=(obj.x-halfln, obj.y), end=(obj.x+halfln, obj.y),
                                        id_=obj.id + "OriginHLine",
                                        stroke=rgb(87, 78, 55), 
                                        stroke_width=_ORIGIN_LINE_THICKNESS),
            svgwrite.shapes.Line(start=(obj.x, obj.y-halfln), end=(obj.x, obj.y+halfln),
                                        id_=obj.id + "OriginVLine",
                                        stroke=rgb(87, 78, 55), 
                                        stroke_width=_ORIGIN_LINE_THICKNESS)]


class MChar(_Canvas):
    def __init__(self, name, color=None, opacity=None,
    visible=True, canvas_color=None,
    **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.color = color or rgb(0, 0, 0)
        self.opacity = opacity or 1
        self.visible = visible
        self.canvas_color = canvas_color or rgb(100, 0, 0, "%")
        # ~ Compute the surface area
        self._compute_hsurface()
        self._compute_vsurface()
    # ~ Horizontals
    @property
    def left(self): return self._left
    @left.setter
    def left(self, newl):
        dl = newl - self.left
        self.x += dl
    @property
    def right(self): return self._right
    @property
    def width(self): return self._width
    @property
    def x(self): return self._x
    @x.setter
    def x(self, newx):
        dx = newx - self.x
        self._x += dx
        self._left += dx
        self._right += dx
        for A in reversed(self.ancestors): # An ancestor IS a Form.
            A._compute_hsurface()
            # ~ A._left = A._compute_left()
            # ~ A._right = A._compute_right()
            # ~ A._width = A._compute_width()
    # ~ Verticals
    @property
    def y(self): return self._y
    @y.setter
    def y(self, newy):
        dy = newy - self.y
        self._y += dy
        self._top += dy
        self._bottom += dy
        for A in reversed(self.ancestors): # A are Forms
            A._compute_vsurface()
            # ~ A._top = A._compute_top()
            # ~ A._bottom = A._compute_bottom()
            # ~ A._height = A._compute_height()
    @property
    def top(self): return self._top
    @property
    def bottom(self): return self._bottom
    @property
    def height(self): return self._height
    def _compute_left(self):
        return self.x + toplevel_scale(glyph(self.name, self.font)["left"])
    def _compute_right(self):
        return self.x + toplevel_scale(glyph(self.name, self.font)["right"])
    def _compute_width(self):
        return toplevel_scale(glyph(self.name, self.font)["width"])
    def _compute_top(self):
        return self.y + toplevel_scale(glyph(self.name, self.font)["top"])
    def _compute_bottom(self):
        return self.y + toplevel_scale(glyph(self.name, self.font)["bottom"])
    def _compute_height(self):
        return toplevel_scale(glyph(self.name, self.font)["height"])
    def _pack_svglst(self):
        # ~ Add bbox rect
        if self.canvas_visible:
            self._svglst.append(_bboxelem(self))
        # ~ Add the music character
        self._svglst.append(
        svgwrite.path.Path(d=glyph(self.name, self.font)["d"],
        id_=self.id, fill=self.color, fill_opacity=self.opacity,
        transform="translate({0} {1}) scale(1 -1) scale({2} {3})".format(
        self.x, self.y, self.xscale * _scale(), self.yscale * _scale())))
        # ~ Origin
        if self.origin_visible:
            for elem in _origelems(self):
                self._svglst.append(elem)


class _Form(_Canvas):
    def __init__(self, content=None, uwidth=None, **kwargs):
        super().__init__(**kwargs)
        self.content = content if content else []
        self.FIXTOP = self.y + toplevel_scale(glyph(STAFF_HEIGHT_REFERENCE_GLYPH, self.font)["top"])
        self.FIXBOTTOM = self.y + toplevel_scale(glyph(STAFF_HEIGHT_REFERENCE_GLYPH, self.font)["bottom"])
        # ~ Wozu das fixheight??
        self.FIXHEIGHT = toplevel_scale(glyph(STAFF_HEIGHT_REFERENCE_GLYPH, self.font)["height"])
        self.uwidth = uwidth
        for D in descendants(self, False):
            D.ancestors.insert(0, self) # Need smteq??
        for C in self.content:
            if not(C.absx):
                # ~ Call child's setter
                C.x += self.x
            if not(C.absy):
                C.y += self.y
    def addcont(self, child):
        print("Adding to cont")
        # ~ Tell child & his children about their parents
        child.ancestors.insert(0, self)
        if isinstance(child, _Form):
            for D in descendants(child, False):
                D.ancestors.insert(0, self)
        for A in reversed(self.ancestors):
            child.ancestors.insert(0, A)
            if isinstance(child, _Form):
                for D in descendants(child, False):
                    D.ancestors.insert(0, A)
        self.content.append(child)
        if not(child.absx):
            child.x += self.x
        if not(child.absy):
            child.y += self.y
        for D in descendants(self):
            D._compute_hsurface()
            D._compute_vsurface()
        self._compute_hsurface()
        self._compute_vsurface()
        for A in reversed(self.ancestors):
            A._compute_hsurface()
            A._compute_vsurface()
    # ~ Horizontal Attributes
    @property
    def x(self): return self._x
    @property
    def left(self): return self._left
    @property
    def right(self): return self._right
    @property
    def width(self): return self.uwidth or self._width
    @x.setter
    def x(self, newx):
        dx = newx - self.x
        self._x += dx
        self._left += dx
        self._right += dx
        for d in descendants(self, False):
            d._x += dx
            d._left += dx
            d._right += dx
        for A in reversed(self.ancestors):
            A._compute_hsurface()
            # ~ A._left = A._compute_left()
            # ~ A._right = A._compute_right()
            # ~ A._width = A._compute_width()
    # ~ Vertical Attributes
    @property
    def y(self): return self._y
    @y.setter # move if C.absy check to here
    def y(self, newy):
        dy = newy - self.y
        self._y += dy
        self._top += dy
        self._bottom += dy
        for D in descendants(self, False):
            D._y += dy
            D._top += dy
            D._bottom += dy
        # ~ Shifting Y might have an impact on ancestor's width!
        for A in reversed(self.ancestors):
            A._compute_vsurface()
    @property
    def top(self): return self._top
    @property
    def bottom(self): return self._bottom
    @property
    def height(self): return self._height
    def _compute_left(self):
        return min([self.x] + list(map(lambda c: c.left, self.content)))
    def _compute_right(self):
        return max([self.x] + list(map(lambda c: c.right, self.content)))
    def _compute_width(self): return self.right - self.left
    def _compute_top(self):
        return min([self.FIXTOP] + list(map(lambda C: C.top, self.content)))
    def _compute_bottom(self):
        return max([self.FIXBOTTOM] + list(map(lambda C: C.bottom, self.content)))
    def _compute_height(self): return self.bottom - self.top
    def _pack_svglst(self):
        # ~ Bbox
        if self.canvas_visible: self._svglst.append(_bboxelem(self))
        # ~ Add content
        for C in self.content:
            C.xscale *= self.xscale
            C.yscale *= self.yscale
            C._pack_svglst() # Recursively gather svg elements
            self._svglst.extend(C._svglst)
        # ~ Origin
        if self.origin_visible: self._svglst.extend(_origelems(self))

class SForm(_Form):
    def __init__(self, canvas_color=None, **kwargs):
        super().__init__(**kwargs)
        self.canvas_color = canvas_color or rgb(0, 100, 0, "%")
        self.domain = "stacked"
        self._compute_hsurface()
        self._compute_vsurface()

class HForm(_Form):
    def __init__(self, canvas_color=None, **kwargs):
        super().__init__(**kwargs)
        self.canvas_color = canvas_color or rgb(0, 0, 100, "%")
        self.domain = "horizontal"
        # ~ First Lineup!
        self._lineup()
        self._compute_hsurface()
        self._compute_vsurface()
    def _lineup(self):
        for i, C in enumerate(self.content[1:]):
            print(">>>>>>>>",self.content[1:][i].left)
            self.content[1:][i].left = self.content[i].right

###### Clocks
class Clock:
    def __init__(self, dur):
        self.dur = dur
class Pitch:
    def __init__(self, spn):
        self.spn = spn
class Note(SForm, Clock, Pitch):
    def __init__(self, dur=None, domain=None, **kwargs):
        super().__init__(**kwargs)
        self.dur = dur or 1
        self.domain = domain or None
        self.__head = None
