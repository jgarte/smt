
from subprocess import run
from tempfile import TemporaryFile

class BBox():
    def __init__(self, x, y, left, right, top, bottom, width, height):
        self.x = x
        self.y = y
        self.left = left
        self.right = right
        self.top = top
        self.bottom = bottom
        self.width = width
        self.height = height

class Glyph():
    def __init__(self, name, bbox, pathd):
        self.name = name
        self.bbox = bbox
        self.pathd = pathd
        
# ~ This is the current font in-use
font = "haydn-11"

# ~ def instfont(srcpath):
        # ~ bbox_tmp = TemporaryFile()
