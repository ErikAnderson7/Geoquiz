// Stores information used to send messages to the websocket
// Also has a field hasGuessed used to control displaying other user's guesses
class MultiplayerGame {
    constructor(username, room) {
        this.username = username;
        this.room = room;
        this.hasGuessed = false;
    }

    get room() {
        return this._room;
    }

    set room(room) {
        this._room = room;
    }

    get username() {
        return this._username;
    }

    set username(username) {
        this._username = username;
    }

    get hasGuessed() {
        return this._hasGuessed;
    }
    
    set hasGuessed(guessed) {
        this._hasGuessed = guessed;
    }
}

// Called when user clicks a country on the map
// Emits guess event to the server
function checkAnswer(cid, gcountry) {
    if(!Game.hasGuessed) {
        var answer = {guess: cid, country: gcountry, room: Game.room, username: Game.username};
        Game.hasGuessed = true;
        socket.emit('guess', answer);
    }
}

// Clears the map by removing the color fills from user guesses
function resetMap() {
    var countries = document.getElementsByClassName("country");
    for(var i = 0; i < countries.length; i++) {
        countries[i].style['fill'] = null;
    }
}

// Toggles showing the leaderboard to the user
function toggleLeaderboard() {
    var popup = document.getElementById("leaderboard-popup");
    var button = document.getElementById("leaderboard-button");
    if(popup.classList.toggle("show")) {
        button.value = "Hide Leaderboard";
    }
    else {
        button.value = "Show Leaderboard"
    }    
    
}  

// Fills the countries that the users have guessed with their selected color if the user has submitted their own guess
function displayGuesses(user_guesses, users) {
    if(Game.hasGuessed) {
        for(var user in user_guesses) {
            var guess = user_guesses[user];
            if(user == Game.username){
                usersGuess(users[user]);
            }
            var correct = guess.Correct;
            if(correct == "True"){
                var country = "country" + String(guess.GuessID);
                document.getElementById(country).style['fill'] = "green";
            }
            else {
                var incorrect_country = "country" + String(guess.GuessID);
                var correct_country = "country" + String(guess.CorrectID);
                document.getElementById(incorrect_country).style['fill'] = users[user]['color'];              
                document.getElementById(correct_country).style['fill'] = "green";
            }
        }
    }
}

// Updates the user's score in the bottom bar
function usersGuess(user) {
    document.getElementById("guess-correct-count").innerHTML = user.correctGuesses;
    document.getElementById("guess-total-count").innerHTML = user.totalGuesses;
}

// Updates the leaderboard
function updateLeaderboard(users) {
    var sorted_users = sortByAverageDistance(users);
    var leaderboard = document.getElementById("leaderboard-popup")
    leaderboard.innerHTML = "";
    for(var i in sorted_users) {
        var username = sorted_users[i][0];
        var score = sorted_users[i][1];
        var rank = parseInt(i) + 1;
        var color = users[username]['color'];
        leaderboard.innerHTML += '<h3 style="color:' + color + '">' + String(rank) + ": " + username + "</h3>"; 
        leaderboard.innerHTML += "Correct Guesses: " + String(score.correctGuesses) + " out of " + String(score.totalGuesses);
        leaderboard.innerHTML += "<br>Average Distance: " + String(parseInt(score.averageDistance)) + " Km<br>";
    }
    leaderboard.innerHTML += "<br>";
}

// Used in updateLeaderboard to rank users by the average distance of their guesses
function sortByAverageDistance(users) {
    var u = Object.keys(users).map(function(key) {
        return [key, users[key]];
    });
    var sorted_users = u.sort(function(x, y) {
        return x[1]['averageDistance'] - y[1]['averageDistance'];
    });
    return sorted_users;
}