import xml.etree.ElementTree as ET
tree = ET.parse('/home/amir/haydn/svg/haydn-11.svg')


for x in tree.iter():
    if "glyph-name" in x.attrib:
        print(x.attrib["glyph-name"])
