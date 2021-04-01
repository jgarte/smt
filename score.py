from engine import *


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
    def __init__(self, length=None, thickness=None, ending=None, **kwargs):
        super().__init__(length=(length or (3.0 * STAFF_SPACE)),
        thickness=(thickness or Staff.LINE_THICKNESS), ending=(ending or "square"),
        **kwargs)
# print(Stem(direction="up",x=10,y=0).x)

class Note(SForm, Clock, Pitch):
    def __init__(self, head=None, flag=None, stem=None, duration=None, pitch=None, **kwargs):
        Clock.__init__(self, duration)
        Pitch.__init__(self, pitch)
        SForm.__init__(self, **kwargs)
        # Head holds the head Char object
        self.head = head
        self.flag = flag
        self.stem = stem
    # @property
    # def stem(self): return self._stem
    # @stem.setter
    # def stem(self, new_stem_obj):

class Accidental(SForm, Pitch):
    def __init__(self, symbol=None, pitch=None, **kwargs):
        SForm.__init__(self, **kwargs)
        Pitch.__init__(self, pitch)
        self.symbol = symbol

class Clef(SForm, Pitch):
    def __init__(self, symbol=None, pitch=None, **kwargs):
        SForm.__init__(self, **kwargs)
        Pitch.__init__(self, pitch)
        self.symbol = symbol
