from .. import Tile, TileFile
import math

def popTwo(l):
  first = l.pop(0) if l else None
  second = l.pop(0) if l else None
  return [first, second]

FOURWAY_SPLIT = [[0, 0, 0.5, 0.5], [0.5, 0, 0.5, 0.5], [0, 0.5, 0.5, 0.5], [0.5, 0.5, 0.5, 0.5]]

def pyramidTile(items, color= "#000000"):
  tileFile = TileFile()
  n = len(items)
  assert n>0
  if n==1:
    tileFile.root = Tile()
    if items[0].endswith(".json"):
      tileFile.root.addTile(items[0], [0, 0, 1.0])
    else:
      tileFile.root.addImage(items[0], [0, 0, 1.0])
    return tileFile
  l = int(math.ceil(n**0.5))
  rows = [items[l*i:l*(i+1)] for i in range(l)]
  rows = [r for r in rows if r]
  k = 0
  while len(rows)>1 or len(rows[0])>1:
    newRows = []
    w = (len(rows[0])+1)/2
    h = (len(rows)+1)/2
    while rows:
      newRows.append([])
      next = popTwo(rows)
      while next[0]:
        subTiles = popTwo(next[0]) + popTwo(next[1])
        if sum([s is not None for s in subTiles]):
          tile = Tile()
          tile.title = "_pyramid_%s" % k
          shape = [0, 0]
          for s, b in zip(subTiles, FOURWAY_SPLIT):
            if s is not None:
              if not isinstance(s, basestring):
                s_shape = s.shape if s.shape is not None else [1, 1]
                tile.addTile("#%s" % s.title, b)
              else:
                s_shape = [1, 1]
                if s.endswith(".json"):
                  tile.addTile(s, b)
                else:
                  tile.addImage(s, b)
              shape = [max(shape[0], b[0]+s_shape[0]*b[2]), \
                       max(shape[1], b[1]+s_shape[1]*b[2])]
          if color is not None:
            tile.color = color
          tile.shape = shape
          newRows[-1].append(tile)
          tileFile.addSubtile(tile.title, tile)
          k += 1
        else:
          newRows[-1].append(None)
    rows = newRows
  tileFile.root = rows[0][0]
  rescale = max(tileFile.root.shape)
  if rescale<1.0:
    tileFile.root.shape = [s/rescale for s in tileFile.root.shape]
    for link in tileFile.root.links:
      link.transform = [t/rescale for t in link.transform]
  return tileFile





