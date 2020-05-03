// DEFINE VARIABLES
// Define size of map group
// Full world map is 2:1 ratio
// Using 12:5 because we will crop top and bottom of map
w = 3000;
h = 1250;
// variables for catching min and max zoom factors
var minZoom;
var maxZoom;

// DEFINE FUNCTIONS/OBJECTS
// Define map projection
var projection = d3
  .geoEquirectangular()
  .center([0, 15]) // set centre to further North as we are cropping more off bottom of map
  .scale([w / (2 * Math.PI)]) // scale to fit group width
  .translate([w / 2, h / 2]) // ensure centred in group
;

// Define map path
var path = d3
  .geoPath()
  .projection(projection)
;

// Create function to apply zoom to countriesGroup
function zoomed() {
  t = d3
    .event
    .transform
  ;
  countriesGroup
    .attr("transform","translate(" + [t.x, t.y] + ")scale(" + t.k + ")")
  ;
}

// Define map zoom behaviour
var zoom = d3
  .zoom()
  .on("zoom", zoomed);

function getTextBox(selection) {
  selection.each(function(d) {
    d.bbox = this.getBBox();
  });
}

// Function that calculates zoom/pan limits and sets zoom to default value 
function initiateZoom() {
  // Define a "minzoom" whereby the "Countries" is as small possible without leaving white space at top/bottom or sides
  minZoom = Math.max($("#map-holder").width() / w, $("#map-holder").height() / h);
  // set max zoom to a suitable factor of this value
  maxZoom = 20 * minZoom;
  // set extent of zoom to chosen values
  // set translate extent so that panning can't cause map to move out of viewport
  zoom
    .scaleExtent([minZoom, maxZoom])
    .translateExtent([[0, 0], [w, h]])
  ;
  // define X and Y offset for centre of map to be shown in centre of holder
  midX = ($("#map-holder").width() - minZoom * w) / 2;
  midY = ($("#map-holder").height() - minZoom * h) / 2;
  // change zoom transform to min zoom and centre offsets

  d3.select("#map-svg").call(zoom.transform, d3.zoomIdentity.translate(midX, midY).scale(minZoom));
}

// on window resize
$(window).resize(function() {
  // Resize SVG
  d3.select("#map-svg").attr("width", $("#map-holder").width())
     .attr("height", $("#map-holder").height());
  initiateZoom();
});

// Draw Game Map
// Does not display elements such as name of the county
function drawGameMap() {
  $("#map-holder").empty(); // Clear the map contents.

  var svg = d3
    .select("#map-holder")
    .append("svg")
    .attr("id", "map-svg")
    .attr("class", "map-svg")
    .attr("width", $("#map-holder").width())
    .attr("height", $("#map-holder").height())
    .call(zoom);

  d3.json(
    "/game/getGameMap", function(response) {
      json = JSON.parse(response); 
      countriesGroup = svg.append("g").attr("id", "game-map");
      // add a background rectangle
      countriesGroup
        .append("rect")
        .attr("x", 0)
        .attr("y", 0)
        .attr("width", 3000)
        .attr("height", 1500);
      // draw a path for each feature/country
      countries = countriesGroup
        .selectAll("path")
        .data(json.features)
        .enter()
        .append("path")
        .attr("d", path)
        .attr("id", function(d, i) {
          return "country" + d.properties.id;
        })
        .attr("class", "country")
        .on("click", function(d, i) {
          var country = document.getElementById("prompt-country").innerHTML;
          checkAnswer(i, country);
        });
      initiateZoom("#map-holder");
    }
  );
}

function drawCountry(i) {
  var url = location.href + "/game/getCountryMap?i=" + i;
  d3.json(
    url, function(json) {
      json = JSON.parse(json);
      countriesGroup = svg.append("g").attr("id", "map");
      // add a background rectangle
      countriesGroup
        .append("rect")
        .attr("x", 0)
        .attr("y", 0)
        .attr("width", 3000)
        .attr("height", 1500);
      // draw a path for each feature/country
      countries = countriesGroup
        .selectAll("path")
        .data(json.features)
        .enter()
        .append("path")
        .attr("d", path)
        .attr("id", function(d, i) {
          return "country" + d.properties.id;
        })
        .attr("class", "country")
        .on("click", function(d, i) {console.log(d)});
      initiateZoom();
    }
  );

  initiateZoom();
}

drawGameMap();