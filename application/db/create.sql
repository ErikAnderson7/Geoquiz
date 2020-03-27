CREATE DATABASE geoquiz;

\connect geoquiz;

CREATE TABLE guesses (
    GuessID serial PRIMARY KEY,
    CorrectCountry INT,
    GuessCountry INT
);