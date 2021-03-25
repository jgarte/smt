
"""
Semantic Music Typesetting
"""

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
_ruledomains = set()
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
def _getglyph(name, fontname):
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
            "/home/amir/Work/Python/smt/fontinstprep.ff", 
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
_PXLPERMM = 3.7795275591 # Pixel per mm

def mmtopxl(mm): return mm * _PXLPERMM
def chlapik_staff_space(rastral):
    return {
    2: mmtopxl(1.88), 3: mmtopxl(1.755), 4: mmtopxl(1.6),
    5: mmtopxl(1.532), 6: mmtopxl(1.4), 7: mmtopxl(1.19),
    8: mmtopxl(1.02)}[rastral]

space = chlapik_staff_space(2)
scale = 1
def _scale():
    return scale * ((4 * space) / _getglyph("clefs.C", "Haydn")["height"])
def toplevel_scale(R): return R * _scale()

_LEFT_MARGIN = mmtopxl(36)
_TOP_MARGIN = mmtopxl(56)


##### Score Objects
class _SmtObj:
    def __init__(self, id_=None, domain=None, tst=None, _rules_applied_to=False):
        self.ancestors = []
        self.id = id_ or self._assign_id()
        self._svglst = []
        self.domain = domain
        self._rules_applied_to = _rules_applied_to
        self._tst = tst or []
    
    def _assign_id(self):
        self.__class__._idcounter += 1
        return self.__class__.__name__ + str(self.__class__._idcounter)
            
    def parent(self): return self.ancestors[-1]
    def root(self): return self.ancestors[0]
    
    def my_idx_in_parent_content(self):
        for i, C in enumerate(self.parent().content):
            if (C is self) and (C.id == self.id):
                return i
    
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
pgw = mmtopxl(210)
pgh =mmtopxl(297)


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
    return D


def members(obj): return [obj] + descendants(obj, lastgen_first=False)

def getallin(typeof, obj):
    """Returns an iterable of all types in obj."""
    return filter(lambda O: isinstance(O, typeof), members(obj))

def _rule_appl_elig_objs(obj):
    # Put in list to get False [] if nothing was filtered. 
    return list(filter(lambda O: (O.domain in _ruledomains) and
    (isinstance(O, tuple(_ruletargets))) and
    not(O._rules_applied_to), 
    members(obj)))

class _Canvas(_SmtObj):
    def __init__(self, absx=None, absy=None, toplevel=False, font=None,
    canvas_opacity=None, xoff=None, yoff=None, xscale=scale, yscale=scale,
    canvas_visible=True, origin_visible=True,
    **kwargs):
        super().__init__(**kwargs)
        # Only the first item in a hform will need _hlineup, for him 
        # this is set by HForm itself.
        self._is_hlineup_head = False
        self.font = font or current_font
        self.canvas_opacity = canvas_opacity or 0.3
        self.canvas_visible = canvas_visible
        self.origin_visible = origin_visible
        self.xoff = xoff or 0
        self.yoff = yoff or 0
        self._dleft = 0
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
    def right(self): return self._right
    

    @left.setter
    def left(self, newl):
        # Public x-setter gets DESTINATION & passes (newx-destination - x) to 
        # the shift_x function (which gets DELTAX as argument).
        # self.x = self.x + (newl - self.left)
        deltal = newl - self.left
        self.x = self.x + deltal
    @right.setter
    def right(self):
        print("Implement me!")

    # This is used eg by h-lineup
    # def _shift_left(self, newl):
        # # Shiftx gets the difference to the Destination as argument.
        # self._shift_x_by(newl - self.left)

    def _shift_left(self, deltal):
        # Shiftx gets the difference to the Destination as argument.
        self._shift_x_by(deltal)
        
    def _assign_left(self, newl):
        self._assign_x(self.x + (newl - self.left))

    @property
    def y(self): return self._y

    def _compute_horizontals(self):
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
                    rule = _ruletable[order]
                    for obj in eligible_objs:
                        if isinstance(obj, rule["T"]) and (obj.domain in rule["D"]):
                            rule["F"](obj)
                            obj._rules_applied_to = True
                # Maybe some rule has created new objs, or even defined new rules!
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


class Char(_Canvas):
    
    _idcounter = -1
    
    def __init__(self, name, color=None, opacity=None,
    visible=True, canvas_color=None,
    **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.glyph = _getglyph(self.name, self.font)
        self.color = color or rgb(0, 0, 0)
        self.opacity = opacity or 1
        self.visible = visible
        self.canvas_color = canvas_color or rgb(100, 0, 0, "%")
        self._compute_horizontals()
        self._compute_vsurface()
    
    # This function is the basis for all horizontal shifting operations.
    def _assign_x(self, newx):
        dx = newx - self.x # save before modification!
        self._x = newx
        self._left += dx
        self._right += dx
        for A in reversed(self.ancestors): # An ancestor is always a Form!!
            # if isinstance(A, HForm) and lineup_ancestors:
                # A._lineup()
            A._compute_horizontals()
    
    # def _shift_x_by(self, deltax):
        # # Delta x is used for a homogeneous shifting of x, left & right: 
        # self._x += deltax
        # self._left += deltax
        # self._right += deltax
        # for A in reversed(self.ancestors): # An ancestor is always a Form!!
            # A._compute_horizontals()
    
    @property
    def right(self): return self._right
    @property
    def width(self): return self._width
    @property
    def x(self): return self._x
    
    # When user assigns x:
    @_Canvas.x.setter
    def x(self, newx):
        # self._is_hlineup_head = True
        self._assign_x(newx)
    
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
        # Add bbox rect
        if self.canvas_visible:
            self._svglst.append(_bboxelem(self))
        # Add the music character
        self._svglst.append(svgwrite.path.Path(d=_getglyph(self.name, self.font)["d"],
        id_=self.id, fill=self.color, fill_opacity=self.opacity,
        transform="translate({0} {1}) scale(1 -1) scale({2} {3})".format(
        self.x, self.y, self.xscale * _scale(), self.yscale * _scale())))
        # Add the origin
        if self.origin_visible:
            for elem in _origelems(self):
                self._svglst.append(elem)


class _Form(_Canvas):

    _idcounter = -1

    def __init__(self, content=None, uwidth=None, **kwargs):
        super().__init__(**kwargs)
        self.content = content or []
        self.FIXTOP = self.y + toplevel_scale(_getglyph(STAFF_HEIGHT_REFERENCE_GLYPH, self.font)["top"])
        self.FIXBOTTOM = self.y + toplevel_scale(_getglyph(STAFF_HEIGHT_REFERENCE_GLYPH, self.font)["bottom"])
        # ~ Wozu das fixheight??
        self.FIXHEIGHT = toplevel_scale(_getglyph(STAFF_HEIGHT_REFERENCE_GLYPH, self.font)["height"])
        self.uwidth = uwidth
        for D in descendants(self, False):
            D.ancestors.insert(0, self) # Need smteq??
        for C in self.content:
            if not(C.absx):
                # Note that this is happening at init-time! When there is no absolute-x,
                # C.x is ONLY the amount of it's x-offset (see Canvas' self._x definition).
                C._assign_x(C.x + self.x)
            if not(C.absy):
                C.y += self.y
    
    # Children is a sequence. This method modifies only ancestor lists.
    def _establish_parental_relationship(self, children):
        for child in children:
            assert isinstance(child, _SmtObj), "Form can only contain MeObjs!"
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
    
    # What about insert instead of append???
    def addcont(self, child): # plural?
        assert isinstance(child, _SmtObj), "Form can only contain MeObjs!"
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
            # lineup lazem mishe
            child.x += self.x
            # child._shift_x_by(child.x + self.x)
        if not(child.absy):
            child.y += self.y
        self._compute_family_hv_surfaces()
        print("Adding..", child, child._is_hlineup_head)
    
    def _compute_family_hv_surfaces(self):
        for D in descendants(self):
            D._compute_horizontals()
            D._compute_vsurface()
        self._compute_horizontals()
        self._compute_vsurface()
        for A in reversed(self.ancestors):
            A._compute_horizontals()
            A._compute_vsurface()
        
    
    @property
    def right(self): return self._right
    
    @property
    def width(self): return self.uwidth or self._width
    @width.setter
    def width(self, neww):
        self._right = self._left + neww
        self._width = neww
        for A in reversed(self.ancestors):
            A._compute_horizontals()
    
    # TODO: Here the case of children with absx MUST be considered, what happens to the dimensions
    # of the form, if a child is not willing to move due to it's absx?
    def _assign_x(self, newx):
        dx = newx - self.x
        self._x = newx
        self._left += dx
        self._right += dx
        for D in descendants(self, False):
            D._x = newx
            D._left += dx
            D._right += dx
        for A in reversed(self.ancestors):
            # if isinstance(A, HForm) and lineup_ancestors:
                # A._lineup()
            A._compute_horizontals()

    
    def _shift_x_by(self, deltax):
        # dx = newx - self.x
        self._x += deltax
        self._left += deltax
        self._right += deltax
        for D in descendants(self, False):
            D._x += deltax
            D._left += deltax
            D._right += deltax
        for A in reversed(self.ancestors):
            A._compute_horizontals()

    @_Canvas.x.setter
    def x(self, newx):
        self._assign_x(newx)
        # If user shifts x, left, right or changes the width,
        # new horizontal line-up is required.
        self._is_hlineup_head = True

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
        """Determines the left-most of either: form's own x coordinate 
        or the left-most site of it's direct children."""
        return min([self.x] + list(map(lambda C: C.left, self.content)))

    def _compute_right(self):
        return max([self.x] + list(map(lambda C: C.right, self.content)))

    def _compute_width(self): return self.right - self.left

    def _compute_top(self):
        return min([self.FIXTOP] + list(map(lambda C: C.top, self.content)))
    def _compute_bottom(self):
        return max([self.FIXBOTTOM] + list(map(lambda C: C.bottom, self.content)))
    def _compute_height(self): return self.bottom - self.top
    def _pack_svglst(self):
        # Bbox
        if self.canvas_visible: self._svglst.append(_bboxelem(self))
        # Add content
        for C in self.content:
            C.xscale *= self.xscale
            C.yscale *= self.yscale
            C._pack_svglst() # Recursively gather svg elements
            self._svglst.extend(C._svglst)
        # Origin
        if self.origin_visible: self._svglst.extend(_origelems(self))


class SForm(_Form):
    
    _idcounter = -1
    
    def __init__(self, canvas_color=None, **kwargs):
        super().__init__(**kwargs)
        self.canvas_color = canvas_color or rgb(0, 100, 0, "%")
        self.domain = "stacked"
        # Content may contain children with absolute x, so compute horizontals with respect to them.
        # See whats happening in _Form init with children without absx!
        self._compute_horizontals()
        self._compute_vsurface()
    
    def append(self, *children):
        """Appends new children to Form's content list."""
        self._establish_parental_relationship(children)
        self.content.extend(children)
        for child in children:
            if not(child.absx):
                # child._shift_x_by(self.x - child.x)
                child._assign_x(child.x + self.x)
            if not(child.absy):
                child.y += self.y
        # Having set the content before would have caused assign_x to trigger computing horizontals for the Form,
        # which would have been to early!????
        self._compute_horizontals()
        self._is_hlineup_head = True
        for A in reversed(self.ancestors):
            if isinstance(A, HForm):
                A._lineup()
            A._compute_horizontals()


class HForm(_Form):

    def __init__(self, canvas_color=None, **kwargs):
        super().__init__(**kwargs)
        self.canvas_color = canvas_color or rgb(0, 0, 100, "%")
        self.domain = "horizontal"
        # Set the first item as in need of lineup
        self.content[0]._is_hlineup_head = True
        self._lineup()
        # then compute surfaces.
        self._compute_horizontals()
        self._compute_vsurface()
    
    # def append(self, *children):
        # self._establish_parental_relationship(children)
        # # We don't know how many new children are going to be appended
        # # to the content list, so first mark the last of existing content
        # # as head of a new line-up chunk, then put all new children at the end
        # # of the contents, then run the lineup operation.
        # self.content[-1]._is_hlineup_head = True
        # self.content.extend(children)
        # self._lineup()
        # self._compute_family_hv_surfaces()
    
    def _lineup_chunks(self):
        enums = filter(lambda L: L[1]._is_hlineup_head, enumerate(self.content))
        indices = list(map(lambda L: L[0], enums))
        indices_tail = indices[1:]
        chunks = []
        # Using slicing to shallow copy object instances
        for i in range(len(indices_tail)):
            chunks.append(self.content[indices[i]:indices_tail[i] - 1])
        chunks.append(self.content[indices[-1]:])
        return chunks
    
    def _lineup(self):
        for chunk in self._lineup_chunks():
            if chunk:
                chunk[0]._is_hlineup_head = False
                # The actual lineup operation:
                for a, b in zip(chunk[:-1], chunk[1:]):
                    # Use internal assignment to avoid labeling as lineup-needy!
                    # b._shift_left(a.right - b.left)
                    b._assign_left(a.right)
        # for a, b in zip(self.content[:-1], self.content[1:]):
            # b.left += a.right
            
    def _lineup(self):
        for a, b in zip(self.content[:-1], self.content[1:]):
            # Use internal assignment to avoid labeling as lineup-needy!
            # b._shift_left(a.right - b.left)
            b._assign_left(a.right)

class Note(SForm):
    def __init__(self, spn=None, dur=None, domain=None, **kwargs):
        super().__init__(**kwargs)
        self.spn = spn
        self.domain = domain or "treble"
        self.dur = dur
        self.head = None
