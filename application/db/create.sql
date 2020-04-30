CREATE DATABASE geoquiz;

/* Connect to the geoquiz database */
\connect geoquiz;

/* Create the guesses table inside the geoquiz database */
CREATE TABLE guesses (
    GuessID serial PRIMARY KEY,
    CorrectCountry INT,
    GuessCountry INT
);