import json
import os
from tile import Tile


class TileFile:
  def __init__(self, **kwargs):
    self.filename = None
    self.basename = None
    self.root = None
    self.subtiles = {}
    self.tileClass = kwargs.get("tileClass", Tile)

  @classmethod
  def load(cls, filename, **kwargs):
    tileFile = TileFile(**kwargs)
    tileFile.filename = filename
    tileFile.basename = filename.decode("utf-8")
    with open(filename) as f:
      js = json.load(f)
      tileFile.root = tileFile.tileClass.fromDict(js["root"], basename=tileFile.basename)
      for key in js["subtiles"]:
        tileFile.subtiles[key] = tileFile.tileClass.fromDict(js["subtiles"][key], basename=tileFile.basename)
    return tileFile

  def addSubtile(self, name, subtile):
    self.subtiles[name] = subtile

  def addSubtree(self, name, subtree):
    self.subtiles.update(subtree.subtiles)
    self.subtiles[name] = subtree.root

  def getTiles(self):
    safeFilename = self.filename.decode("utf-8")
    tiles = {safeFilename: self.root}
    for k, t in self.subtiles.items():
      tiles["%s#%s" % (safeFilename, k)] = t
    for t in tiles.values():
      t.basename = safeFilename
    return tiles

  def save(self, filename=None):
    if filename is None:
      assert self.filename is not None
      filename = self.filename
    else:
      self.filename = filename
    js = {"root": self.root.toDict(), "subtiles": {}}
    for k, t in self.subtiles.items():
      for link in t.links:
        if link.src.startswith("#"):
          link.src = os.path.basename(filename) + link.src
      js["subtiles"][k] = t.toDict()
    with open(filename, "w") as f:
      f.write(json.dumps(js, indent=2))

