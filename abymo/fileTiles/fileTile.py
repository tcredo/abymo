from .. import Tile
from directoryTile import directoryTile
from pyTile import pyTile
from imageTile import imageTile
import os

def fileTile(path, filenameMapping):
  outputFile = filenameMapping[path]
  if path.endswith(".py"):
    try:
      p = pyTile(path, outputFile)
      return p
    except:
      pass
  if os.path.splitext(path)[1].lower() in [".jpg", ".jpeg", ".png"]:
    return imageTile(path, outputFile)
  return directoryTile(path, filenameMapping)
