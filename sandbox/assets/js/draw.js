
function DrawObject(width, height, visible){
    this.canvas = $('<canvas/>', {
  "class": "drawCanvas",
  "Width": width + "px",
  "Height": height + "px"
    })[0];
    if (visible==true){
  $(this.canvas).css({"display": "inline"});
  $(activeCodeBox).parent().append(this.canvas);
    };
    this.paper = new paper.PaperScope();
    this.paper.setup(this.canvas);
    this.paper.view.viewSize = new this.paper.Size(width, height);
    this.redraw();
}

DrawObject.prototype.newPath = function(strokeWidth, opacity, color){
    var path = new this.paper.Path();
    path.strokeColor = color || 'black';
    path.strokeWidth = strokeWidth || 8;
    path.opacity = opacity || 0.6;
    return path;
};

DrawObject.prototype.newPoint = function(x, y){
    return new this.paper.Point(x, y);
};

DrawObject.prototype.newCurve = function(point1, point2, point3, point4) {
  return new this.paper.Curve(point1, point2, point3, point4);
};
  
DrawObject.prototype.circle = function(x, y, radius, stroke, fill){
    var point = this.newPoint(x, y);
    var circle = new this.paper.Path.Circle(point, radius || 50);
    circle.fillColor = fill || 'black';
    circle.strokeColor = stroke || 'black';
    this.redraw();
};

DrawObject.prototype.polygon = function(x, y, n, radius, stroke, fill){
    var point = this.newPoint(x, y);
    var polygon = new this.paper.Path.RegularPolygon(point, n, radius || 20);
    polygon.fillColor = fill || 'white';
    polygon.strokeColor = stroke || 'black';
    polygon.strokeWidth = 4;
    this.redraw();
};

DrawObject.prototype.line = function(x1, y1, x2, y2, strokeWidth, opacity, color){
    var path = this.newPath(strokeWidth, opacity, color);
    path.moveTo(x1, y1);
    path.lineTo(this.newPoint(x2, y2));
    this.redraw();
};

DrawObject.prototype.drawSpline = function(startX, startY, midX, midY, endX, endY){
  var myPath = this.newPath();
  myPath.strokeColor = 'black';
  myPath.add(this.newPoint(startX, startY));
  myPath.add(this.newPoint(midX, midY));
  myPath.add(this.newPoint(endX, endY));

  myPath.smooth();

  this.redraw();
};

DrawObject.prototype.drawADSpline = function(startX, startY, midX, midY, endX, endY){
  var myPath = this.newPath();
  myPath.strokeColor = 'black';
  myPath.add(this.newPoint(startX, startY));
  myPath.add(this.newPoint(midX, midY));
  myPath.add(this.newPoint(endX, endY));

  myPath.smooth();

  this.redraw();
};

function getGuesses (s, k, a, drawObj) {
  var raster = new drawObj.paper.Raster(drawObj.canvas);
  raster.visible = false;
  var dataStr = raster.toDataURL(); // converts to Base 64
  dataStr = dataStr.replace('data:image/png;base64,',''); // clean string
  var json = raster.exportJSON({asString : true});
  var current_data = {imgData: dataStr,
          json: json,
          colname:'graphcomm_explore_splines',
          dbname:'splines',
          trialNum: 1
         };
  $.ajax({
    type: 'GET',
    url: 'http://18.93.15.28:9919/saveimage',
    dataType: 'jsonp',
    traditional: true,
    contentType: 'application/json; charset=utf-8',
    data: current_data,
    success: function(msg) {
      var repackagedOutput =  _.object(_.zip(msg.guesses, msg.margins));
      var trampoline = k(s, repackagedOutput);
      while (trampoline){
  trampoline = trampoline();
      }
    }
  });
};

DrawObject.prototype.redraw = function(){
    this.paper.view.draw();
};

DrawObject.prototype.toArray = function(){
    var context = this.canvas.getContext('2d');
    var imgData = context.getImageData(0, 0, this.canvas.width, this.canvas.height);
    return imgData.data;
};

DrawObject.prototype.distanceF = function(f, cmpDrawObject){
    if (!((this.canvas.width == cmpDrawObject.canvas.width) &&
    (this.canvas.height == cmpDrawObject.canvas.height))){
  console.log(this.canvas.width, cmpDrawObject.canvas.width,
        this.canvas.height, cmpDrawObject.canvas.height);
  throw new Error("Dimensions must match for distance computation!");
    }
    var thisImgData = this.toArray();
    var cmpImgData = cmpDrawObject.toArray();
    return f(thisImgData, cmpImgData);
};

DrawObject.prototype.distance = function(cmpDrawObject){
    var df = function(thisImgData, cmpImgData) {
  var distance = 0;
  for (var i=0; i<thisImgData.length; i+=4) {
      var col1 = [thisImgData[i], thisImgData[i+1], thisImgData[i+2], thisImgData[i+3]];
      var col2 = [cmpImgData[i], cmpImgData[i+1], cmpImgData[i+2], cmpImgData[i+3]];
      distance += euclideanDistance(col1, col2);
  };
  return distance;
    };
    return this.distanceF(df, cmpDrawObject)
};

DrawObject.prototype.destroy = function(){
    this.paper = undefined;
    $(this.canvas).remove();
}

function Draw(s, k, a, width, height, visible){
    return k(s, new DrawObject(width, height, visible));
}

function loadImage(s, k, a, drawObject, url){
    // Synchronous loading - only continue with computation once image is loaded
    var context = drawObject.canvas.getContext('2d');
    var imageObj = new Image();
    imageObj.onload = function() {
  var raster = new drawObject.paper.Raster(imageObj);
  raster.position = drawObject.paper.view.center;
  drawObject.redraw();
  var trampoline = k(s);
  while (trampoline){
      trampoline = trampoline();
  }
    };
    imageObj.src = url;
    return false;
}