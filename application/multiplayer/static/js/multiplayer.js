var socket = io();

var Game;

function joinRoom() {
    var user = document.getElementById("username").value;
    if(user === "") {
        setJoinError("Please choose a username");
        return;
    }
    var roomID = document.getElementById("room").value;
    if(roomID === "") {
        setJoinError("Please enter a room");
        return;
    }
    var c = document.getElementById("color").value;
    console.log(c);
    if(c === "") {
        setJoinError("Please choose a color");
        return;
    }
    var join_message = {username: user, room: roomID, color: c};
    Game = new MultiplayerGame(user, roomID);
    console.log(join_message);
    socket.emit('join', join_message)
}

function HideJoinRoom(){
    document.getElementById('join-room').style.display="none"; 
}

function setJoinError(error) {
    var errorMessage = document.getElementById("join-error-message");
    errorMessage.innerHTML = error;
    errorMessage.style.display = "block";
}

socket.on('connect', function() {
    socket.emit('connected', {data: 'I\'m connected!'});
});

socket.on('message', function(message) {
    console.log(message)
});

socket.on('new-question', function(game) {
    Game.hasGuessed = false;
    resetMap();
    document.getElementById("prompt-country").innerHTML = game.game.question.Country; 
});

socket.on('answer-response', function(game) {
    var guesses = game.game.question.guesses;
    var users = game.game.users;
    updateLeaderboard(users);
    displayGuesses(guesses, users);
});

socket.on('joined', function(message) {
    document.getElementById("prompt-country").innerHTML = message.game.question.Country; 
    updateLeaderboard(message.game.users);
    HideJoinRoom();
});

socket.on('join-error', function(error) {
    setJoinError(error);    
});