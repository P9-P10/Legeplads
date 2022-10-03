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
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    email    VARCHAR NOT NULL,
    password VARCHAR
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
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    owner    INT,
    product  INT,
    quantity INT,
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
       ('bob@fancydomain.com', 'BobTheBodyBuilder'),
       ('JJonahJameson@JustTheFacts.com', 'ScrewYouSpiderMan'),
       ('Egon@olsenbanden.net', 'Hundehoveder');

INSERT INTO UserData(user_id, address, phone, birthday, name)
VALUES (1, 'testStreet', 1234, '22-22-22', 'Test User'),
       (2, 'testSTreet 2', 12345, '33-33-33', 'Bob The Builder'),
       (3, 'testStreet 3 NY', 54646576786, '99-99-99', 'J.Jonah Jameson'),
       (4, 'TestStreet 4', 57, '22-22-22', 'Egon Olsen');

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

INSERT INTO NewsLetter (user_id, wants_letter)
VALUES (1, 1),
       (2, 0),
       (3, 1),
       (4, 1);

INSERT INTO RecoveryQuestions(user_id, question, answer)
VALUES (3, 'What is my most hated superhero?', 'Spiderman'),
       (1, 'Animal?', 'Yes'),
       (2, 'First pet name', 'Pilchard'),
       (4, 'What do i have when i get out of prison?', 'A plan');