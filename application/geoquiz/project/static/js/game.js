// Class that keeps track of the user's score
class GameScore {
    constructor(cg, tg, c) {
        this.correctGuesses = cg;
        this.totalGuesses = tg;
        this.hasGuessed = false;
        this.continent = c;
    }

    get correctGuesses() {
        return this._correctGuesses;
    }

    set correctGuesses(g) {
        this._correctGuesses = g;
    }

    get totalGuesses() {
        return this._totalGuesses;
    }

    set totalGuesses(g) {
        this._totalGuesses = g;
    }

    incCorrect() {
        this._correctGuesses++;
    }

    incTotal() {
        this._totalGuesses++;
    }

    get hasGuessed() {
        return this._hasGuessed;
    }
    
    set hasGuessed(guessed) {
        this._hasGuessed = guessed;
    }

    get continent() {
        return this._continent;
    }
    
    set continent(c) {
        this._continent = c;
    }
}

// Issues a HTTP request to the backend to get a new question.
// Updates the country prompt
function getQuestion(continent) {
    GS.hasGuessed = false;
    var questionButton = document.getElementById("reset-button");
    questionButton.disabled = true;

    var url = "/game/getQuestion";
    if(GS.continent !== 'World') {
        url += "?continent=" + String(GS.continent);
    }

    console.log(url);

    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if(this.readyState == 4 && this.status == 200){
            var question = JSON.parse(this.response);
            document.getElementById("prompt-country").innerHTML = question.Country; 
        }
    }
    xhttp.open("GET", url, true);
    xhttp.send();
}

// Called when a user clicks on a country
// Issues a HTTP request to check the answer using the prompt country and the id of the country they clicked on
function checkAnswer(cid, country) {
    if(!GS.hasGuessed) {
        var xhttp = new XMLHttpRequest();
        xhttp.onreadystatechange = function(i) {
            if(this.readyState == 4 && this.status == 200){
                var answer = JSON.parse(this.response);
                var correct = answer.Correct;
                if(correct == "True"){
                    showPopup("Correct!")
                    GS.incCorrect();
                    GS.incTotal();
                    var country = "country" + String(cid);
                    document.getElementById(country).style['fill'] = "green";
                }
                else {
                    showPopup("Incorrect\nYour Guess: " + answer.Guess + "\nDistance: " + String(answer.Distance) + " Km")
                    GS.incTotal();
                    var incorrect_country = "country" + String(cid);
                    var correct_country = "country" + String(answer.CorrectID);
                    document.getElementById(incorrect_country).style['fill'] = "red";
                    document.getElementById(correct_country).style['fill'] = "green";
                }
                document.getElementById("guess-correct-count").innerHTML = GS.correctGuesses;
                document.getElementById("guess-total-count").innerHTML = GS.totalGuesses;
            }

            var questionButton = document.getElementById("reset-button");
            questionButton.disabled = false;
        }
        var url = "/game/checkAnswer?guess=" + cid + "&country=" + country;
        xhttp.open("GET", url, true);
        xhttp.send();
        GS.hasGuessed = true;
    }
}

// Removes the green/red fill from the countries
// Hides the popup telling the user their result and gets a new question
function resetAndGetNextQuestion() {
    var countries = document.getElementsByClassName("country");
    for(var i = 0; i < countries.length; i++) {
        countries[i].style['fill'] = null;
    }

    hidePopup();

    getQuestion();
}

// Shows the popup telling the user the result of their guess
function showPopup(text) {
    var popup = document.getElementById("myPopup");
    popup.classList.toggle("show");
    popup.innerText = text;
}  

// Hides the popup
function hidePopup() {
    var popup = document.getElementById("myPopup");
    popup.classList.toggle("show");
    popup.innerText = "";
}

function setupGame(continent) {
    GS = new GameScore(0, 0, continent);
    drawGameMap();
    getQuestion();
}

// When the document loads draw the game map and get a question
var GS;
setupGame('World'); // Initialize game with no continent specified