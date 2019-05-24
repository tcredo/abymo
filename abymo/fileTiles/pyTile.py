from .. import Tile, TileFile
from ..layout import pyramidTile, labelTile
import glob
import ast
import math
import os
import svgwrite

def isScriptIf(node):
  if type(node).__name__=="If":
    if node.test.left.id=="__name__":
      ops = node.test.ops
      if len(ops)==1 and type(ops[0]).__name__=="Eq":
        comps = node.test.comparators
        if len(comps)==1 and type(comps[0]).__name__=="Str":
          return comps[0].s=="__main__"
  return False

def isFunctionDef(node):
  if type(node).__name__=="FunctionDef":
    return True
  return False

def isClassDef(node):
  if type(node).__name__=="ClassDef":
    return True
  return False
  
def isImport(node):
  if type(node).__name__=="Import":
    return True
  elif type(node).__name__=="ImportFrom":
    return True
  return False

def readAstNode(node):
  if isScriptIf(node):
    return ["IfNameEqMain"]
  elif isFunctionDef(node):
    return [type(node).__name__, node.name]
  elif isClassDef(node):
    return [type(node).__name__, node.name]
  else:
    return [type(node).__name__]

def pyTile(pyFile, outputFile):
  tree = ast.parse(open(pyFile).read())
  statements = []
  for node in tree.body:
    if not isImport(node):
      statements.append(readAstNode(node))
  images = []
  for i,s in enumerate(statements):
    imageFile = "%s.%s.svg" % (outputFile, i)
    d = svgwrite.Drawing(imageFile, size=("100px", "100px"))
    d.add(d.rect(insert=(2,2),size=(96,96), style="fill: lightblue;"))
    textStyle = "fill:black; font-size:6pt; font-family:monospace;"
    for j, t in enumerate(s):
      d.add(d.text(t, x=[5], y=[10*(j+2)], style=textStyle))
    d.save()
    images.append(imageFile)
  images = [os.path.basename(image) for image in images]
  tileFile = TileFile()
  if images:
    tileFile.addSubtree("pyramid", pyramidTile(images, color="#ffffff"))
    tileFile.root = labelTile(os.path.basename(outputFile) + "#pyramid", os.path.basename(pyFile), outputFile)
  else:
    tileFile.root = labelTile(None, os.path.basename(pyFile), outputFile)
  tileFile.save(outputFile)
  return tileFile
  

