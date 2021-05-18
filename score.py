

"""
Conveniece for creating score objects
"""


import engine as E




class Clock:
    def __init__(self, duration=None):
        self.duration = duration or 0.25

def allclocks(form):
    """Returns True if form's content is made up of Clocks only."""
    return all(map(lambda C: isinstance(C, Clock), form.content))

def clock_chunks(content_list):
    indices = []
    for i in range(len(content_list)):
        if isinstance(content_list[i], Clock):
            indices.append(i)
    chunks = []
    for start, end in zip(indices[:-1], indices[1:]):
        chunks.append(content_list[start:end])
    chunks.append(content_list[indices[-1]:])
    return chunks

class _Pitch:
    def __init__(self, pitch):
        self.pitch = pitch



class Staff(E.VForm):
    def __init__(self, count=5, dist=3, **kwargs):
        c = []
        for i in range(count):
            c.append(E.SForm(content=[E.HLineSeg(length=20, thickness=1)], height=1))
        super().__init__(content=c, **kwargs)


class Stem(E.VLineSeg):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class OpenBeam(E.HLineSeg):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class Note(E.SForm, Clock, _Pitch):
    def __init__(self, head_punch=None, stem_graver=None, obeam_graver=None, cbeam_graver=None,
    duration=None, pitch=None, **kwargs):
        Clock.__init__(self, duration)
        _Pitch.__init__(self, pitch)
        E.SForm.__init__(self, **kwargs)
        
        self._obeam_graver=obeam_graver
        self._cbeam_graver=cbeam_graver
        
        self._head_punch = head_punch
        self._stem_graver = stem_graver

    @property
    def head_punch(self): return self._head_punch
    @head_punch.setter
    def head_punch(self, newhead):
        # wird auch flag sein!!!!!!!!!!!!!!!!!!!!!!!!!!
        self._head_punch = newhead
        self.append(self._head_punch)

    @property
    def stem_graver(self): return self._stem_graver
    @stem_graver.setter
    def stem_graver(self, newstem):
        # Allow only a single stem_graver per note?
        self.delcont(lambda c: isinstance(c, Stem))
        self._stem_graver = newstem
        self.append(self._stem_graver)
    @property
    def obeam_graver(self): return self._obeam_graver
    @obeam_graver.setter
    def obeam_graver(self, new):
        self._obeam_graver = new
        self.append(self._obeam_graver)
    @property
    def cbeam_graver(self): return self._cbeam_graver
    @cbeam_graver.setter
    def cbeam_graver(self, new):
        self._cbeam_graver = new
        self.append(self._cbeam_graver)


class Accidental(E.SForm, _Pitch):
    def __init__(self, punch=None, pitch=None, **kwargs):
        E.SForm.__init__(self, **kwargs)
        _Pitch.__init__(self, pitch)
        self._punch = punch
        if punch:
            self.append(self._punch)
        
    @property
    def punch(self): return self._punch
    @punch.setter
    def punch(self, new):
        self.delcont(lambda c: isinstance(c, E.MChar))
        self._punch = new
        self.append(self._punch)


class Clef(E.SForm, _Pitch):
    def __init__(self, pitch=None, **kwargs):
        E.SForm.__init__(self, **kwargs)
        _Pitch.__init__(self, pitch)
        self._punch = None

    @property
    def punch(self): return self._punch
    @punch.setter
    def punch(self, new):
        self.delcont(lambda c: isinstance(c, e.Char))
        self._punch = new
        self.append(self._punch)

class SimpleTimeSig(E.VForm):
    def __init__(self, num=4, denom=4, **kwargs):
        self.num=num
        self.denom=denom
        self._num_punch=None
        self._denom_punch=None
        super().__init__(**kwargs)

    @property
    def num_punch(self): return self._num_punch
    @num_punch.setter
    def num_punch(self, new):
        self._num_punch = new
        self.append(self._num_punch)
    
    @property
    def denom_punch(self): return self._denom_punch
    @denom_punch.setter
    def denom_punch(self, new):
        if self._denom_punch: # First time setting in a rule
            self.delcont(lambda c: c.id == self._denom_punch.id)
        self._denom_punch = new
        self.append(self._denom_punch)
    
