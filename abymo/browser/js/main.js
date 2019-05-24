
// HTML variables. The tile renderer might also access these.
var canvas;
var sidebar;

var tileRenderer;
var tileStore;

// These variables are used for event handling.
// They should live in the main file, which hooks the renderer class to the browser.
var upKeyPressed = 0;
var downKeyPressed = 0;
var clicked = false;
var mouseX, mouseY;
var currentTouches = new Array;
var sidebarShowing = true;

/* A flag for scheduling a redraw. Set to true when the screen has changed. */
var redraw = true;


/* INPUT HANDLING, MAIN LOOP, INITIALIZATION */

document.onkeydown = function (e) {
  if (e) {
    switch (e.keyCode) {
      // 37 is right, 39 is left 
      case 38:
        upKeyPressed = 1;
        return false;
      case 40:
        downKeyPressed = 1;
        return false;
    }
  }
} 

document.onkeyup = function (e) {
  if (e) {
    console.log("KEYCODE: "+e.keyCode);
    switch (e.keyCode) {
      case 38:
        upKeyPressed = 0;
        break;    
      case 40:
        downKeyPressed = 0;
        break;
      case 67: //c
        centerMainTile();
        redraw = true;
        break;
      case 83: //s
        toggleSidebar();
        break;
    }
  }
}

function findPos(obj) {
  var curleft = 0, curtop = 0;
  if (obj.offsetParent) {
    do {
      curleft += obj.offsetLeft;
      curtop += obj.offsetTop;
    } while (obj = obj.offsetParent);
    return {x:curleft,y:curtop};
  }
  return {x:0,y:0};
}

function mouseMove(e) {
  var pos = findPos(canvas);
  var x = e.pageX - pos.x;
  var y = e.pageY - pos.y;
  if (clicked) {
    tileRenderer.pan(x-mouseX,y-mouseY);
    redraw = true;
  }
  mouseX = x;
  mouseY = y;
  if (clicked) {
    return false;
  }
}

function touchStart(e) {
  e.preventDefault();
  var touches = e.changedTouches;
  for (var i=0; i<touches.length; i++) {
    currentTouches[touches[i].identifier] = {x:touches[i].pageX, y:touches[i].pageY};
  }
}

function touchMove(e) {
  e.preventDefault();
  if (e.targetTouches.length==2) {
    var touch0 = e.targetTouches[0];
    var touch1 = e.targetTouches[1];
    var lastTouch0 = currentTouches[touch0.identifier];
    var lastTouch1 = currentTouches[touch1.identifier];
    tileRenderer.pan((touch0.pageX+touch1.pageX-lastTouch0.x-lastTouch1.x)/2,
                    (touch0.pageY+touch1.pageY-lastTouch0.y-lastTouch1.y)/2);
    var z = Math.pow((Math.pow(touch0.pageX-touch1.pageX,2)
                     +Math.pow(touch0.pageY-touch1.pageY,2))
                    /(Math.pow(lastTouch0.x-lastTouch1.x,2)
                     +Math.pow(lastTouch0.y-lastTouch1.y,2)),0.5);
    tileRenderer.zoom(z,{x:(touch0.pageX+touch1.pageX)/2,
                     y:(touch0.pageY+touch1.pageY)/2});
    redraw = true;
  } else if (e.targetTouches.length==1) {
    var touch = e.targetTouches[0];
    var lastTouch = currentTouches[touch.identifier];
    tileRenderer.pan(touch.pageX-lastTouch.x,touch.pageY-lastTouch.y);
    redraw = true;
  }
  var touches = e.changedTouches;
  for (var i=0; i<touches.length; i++) {
    currentTouches[touches[i].identifier] = {x:touches[i].pageX, y:touches[i].pageY};
  }
}

function touchEnd(e) {
  e.preventDefault();
  var touches = e.changedTouches;
  for (var i=0; i<touches.length; i++) {
    currentTouches[touches[i].identifier] = null;
  }
}

function toggleSidebar() {
  if (sidebarShowing) {
    document.getElementById("sidebar").style.opacity = 1;
    document.getElementById("sidebar").style.left = "-300px";
  } else {
    document.getElementById("sidebar").style.opacity = 1;
    document.getElementById("sidebar").style.left = "0px";
  }
  sidebarShowing = !sidebarShowing;
} 

function resizeWindow() {
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;
  sidebar.style.height = window.innerHeight + "px"; //window.innerHeight;
  redraw = true;
}

function loop() {
  if (upKeyPressed) {
    tileRenderer.zoom(1.05,{x:mouseX,y:mouseY});
    redraw = true;
  }
  if (downKeyPressed) {
    tileRenderer.zoom(1/1.05,{x:mouseX,y:mouseY});
    redraw = true;
  }
  if (tileStore.checkMoreLoaded()) {
    redraw = true;
  }
  if (redraw) {
    var mainTile = tileRenderer.drawRoot();
    if (mainTile.html) {
      document.getElementById("notes").innerHTML = mainTile.html;
    } else {
      document.getElementById("notes").innerHTML = mainTile.title;
    }
    redraw = false;
  }
}

function init() {
  canvas = document.getElementById("abymo");
  sidebar = document.getElementById("sidebar");
  tileStore = new TileStore();
  tileRenderer = new TileRenderer(canvas, tileStore);
  tileRenderer.pan(sidebar.offsetWidth, 0);
  resizeWindow();
  window.onresize = resizeWindow;
  document.onmousemove = mouseMove;
  canvas.onmousedown = function (e) {
    clicked = true;
    e.preventDefault();
  }
  document.onmouseup = function (e) {
    clicked = false;
  }
  canvas.addEventListener("touchstart", touchStart, false);
  canvas.addEventListener("touchmove", touchMove, false);
  canvas.addEventListener("touchend", touchEnd, false);
  canvas.addEventListener("touchcancel", touchEnd, false);
  canvas.addEventListener("touchleave", touchEnd, false);
  var loopId = setInterval(loop,1000/60);
}




