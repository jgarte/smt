

import engine as NGN

# Default ruletable
cmn = NGN.RuleTable()


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

class Staff(NGN.HLineSegment):
    LINE_THICKNESS = 1.0


class Stem(NGN.VLineSegment):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

# print(isinstance(Stem(), _LineSegment))

class Note(NGN.SForm, Clock, Pitch):
    def __init__(self, head_punch=None, stem_graver=None, duration=None, pitch=None, **kwargs):
        Clock.__init__(self, duration)
        Pitch.__init__(self, pitch)
        NGN.SForm.__init__(self, **kwargs)
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
        self.del_children(lambda c: isinstance(c, Stem))
        self._stem_graver = newstem
        self.append(self._stem_graver)


class Accidental(NGN.SForm, Pitch):
    def __init__(self, punch=None, pitch=None, **kwargs):
        NGN.SForm.__init__(self, **kwargs)
        Pitch.__init__(self, pitch)
        self._punch = punch
        
    @property
    def punch(self): return self._punch
    @punch.setter
    def punch(self, new):
        self.del_children(lambda c: isinstance(c, NGN.Char))
        self._punch = new
        self.append(self._punch)
        

class Clef(NGN.SForm, Pitch):
    def __init__(self, punch=None, pitch=None, **kwargs):
        NGN.SForm.__init__(self, **kwargs)
        Pitch.__init__(self, pitch)
        self._punch = punch

    @property
    def punch(self): return self._punch
    @punch.setter
    def punch(self):
        self.del_children(lambda c: isinstance(c, NGN.Char))
        self._punch = new
        self.append(self._punch)
