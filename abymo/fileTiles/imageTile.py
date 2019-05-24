import os
from PIL import Image
from directoryTile import directoryTile
from .. import Tile, TileFile


def imageTile(path, outputFile):
  try:
    w,h = Image.open(path).size
    if w*h > 89478485:
      print "Big image: %s" % path
    ext = os.path.splitext(path)[1]
    tile = Tile()
    tile.color = "#000000"
    linkFile = "%s.image%s" % (outputFile, ext)
    if not os.path.exists(linkFile):
      os.symlink(path, linkFile)
    tile.addImage("%s.image%s" % (os.path.basename(outputFile), ext), [0, 0, 1])
    t = TileFile()
    t.root = tile
    t.save(outputFile)
  except Exception as e:
    print e
    directoryTile(path, {path: outputFile})


    

