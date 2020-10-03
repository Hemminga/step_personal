-- This file will create a blank database

CREATE TABLE IF NOT EXISTS event(
    id PRIMARY KEY AUTOINCREMENT,
    eventid INTEGER UNIQUE,
    level TEXT,
    start TEXT,
    score TEXT,
    format TEXT,
    boards TEXT
);

CREATE TABLE IF NOT EXISTS pairs(
    id PRIMARY KEY AUTOINCREMENT,
    player1 INTEGER,
    player2 INTEGER,
    FOREIGN KEY (player1) REFERENCES player(id),
    FOREIGN KEY (player2) REFERENCES player(id)
);

CREATE TABLE IF NOT EXISTS player(
    id PRIMARY KEY AUTOINCREMENT,
    name TEXT
);

CREATE TABLE standings(
    id PRIMARY KEY AUTOINCREMENT,
    pair INTEGER,
    rank INTEGER,
    score TEXT,
    FOREIGN KEY (pair) REFERENCES pairs(id)
)