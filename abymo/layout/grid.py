from .. import Tile
import math

def grid(n, padding=0.0):
  if n<1:
    return []
  l = int(math.ceil(n**0.5))
  d = (1.0-2*padding)/l
  return [[padding+(d*(i%l)), padding+(d*(i//l)), d] for i in range(n)]

def gridTile(items, padding=0.01, color= "#000000"):
  g = grid(len(items), padding)
  tile = Tile()
  tile.color = color
  for i, item in enumerate(items):
    t = g[i]
    if item.endswith(".json"):
      tile.addTile(item, t)
    else:
      tile.addImage(item,t)
  return tile
