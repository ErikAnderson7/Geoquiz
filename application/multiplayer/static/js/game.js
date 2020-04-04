class MultiplayerGame {
    constructor(username, room) {
        this.username = username;
        this.room = room;
        this.correctGuesses = 0;
        this.totalGuesses = 0;
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
}

function getQuestion() {
    var questionButton = document.getElementById("reset-button");
    questionButton.disabled = true;

    socket.emit('get-question', {data: 'I Would like a question please'});
}

function checkAnswer(cid, gcountry) {
    console.log("Guessing Country: " + String(cid));
    var answer = {guess: cid, country: gcountry, room: Game.room, username: Game.username};
    console.log(answer);
    socket.emit('check-answer', answer);
}

function resetAndGetNextQuestion() {
    var countries = document.getElementsByClassName("country");
    for(var i = 0; i < countries.length; i++) {
        countries[i].style['fill'] = null;
    }

    hidePopup();

    getQuestion();
}

function showPopup(text) {
    var popup = document.getElementById("myPopup");
    popup.classList.toggle("show");
    popup.innerText = text;
}  

function hidePopup() {
    var popup = document.getElementById("myPopup");
    popup.classList.toggle("show");
    popup.innerText = "";
}