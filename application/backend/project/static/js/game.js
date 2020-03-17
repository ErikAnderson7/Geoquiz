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
                var country = "country" + String(cid);
                console.log(country);
                document.getElementById(country).style['fill'] = "green";
            }
            else {
                console.log("Incorrect");
                var incorrect_country = "country" + String(cid);
                var correct_country = "country" + String(answer.CorrectID);
                document.getElementById(incorrect_country).style['fill'] = "red";
                document.getElementById(correct_country).style['fill'] = "green";
            }
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