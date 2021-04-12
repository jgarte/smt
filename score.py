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
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

def _remove_from_content_ip(obj, type_):
    """Removes any objects of type type_ from obj."""
    for i, C in enumerate(obj.content):
        if isinstance(C, type_):
            del obj.content[i]


class Note(SForm, Clock, Pitch):
    def __init__(self, head=None, flagsym=None, stem=None, duration=None, pitch=None, **kwargs):
        Clock.__init__(self, duration)
        Pitch.__init__(self, pitch)
        SForm.__init__(self, **kwargs)
        # Head holds the head Char object
        self._head = head
        self._flagsym = flagsym
        self._stem = stem

    @property
    def head(self): return self._head
    @head.setter
    def head(self, newhead):
        # wird auch flag sein!!!!!!!!!!!!!!!!!!!!!!!!!!
        _remove_from_content_ip(self, Char)
        self._head = newhead
        self.append(self._head)

    @property
    def stem(self): return self._stem
    @stem.setter
    def stem(self, newstem):
        # print(self, self.x)
        # Allow only a single stem per note?
        _remove_from_content_ip(self, Stem)
        self._stem = newstem
        self.append(self._stem)
        # print(self, self.x)

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
