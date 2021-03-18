
import tempfile
import xml.etree.ElementTree as ET
import subprocess as sp
import copy as cp
import svgwrite
# ~ Alias name
from svgwrite.utils import rgb


############### rules

# _ruleregistry = []
# def rule(targets, domains, fn):
    # for r in _ruleregistry:
        # if fn is r["F"]:
            # return
    # _ruleregistry.append({"T": targets, "D": domains, "F": fn})

# ~ New rule is by default applicable to all hitherto defined domains
_ruledomains = set(("stacked", "horizontal"))
_ruletargets = set((object,))
_ruletable = {}

def r(order, targets, domains, func):
    if order in _ruletable:
        # ~ raise Exception("Rule order exists")
        return
    else:
        _ruletargets.update(tuple(targets))
        _ruledomains.update(tuple(domains))
        _ruletable[order] = {"T": targets, "D": domains, "F": func}

##### Font
_fonts = {}
current_font = "Haydn"
STAFF_HEIGHT_REFERENCE_GLYPH = "clefs.C"

def _fontdict(fontname): return _fonts[fontname]
def glyphs(fontname): return _fontdict(fontname).keys()
def getglyph(name, fontname):
    """Returns glyph's dictionary"""
    return _fontdict(fontname)[name]

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
    _fonts[fontname] = D

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
    return scale * ((4 * space) / getglyph("clefs.C", "Haydn")["height"])
def toplevel_scale(R): return R * _scale()

_LEFT_MARGIN = mmtopx(36)
_TOP_MARGIN = mmtopx(56)


##### Score Objects
class _MeObj:
    def __init__(self, id_=None, domain=None, tst=None, _rules_applied_to=False):
        self.ancestors = []
        self.id = id_ or self.__class__.__name__ + str(self.__class__._idcounter); self.__class__._idcounter += 1
        self._svglst = []
        self.domain = domain
        self._rules_applied_to = _rules_applied_to
        self._tst = tst or []
    def parent(self): return list(reversed(self.ancestors))[0]
    def render(self):
        D = svgwrite.drawing.Drawing(filename="/tmp/me.svg", size=(pgw,pgh),debug=True)
        self._apply_rules()
        # ~ Form's packsvglst will call packsvglst on descendants recursively
        self._pack_svglst()
        # ~ print(self._svglst)
        for elem in self._svglst:
            D.add(elem)
        D.save(pretty=True)
    
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


# ~ def _descendants(obj, N, D):
    # ~ """"""
    # ~ if isinstance(obj, _Form) and obj.content:
        # ~ if not(N in D):
            # ~ D[N] = []
            # ~ for x in obj.content:
                # ~ D[N].append(x)
            # ~ D[N] = cp.copy(obj.content)
        # ~ else:
            # ~ D[N].extend(obj.content)
            # ~ for x in obj.content:
                # ~ D[N].append(x)
        # ~ # need objs themselves
        # ~ for child in obj.content:
            # ~ D[N].append(child)
        # ~ for child in obj.content:
            # ~ _descendants(child, N+1, D)
            # ~ _descendants(child, N+1, D)
    # ~ return D

# ~ Why am I not writing this as a method to FORM?
def _descendants(obj, N, D):
    if isinstance(obj, _Form) and obj.content:
        if N not in D:
            # ~ Shallow copy only the outer content List,
            D[N] = cp.copy(obj.content)
        else:
            D[N].extend(obj.content)
        for C in obj.content:
            _descendants(C, N+1, D)
    return D
    
def descendants(obj, lastgen_first=True):
    D = []
    for _, gen in sorted(_descendants(obj, 0, {}).items(), reverse=lastgen_first):
        D.extend(gen)
    # ~ for i in sorted(d.keys(), reverse=lastgen_first):
    # ~ for _, gen in sorted(_descendants(obj, 0, {}).items(), reverse=lastgen_first):
        # ~ D.extend(d[i])
    return D


def members(obj): return [obj] + descendants(obj, lastgen_first=False)

def getallin(typeof, obj):
    """Returns an iterable of all types in obj."""
    return filter(lambda O: isinstance(O, typeof), members(obj))

def _rule_appl_elig_objs(obj):
    # put in list to get False [] if nothing was filtered. 
    return list(filter(
    lambda O: (O.domain in _ruledomains) and
    (isinstance(O, tuple(_ruletargets))) and
    not(O._rules_applied_to), 
    members(obj)))

class _Canvas(_MeObj):
    def __init__(self, absx=None, absy=None, toplevel=False, font=None,
    canvas_opacity=None, xoff=None, yoff=None, xscale=scale, yscale=scale,
    canvas_visible=True, origin_visible=True,
    **kwargs):
        super().__init__(**kwargs)
        self.font = font or current_font
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
    @property
    def x(self): return self._x
    @property
    def left(self): return self._left
    @property
    def y(self): return self._y
    def _compute_hsurface(self):
        self._left = self._compute_left()
        self._right = self._compute_right()
        self._width = self._compute_width()
    def _compute_vsurface(self):
        self._top = self._compute_top()
        self._bottom = self._compute_bottom()
        self._height = self._compute_height()
    def _apply_rules(self):
        """
        Applies rules to OBJ and all it's descendants. 
        """
        eligible_objs = _rule_appl_elig_objs(self)
        while True:
            if eligible_objs:
                # Must iterate over rules first, then over objs.
                # It is the order of rules to be applied which matters here! 
                for order in sorted(_ruletable):
                    for obj in eligible_objs:
                        rule = _ruletable[order]
                        if isinstance(obj, rule["T"]) and (obj.domain in rule["D"]):
                            print(obj, rule["T"],rule["F"])
                            rule["F"](obj)
                            obj._rules_applied_to = True
                eligible_objs = _rule_appl_elig_objs(self)
            else:
                break

    
def _bboxelem(obj): 
    return svgwrite.shapes.Rect(insert=(obj.left, obj.top),
                                size=(obj.width, obj.height), 
                                fill=obj.canvas_color,
                                fill_opacity=obj.canvas_opacity, 
                                id_=obj.id + "BBox")

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
    _idcounter = 0
    def __init__(self, name, color=None, opacity=None,
    visible=True, canvas_color=None,
    **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.glyph = getglyph(self.name, self.font)
        self.color = color or rgb(0, 0, 0)
        self.opacity = opacity or 1
        self.visible = visible
        self.canvas_color = canvas_color or rgb(100, 0, 0, "%")
        # ~ Compute the surface area
        self._compute_hsurface()
        self._compute_vsurface()
    @_Canvas.left.setter
    def left(self, newl):
        dl = newl - self.left
        self.x += dl
    @property
    def right(self): return self._right
    @property
    def width(self): return self._width
    @property
    def x(self): return self._x
    @_Canvas.x.setter
    def x(self, newx):
        dx = newx - self.x
        self._x += dx
        self._left += dx
        self._right += dx
        for A in reversed(self.ancestors): # An ancestor IS a Form.
            A._compute_hsurface()
    @_Canvas.y.setter
    def y(self, newy):
        dy = newy - self.y
        self._y += dy
        self._top += dy
        self._bottom += dy
        for A in reversed(self.ancestors): # A are Forms
            A._compute_vsurface()
    @property
    def top(self): return self._top
    @property
    def bottom(self): return self._bottom
    @property
    def height(self): return self._height
    def _compute_left(self):
        return self.x + toplevel_scale(self.glyph["left"])
    def _compute_right(self):
        return self.x + toplevel_scale(self.glyph["right"])
    def _compute_width(self):
        return toplevel_scale(self.glyph["width"])
    def _compute_top(self):
        return self.y + toplevel_scale(self.glyph["top"])
    def _compute_bottom(self):
        return self.y + toplevel_scale(self.glyph["bottom"])
    def _compute_height(self):
        return toplevel_scale(self.glyph["height"])
    def _pack_svglst(self):
        # ~ Add bbox rect
        if self.canvas_visible:
            self._svglst.append(_bboxelem(self))
        # ~ Add the music character
        self._svglst.append(svgwrite.path.Path(d=getglyph(self.name, self.font)["d"],
        id_=self.id, fill=self.color, fill_opacity=self.opacity,
        transform="translate({0} {1}) scale(1 -1) scale({2} {3})".format(
        self.x, self.y, self.xscale * _scale(), self.yscale * _scale())))
        # ~ print(self.id, self._svglst)
        # ~ Origin
        if self.origin_visible:
            for elem in _origelems(self):
                self._svglst.append(elem)


class _Form(_Canvas):
    # ~ __IDNAME = "Form"
    _idcounter = 0
    def __init__(self, content=None, uwidth=None, **kwargs):
        super().__init__(**kwargs)
        self.content = content or []
        # ~ self.id = _id or self.__ + str(_Form.__idcount); _Form.__idcount += 1
        self.FIXTOP = self.y + toplevel_scale(getglyph(STAFF_HEIGHT_REFERENCE_GLYPH, self.font)["top"])
        self.FIXBOTTOM = self.y + toplevel_scale(getglyph(STAFF_HEIGHT_REFERENCE_GLYPH, self.font)["bottom"])
        # ~ Wozu das fixheight??
        self.FIXHEIGHT = toplevel_scale(getglyph(STAFF_HEIGHT_REFERENCE_GLYPH, self.font)["height"])
        self.uwidth = uwidth
        for D in descendants(self, False):
            D.ancestors.insert(0, self) # Need smteq??
        for C in self.content:
            if not(C.absx):
                # ~ Call child's setter
                C.x += self.x
            if not(C.absy):
                C.y += self.y
    def addcont(self, child): # plural?
        assert isinstance(child, _MeObj), "Form can only contain MeObjs!"
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
        # ~ print("+++++++++", self.id, self.content)
    
    @_Canvas.left.setter
    def left(self, newl):
        dl = newl - self.left
        self.x += dl
    
    @property
    def right(self): return self._right
    @property
    def width(self): return self.uwidth or self._width
    
    
    @_Canvas.x.setter
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

    @_Canvas.y.setter # move if C.absy check to here
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
            # ~ print(self.id, C.id, self._svglst, C.content if isinstance(C, _Form) else "!")
            C.xscale *= self.xscale
            C.yscale *= self.yscale
            C._pack_svglst() # Recursively gather svg elements
            self._svglst.extend(C._svglst)
            # ~ print(self.id, C.id, self._svglst)
        # ~ self._svglst.extend(list(map(lambda C: C._svglst, self.content)))
            # ~ print(self.id, C.id, self._svglst)
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
        for a, b in zip(self.content[:-1], self.content[1:]):
            b.left = a.right


class Note(SForm):
    def __init__(self, spn=None, dur=None, domain=None, **kwargs):
        super().__init__(**kwargs)
        self.spn = spn
        self.domain = domain or "treble"
        self.dur = dur
        self.head = None
