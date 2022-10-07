PRAGMA FOREIGN_KEYS = ON;

DROP TABLE IF EXISTS Users;
DROP TABLE IF EXISTS UserData;

CREATE TABLE Users
(
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    email    VARCHAR NOT NULL,
    password VARCHAR
);

CREATE TABLE IF NOT EXISTS UserData
(
    id       INT PRIMARY KEY,
    address  VARCHAR,
    phone    INT,
    birthday VARCHAR,
    CONSTRAINT person_data
        FOREIGN KEY (id)
            REFERENCES Users (id)
            ON DELETE CASCADE
);

INSERT INTO Users(email, password)
VALUES ('test@mail.mail', 'Securepass'),
       ('bob@fancydomain.com', 'bobsSecurePass'),
       ('JJonahJameson@JustTheFacts.com', 'ScrewYouSpiderMan'),
       ('Egon@olsenbanden.net', 'Hundehoveder');

INSERT INTO UserData(id, address, phone, birthday)
VALUES (1, 'testStreet', 1234, '22-22-22'),
       (2, 'testSTreet 2', 12345, '33-33-33'),
       (3, 'testStreet 3 NY', 54646576786, '99-99-99'),
       (4, 'TestStreet 4', 57, '22-22-22');