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

-- @TODO This needs a rethink. Later I'm referencing players by id
-- but I do need to get to a player as part of of a specific pair
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
);

CREATE TABLE IF NOT EXISTS board(
    id PRIMARY KEY AUTOINCREMENT,
    number INTEGER,
    dealer TEXT,
    vulnerable, TEXT
);

CREATE TABLE IF NOT EXISTS hand(
    id PRIMARY KEY AUTOINCREMENT,
    player INTEGER,
    board id,
    seat TEXT,
    spades TEXT,
    hearts TEXT,
    diamonds TEXT,
    clubs TEXT,
    FOREIGN KEY (player) REFERENCES player(id),
    FOREIGN KEY (board) REFERENCES board(id)
);