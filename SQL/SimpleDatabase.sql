PRAGMA FOREIGN_KEYS = ON;

DROP TABLE IF EXISTS Users;
DROP TABLE IF EXISTS UserData;

CREATE TABLE Users
(
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    password VARCHAR

);

CREATE TABLE IF NOT EXISTS UserData
(
    id       INT,
    address  VARCHAR,
    phone    INT,
    birthday VARCHAR,
    email    VARCHAR NOT NULL,
    CONSTRAINT person_data
        FOREIGN KEY (id)
            REFERENCES Users (id)
            ON DELETE CASCADE
);

INSERT INTO Users(password)
VALUES ('Securepass'),
       ('bobsSecurePass'),
       ('ScrewYouSpiderMan'),
       ('Hundehoveder');

INSERT INTO UserData(id, address, phone, birthday, email)
VALUES (1, 'testStreet', 1234, '22-22-22', 'test@mail.mail'),
       (2, 'testSTreet 2', 12345, '33-33-33', 'bob@fancydomain.com'),
       (3, 'testStreet 3 NY', 54646576786, '99-99-99', 'JJonahJameson@JustTheFacts.com'),
       (4, 'TestStreet 4', 57, '22-22-22', 'Egon@olsenbanden.net');