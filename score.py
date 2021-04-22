

# from engine import *
import engine as E

# __all__ = engine.__all__ + [
    # "Stem", "Note", "Accidental", "Clef", 
    # "allclocks", "clock_chunks", "Clock"
    # ]


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

class Beam(E.HLineSeg):
    def __init__(self, state="open", **kwargs):
        self.state=state
        super().__init__(**kwargs)

class Note(E.SForm, Clock, _Pitch):
    def __init__(self, head_punch=None, stem_graver=None, open_beam=False,
    close_beam=False, duration=None, pitch=None, **kwargs):
        Clock.__init__(self, duration)
        _Pitch.__init__(self, pitch)
        E.SForm.__init__(self, **kwargs)
        
        self.open_beam=open_beam
        self.close_beam=close_beam
        
        # self._head_punch = head_punch
        self._stem_graver = stem_graver
        # self.beam_graver = beam_graver

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


class Accidental(E.SForm, _Pitch):
    def __init__(self, punch=None, pitch=None, **kwargs):
        E.SForm.__init__(self, **kwargs)
        _Pitch.__init__(self, pitch)
        self._punch = punch
        
    @property
    def punch(self): return self._punch
    @punch.setter
    def punch(self, new):
        self.delcont(lambda c: isinstance(c, e.Char))
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

class TimeSig(E.VForm):
    def __init__(self, top_=4, bottom_=4, **kwargs):
        self.top_=top_
        self.bottom_=bottom_
        super().__init__(**kwargs)

    @property
    def top_punch(self): return self._top_punch
    @top_punch.setter
    def top_punch(self, new):
        self._top_punch = new
        self.append(self._top_punch)
    
    @property
    def bottom_punch(self): return self._bottom_punch
    @bottom_punch.setter
    def bottom_punch(self, new):
        self._bottom_punch = new
        self.append(self._bottom_punch)
    
