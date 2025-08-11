DROP SCHEMA IF EXISTS lianes_library;
CREATE SCHEMA lianes_library;
USE lianes_library;

CREATE TABLE Books (
	ISBN Char(17) PRIMARY KEY,
    Title VARCHAR(45),
    Author VARCHAR(45),
    Genre VARCHAR(45),
	BookCondition VARCHAR(15),
    IsInStock TINYINT(1) NOT NULL DEFAULT 1,
    ShelfLocation VARCHAR(45),
    ShelfRow INT
);

CREATE TABLE Friends (
	FriendID INT auto_increment PRIMARY KEY,
    FName VARCHAR(45),
    LName VARCHAR(45),
    MaxLoans INT,
    ISBN CHAR
);

CREATE TABLE Loans (
	LoanID INT auto_increment PRIMARY KEY,
    BorrowDate DATETIME NOT NULL,
    DueDate DATETIME NOT NULL,
    ReturnReminder DATETIME,
    ISBN CHAR(17),
    FriendID INT,
    FOREIGN KEY (ISBN) REFERENCES Books(ISBN),
	FOREIGN KEY (FriendID) REFERENCES Friends(FriendID)
);

CREATE TABLE Contacts (
	ContactID INT auto_increment PRIMARY KEY,
	FriendID INT,
    `type` VARCHAR(45),
    contact VARCHAR(45),
    FOREIGN KEY (FriendID) REFERENCES Friends(FriendID)
);

-- === BOOKS & STORAGE ===
INSERT INTO Books (ISBN, Title, Author, Genre, BookCondition, IsInStock, ShelfLocation, ShelfRow) VALUES
('978-0-452-28423-4', '1984', 'George Orwell', 'Dystopian', 'Good', TRUE, 'A1', 1),
('978-0-618-00221-3', 'The Hobbit', 'J.R.R. Tolkien', 'Fantasy', 'Excellent', TRUE, 'A1', 1),
('978-0-06-231609-7', 'Sapiens', 'Yuval Harari', 'History', 'Fair', FALSE, 'A1', 1),
('978-0-06-085052-4', 'Brave New World', 'Aldous Huxley', 'Dystopian', 'Good', TRUE, 'A1', 2),
('978-0-316-76948-0', 'The Catcher in the Rye', 'J.D. Salinger', 'Fiction', 'Fair', TRUE, 'A1', 2),
('978-0-06-112008-4', 'To Kill a Mockingbird', 'Harper Lee', 'Fiction', 'Excellent', TRUE, 'A1', 2),
('978-0-7432-7356-5', 'The Great Gatsby', 'F. Scott Fitzgerald', 'Fiction', 'Good', TRUE, 'A1', 2),
('978-0-374-53355-7', 'Thinking, Fast and Slow', 'Daniel Kahneman', 'Psychology', 'Excellent', TRUE, 'A1', 3),
('978-0-13-235088-4', 'Clean Code', 'Robert C. Martin', 'Programming', 'Good', TRUE, 'A1', 3),
('978-0-7352-1129-0', 'Atomic Habits', 'James Clear', 'Self-help', 'Excellent', TRUE, 'A1', 3),
('978-0-441-17271-9', 'Dune', 'Frank Herbert', 'Sci-Fi', 'Fair', TRUE, 'B1', 1),
('978-0-8041-3903-1', 'The Martian', 'Andy Weir', 'Sci-Fi', 'Good', TRUE, 'B1', 1),
('978-0-399-59050-4', 'Educated', 'Tara Westover', 'Memoir', 'Excellent', TRUE, 'B1', 1),
('978-1-5247-6313-8', 'Becoming', 'Michelle Obama', 'Memoir', 'Excellent', TRUE, 'B1', 2),
('978-1-4555-8660-3', 'Deep Work', 'Cal Newport', 'Productivity', 'Good', TRUE, 'B1', 2),
('978-0-8041-3935-2', 'Zero to One', 'Peter Thiel', 'Business', 'Fair', TRUE, 'B1', 2),
('978-0-307-36196-4', 'The Lean Startup', 'Eric Ries', 'Business', 'Excellent', TRUE, 'B1', 2),
('978-0-8129-8163-8', 'The Power of Habit', 'Charles Duhigg', 'Self-help', 'Good', TRUE, 'B1', 3),
('978-0-316-17232-9', 'Blink', 'Malcolm Gladwell', 'Psychology', 'Good', TRUE, 'B1', 3),
('978-0-316-01792-7', 'Outliers', 'Malcolm Gladwell', 'Psychology', 'Good', TRUE, 'B1', 3),
('978-0-307-26543-1', 'The Road', 'Cormac McCarthy', 'Fiction', 'Fair', TRUE, 'C1', 1),
('978-0-06-231500-7', 'The Alchemist', 'Paulo Coelho', 'Fiction', 'Excellent', TRUE, 'C1', 1),
('978-0-375-70270-9', 'Norwegian Wood', 'Haruki Murakami', 'Fiction', 'Good', TRUE, 'C1', 1),
('978-1-4000-3461-6', 'Kafka on the Shore', 'Haruki Murakami', 'Fiction', 'Excellent', TRUE, 'C1', 2),
('978-0-7564-0412-3', 'The Name of the Wind', 'Patrick Rothfuss', 'Fantasy', 'Good', TRUE, 'C1', 2),
('978-0-06-245771-4', 'The Subtle Art of Not Giving a F*ck', 'Mark Manson', 'Self-help', 'Fair', TRUE, 'C1', 2),
('978-0-399-58817-5', 'Born a Crime', 'Trevor Noah', 'Memoir', 'Excellent', TRUE, 'C1', 2),
('978-1-5247-6316-9', 'A Promised Land', 'Barack Obama', 'Memoir', 'Excellent', TRUE, 'C1', 3),
('978-0-307-35288-8', 'Quiet', 'Susan Cain', 'Psychology', 'Good', TRUE, 'C1', 3),
('978-0-465-06710-7', 'The Design of Everyday Things', 'Don Norman', 'Design', 'Good', TRUE, 'C1', 3);

-- === FRIENDS ===
INSERT INTO Friends (FName, LName, MaxLoans) VALUES
('Alice', 'Smith', 3), ('Bob', 'Brown', 2), ('Clara', 'Jones', 4), ('David', 'Lee', 3),
('Eva', 'Kim', 2), ('Frank', 'Wong', 5), ('Grace', 'Moore', 2), ('Henry', 'White', 3),
('Ivy', 'Clark', 2), ('Jack', 'Hall', 4), ('Kara', 'Young', 3), ('Liam', 'Scott', 2),
('Mia', 'Adams', 3), ('Noah', 'Evans', 4), ('Olivia', 'Turner', 2), ('Paul', 'Collins', 5),
('Quinn', 'Parker', 3), ('Rosa', 'Bell', 2), ('Sam', 'Reed', 3), ('Tina', 'Foster', 2),
('Uma', 'Gray', 3), ('Vince', 'Morgan', 2), ('Wendy', 'Cook', 4), ('Xander', 'Hughes', 3),
('Yara', 'Barnes', 2), ('Zack', 'Russell', 4), ('Amy', 'Wells', 3), ('Ben', 'Griffin', 2),
('Cara', 'Sanders', 3), ('Drew', 'Myers', 2);

-- CONTACTS
INSERT INTO Contacts (FriendID, `type`, contact) VALUES
-- Friend 1
(1, 'email', 'alice@example.com'),
(1, 'phone', '1111111111'),
(1, 'street', 'Main St 1'),
(1, 'city', 'Berlin'),
-- Friend 2
(2, 'email', 'bob@example.com'),
(2, 'phone', '2222222222'),
-- Friend 3
(3, 'email', 'clara@example.com'),
(3, 'street', 'Oak St 3'),
(3, 'city', 'Hamburg'),
-- Friend 4
(4, 'phone', '4444444444'),
(4, 'city', 'Cologne'),
-- Friend 5
(5, 'email', 'eva@example.com'),
-- Friend 6
(6, 'email', 'frank@example.com'),
(6, 'phone', '6666666666'),
(6, 'street', 'Birch St 6'),
(6, 'city', 'Stuttgart'),
-- Friend 7
(7, 'email', 'grace@example.com'),
(7, 'phone', '7777777777'),
-- Friend 8
(8, 'phone', '8888888888'),
(8, 'street', 'Fir St 8'),
(8, 'city', 'Dresden'),
-- Friend 9
(9, 'email', 'ivy@example.com'),
-- Friend 10
(10, 'phone', '1010101010'),
-- Friend 11
(11, 'email', 'kara@example.com'),
(11, 'street', 'Cherry St 11'),
(11, 'city', 'Bremen'),
-- Friend 12
(12, 'email', 'liam@example.com'),
(12, 'phone', '3030303030'),
(12, 'street', 'Beech St 12'),
(12, 'city', 'Nuremberg'),
-- Friend 13
(13, 'phone', '4040404040'),
-- Friend 14
(14, 'email', 'noah@example.com'),
(14, 'city', 'Duisburg'),
-- Friend 15
(15, 'email', 'olivia@example.com'),
(15, 'phone', '6060606060'),
-- Friend 16
(16, 'email', 'paul@example.com'),
(16, 'phone', '7070707070'),
(16, 'street', 'Hazel St 16'),
(16, 'city', 'Wuppertal'),
-- Friend 17
(17, 'phone', '8080808080'),
(17, 'street', 'Cedar St 17'),
(17, 'city', 'Bielefeld'),
-- Friend 18
(18, 'email', 'rosa@example.com'),
-- Friend 19
(19, 'phone', '1122334455'),
(19, 'street', 'Walnut St 19'),
(19, 'city', 'Mannheim'),
-- Friend 20
(20, 'email', 'tina@example.com'),
(20, 'phone', '2233445566'),
-- Friend 21
(21, 'email', 'uma@example.com'),
(21, 'phone', '3344556677'),
(21, 'street', 'Yew St 21'),
(21, 'city', 'Wiesbaden'),
-- Friend 22
(22, 'phone', '4455667788'),
-- Friend 23
(23, 'email', 'wendy@example.com'),
(23, 'street', 'Cottonwood St 23'),
(23, 'city', 'Mönchengladbach'),
-- Friend 24
(24, 'email', 'xander@example.com'),
(24, 'phone', '6677889900'),
-- Friend 25
(25, 'email', 'yara@example.com'),
(25, 'phone', '7788990011'),
(25, 'street', 'Rowan St 25'),
(25, 'city', 'Kiel'),
-- Friend 26
(26, 'phone', '8899001122'),
(26, 'street', 'Magnolia St 26'),
(26, 'city', 'Halle'),
-- Friend 27
(27, 'email', 'amy@example.com'),
-- Friend 28
(28, 'email', 'ben@example.com'),
(28, 'phone', '1011121314'),
-- Friend 29
(29, 'phone', '1213141516'),
(29, 'street', 'Dogwood St 29'),
(29, 'city', 'Rostock'),
-- Friend 30
(30, 'email', 'drew@example.com'),
(30, 'phone', '1314151617'),
(30, 'street', 'Mulberry St 30'),
(30, 'city', 'Heidelberg');

-- === LOANS ===

-- Loan 1: OVERDUE (Alice Smith)
INSERT INTO Loans (BorrowDate, DueDate, ReturnReminder, ISBN, FriendID) VALUES
('2025-07-01 10:00:00', '2025-07-15 10:00:00', '2025-07-12 10:00:00', '978-0-618-00221-3', 1);

-- Loan 2: OVERDUE (Bob Brown's First Loan)
INSERT INTO Loans (BorrowDate, DueDate, ReturnReminder, ISBN, FriendID) VALUES
('2025-07-10 11:30:00', '2025-07-24 11:30:00', '2025-07-21 11:30:00', '978-0-06-085052-4', 2);

-- Loan 3: REMINDER FOR TODAY (Clara Jones)
INSERT INTO Loans (BorrowDate, DueDate, ReturnReminder, ISBN, FriendID) VALUES
('2025-07-18 15:00:00', '2025-08-01 15:00:00', '2025-07-29 15:00:00', '978-0-316-76948-0', 3);

-- Loan 4: Active Loan (David Lee)
INSERT INTO Loans (BorrowDate, DueDate, ReturnReminder, ISBN, FriendID) VALUES
('2025-07-20 09:00:00', '2025-08-03 09:00:00', '2025-07-31 09:00:00', '978-0-06-112008-4', 4);

-- Loan 5: Active Loan (Eva Kim)
INSERT INTO Loans (BorrowDate, DueDate, ReturnReminder, ISBN, FriendID) VALUES
('2025-07-25 14:00:00', '2025-08-08 14:00:00', '2025-08-05 14:00:00', '978-0-7432-7356-5', 5);

-- Loan 6: Active Loan (Frank Wong)
INSERT INTO Loans (BorrowDate, DueDate, ReturnReminder, ISBN, FriendID) VALUES
('2025-07-28 16:45:00', '2025-08-11 16:45:00', '2025-08-08 16:45:00', '978-0-374-53355-7', 6);

-- Loan 7: Bob Brown's Second Loan (Active)
INSERT INTO Loans (BorrowDate, DueDate, ReturnReminder, ISBN, FriendID) VALUES
('2025-07-26 12:00:00', '2025-08-09 12:00:00', '2025-08-06 12:00:00', '978-0-13-235088-4', 2);


-- === UPDATE BOOK & FRIEND STATUS ===

-- Update IsInStock status for all 7 borrowed books
UPDATE Books SET IsInStock = 0 WHERE ISBN IN (
    '978-0-618-00221-3',
    '978-0-06-085052-4',
    '978-0-316-76948-0',
    '978-0-06-112008-4',
    '978-0-7432-7356-5',
    '978-0-374-53355-7',
    '978-0-13-235088-4'
);

-- Decrement MaxLoans for friends who borrowed books
UPDATE Friends SET MaxLoans = MaxLoans - 2 WHERE FriendID = 2; -- Bob Brown borrowed 2 books
UPDATE Friends SET MaxLoans = MaxLoans - 1 WHERE FriendID IN (1, 3, 4, 5, 6); -- Others borrowed 1 book