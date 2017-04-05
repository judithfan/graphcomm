var path;
var pathNorm;

// The mouse has to drag at least N pt
// before the next drag event is fired:
tool.minDistance = 5;
paper.install(window);

function eG(t,m,s) { // eG = evaluateGaussian
    val = 1/(s*Math.sqrt(2*Math.PI)) * Math.exp(- Math.pow(m-t,2)/(2 * Math.pow(s,2)));
    return val;
}

function gS(t,s) { // gS = genStops
    n = eG(0,0,s);
    c = 1 - eG(t,0,s)/n;
    var s = new Color(c,c,c);
    // console.log(c);
    return s;
}

function onMouseDown(event) {
    if (path) {
        path.selected = false;
    };
    path = new Path();
    path2 = new Path();
    _p = new Path();
    path.strokeColor = 'black';
    path.strokeWidth = 5;
    path.fullySelected = true;
}

function onMouseDrag(event) {
    path.add(event.point); 
    
    var pathNorm = new Path();
    pathNorm.strokeWidth = 10;
    pathNorm.strokeColor = 'black';
    pathNorm.opacity = 0.5;
    var vector = event.delta;

    // rotate the vector by 90 degrees:
    vector.angle += 90;

    // change its length to 5 pt:
    vector.length = 10;
    
    pathNorm.add(event.middlePoint + vector);
    pathNorm.add(event.middlePoint - vector);  
    
    pathNorm.strokeColor = {
        gradient: {
            stops: [[gS(-4,1), 0], [gS(-3,1), 0.125], [gS(-2,1), 0.25],[gS(-1,1), 0.375],
                    [gS(0,1), 0.5], [gS(1,1), 0.625], [gS(2,1), 0.75],[gS(3,1), 0.875],[gS(4,1), 1]],
            radial: false
        },
        origin: event.middlePoint + vector,
        destination: event.middlePoint - vector
    };  
    
    
}

function onMouseUp(event) {
    path.selected = false;
    path.smooth(10);
    
    svgString = paper.project.exportJSON({asString:true});
    var serializer = new XMLSerializer();
    var svg = paper.project.exportSVG();
    var svg_string = serializer.serializeToString(svg);  
    // console.log(svg_string);
    
    var blob = new Blob([svg_string], {"type": "image/svg+xml"});          
    // console.log(blob);    
    
    a = document.createElement('a');
    a.type = 'image/svg+xml';
    a.href = window.URL.createObjectURL(blob);
    
    var canvas = document.getElementById("canvas");
    var ctx = canvas.getContext("2d");

    var img = new Image();
    img.onload = imageOnLoad; 
    img.onerror=function(){console.log("Image failed to load")};    
    img.src = a.href;
    
    
    function imageOnLoad() {
        ctx.drawImage(img, 0, 0);
        var myImageData = ctx.getImageData(0,0,100,100);
        pngUrl = canvas.toDataURL();
        pngUrl = pngUrl.replace('data:image/png;base64,','');
        var sum = _.reduce(myImageData.data, function(memo, num){ return memo + num; }, 0);
        // console.log(sum);
        // console.log(_.unique(myImageData.data));
        
    };
    
    }