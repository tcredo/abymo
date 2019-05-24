from PyQt5.QtCore import QRect, QRectF
from PyQt5.QtWidgets import QApplication
from PyQt5.QtSvg import QSvgRenderer
from PyQt5.QtGui import QImage, QPainter, QPixmap, QColor
from renderer import Renderer
from ..util import resolveRelativePath
from .. import Tile, TileFile, TileLoader


class QtRenderingTile(Tile):
  def __init(self, *args, **kwargs):
    super(QtRenderingTile, self).__init__(*args, **kwargs)
    # TODO: move rendering related member variables here
    self.scale = kwargs.get("renderScale", 200)

  def render(self, ctx):
    self.scale = 200 # TODO: Why doesn't this work in __init__?
    shape = self.shape if self.shape is not None else [1, 1]
    dimensions = [int(self.scale*d) for d in shape]
    tmpRender = QPixmap(*dimensions)
    background = (255,255,255,0)
    tmpRender.fill(QColor(*background))
    painter = QPainter(tmpRender)
    minDepth = 1000
    for link in self.links:
      minDepth = min(minDepth, self.renderLink(link, painter, ctx))
    self.currentDepth = minDepth + 1
    self.currentRender = tmpRender

  def renderLink(self, link, painter, ctx):
    src = resolveRelativePath(self.basename, link.src)
    if link.type==0:
      tile = ctx.getTile(src)
      shape = tile.shape if tile.shape is not None else [1.,1.]
      if tile.currentRender is not None:
        pixmap = tile.currentRender
      elif tile.precompute is not None:
        pixmap = QPixmap(resolveRelativePath(self.basename, tile.precompute))
      else:
        assert tile.currentDepth==0
        return 0
      painter.drawPixmap(self.convertRect(link.transform, shape), pixmap)
      return tile.currentDepth
    else:
      assert link.type==1
      self.drawImage(painter, src, link.transform)
      return 1000

  def drawImage(self, painter, src, t):
    if src.endswith("svg"):
      svg = QSvgRenderer(src)
      svg.render(painter, QRectF(self.convertRect(t)))
    else:
      pixmap = QPixmap(src)
      pixmapShape = [pixmap.width(), pixmap.height()]
      shape = [d/float(max(pixmapShape)) for d in pixmapShape]
      painter.drawPixmap(self.convertRect(t, shape), pixmap)

  def convertRect(self, transform, shape=[1.,1.]):
    x = int(self.scale*transform[0])
    y = int(self.scale*transform[1])
    width = int(self.scale*shape[0]*transform[2])
    height = int(self.scale*shape[1]*transform[2])
    return QRect(x, y, width, height)

  def resetRender(self):
    self.currentRender = None
    self.currentDepth = 0
    self.precompute = None


class QtRenderer(Renderer):
  contextClass = TileLoader
  tileClass = QtRenderingTile
  def setup(self, tiles):
    self.app = QApplication([])


def qtRender(updateList):
  QtRenderer().render(updateList)

