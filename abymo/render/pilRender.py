import os
import tempfile
from cachetools import LRUCache
from PIL import Image
from renderer import Renderer
from ..util import resolveRelativePath
from .. import Tile, TileFile, TileLoader


def preconvertSvg(tiles):
  # TODO: Make the SVG files in a temp directory, and map them during rendering.
  # Clean up afterwards.
  svgFiles = []
  for tile in tiles:
    images = [i for i in tile.links if i.type==1]
    svg = [i for i in images if i.src[-4:]==".svg"]
    svgFiles += [resolveRelativePath(tile.basename, i.src) for i in svg]
  commandFileDescriptor, commandFilePath = tempfile.mkstemp()
  with os.fdopen(commandFileDescriptor, "w") as f:
    for filename in svgFiles:
      command = u"%s -w 200 -h 200 -e %s.png\n" % (filename, filename)
      f.write(command.encode("utf-8"))
  print "Converting %s SVG files ..." % len(svgFiles)
  os.system("cat %s | inkscape --shell > /dev/null" % commandFilePath)
  os.remove(commandFilePath)


class RenderingContext(TileLoader):
  def getImage(self, imageFilename, _cache=LRUCache(maxsize=100)):
    """Open image files, using a cache to avoid expensive loading."""
    if _cache.get(imageFilename):
      return _cache[imageFilename]
    else:
      try:
        if imageFilename[-4:]==".svg":
          #basename = imageFilename[:-4]
          #os.system("inkscape -z -e %s.png -w 200 -h 200 %s.svg" % (basename, basename))
          image = Image.open(imageFilename+".png")
        else:
          image = Image.open(imageFilename)
        _cache.update([(imageFilename, image)])
        return image
      except IOError:
        return False


class RenderingTile(Tile):
  def __init(self, *args, **kwargs):
    super(RenderingTile, self).__init__(*args, **kwargs)
    # TODO: move rendering related member variables here

  def render(self, ctx, scale=200):
    background = self.color if self.color else (255,255,255,0)
    shape = self.shape if self.shape is not None else [1, 1]
    dimensions = [int(scale*d) for d in self.shape]
    tmpRender = Image.new("RGBA", dimensions, background)
    minDepth = 1000
    for link in self.links:
      t = link.transform
      x0 = int(scale*t[0])
      y0 = int(scale*t[1])
      src = resolveRelativePath(self.basename, link.src)
      if link.type==0:
        tile = ctx.getTile(src)
        minDepth = min(minDepth, tile.currentDepth)
        if tile.currentRender is not None:
          image = tile.currentRender
        elif tile.precompute is not None:
          image = ctx.getImage(resolveRelativePath(self.basename, tile.precompute))
        else:
          assert tile.currentDepth==0
          continue
        s = tile.shape if tile.shape is not None else [1, 1]
        if image is None:
          continue
      else:
        assert link.type==1
        image = ctx.getImage(src)
        s = [d/float(max(image.size)) for d in image.size]
      if not image:
        print "Missing image for src: %s, from tile %s." % (src, self.basename)
      x1 = int(scale*t[0] + scale*t[2]*s[0])
      y1 = int(scale*t[1] + scale*t[2]*s[1])
      image = image.resize((x1-x0,y1-y0),Image.ANTIALIAS)
      if image.mode=="RGBA":
        tmpRender.paste(image,(x0,y0,x1,y1),image)
      else:
        tmpRender.paste(image,(x0,y0,x1,y1))
    self.currentDepth = minDepth + 1
    self.currentRender = tmpRender

  def resetRender(self):
    self.currentRender = None
    self.currentDepth = 0
    self.precompute = None


class PilRenderer(Renderer):
  contextClass = RenderingContext
  tileClass = RenderingTile
  def setup(self, tiles):
    preconvertSvg(tiles)


def pilRender(updateList):
  PilRenderer().render(updateList)

