from tile import Tile
from tileFile import TileFile
from cachetools import LRUCache


class TileLoader:
  def __init__(self, renderingTiles={}, tileClass=Tile):
    self.renderingTiles = renderingTiles
    self.tileCache = LRUCache(maxsize=1000)
    self.tileClass = tileClass

  def getTile(self, tilename):
    if tilename in self.renderingTiles:
      return self.renderingTiles[tilename]
    if "#" in tilename:
      filename, anchor = tilename.split("#")
      return self.loadTileFile(filename).subtiles[anchor]
    else:
      return self.loadTileFile(tilename).root

  def loadTileFile(self, filename):
    if not self.tileCache.get(filename):
      tileFile = TileFile.load(filename, tileClass=self.tileClass)
      self.tileCache.update([(filename, tileFile)])
    return self.tileCache[filename]

