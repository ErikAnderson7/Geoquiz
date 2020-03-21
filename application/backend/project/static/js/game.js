class GameScore {
    constructor(cg, tg) {
        this.correctGuesses = cg;
        this.totalGuesses = tg;
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
}

const GS = new GameScore(0, 0);

function getQuestion() {
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if(this.readyState == 4 && this.status == 200){
            console.log(this.response);
            var question = JSON.parse(this.response);
            console.log(question.Country);
            document.getElementById("prompt-country").innerHTML = question.Country; 
        }
    }
    xhttp.open("GET", "/game/getQuestion", true);
    xhttp.send();
}

function checkAnswer(cid, country) {
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function(i) {
        if(this.readyState == 4 && this.status == 200){
            console.log(this.response);
            var answer = JSON.parse(this.response);
            var correct = answer.Correct;
            if(correct == "True"){
                console.log("Correct");
                GS.incCorrect();
                GS.incTotal();
                var country = "country" + String(cid);
                console.log(country);
                document.getElementById(country).style['fill'] = "green";
            }
            else {
                console.log("Incorrect");
                GS.incTotal();
                var incorrect_country = "country" + String(cid);
                var correct_country = "country" + String(answer.CorrectID);
                document.getElementById(incorrect_country).style['fill'] = "red";
                document.getElementById(correct_country).style['fill'] = "green";
            }
            document.getElementById("prompt-correct-count").innerHTML = GS.correctGuesses;
            document.getElementById("prompt-total-count").innerHTML = GS.totalGuesses;
        }
    }
    var url = "/game/checkAnswer?guess=" + cid + "&country=" + country;
    console.log(url);
    xhttp.open("GET", url, true);
    xhttp.send();
}

function resetAndGetNextQuestion() {
    var countries = document.getElementsByClassName("country");
    for(var i = 0; i < countries.length; i++) {
        countries[i].style['fill'] = "#1b262c";
    }

    getQuestion();
}

getQuestion();