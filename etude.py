import svgwrite

dwg = svgwrite.Drawing('/tmp/test.svg', profile='full', debug=True)
# ~ dwg.add(dwg.line((0, 0), (10, 0), stroke=svgwrite.rgb(10, 10, 16)))
# ~ dwg.add(dwg.text('Test', insert=(0, 0.2)))
# ~ dwg.save()

p=dwg.path(d="",transform="scale(1 2) translate(2 4)")
P=svgwrite.path.Path(d="",transform="scale(1 2) translate({0} {1})".format(2,3.34879))
# ~ print("scale({0} {1}) scale({2} {3})".format(1,2.3478987,4,5.0000003))
print(P.attribs)
