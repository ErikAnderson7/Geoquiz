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
});