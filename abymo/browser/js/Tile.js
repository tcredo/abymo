function Tile(src) {
  this.src = src;
  this.items = new Array();
  this.background = false;
  this.image = false;
  this.title = false;
  this.hasChildren = false;
  this.html = false;
  this.shape = false;
}

function Item(type,t,link) {
  this.type = type;
  this.t = t;
  this.link = link;
}

function resolveRelativePath(base_path, rel_path) {
  var new_parts = base_path.split("/");
  new_parts.pop();
  var rel_parts = rel_path.split("/");
  while (rel_parts.length) {
    var part = rel_parts.shift();
    if (part==".") {
      continue;
    } else if (part=="..") {
      new_parts.pop();
    } else {
      new_parts.push(part);
    }
  }
  return new_parts.join("/");
}

function parseItem(array, tileSrc) {
  var itemType = -1;
  if (array["type"]=="link") {
    itemType = 0;
  } else if (array["type"]=="img") {
    itemType = 1;
  } else {
    return false;
  }
  var src = resolveRelativePath(tileSrc, array["src"]);
  var t = array["transform"];
  return new Item(itemType,t,src);
}

function parseJsonTile(jsonTile, tileSrc) {
  var tile = new Tile(tileSrc);
  if ("color" in jsonTile) {
    tile.background = jsonTile["color"];
  }
  if ("html" in jsonTile) {
    tile.html = jsonTile["html"];
  }
  if ("shape" in jsonTile) {
    tile.shape = jsonTile["shape"];
  }
  tile.title = jsonTile["title"];
  tile.image = resolveRelativePath(tileSrc, jsonTile["precompute"]);
  for (i=0;i<jsonTile["items"].length;i++) {
    var array = jsonTile["items"][i];
    var item = parseItem(array, tileSrc);
    if (item) {
      tile.items.push(item);
    }
    if (item.type==0) {
      tile.hasChildren = true;
    }
  }
  return tile;
}

