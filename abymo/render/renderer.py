import os
from .. import Tile, TileFile, TileLoader


class Renderer:
  contextClass = None
  # tileClass must implement tile.render(context)
  tileClass = None

  def setup(self, tiles):
    pass

  def render(self, updateList):
    tileFiles = []
    tiles = {}
    toRender = []
    for filename in updateList:
      tileFile = TileFile.load(filename, tileClass=self.tileClass)
      tileFiles.append(tileFile)
      subtiles = tileFile.getTiles()
      tiles.update(subtiles)
      toRender += subtiles.keys()
      [t.resetRender() for t in subtiles.values()]
    self.setup([tiles[k] for k in toRender])
    ctx = self.contextClass(tiles)
    MIN_DEPTH = 15
    iteration = 0
    while toRender:
      iteration += 1
      print "Rendering pass %s, %s tiles still to render ..." % (iteration, len(toRender))
      for src in toRender[:]:
        tile = ctx.getTile(src)
        tile.render(ctx)
        if tile.currentDepth >= MIN_DEPTH:
          toRender.remove(src)
          precompute_file = "%s.precompute.png" % src.replace("#", "__")
          # For now this relies on the fact the QPixmap and Image have the same
          # interface for saving.
          tile.currentRender.save(precompute_file)
          tile.precompute = os.path.relpath(precompute_file, os.path.dirname(src))
          tile.currentRender = None
    for tileFile in tileFiles:
      tileFile.save()

