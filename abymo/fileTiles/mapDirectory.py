import glob
import hashlib
import os
import tempfile

def basicPathMapping(path):
  return hashlib.md5(os.path.abspath(path)).hexdigest()

def getAllFiles(sourceDir):
  """Get all files in a directory and subdirectories."""
  filelist = tempfile.NamedTemporaryFile().name
  sd = sourceDir.replace(" ", "\ ")
  command = "find %s/ ! -type l > %s" % (sd, filelist)
  os.system(command)
  return [os.path.abspath(f.strip()) for f in open(filelist).readlines()]

def getNewFiles(sourceDir, timestampFile):
  """Get all recently updated files in a directory and subdirectories."""
  filelist = tempfile.NamedTemporaryFile().name
  sd = sourceDir.replace(" ", "\ ")
  command = "find %s/ ! -type l -newer %s > %s" % (sd, timestampFile, filelist)
  os.system(command)
  return [f.strip() for f in open(filelist).readlines()]

def createFileMapping(sourceDir, tileDir, ignorePaths=[], ignoreExtensions=[]):
  files = getAllFiles(sourceDir)
  files = [f for f in files if os.path.splitext(f)[1] not in ignoreExtensions]
  inIgnorePaths = lambda x: sum([f.startswith(p) for p in ignorePaths])
  files = [f for f in files if not inIgnorePaths(f)]
  return dict([(f, "%s/%s.json" % (tileDir, basicPathMapping(f))) for f in files])

def filesToUpdate(filenameMapping, sourceDir, tileDir, timestampFile):
  """Produces a list of files to update, if they are missing a tile or have been changed since last run."""
  newFiles = getNewFiles(sourceDir, timestampFile)
  existingTiles = set(glob.glob("%s/*.json" % tileDir))
  filesToUpdate = set([])
  for p in filenameMapping.keys():
    if filenameMapping[p] not in existingTiles or p in newFiles:
      filesToUpdate.add(p)
      path = p
      while path!=sourceDir:
        path = os.path.dirname(path)
        filesToUpdate.add(path)
  return list(filesToUpdate)

