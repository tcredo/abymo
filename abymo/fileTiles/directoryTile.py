from .. import Tile, TileFile
from ..layout import gridTile, pyramidTile
import os
import stat
import svgwrite

def directoryTile(path, filenameMapping):
  outputFile = filenameMapping[path]
  isLnk = os.path.islink(path)
  mode = os.stat(path).st_mode
  isDir = stat.S_ISDIR(mode)
  readable = bool(mode & stat.S_IROTH)
  if path.endswith("/"):
    name = os.path.basename(os.path.dirname(path))
  else:
    name = os.path.basename(path)
  tileFile = TileFile()
  tile = Tile()
  tile.title = path
  tileFile.root = tile
  tile.color = "#000000"
  if readable and isDir:
    if isLnk:
      rectStyle = "border: 3px #000064;"
    else:
      rectStyle = "border: 3px #006464;"
    imageFile = "%s.0.svg" % (outputFile)
    d = svgwrite.Drawing(imageFile, size=("100px", "100px"))
    d.add(d.rect(insert=(10, 10), size=(80,80), style=rectStyle))
    textStyle = "fill: white; font-size:5pt; font-family:monospace;"
    d.add(d.text(name, x=[5], y=[8], style=textStyle))
    d.save()
    tile.addImage(os.path.basename(imageFile), [0,0,1])
    items = [os.path.join(path,item) for item in os.listdir(path)]
    items.sort(key=lambda x: (os.path.splitext(x)[1], x))
    items = [os.path.basename(filenameMapping[i]) for i in items if i in filenameMapping]
    if items:
      tileFile.addSubtree("pyramid", pyramidTile(items))
      tile.addTile(os.path.basename(outputFile) + "#pyramid", [0.05,0.1,0.85])
  else:
    if not readable:
      rectStyle = "fill: #640000;"
    elif not isDir:
      rectStyle = "fill: #006400;"
    imageFile = "%s.0.svg" % (outputFile)
    d = svgwrite.Drawing(imageFile, size=("100px", "100px"))
    d.add(d.rect(size=(100,100), style=rectStyle))
    textStyle = "fill: white; font-size:8pt; font-family:monospace;"
    for j, t in enumerate([name]):
      d.add(d.text(t, x=[0], y=[12*(j+1)], style=textStyle))
    d.save()
    tile.addImage(os.path.basename(imageFile), [0,0,1])
  tileFile.save(outputFile)
 
