from .. import Tile
import svgwrite
import os

def labelTile(child, label, outputFile):
  tile = Tile()
  tile.color = "#ffffff"
  imageFile = "%s.label.svg" % (outputFile,)
  d = svgwrite.Drawing("%s" % imageFile, size=("100px", "100px"))
  d.add(d.rect(size=(100,100), style="fill: white;"))
  textStyle = "fill: black; font-size:5pt; font-style:bold; font-family:monospace;"
  for j, t in enumerate([label]):
    d.add(d.text(t, x=[5], y=[8], style=textStyle))
  d.save()
  tile.addImage(os.path.basename(imageFile), [0,0,1])
  if child is not None:
    tile.addTile(child, [0.05,0.1,0.85])
  return tile
