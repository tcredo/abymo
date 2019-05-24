import pygame
import stat
import sys
import time
from pygame.locals import *
from ..util import compose, invert, zoom, resolveRelativePath
from .. import Tile, TileFile, TileLoader


def drawTilePygame(surface, cache, tilename, t, dims, smallFont):
  """ Recursively draw boxes representing the file structure starting at path. """
  size_cutoff = 20
  DIR_COLOR = (0,0,100)
  TEXT_COLOR = (255,255,255)
  if t[0]>dims[0] or t[1]>dims[1] or t[0]+t[2]<0 or t[1]+t[2]<0:
    return
  tile = cache.getTile(tilename)
  s = tile.shape if tile.shape else [1., 1.]
  rect = (int(t[0]),int(t[1]),int(s[0]*t[2]),int(s[1]*t[2]))
  if t[2]<=200:
    image = pygame.image.load(resolveRelativePath(tile.basename, tile.precompute))
    image = pygame.transform.scale(image, (int(s[0]*t[2]),int(s[1]*t[2])))
    surface.blit(image, rect)
  else:
    pygame.draw.rect(surface,DIR_COLOR,rect,2)
    for i, link in enumerate(tile.links):
      src = resolveRelativePath(tile.basename, link.src)
      if link.type==0:
        if link.transform[2]*t[2]<size_cutoff: # hack
          continue
        drawTilePygame(surface, cache, src, compose(t, link.transform), dims, smallFont)
      else:
        assert link.type==1
  if t[2]>50:
    surface.blit(smallFont.render(tile.title,True,TEXT_COLOR),(rect[0],rect[1]))


class PygameBrowser:
  def __init__(self, rootTile):
    # Parameters
    self.cache = TileLoader()
    self.dims = [500,500]
    frameRate = 0.03

    # Initialization
    pygame.init()
    pygame.display.set_caption("Tile browser")
    self.screen = pygame.display.set_mode(self.dims,RESIZABLE)
    self.screen.fill((0,0,0))
    self.t = [0, 0, self.dims[0]]
    self.drag_pos = False
    lastUpdate = time.time()
    self.redraw = True

    # Main UI loop
    while True:
      while time.time()-lastUpdate < frameRate:
        time.sleep(0.005)
      lastUpdate = time.time()
      self.handleEvents()
      if self.redraw:
        self.drawScreen(rootTile)

  def drawScreen(self, rootTile):
    self.screen.fill((0,0,0))
    smallFont = pygame.font.SysFont("blah",16)
    drawTilePygame(self.screen, self.cache, rootTile,self.t, self.dims, smallFont)
    pygame.display.flip()
    self.redraw = False

  def handleEvents(self):
    events = pygame.event.get()
    pos = pygame.mouse.get_pos()
    if self.drag_pos:
      self.t[0] += pos[0] - self.drag_pos[0]
      self.t[1] += pos[1] - self.drag_pos[1]
      self.drag_pos = pos
      self.redraw = True
    for event in events:
      if event.type==QUIT: self.shutdown()
      elif event.type==VIDEORESIZE:
        self.dims = event.dict['size']
        self.screen = pygame.display.set_mode(self.dims,RESIZABLE)
        self.redraw = True
      elif event.type == pygame.MOUSEBUTTONDOWN:
        if event.button == 1:
          self.drag_pos = pos
      elif event.type == pygame.MOUSEBUTTONUP:
        if event.button == 1:
          self.drag_pos = False
        elif event.button==4: self.zoomIn(pos)
        elif event.button==5: self.zoomOut(pos)
      elif event.type == pygame.KEYDOWN:
        if event.key == pygame.K_UP: self.zoomIn(pos)
        elif event.key == pygame.K_DOWN: self.zoomOut(pos)
      elif event.type == pygame.KEYUP:
        if event.key==pygame.K_ESCAPE: self.shutdown()
        elif event.key == pygame.K_UP: self.zoomIn(pos)
        elif event.key == pygame.K_DOWN: self.zoomOut(pos)

  def zoomIn(self, pos):
    self.t = zoom(1.1, self.t, pos)
    self.redraw = True

  def zoomOut(self, pos):
    self.t = zoom(1/1.1, self.t, pos)
    self.redraw = True

  def shutdown(self):
    pygame.display.quit()
    pygame.quit()
    sys.exit()

