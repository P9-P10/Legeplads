PRAGMA FOREIGN_KEYS = OFF;

DROP TABLE IF EXISTS Users;
DROP TABLE IF EXISTS UserData;
DROP TABLE IF EXISTS Orders;
DROP TABLE IF EXISTS Products;
DROP TABLE IF EXISTS NewsLetter;
DROP TABLE IF EXISTS RecoveryQuestions;

PRAGMA FOREIGN_KEYS = ON;
CREATE TABLE Users
(
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    email         VARCHAR NOT NULL,
    password      VARCHAR,
    creation_date DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS UserData
(
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id  INT,
    address  VARCHAR,
    name     VARCHAR,
    phone    INT,
    birthday VARCHAR,
    CONSTRAINT person_data
        FOREIGN KEY (user_id)
            REFERENCES Users (id)
            ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Orders
(
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    owner      INT,
    product    INT,
    quantity   INT,
    order_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT orders_constraints
        FOREIGN KEY (owner)
            REFERENCES Users (id)
            ON DELETE CASCADE,
    FOREIGN KEY (product) references Products (product_id)

);

CREATE TABLE IF NOT EXISTS Products
(
    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name       VARCHAR
);

CREATE TABLE NewsLetter
(
    user_id      INT,
    wants_letter INT,
    FOREIGN KEY (user_id) REFERENCES UserData (id)
);

CREATE TABLE RecoveryQuestions
(
    user_id  INTEGER,
    question VARCHAR,
    answer   VARCHAR,
    FOREIGN KEY (user_id) REFERENCES Users (id)
);

INSERT INTO Users(email, password)
VALUES ('test@mail.mail', 'Securepass'),
       ('bob@fancydomain.com', 'BobTheBodyBuilder');
INSERT INTO Users(email, password, creation_date)
VALUES ('JJonahJameson@JustTheFacts.com', 'ScrewYouSpiderMan', '2020-10-05 06:38:29'),
       ('Egon@olsenbanden.net', 'Hundehoveder', '2001-10-05 06:38:29');


INSERT INTO UserData(user_id, address, phone, birthday, name)
VALUES (1, 'testStreet', 1234, '2001-10-05 06:38:29', 'Test User'),
       (2, 'testSTreet 2', 12345, '1966-10-05 06:38:29', 'Bob The Builder'),
       (3, 'testStreet 3 NY', 54646576786, '1970-10-05 06:38:29', 'J.Jonah Jameson'),
       (4, 'TestStreet 4', 57, '1962-10-05 06:38:29', 'Egon Olsen');

INSERT INTO Products(name)
VALUES ('Hammer'),
       ('second'),
       ('Daily Bugle'),
       ('Cigar'),
       ('fith'),
       ('pilsner'),
       ('Stetoskob');

INSERT INTO Orders(owner, product, quantity)
VALUES (1, 1, 1),
       (1, 2, 1),
       (1, 4, 1),
       (1, 1, 5),
       (4, 4, 5),
       (3, 3, 2),
       (4, 5, 3),
       (4, 6, 1);

INSERT INTO Orders(owner, product, quantity, order_time)
VALUES (4, 4, 5, '2019-10-05 06:38:29'),
       (4, 5, 5, '2002-10-05 06:38:29'),
       (2, 1, 5, '2002-10-05 06:38:29');

INSERT INTO NewsLetter (user_id, wants_letter)
VALUES (1, 1),
       (2, 0),
       (3, 1),
       (4, 1);

INSERT INTO RecoveryQuestions(user_id, question, answer)
VALUES (3, 'What is my most hated "superhero?"', 'Spider-Man'),
       (1, 'Animal?', 'Yes'),
       (2, 'First pet name', 'Pilchard'),
       (4, 'What do i have when i get out of prison?', 'A plan');