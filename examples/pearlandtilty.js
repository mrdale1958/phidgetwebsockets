/* Los Mochis Tilty Table is an interactive tour of enbvironmental issues in Mexico. 

Moving along the vertical axis (spin) accesses different, more and less local sites and content
Moving along the plane (tilt) (north, south, east west) lets the user explore the 
view from the current zoom level and nacvigate to other sites of interest.

*/

/* instruction t4exts that appear at different levels of zoom */
var defaultSpinInstruction = "Rotar en el sentido de las manecillas del reloj para acercar la imagen";
var defaultTiltInstruction = "Inclinar hacia abajo y arriba para movere hacia el Norte";
var huntForHotSpotTiltInstruction = "Ubica los puntos marcados en el mapa";
var huntForHotSpotSpinInstruction = "Ubica los puntos marcados en el mapa";
var spinToContinue= "Gira a la derecha para continuar el recorrido";
var spinToGoBack = "Gira a la izquierda para regresar";
var zoomInToActiveRegions = "Haz un acercamiento en las zonas con color";

/* for each zoom layer (larger is closer to earth) define the visibility of various eleents
    through a set of key:value pairs

A value of true for a key indicates it is a hotspot with visual content. 
    Upon reaching that zoom level (by spinning) the <div> with id=key will be made visible 
    and the map will be panned to the corresponding 'hotspot' These divs are defined in 
    the html file and are of the form
    <div class="instructions" id="site1">
      <img src="cedulas/Tilty 1.png" id="site1_img">
    </div>
 
A value of false for a key indicates it is a region of interest that can be shown via a 
  shapefile in GeoJson format which will be turned on at that particular zoom level.

A string value for a key indicates the index to a hotspot that should be indicated  at this zoom level

*/



var zoomLayers = {
  '0' : { 
    'pannable' : false,
    'mapZoom' : 4,
    'pearland' : true,
    'spinInstruction' : defaultSpinInstruction,
    'tiltInstruction' : defaultTiltInstruction,

  },
  '1' : { 
    'pannable' : true,
    'mapZoom' : 5,
    'pearland' : false,
    'spinInstruction' : defaultSpinInstruction,
    'tiltInstruction' : defaultTiltInstruction,
  },
  '2' : { 
    'mapZoom' : 6,
    'pannable' : true,
    'pearland' : false,
    'spinInstruction' : defaultSpinInstruction,
    'tiltInstruction' : defaultTiltInstruction,
  },
  '3' : { 
    'pannable' : true,
    'mapZoom' : 7,
    'pearland' : false,
    'spinInstruction' : defaultSpinInstruction,
    'tiltInstruction' : defaultTiltInstruction,
  },
  '4' : { 
    'pannable' : true,
    'mapZoom' : 8,
    'pearland' : false,
    'spinInstruction' : defaultSpinInstruction,
    'tiltInstruction' : defaultTiltInstruction,
  },
  '5': {
    'pannable' : true,
    'mapZoom' : 9,
    'pearland' : false,
    'spinInstruction' : defaultSpinInstruction,
    'tiltInstruction' : defaultTiltInstruction,
  },
  '6': {
    'pannable' : true,
    'mapZoom' : 10,
    'pearland' : false,
    'spinInstruction' : defaultSpinInstruction,
    'tiltInstruction' : defaultTiltInstruction,
  },
  '6': {
    'pannable' : true,
    'mapZoom' : 11,
    'pearland' : false,
    'spinInstruction' : defaultSpinInstruction,
    'tiltInstruction' : defaultTiltInstruction,
  },

  '7': { 
    'pannable' : true,
    'mapZoom' : 12,
    'pearland' : false,
    'spinInstruction' : defaultSpinInstruction,
    'tiltInstruction' : defaultTiltInstruction,
  },
  '8': {
    'pannable' : true,
    'mapZoom' : 13,
    'pearland' : false,
    'spinInstruction' : defaultSpinInstruction,
    'tiltInstruction' : defaultTiltInstruction,
  },

  '9': {
    'pannable' : true,
    'mapZoom' : 14,
    'pearland' : false,
    'spinInstruction' : defaultSpinInstruction,
    'tiltInstruction' : defaultTiltInstruction,
  },
  '10': {
    'pannable' : true,
    'mapZoom' : 15,
    'pearland' : false,
     'spinInstruction' : defaultSpinInstruction,
    'tiltInstruction' : defaultTiltInstruction,
  },

  '11': {
    'pannable' : true,
    'mapZoom' : 16,
    'pearland' : false,
    'spinInstruction' : defaultSpinInstruction,
    'tiltInstruction' : defaultTiltInstruction,
  },
  '12': {
    'pannable' : true,
    'mapZoom' : 17,
    'pearland' : false,
    'spinInstruction' : defaultSpinInstruction,
    'tiltInstruction' : defaultTiltInstruction,
  },
  '13': {
    'pannable' : true,
    'mapZoom' : 18,
    'pearland' : false,
    'spinInstruction' : defaultSpinInstruction,
    'tiltInstruction' : defaultTiltInstruction,
  },
  '14': {
    'pannable' : true,
    'mapZoom' : 19,
    'pearland' : false,
    'spinInstruction' : defaultSpinInstruction,
    'tiltInstruction' : defaultTiltInstruction,
  },
  
};

var hotspots = {
  "pearland" : [29.559701202795658,-95.31452893710866],
  

};


/* regions of interest */

var features = {
}

var targetColor = '#ff0000';
var targetWidth = 0.03; // portion of visible map

var maxZoom = 19;
var minZoom = 3;
var currentZoom = 0;
var targetRectangle;
var currentScale = 1.0;
var mapData = [];
var clicksPerRev =  256; // weirdly not 3.14159 * 4 *
var revsPerFullZoom = (maxZoom - minZoom)/8;
var clicksPerZoomLevel =  clicksPerRev / revsPerFullZoom;
var maxClicks = clicksPerRev * revsPerFullZoom * 1.0;
var currentSpinPosition = 0;
var panSensorSensitivity = 90;


// General globals
var ws;
var launchWebSocket = function()
{
  try {
    ws = new WebSocket("ws://127.0.0.1:5678/");
  } 
  catch(e)
  {
    console.log("failed to attach local web socket: " + e);
    try 
    {
      ws = new WebSocket("ws://192.168.1.89:5678/");
    }
    catch(e)
    {
      console.log("failed to attach remote web socket: " + e);
    }
  } 
  ws.onmessage = handleWebSocketMessage;
  ws.onopen = handleWebSocketOpen;
  ws.onerror = handleWebSocketError;
  ws.onclose = handleWebSocketClose;
};
var messages = document.createElement('ul');
var jsonData;

var loadedFeatures = [];

var trapiche = null;
var floatZoom = 14.0;
var mexicoCenter = null;
var mexicoFullZoom = 5;
var idleTimer;
var map;


var hotspot = {};

var lastZoom = -1;

var  handleWebSocketOpen = function()
{
  console.log("websocket open at "+ new Date().toLocaleString());
};

var handleWebSocketError = function(evt)
{
  console.log("websocket error" + evt);
};

var  handleWebSocketClose = function (event) {
  //alert(event.code);
  // See http://tools.ietf.org/html/rfc6455#section-7.4.1
  if (event.code == 1000)
    reason = "Normal closure, meaning that the purpose for which the connection was established has been fulfilled.";
  else if(event.code == 1001)
    reason = "An endpoint is \"going away\", such as a server going down or a browser having navigated away from a page.";
  else if(event.code == 1002)
    reason = "An endpoint is terminating the connection due to a protocol error";
  else if(event.code == 1003)
    reason = "An endpoint is terminating the connection because it has received a type of data it cannot accept (e.g., an endpoint that understands only text data MAY send this if it receives a binary message).";
  else if(event.code == 1004)
    reason = "Reserved. The specific meaning might be defined in the future.";
  else if(event.code == 1005)
    reason = "No status code was actually present.";
  else if(event.code == 1006)
    reason = "The connection was closed abnormally, e.g., without sending or receiving a Close control frame";
  else if(event.code == 1007)
    reason = "An endpoint is terminating the connection because it has received data within a message that was not consistent with the type of the message (e.g., non-UTF-8 [http://tools.ietf.org/html/rfc3629] data within a text message).";
  else if(event.code == 1008)
    reason = "An endpoint is terminating the connection because it has received a message that \"violates its policy\". This reason is given either if there is no other sutible reason, or if there is a need to hide specific details about the policy.";
  else if(event.code == 1009)
    reason = "An endpoint is terminating the connection because it has received a message that is too big for it to process.";
  else if(event.code == 1010) // Note that this status code is not used by the server, because it can fail the WebSocket handshake instead.
    reason = "An endpoint (client) is terminating the connection because it has expected the server to negotiate one or more extension, but the server didn't return them in the response message of the WebSocket handshake. <br /> Specifically, the extensions that are needed are: " + event.reason;
  else if(event.code == 1011)
    reason = "A server is terminating the connection because it encountered an unexpected condition that prevented it from fulfilling the request.";
  else if(event.code == 1015)
    reason = "The connection was closed due to a failure to perform a TLS handshake (e.g., the server certificate can't be verified).";
  else
    reason = "Unknown reason";

  console.log("The connection was closed for reason: " + reason);
};


var setInstructions = function(texta, textb) 
{
  var element = document.getElementById("circletext");
  element.innerHTML = "";
  var instructions = SVG('circletext');
  instructions.size(1040,1040).center(525,525);
  var defs = instructions.defs();
  var topArcPath = "   M 1010, 525   a 485,485  0 1 0   -970,0 ";
  var bottomArcPath = "M   40, 525   a 485,485  0 1 0    970,0 ";
  var leftArcPath  = " M  525, 40    a 485,485  0 1 0    0,970 ";
  var rightArcPath = " M  525, 1010  a 485,485  0 1 0    0,-970 ";

  var topGroup = instructions.group();
  topGroup.path(topArcPath).fill("none");
  var topText = topGroup.text(texta).fill("#0f0");
  topText.path(topArcPath);

  var leftGroup = instructions.group();
  leftGroup.path(leftArcPath).fill("none");
  var leftText = leftGroup.text(textb).fill("#ff0");
  leftText.path(leftArcPath);

  var bottomGroup = instructions.group();
  bottomGroup.path(bottomArcPath).fill('none');
  var bottomText = bottomGroup.text(texta).fill("#0f0");
  bottomText.path(bottomArcPath);

  var rightGroup = instructions.group();
  rightGroup.path(rightArcPath).fill('none');
  var rightText = rightGroup.text(textb).fill("#ff0");
  rightText.path(rightArcPath);

};

var openCedula = function(featureKey)
{
 // console.log("opening cedula " + featureKey);
 document.getElementById(featureKey).style.display = "block";

 document.getElementById(featureKey + "_img").classList.add('open');
};

var closeCedula = function(featureKey)
{
 //console.log("closing cedula " + featureKey);
 document.getElementById(featureKey).style.display = "none";

 document.getElementById(featureKey + "_img").classList.remove('open');
};

var doZoom = function(newLayer)
{

  // could get optimized to not unload a feture we know we are about to load
  //console.log("doZoom " + newLayer);
  if (newLayer == lastZoom) return;
  if (newLayer < 0) newLayer = 0;
  if (newLayer >= Object.keys(zoomLayers).length) newLayer = Object.keys(zoomLayers).length - 1;
  currentZoom = newLayer;
  //console.log("leaving layer " + lastZoom + " at " + map.getCenter());
  if (lastZoom == -1)
  {
    // This can only happen when initializing
    nextFeatureSet = zoomLayers[newLayer];
    setInstructions(zoomLayers[newLayer]['spinInstruction'],zoomLayers[newLayer]['tiltInstruction']);
    for (featureKey in nextFeatureSet) 
    {
      if ( featureKey == 'pannable' || featureKey == 'mapZoom' ) continue;
      if (  nextFeatureSet[featureKey] == true)
      {
       // console.log("moving to " + hotspot[featureKey] + " and opening open cedula for layer " + featureKey + " in zoom layer " + lastZoom);
        //fly to hotspot[featureKey] and open the badge
        map.panTo(hotspot[featureKey].position);
        openCedula(featureKey);
      } 
      else
      {
        // load/enable the shapefeature 
        // strings indicate markers to turn on
        if ( typeof(nextFeatureSet[featureKey]) == "string" )
        {
          if (hotspot[nextFeatureSet[featureKey]])
          {
            //console.log("lighting hotspot " + featureKey);

            hotspot[nextFeatureSet[featureKey]].setMap(map);
          }
          //else console.log(nextFeatureSet[featureKey] + " has no marker ");
        }
        else
          // false indicates a region of interest 
        {

          if (features[featureKey])

          {
            features[featureKey]['mapdata'].setMap(map);
            features[featureKey]['mapdata'].setStyle(features[featureKey]['style']);
          }
          //else console.log(featureKey + " has no mapdata ");
        }
      }
    }
    map.setZoom(Math.min(maxZoom,Math.max(minZoom,zoomLayers[newLayer]['mapZoom'])));
    //lastZoom = map.getZoom();
    lastZoom = newLayer;
    //console.log("entered layer " + newLayer + " at " + map.getCenter());
    paintTarget();
    return;

  }  
  currentFeatureSet = zoomLayers[lastZoom];
  nextFeatureSet = zoomLayers[newLayer];
  for (featureKey in currentFeatureSet)
  {
    if ( featureKey == 'pannable' ||
      featureKey == 'mapZoom' || 
      featureKey == 'spinInstruction' || 
      featureKey == 'tiltInstruction' || 
      featureKey == 'hotspots'  
      ) continue;
    if ( currentFeatureSet[featureKey] == true && currentFeatureSet[featureKey] != nextFeatureSet[featureKey] )
      {
     // console.log("closing open cedula for layer " + featureKey + " in zoom layer " + lastZoom);
      //document.getElementById(featureKey).style.display = "none";
      closeCedula(featureKey)
    } 
    else
    {
      //unload the feature
      if ( typeof(currentFeatureSet[featureKey]) == "string"  && 
        ( (! nextFeatureSet['hotspots'] && currentFeatureSet[featureKey] == nextFeatureSet[featureKey]) ||
          ( currentFeatureSet[featureKey] != nextFeatureSet[featureKey])))
      {
        //console.log("closing open cedula for site " + featureKey + " at " + currentFeatureSet[featureKey] + " in zoom layer " + lastZoom);
        if (hotspot[currentFeatureSet[featureKey] ])
        {
          //console.log("killing hotspot " + featureKey);
          hotspot[currentFeatureSet[featureKey] ].setMap(null);
          closeCedula(currentFeatureSet[featureKey] )

        }

      }
      else
      {
        //map.data.remove(featureKey);
        if (features[featureKey])

        {              
          features[featureKey]['mapdata'].setMap(null);

        }
      }
    }
  }
  nextFeatureSet = zoomLayers[newLayer];
  setInstructions(zoomLayers[newLayer]['spinInstruction'],zoomLayers[newLayer]['tiltInstruction']);
  for (featureKey in nextFeatureSet) 
  {
    if ( featureKey == 'pannable' || 
      featureKey == 'mapZoom' || 
      featureKey == 'spinInstruction' || 
      featureKey == 'tiltInstruction' || 
      featureKey == 'hotspots'  ) continue;
    if (  nextFeatureSet[featureKey] == true && 
        currentFeatureSet[featureKey] != nextFeatureSet[featureKey])
    {
     // console.log("moving to " + hotspot[featureKey] + " and opening open cedula for layer " + featureKey + " in zoom layer " + newLayer);
      //fly to hotspot[featureKey] and open the badge
      map.panTo(hotspot[featureKey].position);
      openCedula(featureKey);
    } 
    else
    {
      // load/enable the shapefeature 
      // strings indicate markers to turn on
      if ( typeof(nextFeatureSet[featureKey]) == "string" )
      {
        if (hotspot[nextFeatureSet[featureKey]])
        {
          //console.log("lighting hotspot " + featureKey);

          hotspot[nextFeatureSet[featureKey]].setMap(map);
        }
        //else console.log(nextFeatureSet[featureKey] + " has no marker ");
      }
      else
        // false indicates a region of interest 
      {

        if (features[featureKey])

        {
          features[featureKey]['mapdata'].setMap(map);
          features[featureKey]['mapdata'].setStyle(features[featureKey]['style']);
        }
        //else console.log(featureKey + " has no mapdata ");
      }
    }

  }
  map.setZoom(Math.min(maxZoom,Math.max(minZoom,zoomLayers[newLayer]['mapZoom'])));
  //lastZoom = map.getZoom();
  lastZoom = newLayer;
  //console.log("entered layer " + newLayer + " at " + map.getCenter());
  paintTarget();

};


var startIdleTimer = function() 
{
  idleTimer = setTimeout(function(){
    window.location.reload(1);
  }, 10 * 60 * 1000);
};

var restartIdleTimer = function() 
{
  clearTimeout(idleTimer);
  startIdleTimer();
};

var shapeloaded = function(newfeatures)
{
  for (feature in newfeatures) 
  {
    if (!features.hasOwnProperty(newfeatures[feature].f.NOMGEO))
    {
      data1 = new google.maps.Data();
      data1.add(newfeatures[feature]);
      features[newfeatures[feature].f.NOMGEO] = { 
        'style' : 
        { 
          fillColor: 'magenta',
          strokeWeight: 1
        },
        'mapdata': data1,
      }
    } 
  }          
};

var initializemap = function() {
  if (map == null) {
    var mapOptions = {
      center: mexicoCenter,
      zoom : minZoom,
      disableDefaultUI: true,
      backgroundColor: '#000000',
      mapTypeId: google.maps.MapTypeId.HYBRID,
    };
    //mapTypeId: google.maps.MapTypeId.HYBRID,
    map = new google.maps.Map(document.getElementById('map-canvas'), mapOptions);
    //mapType = new google.maps.StyledMapType(mapStyle, styledMapOptions);
    //map.mapTypes.set('geoconnectable', mapType);
    //map.setMapTypeId('geoconnectable');
    map.data.setStyle({
      fillColor: 'yellow',
      strokeWeight: 1
    });
    featuresets = {} ;
    mexicoCenter = new google.maps.LatLng(23.43348438907877, -103.05326881250002);
    trapiche = new google.maps.LatLng(25.790466,-108.985886);
    
    for (latlon in hotspots)
    {
      var loc =  new google.maps.LatLng(hotspots[latlon][0],hotspots[latlon][1]);
      hotspot[latlon] = new google.maps.Marker({
        position: loc,
        title: latlon
      });
    }
    map.data.addListener('addfeature', function(e) {
      var name = e.feature.getProperty("NOMGEO");
      if (! name ) 
      {
        name = e.feature.getProperty("NAME_FAO");
        if (! name ) name = "idunno";
      }
      featuresets[name] = e.feature;

    });
    

    map.addListener('zoom_changed', function()
    {
      //console.log("got new zoom", map.getZoom(), zoomLayers[currentZoom]);
      //doZoom(map.getZoom());
      //map.data.forEach(function (feature) { map.data.remove(feature);});
    });
  //map.data.loadGeoJson('encuesta_intercensal_2015/shps/df/df_entidad.geojson', null, shapeloaded);
    //map.data.loadGeoJson('encuesta_intercensal_2015/shps/sin/sin_entidad.geojson');
    

    for ( feature in features)
    {
      data1 = new google.maps.Data();

      //console.log("loading " + feature);
      data1.loadGeoJson(features[feature]['geojson'], null, shapeloaded);
      features[feature]['mapdata'] = data1;
    }
    
    map.data.addListener('mouseover', function(event) {
      map.data.revertStyle();
      map.data.overrideStyle(event.feature, {strokeWeight: 8});
    });
    
    


    targetRectangle =  new google.maps.Rectangle();
    doZoom(0);

  }
};

var paintTarget = function()
{
  currView = map.getBounds();
  if (currView == undefined) return;
  currLeft = currView.getNorthEast().lng();
  currRight = currView.getSouthWest().lng();
  currTop = currView.getNorthEast().lat();
  currBottom = currView.getSouthWest().lat();
  currWidth = currLeft - currRight;
  currHeight = currTop - currBottom;
  currCenter = map.getCenter();
  hotBounds = new google.maps.LatLngBounds(
    {lat: currCenter.lat()-targetWidth*currHeight, lng: currCenter.lng()-targetWidth*currWidth},
    {lat: currCenter.lat()+targetWidth*currHeight, lng: currCenter.lng()+targetWidth*currWidth});

  var strokeOpacity = 0.0;
  var fillOpacity = 0.0;
  if (zoomLayers[currentZoom]['pannable'])
  {
    fillOpacity = 0.35;
    strokeOpacity = 0.8;
    targetColor = '#ff0000';
    for (featureKey  in currentFeatureSet)
    {
      if ( typeof(currentFeatureSet[featureKey]) == "string" )
      {
        if (hotspot[currentFeatureSet[featureKey]])
        {
          if (hotBounds.contains(hotspot[currentFeatureSet[featureKey]].position))
          {
            targetColor = '#00ff00';
            break;
          }
          
        }
      }
    }
  }

  targetRectangle.setOptions({
    strokeColor: targetColor,
    strokeOpacity: strokeOpacity,
    strokeWeight: 2,
    fillColor: targetColor,
    fillOpacity: fillOpacity,
    map: map,
    bounds: {
      north: currCenter.lat()+targetWidth*currHeight,
      south: currCenter.lat()-targetWidth*currHeight,
      west: currCenter.lng()-targetWidth*currWidth,
      east: currCenter.lng()+targetWidth*currWidth
    }
  });


};

var connectLocal = function() 
{
  ws = new WebSocket("ws://127.0.0.1:5678/");
  ws.onmessage = handleWebSocketMessage;
};

var connectPi = function() 
{
  ws = new WebSocket("ws://192.168.1.89:5678/");
  ws.onmessage = handleWebSocketMessage;
  
};

var disconnectWS = function()
{
  ws.close();
};

var zoomIn = function() 
{
  //doZoom(currentZoom + 1);
  var dummyEvent = { 'data' : '{"gesture":"zoom", "vector" : { "delta" : 20 }}'};
  handleWebSocketMessage(dummyEvent);
};

var zoomOut = function() 
{
  //doZoom(currentZoom - 1);
  var dummyEvent = { 'data' : '{"gesture":"zoom", "vector" : { "delta" : -20 }}'};
  handleWebSocketMessage(dummyEvent);
  
};

var handleWebSocketMessage = function (event) {
  if (! map) return;
  jsonData = JSON.parse(event.data);
    //var currentZoom = map.getZoom();
    currentFeatureSet = zoomLayers[lastZoom];
    if (jsonData.type == 'spin') {
      document.getElementById('EncoderID').innerHTML(jsonData.packet.sensorID);
      document.getElementById('EncoderIndex').innerHTML(jsonData.packet.encoderIndex);
      document.getElementById('EncoderDelta').innerHTML(jsonData.packet.encoderDelta);
      document.getElementById('EncoderElapsedTime').innerHTML(jsonData.packet.encoderElapsedTime);
      document.getElementById('EncoderPosition').innerHTML(jsonData.packet.encoderPosition);
    } else if (jsonData.type == 'tilt') {
      document.getElementById('TiltsensorID').innerHTML(jsonData.packet.sensorID);
      document.getElementById('TiltX').innerHTML(jsonData.packet.tiltX);
      document.getElementById('TiltY').innerHTML(jsonData.packet.tiltY);
      document.getElementById('TiltMagnitude').innerHTML(jsonData.packet.tiltMagnitude);
    } else if (jsonData.gesture == 'pan') {
    //var dampingZoom = map.getZoom()*minZoom/maxZoom;

    if (jsonData.vector.x == 0.0 && jsonData.vector.y == 0.0) return;  
    //console.log("sensor message: " + jsonData.type + "-" + jsonData.vector.x + "," +jsonData.vector.y);

    if (zoomLayers[currentZoom]['pannable']) map.panBy(panSensorSensitivity*jsonData.vector.x, panSensorSensitivity*jsonData.vector.y);
    paintTarget();
  } 
  else if (jsonData.gesture == 'zoom') 
  {

    currentSpinPosition += jsonData.vector.delta;
    //console.log(currentSpinPosition);
    //console.log("sensor message: " + jsonData.gesture + " " + jsonData.vector.delta + "; currentSpinPosition=" +currentSpinPosition);
    if (currentSpinPosition < 0) currentSpinPosition = 0;
    var proposedZoom =  Math.floor(currentSpinPosition/clicksPerZoomLevel);
    restartIdleTimer();

    if (proposedZoom != currentZoom) 
    {
      doZoom(Math.min(Object.keys(zoomLayers).length - 1, Math.max(0,proposedZoom))); 
    }
    else 
    {
      currView = map.getBounds();
      if (currView != undefined) 
      {
        currLeft = currView.getNorthEast().lng();
        currRight = currView.getSouthWest().lng();
        currTop = currView.getNorthEast().lat();
        currBottom = currView.getSouthWest().lat();
        currWidth = currLeft - currRight;
        currHeight = currTop - currBottom;
        currCenter = map.getCenter();
        hotBounds = new google.maps.LatLngBounds(
          {lat: currCenter.lat()-targetWidth*currHeight, lng: currCenter.lng()-targetWidth*currWidth},
          {lat: currCenter.lat()+targetWidth*currHeight, lng: currCenter.lng()+targetWidth*currWidth});
        var hotspotFound = false;
        for (featureKey  in currentFeatureSet)
        {
          if ( typeof(currentFeatureSet[featureKey]) == "string" )
          {
            if (currentFeatureSet['hotspots']  && hotspot[currentFeatureSet[featureKey]])
            {
              if (hotBounds.contains(hotspot[currentFeatureSet[featureKey]].position))
              {
                if ( ! hotspotFound )
                {
                  //console.log("zoomed in on " + currentFeatureSet[featureKey] + " in " + hotBounds );
                  openCedula(currentFeatureSet[featureKey]);
                  hotspotFound = true;
                }
                //else 
                  //console.log("would like to have zoomed in on " + currentFeatureSet[featureKey] + " in " + hotBounds );
                

              }
              else
              {
                //console.log("zoomed in on something else. Closing " + currentFeatureSet[featureKey] + " in " + hotBounds );
                closeCedula(currentFeatureSet[featureKey]);
              }
            }
          }
        } 
      }
    }


  } 
  else if (jsonData.gesture == 'combo') 
  {
    var dampingZoom = map.getZoom()*minZoom/maxZoom;

    if (jsonData.vector.x != 0.0 && jsonData.vector.y != 0.0) 
    {                
      map.panBy(100*jsonData.vector.x, 100*jsonData.vector.y);
      restartIdleTimer();
    }
    currentSpinPosition += jsonData.vector.delta;
    if (currentSpinPosition < 0) currentSpinPosition = 0;
    var proposedZoom = Math.floor(currentSpinPosition/clicksPerZoomLevel);
    if (proposedZoom != currentZoom) 
    {
      doZoom(proposedZoom);
      restartIdleTimer();
    }


  } else { 
    messages = document.getElementsByTagName('ul')[0];
    var message = document.createElement('li');
    var content = document.createTextNode(event.data);
    message.appendChild(content);
    messages.appendChild(message);
  }
};
launchWebSocket();

startIdleTimer();

