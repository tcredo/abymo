import sys
from cachetools import LRUCache
from PyQt5.QtCore import Qt, QRectF, QTimer
from PyQt5.QtGui import QImage, QPainter, QPixmap, QColor, QCursor
from PyQt5.QtSvg import QSvgRenderer
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QMainWindow
from ..util import compose, invert, zoom, resolveRelativePath
from .. import Tile, TileFile, TileLoader


class QtTile(Tile):
  def draw(self, painter, transform, tileCache, imageCache):
    #if self.isOutOfBounds(transform):
    #  return
    if transform[2]<=200:
      imageFile = resolveRelativePath(self.basename, self.precompute)
      self.drawImage(painter, imageFile, transform, imageCache, self.shape)
    else:
      for i, link in enumerate(self.links):
        self.renderLink(painter, transform, link, tileCache, imageCache)

  def renderLink(self, painter, transform, link, tileCache, imageCache):
    src = resolveRelativePath(self.basename, link.src)
    if link.type==0:
      tile = tileCache.getTile(src)
      tile.draw(painter, compose(transform, link.transform), tileCache, imageCache)
    else:
      assert link.type==1
      self.drawImage(painter, src, compose(transform, link.transform), imageCache)

  def drawImage(self, painter, imageFile, t, imageCache, s=None):
    if imageFile.endswith("svg"):
      svg = QSvgRenderer(imageFile)
      #svg.load(imageFile)
      svg.render(painter, QRectF(t[0], t[1], t[2], t[2]))
    else:
      pixmap = imageCache.get(imageFile)
      if not pixmap:
        pixmap = QPixmap(imageFile)
        imageCache.update([(imageFile, pixmap)])
      # TODO: When the symlink has the wrong extension this causes a crash.
      if s is not None:
        width = s[0]*t[2]
        height = s[1]*t[2]
      else:
        maxDimension = float(max(pixmap.width(), pixmap.height()))
        width = t[2]*pixmap.width()/maxDimension
        height = t[2]*pixmap.height()/maxDimension
      painter.drawPixmap(int(t[0]), int(t[1]), int(width), int(height), pixmap)


class QtTileBrowser(QMainWindow):
  def __init__(self, rootTile):
    app = QApplication(sys.argv) 
    QMainWindow.__init__(self)
    self.rootTile = rootTile
    self.history = []
    self.tileCache = TileLoader(tileClass=QtTile)
    self.imageCache = LRUCache(maxsize=1000)
    self.dimensions = [500, 500]
    self.rootTransform = [0, 0, self.dimensions[0]]
    self.pixmap = QPixmap(*self.dimensions)
    self.label = QLabel()
    self.label.setMinimumSize(1, 1)
    self.setCentralWidget(self.label)
    self.resize(*self.dimensions)
    self.setMouseTracking(True)
    self.mouseDrag = None
    self.keys = {}
    self.show()
    timer = QTimer()
    timer.timeout.connect(self.drawRoot)
    timer.start(1000//60)
    sys.exit(app.exec_())

  def mousePressEvent(self, event):
    if event.buttons()==Qt.LeftButton:
      self.mouseDrag = [event.x(), event.y()]

  def mouseMoveEvent(self, event):
    mousePos = [event.x(), event.y()]
    if event.buttons()==Qt.LeftButton:
      self.rootTransform[0] += mousePos[0]-self.mouseDrag[0]
      self.rootTransform[1] += mousePos[1]-self.mouseDrag[1]
      self.mouseDrag = mousePos

  def keyPressEvent(self, event):
    self.keys[event.key()] = True

  def keyReleaseEvent(self, event):
    self.keys[event.key()] = False

  def resizeEvent(self, event):
    size = event.size()
    self.dimensions = [size.width(), size.height()]
    self.pixmap = QPixmap(size)

  def drawRoot(self):
    pos = self.label.mapFromGlobal(QCursor.pos())
    mousePosition = [pos.x(), pos.y()]
    if self.keys.get(Qt.Key_Up, False):
      self.rootTransform = zoom(1.08, self.rootTransform, mousePosition)
    elif self.keys.get(Qt.Key_Down, False):
      self.rootTransform = zoom(1/1.08, self.rootTransform, mousePosition)
    self.adjustRoot()
    self.pixmap.fill(QColor(0, 0, 0))
    with QPainter(self.pixmap) as painter:
      root = self.tileCache.getTile(self.rootTile)
      root.draw(painter, self.rootTransform, self.tileCache, self.imageCache)
    self.label.setPixmap(self.pixmap)

  def isOutOfBounds(self, transform):
    return (transform[0]>self.dimensions[0] or \
            transform[1]>self.dimensions[1] or \
            transform[0]+transform[2]<0 or     \
            transform[1]+transform[2]<0)

  def coversScreen(self, transform, shape=[1.,1.]):
    return (transform[0]<=0 and \
            transform[1]<=0 and \
            transform[0]+transform[2]*shape[0]>=self.dimensions[0] and \
            transform[1]+transform[2]*shape[1]>=self.dimensions[1])

  def adjustRoot(self):
    if not self.coversScreen(self.rootTransform):
      if self.history:
        last = self.history.pop()
        self.rootTile = last[0]
        self.rootTransform = compose(self.rootTransform, invert(last[1]))
    else:
      tile = self.tileCache.getTile(self.rootTile)
      for link in tile.links:
        if link.type==0:
          t = compose(self.rootTransform, link.transform)
          if self.coversScreen(t):
            self.history.append((self.rootTile, link.transform))
            self.rootTransform = t
            self.rootTile = resolveRelativePath(tile.basename, link.src)
            break


