var socket = io();

socket.on('connect', function() {
    socket.emit('connected', {data: 'I\'m connected!'});
});

socket.on('message', function(message) {
    console.log(message)
});

socket.on('question', function(question) {
    console.log(question.Country);
    document.getElementById("prompt-country").innerHTML = question.Country; 
});

socket.on('answer-response', function(answer) {
    console.log(answer);
    var correct = answer.Correct;
    if(correct == "True"){
        console.log("Correct!");
        showPopup("Correct!")
        GS.incCorrect();
        GS.incTotal();
        var country = "country" + String(answer.GuessID);
        console.log(country);
        document.getElementById(country).style['fill'] = "green";
    }
    else {
        showPopup("Incorrect\nYour Guess: " + answer.Guess + "\nDistance: " + String(answer.Distance) + " Km")
        GS.incTotal();
        var incorrect_country = "country" + String(answer.GuessID);
        var correct_country = "country" + String(answer.CorrectID);
        document.getElementById(incorrect_country).style['fill'] = "red";
        document.getElementById(correct_country).style['fill'] = "green";
    }
    document.getElementById("guess-correct-count").innerHTML = GS.correctGuesses;
    document.getElementById("guess-total-count").innerHTML = GS.totalGuesses;

    var questionButton = document.getElementById("reset-button");
    questionButton.disabled = false;
});