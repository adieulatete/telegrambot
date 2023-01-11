CREATE TABLE user (
    userid integer primary key
);


CREATE TABLE category (
    categoryid integer primary key,
    categoryname varchar(255),
    aliases text,
    userid integer,
    FOREIGN KEY (userid) REFERENCES user(userid) ON DELETE CASCADE
);


CREATE TABLE expense (
    expenseid integer primary key,
    amount integer,
    created datetime,
    raw_text text,
    categoryid integer,
    userid integer,
    FOREIGN KEY (categoryid) REFERENCES category(categoryid) ON DELETE CASCADE
);
