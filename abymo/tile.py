from link import Link


class Tile:
  def __init__(self, **kwargs):
    self.links = []
    self.color = kwargs.get("color", None)
    self.html = kwargs.get("html", None)
    self.title = kwargs.get("title", None)
    self.precompute = None
    self.shape = [1.0, 1.0]
    self.basename = kwargs.get("basename", None)
    self.currentDepth = 0
    self.currentRender = None

  def addImage(self, src, transform):
    l = Link(type=1)
    l.src = src
    l.transform = transform
    self.links.append(l)

  def addTile(self, src, transform):
    l = Link(type=0)
    l.src = src
    l.transform = transform
    self.links.append(l)

  @classmethod
  def fromDict(cls, jsonTile, **kwargs):
    """Reads a tile from a JSON dictionary object."""
    tile = cls(**kwargs)
    tile.links = [Link.fromDict(d) for d in jsonTile["items"]]
    tile.color = jsonTile.get("color", None)
    tile.html = jsonTile.get("html", None)
    tile.shape = jsonTile.get("shape", [1.0, 1.0])
    tile.title = jsonTile.get("title", "")
    tile.currentDepth = jsonTile.get("currentDepth", 0)
    tile.precompute = jsonTile.get("precompute", "")
    return tile

  def toDict(self):
    """Save the render, and set the precompute attribute in tile json."""
    jsonDict = {"precompute": self.precompute,
                "title": self.title,
                "items": [i.toDict() for i in self.links],
                "currentDepth": self.currentDepth}
    if self.color is not None:
      jsonDict["color"] = self.color
    if self.html is not None:
      jsonDict["html"] = self.html
    if self.shape is not None:
      jsonDict["shape"] = self.shape
    return jsonDict

