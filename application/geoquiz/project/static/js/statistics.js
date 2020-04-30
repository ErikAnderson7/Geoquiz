// Event listener for when the radio button value is changed between country and global stats
$("input[name=stat-type]:radio").change(function () {
    var globalstats = document.getElementById("global");
    if(globalstats.checked) {
        document.getElementById("stat-type-selector").style.height = "10%";
        document.getElementById("stats").style.height = "85%";
        document.getElementById("country-picker-label").style.display = "none";
        document.getElementById("country-picker").style.display = "none";
    }

    var countrystats = document.getElementById("country");
    if(countrystats.checked) {
        document.getElementById("stat-type-selector").style.height = "20%";
        document.getElementById("stats").style.height = "75%";
        document.getElementById("country-picker-label").style.display = "block";
        document.getElementById("country-picker").style.display = "block";
    }

    updateStats();
});

// Event listener for when the selected country changes
$("#country-picker").change(function() {
    updateStats()
})

// Displays the selected map and displays stats in the sidebar
function updateStats() {
    var globalstats = document.getElementById("global");
    if(globalstats.checked) {
        drawGlobalStatsMap();
        globalSidebarStats();
    }

    var countrystats = document.getElementById("country");
    if(countrystats.checked) {
        var country = document.getElementById("country-picker").value;
        drawStatsMap(country);
        perCountrySiderbarStats(country);        
    }
}

// Gets the global stats and displays them in the side bar
function globalSidebarStats() {
    var url = "/stats/globalStats";
    document.getElementById("stats").innerHTML = "";

    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if(this.readyState == 4 && this.status == 200){
            var response = JSON.parse(this.response);
            document.getElementById("stats").innerHTML = globalStatsHTML(response); 
        }
    }
    xhttp.open("GET", url, true);
    xhttp.send();
}

// Gets the stats for the requested country and displays them in the side bar
function perCountrySiderbarStats(country) {
    var url = `/stats/whenCorrect?country=${country}`;
    document.getElementById("stats").innerHTML = "";

    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if(this.readyState == 4 && this.status == 200){
            var response = JSON.parse(this.response);
            document.getElementById("stats").innerHTML = perCountryStatsHTML(response); 
        }
    }
    xhttp.open("GET", url, true);
    xhttp.send();
}

// Parses the JSON request and creates the HTML to be displayed in the sidebar
function perCountryStatsHTML(data) {
    var html = `<h3 class="stat-line">Guessed Correctly ${data.timesGuessedCorrectly} times out of ${data.totalGuesses} guesses</h3>`;
    html += `<h3 class="stat-line"> Percent Guessed Correctly: ${(data.percentGuessedCorrectly*100).toFixed(2)}%</h3>`;
    html += `<h3 class="stat-line"> Average Guess Distance: ${data.averageDistance} Km</h3>`;
    if(data.mostCommonlyConfused != null) {
        html += `<h3 class="stat-line"> Most Commonly Guessed Countries:</h3>`;
        Object.keys(data.mostCommonlyConfused).forEach(function(key) {
            html += `<h3 class="stat-line">${key}: ${data.mostCommonlyConfused[key].name}<br>`;
            html += `Percent of Guesses: ${(data.mostCommonlyConfused[key].percentage*100).toFixed(2)}%<br>`;
            html += `Times Guessed: ${data.mostCommonlyConfused[key].times}<br>`;
            html += `Distance: ${data.mostCommonlyConfused[key].distance} Km</h3>`;
        });
    }

    return html;
}

function globalStatsHTML(data) {
    var html = `<h3 class="stat-line">${data.totalCorrectGuesses} Correct Guesses out of ${data.totalGuesses} Total Guesses</h3>`;
    html += `<h3 class="stat-line"> Percent Guessed Correctly: ${(data.percentGuessedCorrectly*100).toFixed(2)}%</h3>`;
    html += `<h3 class="stat-line"> Average Guess Distance: ${data.averageDistance} Km</h3>`;
    if(data.mostCommonlyGuessedCorrectly != null) {
        html += `<h3 class="stat-line"> Most Commonly Guessed Correctly Countries:</h3>`;
        Object.keys(data.mostCommonlyGuessedCorrectly).forEach(function(key) {
            html += `<h3 class="stat-line">${key}: ${data.mostCommonlyGuessedCorrectly[key].name}<br>`;
            html += `${(data.mostCommonlyGuessedCorrectly[key].percentage*100).toFixed(2)}% Guessed Correctly<br>`;
            html += `${data.mostCommonlyGuessedCorrectly[key].times}/${data.mostCommonlyGuessedCorrectly[key].total} Correct Guesses</h3>`;
        });
    }

    return html;
}

// Calculates the fill color for a country depending on the percentage
// Less guessed countries will be greenish in color and highly guessed in blue
function getColor(percentage) {
    // #feeb65 
    var startRed = 254.0;
    var startGreen = 235.0;
    var startBlue = 101.0;

    // #1a237e 
    var endRed = 26.0;
    var endGreen = 35.0;
    var endBlue = 126.0;

    var diffRed = endRed - startRed;
    var diffGreen = endGreen - startGreen;
    var diffBlue = endBlue - startBlue;

    var r = (diffRed * percentage) + startRed;
    var g = (diffGreen * percentage) + startGreen;
    var b = (diffBlue * percentage) + startBlue;

    var colorString = `rgb(${r}, ${g}, ${b})`;
    return(colorString);
}

// When stats page is opened start with global stats
drawGlobalStatsMap();
globalSidebarStats();