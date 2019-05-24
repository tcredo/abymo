import os
import tempfile
import shutil
import SimpleHTTPServer
import SocketServer


class SilentHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
  def log_message(self, format, *args):
    return

def runAbymo(tileDir, startTile):
  htmlDir = tempfile.mkdtemp()
  jsPath = os.path.join(os.path.split(__file__)[0], "js")
  with open(os.path.join(htmlDir, "abymo.js"), "w") as js:
    js.write("""var ROOT_TILE_SRC = "data/%s"\n""" % startTile)
    for f in ["Tile.js", "TileStore.js", "TileRenderer.js", "main.js"]:
      js.write(open(os.path.join(jsPath,f)).read())
  for f in ["abymo.html","abymo.css"]:
    shutil.copyfile(os.path.join(jsPath, f), os.path.join(htmlDir, f))
  os.chdir(htmlDir)
  os.symlink(tileDir, "data")
  os.system("chromium-browser http://localhost:8000/abymo.html &")
  Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
  SocketServer.TCPServer.allow_reuse_address = True
  httpd = SocketServer.TCPServer(("", 8000), SilentHandler)
  try:
    httpd.serve_forever()
  finally:
    httpd.shutdown()

