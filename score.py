

from engine import *
from engine import _LineSegment


# Default ruletable
cmn = RuleTable()


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

class Pitch:
    def __init__(self, pitch):
        self.pitch = pitch


STAFF_LINE_THICKNESS = 1.0

class Staff(HLineSegment):
    LINE_THICKNESS = 1.0


class Stem(VLineSegment):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

# print(isinstance(Stem(), _LineSegment))

class Note(SForm, Clock, Pitch):
    def __init__(self, head_hammer=None, flagsym=None, stem_stichel=None, duration=None, pitch=None, **kwargs):
        Clock.__init__(self, duration)
        Pitch.__init__(self, pitch)
        SForm.__init__(self, **kwargs)
        # Head holds the head_hammer Char object
        self._head_char = head_hammer
        self._flag_char = flagsym
        self._stem_stichel = stem_stichel

    @property
    def head_hammer(self): return self._head_char
    @head_hammer.setter
    def head_hammer(self, newhead):
        # wird auch flag sein!!!!!!!!!!!!!!!!!!!!!!!!!!
        self._head_char = newhead
        self.append(self._head_char)

    @property
    def stem_stichel(self): return self._stem_stichel
    
    @stem_stichel.setter
    def stem_stichel(self, newstem):
        # print("before append",self.id, self.x)
        # Allow only a single stem_stichel per note?
        self.del_children(lambda c: isinstance(c, Stem))
        self._stem_stichel = newstem
        self.append(self._stem_stichel)
        # print("After append", self.id, self.x)

class Accidental(SForm, Pitch):
    def __init__(self, accidental_hammer=None, pitch=None, **kwargs):
        SForm.__init__(self, **kwargs)
        Pitch.__init__(self, pitch)
        self.accidental_hammer = accidental_hammer
        

class Clef(SForm, Pitch):
    def __init__(self, symbol=None, pitch=None, **kwargs):
        SForm.__init__(self, **kwargs)
        Pitch.__init__(self, pitch)
        self.symbol = symbol
