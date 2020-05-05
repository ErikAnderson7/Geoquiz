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
    .transform;
  countriesGroup
    .attr("transform","translate(" + [t.x, t.y] + ")scale(" + t.k + ")");
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

// Draws percountry stats map 
// Colors each country depending on the percentage of all guesses each country was guessed for a given country
function drawStatsMap(country) {
  $("#map-holder").empty(); // Clear the map contents.
  
  var svg = d3
    .select("#map-holder")
    .append("svg")
    .attr("id", "map-svg")
    .attr("class", "map-svg")
    .attr("width", $("#map-holder").width())
    .attr("height", $("#map-holder").height())
    .call(zoom);

  d3.json(`/stats/perCountryMap?country=${country}`, function(response) {
      json = JSON.parse(response);
      countriesGroup = svg.append("g").attr("id", "stats-map");
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
        .attr("style", function(d) {
          var color = getColor(d.properties.percentOfGuesses);
          var style = `fill:${color};`;
          if(d.properties.name === country) {
            style += 'stroke:green;stroke-width:6;';
          }
          return style;
        })
        .on("mouseover", function(d, i) {
          d3.select("#countryLabel" + d.properties.id).style("display", "block");
        })
        .on("mouseout", function(d, i) {
          d3.select("#countryLabel" + d.properties.id).style("display", "none");
        });
      countryLabels = countriesGroup
        .selectAll("g")
        .data(json.features)
        .enter()
        .append("g")
        .attr("class", "countryLabel")
        .attr("id", function(d) {
            return "countryLabel" + d.properties.id;
        })
        .attr("transform", function(d) {
            return (
              "translate(" + path.centroid(d)[0] + "," + path.centroid(d)[1] + ")"
            );
        })
        // add mouseover functionality to the label
        .on("mouseover", function(d, i) {
            d3.select(this).style("display", "block");
        })
        .on("mouseout", function(d, i) {
            d3.select(this).style("display", "none");
        });
      // add the text to the label group showing country name
      countryLabels
        .append("text")
        .attr("class", "countryName")
        .style("text-anchor", "middle")
        .attr("dx", 0)
        .attr("dy", 0)
        .attr("font-size", "20")
        .html(function(d) {
          var text = `<tspan x="0" dy=".6em">${d.properties.name}</tspan>
                      <tspan x="0" dy="1.2em">Distance: ${String(parseInt(d.properties.distance))} Km</tspan>
                      <tspan x="0" dy="1.2em">Times Guessed: ${d.properties.count}</tspan>
                      <tspan x="0" dy="1.2em">Percent of Guesses: ${(d.properties.percentOfGuesses*100).toFixed(2)}%</tspan>`;
          return text;
        })
        .call(getTextBox);
      // add a background rectangle the same size as the text
      countryLabels
        .insert("rect", "text")
        .attr("class", "countryLabelBg")
        .attr("rx", "10")
        .attr("ry", "10")
        .attr("transform", function(d) {
          return "translate(" + (d.bbox.x - 20) + "," + (d.bbox.y - 10) + ")";
        })
        .attr("width", function(d) {
          return 280;
        })
        .attr("height", function(d) {
          return 120;
        });
      initiateZoom();
    }
  );
}

// Draws the global stats map
// Colors each country depending on what percentage of guesses for that country were correct
function drawGlobalStatsMap() {
  $("#map-holder").empty(); // Clear the map contents.
  
  var svg = d3
    .select("#map-holder")
    .append("svg")
    .attr("id", "map-svg")
    .attr("class", "map-svg")
    .attr("width", $("#map-holder").width())
    .attr("height", $("#map-holder").height())
    .call(zoom);

  d3.json("/stats/globalMap", function(response) {
      json = JSON.parse(response); 
      countriesGroup = svg.append("g").attr("id", "stats-map");
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
        .attr("style", function(d) {
          var color = getColor(d.properties.percentCorrect);
          return `fill:${color}`;
        })
        .on("mouseover", function(d, i) {
          d3.select("#countryLabel" + d.properties.id).style("display", "block");
        })
        .on("mouseout", function(d, i) {
          d3.select("#countryLabel" + d.properties.id).style("display", "none");
        });
      countryLabels = countriesGroup
        .selectAll("g")
        .data(json.features)
        .enter()
        .append("g")
        .attr("class", "countryLabel")
        .attr("id", function(d) {
            return "countryLabel" + d.properties.id;
        })
        .attr("transform", function(d) {
            return (
              "translate(" + path.centroid(d)[0] + "," + path.centroid(d)[1] + ")"
            );
        })
        // add mouseover functionality to the label
        .on("mouseover", function(d, i) {
            d3.select(this).style("display", "block");
        })
        .on("mouseout", function(d, i) {
            d3.select(this).style("display", "none");
        });
      // add the text to the label group showing country name
      countryLabels
        .append("text")
        .attr("class", "countryName")
        .style("text-anchor", "middle")
        .attr("dx", 0)
        .attr("dy", 0)
        .attr("font-size", "20")
        .html(function(d) {
          var text = `<tspan x="0" dy=".6em">${d.properties.name}</tspan>
                      <tspan x="0" dy="1.2em">${d.properties.correctCount} Correct Guesses</tspan>
                      <tspan x="0" dy="1.2em">${d.properties.totalCount} Total Attempts</tspan>
                      <tspan x="0" dy="1.2em">Correct Guesses: ${(d.properties.percentCorrect*100).toFixed(2)}%</tspan>`;
          return text;
        })
        .call(getTextBox);
      // add a background rectangle the same size as the text
      countryLabels
        .insert("rect", "text")
        .attr("class", "countryLabelBg")
        .attr("rx", "10")
        .attr("ry", "10")
        .attr("transform", function(d) {
          return "translate(" + (d.bbox.x - 25) + "," + (d.bbox.y - 10) + ")";
        })
        .attr("width", function(d) {
          return 280;
        })
        .attr("height", function(d) {
          return 120;
        });
      initiateZoom();
    }
  );
}

function drawCountry(i) {
  var url = "/game/getCountryMap?country=" + i;
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