class Link:
  """Stores a type (0 or 1 for link or image), a transform, and a file source."""
  def __init__(self, **kwargs):
    """Blank initialization. Use the factory methods instead."""
    self.transform = None
    self.src = None
    self.type = kwargs.get("type", None)

  @classmethod
  def fromDict(cls, d):
    """Interprets the item data from a dict parsed from JSON."""
    item = Link()
    item.src = d["src"]
    item.transform = d["transform"]
    if len(item.transform)==3:
      item.transform = item.transform[:] + [item.transform[2]]
    assert d["type"]=="link" or d["type"]=="img"
    item.type = 0 if d["type"]=="link" else 1
    return item

  def toDict(self):
    return {"type": "link" if self.type==0 else "img",
            "transform": self.transform,
            "src": self.src}
