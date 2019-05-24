var PRELOAD_CUTOFF = 150;
var PRECOMPUTE_CUTOFF = 200;
var drawImagesToPixels = true; // TODO: This should be controlled by individual tiles.

function TileRenderer(canvas, tileStore) {
  this.tileStore = tileStore;
  this.screenT = [25,25,450.0];
  this.rootTileSrc = ROOT_TILE_SRC;
  this.rootTile = this.tileStore.getTile(this.rootTileSrc);
  this.tile_history = [];
  this.canvas = canvas;
  if (this.canvas.getContext) {
    this.context = this.canvas.getContext("2d");
  }
}

TileRenderer.prototype.zoom = function(s,center) {
  if (s>1.0 && this.screenT[2]*s > 1e6) {
    return; // drawing rects unreliable in firefox at this scale
  }
  var z = [(1-s)*center.x, (1-s)*center.y, s];
  this.screenT = compose(z,this.screenT);
  this.adjustRoot();
}

TileRenderer.prototype.pan = function(x,y) {
  this.screenT = [this.screenT[0]+x,this.screenT[1]+y,this.screenT[2]];
  this.adjustRoot();
}

TileRenderer.prototype.adjustRoot = function() {
  if (this.coverScreen(this.screenT, this.rootTile)) {
    for (var i=0; i<this.rootTile.items.length; i++) {
      var item = this.rootTile.items[i];
      if (item.type==0) {
        var t = compose(this.screenT,item.t);
        var linkedTile = this.tileStore.getTile(item.link);
        if (linkedTile && this.coverScreen(t, linkedTile)) {
          if (this.tileStore.getImage(linkedTile.image)) {
            this.tile_history.push([this.rootTile.src,item.t.slice()]);
            this.rootTile = linkedTile;
            this.screenT = t;
          }
          break;
        }
      }
    }
  } else {
    if (this.tile_history.length) {
      var last = this.tile_history.pop();
      // History stores paths relative to base file, so no need to relativize.
      this.rootTile = this.tileStore.getTile(last[0]);
      this.screenT = compose(this.screenT,invert(last[1]));
    } else {
      // TODO: Move this little hack into the tile files. default_history or some attribute like that?
      var last = [this.rootTileSrc, [0.34, 0.34, 0.32]]
    }

  }
}

TileRenderer.prototype.centerMainTile = function() {
  this.screenT = compose([0,0,500],compose(invert(mainTileT),this.screenT));
}

TileRenderer.prototype.drawRoot = function() {
  if (!this.rootTile) {
    this.rootTile = this.tileStore.getTile(this.rootTileSrc);
  }
  this.mainTile = null;
  this.mainTileScore = 0;
  this.mainTileT = null;
  this.context.fillStyle = "#aaaaaa";
  this.context.clearRect(0,0,canvas.width,canvas.height);
  this.context.fillRect(0,0,canvas.width,canvas.height);
  this.drawTile(this.rootTile, this.screenT, this.context, this.canvas);
  return this.mainTile;
}

TileRenderer.prototype.coverScreen = function(t, tile) {
  if (tile.shape) {
    var shape = tile.shape;
  } else {
    var shape = [1.0, 1.0];
  }
  return t[0]<=0 
      && t[1]<=0 
      && t[0]+t[2]*shape[0]>=this.canvas.width 
      && t[1]+t[2]*shape[1]>=this.canvas.height;
}

TileRenderer.prototype.drawTile = function(tile, t) {
  if (!tile) {
    return
  } else if (t[0]>this.canvas.width || t[0]+t[2]<0) {
    return;
  } else if (t[1]>this.canvas.height || t[1]+t[2]<0) {
    return;
  }
  var overlapW = Math.max(0,Math.min(this.canvas.width,t[0]+t[2])-Math.max(0,t[0]));
  var overlapH = Math.max(0,Math.min(this.canvas.height,t[1]+t[2])-Math.max(0,t[1]));
  var overlapRatio = (1.0*overlapW*overlapH)/Math.max(t[2]*t[2],this.canvas.width*this.canvas.height);
  if (overlapRatio>this.mainTileScore) {
    this.mainTile = tile;
    this.mainTileScore = overlapRatio;
    this.mainTileT = t;
  }
  if (t[2]>PRELOAD_CUTOFF) {
    for (var i=0, len=tile.items.length; i<len; ++i) {
      if (tile.items[i].type==0) {
        this.tileStore.getTile(tile.items[i].link);
      } else if (tile.items[i].type==1) {
        this.tileStore.getImage(tile.items[i].link);
      }
    }
  }
  if (t[2]>PRECOMPUTE_CUTOFF && this.tileStore.allItemsLoaded(tile)) {
    if (tile.background) {
      this.context.fillStyle = tile.background;
      if (tile.shape) {
        var shape = tile.shape;
        this.context.fillRect(t[0],t[1],shape[0]*t[2],shape[1]*t[2]);
      } else {
        this.context.fillRect(t[0],t[1],t[2],t[2]);
      }
    }
    for (var i=0, len=tile.items.length; i<len; ++i) {
      var item = tile.items[i];
      var itemTransform = compose(t, item.t);
      if (item.type==0) {
        this.drawTile(this.tileStore.getTile(item.link), itemTransform);
      } else if (item.type==1) {
        var image = this.tileStore.getImage(item.link);
        if (image) {
          var box = imageBox(itemTransform, image.width, image.height);
          this.context.drawImage.apply(this.context, [image].concat(box));
        }
      }
    }
  } else if (tile.image) {
    var image = this.tileStore.getImage(tile.image);
    if (image) {
      // Fix here, this doesn't respect current bounding box implementation.
      if (tile.shape) {
        var shape = tile.shape;
        this.context.drawImage(image, t[0], t[1], shape[0]*t[2], shape[1]*t[2]);
      } else {
        var box = imageBox(t, 1, 1);
        this.context.drawImage.apply(this.context, [image].concat(box));
        // Equivalent to:
        // context.drawImage(image, box[0], box[1], box[2], box[3]);
      }
    }
  }
}

function compose(t0,t1) {
  return [t0[0] + t0[2]*t1[0],
          t0[1] + t0[2]*t1[1],
          t0[2]*t1[2]];
}

function invert(t) {
  return [-t[0]/t[2],-t[1]/t[2],1/t[2]];
}

function imageBox(t, width, height) {
  var w, h;
  if (width == height) {
    w = t[2];
    h = t[2];
  } else {
    var s = Math.max(width, height);
    w = width*t[2]/s;
    h = height*t[2]/s;
  }
  if (drawImagesToPixels) {
    // In firefox you'll get seams between chopped image tiles unless you round to pixels.
    var x = Math.floor(t[0]);
    var y = Math.floor(t[1]);
    var sx = Math.ceil(t[0]+w)-x;
    var sy = Math.ceil(t[1]+h)-y;
    return [x, y, sx, sy];
  } else {
    return [t[0], t[1], w, h];
  }
}

