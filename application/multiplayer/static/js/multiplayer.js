var socket = io();

var Game;

function joinRoom() {
    user = document.getElementById("username").value;
    roomID = document.getElementById("room").value;
    var join_message = {username: user, room: roomID};
    Game = new MultiplayerGame(user, roomID);
    console.log(join_message);
    socket.emit('join', join_message)
    HideJoinRoom();
}

function HideJoinRoom(){
    document.getElementById('join-room').style.display="none"; 
}

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
        Game.incCorrect();
        Game.incTotal();
        var country = "country" + String(answer.GuessID);
        console.log(country);
        document.getElementById(country).style['fill'] = "green";
    }
    else {
        showPopup("Incorrect\nYour Guess: " + answer.Guess + "\nDistance: " + String(answer.Distance) + " Km")
        Game.incTotal();
        var incorrect_country = "country" + String(answer.GuessID);
        var correct_country = "country" + String(answer.CorrectID);
        document.getElementById(incorrect_country).style['fill'] = "red";
        document.getElementById(correct_country).style['fill'] = "green";
    }
    document.getElementById("guess-correct-count").innerHTML = Game.correctGuesses;
    document.getElementById("guess-total-count").innerHTML = Game.totalGuesses;

    var questionButton = document.getElementById("reset-button");
    questionButton.disabled = false;
});

socket.on('user-joined', function(message) {
    console.log(message);
});

/* when a user joins setup all the stuff that needs to be set up
    currently just sets the question */
socket.on('joined', function(message) {
    console.log(message);
    document.getElementById("prompt-country").innerHTML = message.game.question.Country; 
});