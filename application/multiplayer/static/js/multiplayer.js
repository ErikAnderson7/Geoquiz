var socket = io();

var Game;

// Handles users joining a game, checks for blank field values
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
    if(c === "") {
        setJoinError("Please choose a color");
        return;
    }
    var join_message = {username: user, room: roomID, color: c};
    Game = new MultiplayerGame(user, roomID);
    socket.emit('join', join_message)
}

// Hides the join room box when the user successfully joins a room
function HideJoinRoom(){
    document.getElementById('join-room').style.display="none"; 
}

// If there is an error during joining a room display the error message
function setJoinError(error) {
    var errorMessage = document.getElementById("join-error-message");
    errorMessage.innerHTML = error;
    errorMessage.style.display = "block";
}

// Updates the question field and clears the map when a new question has been sent
socket.on('new-question', function(game) {
    Game.hasGuessed = false;
    resetMap();
    document.getElementById("prompt-country").innerHTML = game.game.question.Country; 
});

// When a user has submitted a guess update the leaderboard and display the guess
socket.on('answer-response', function(game) {
    var guesses = game.game.question.guesses;
    var users = game.game.users;
    updateLeaderboard(users);
    displayGuesses(guesses, users);
});

// When a user has successfully joined the game update the leaderboard to add the new user to the leaderboard
// Also hides the join room box
socket.on('joined', function(message) {
    document.getElementById("prompt-country").innerHTML = message.game.question.Country; 
    updateLeaderboard(message.game.users);
    HideJoinRoom();
});

// When an error occurs during joining a game show the error message
socket.on('join-error', function(error) {
    setJoinError(error);    
});

// When a user has disconnected remove them from the leaderboard
socket.on('user-disconnected', function(message) {
    updateLeaderboard(message.game.users);
});