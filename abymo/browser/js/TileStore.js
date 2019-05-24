function TileStore() {
  this.images = {};
  this.tiles = {};
  this.moreLoaded = false;
}

TileStore.prototype.getImage = function(imageSrc) {
  if (imageSrc in this.images) {
    return this.images[imageSrc];
  } else {
    this.images[imageSrc] = false;
    var img = new Image();
    var self = this;
    img.onload = function() {
      self.images[imageSrc] = img;
      self.moreLoaded = true;
    }
    img.src = imageSrc;
    return false;
  }
}

TileStore.prototype.getTile = function(tileSrc) {
  if (tileSrc in this.tiles) {
    return this.tiles[tileSrc];
  } else {
    this.tiles[tileSrc] = false;
    var xmlHttp = new XMLHttpRequest();
    var self = this;
    xmlHttp.onreadystatechange = function() {
      if (xmlHttp.readyState==4) {
        var js = JSON.parse(xmlHttp.responseText);
        var tile = parseJsonTile(js["root"], tileSrc);
        self.getImage(tile.image);
        self.tiles[tileSrc] = tile;
        self.moreLoaded = true;
        for (var key in js["subtiles"]) {
          var src = tileSrc + "#" + key;
          var tile = parseJsonTile(js["subtiles"][key], src);
          self.getImage(tile.image);
          self.tiles[src] = tile;
        }
      }
    }
    xmlHttp.open("GET",tileSrc,true);
    xmlHttp.setRequestHeader('Cache-Control', 'no-cache');
    xmlHttp.send();
    return false;
  }
}

TileStore.prototype.allItemsLoaded = function(tile) {
  for (var i=0, len=tile.items.length; i<len; ++i) {
    var item = tile.items[i];
    if (item.type==0) {
      var childTile = this.getTile(item.link);
      if (!childTile) {
        return false;
      } else if (childTile.image && !this.getImage(childTile.image)) {
        return false;
      }
    } else if (item.type==1) {
      if (!this.getImage(item.link)) {
        return false;
      }
    }
  }
  return true;
}

TileStore.prototype.checkMoreLoaded = function () {
  var moreLoaded = this.moreLoaded;
  this.moreLoaded = false;
  return moreLoaded;
}

