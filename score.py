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

class Note(SForm, Clock, Pitch):
    def __init__(self, duration=None, pitch=None, **kwargs):
        Clock.__init__(self, duration)
        Pitch.__init__(self, pitch)
        SForm.__init__(self, **kwargs)
        # Head holds the head Char object
        self.char = None
        self.flag = None
        self.stem = None

class Accidental(SForm, Pitch):
    def __init__(self, pitch=None, **kwargs):
        SForm.__init__(self, **kwargs)
        Pitch.__init__(self, pitch)
        self.char = None

class Clef(SForm, Pitch):
    def __init__(self, pitch=None, **kwargs):
        SForm.__init__(self, **kwargs)
        Pitch.__init__(self, pitch)
        self.char = None

