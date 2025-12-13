INSERT INTO user (id, username, email, password, role, avatar, saved_xp, saved_level, saved_streak)
VALUES
(2, 'dave', 'dave@mail.com', 'password123', 'user', 'avatar1.jpg', 20, 1, 2),
(3, 'mark', 'mark@mail.com', 'password123', 'user', 'avatar2.jpg', 40, 1, 3),
(4, 'john', 'john@mail.com', 'password123', 'user', 'avatar1.jpg', 50, 2, 1),
(5, 'alex', 'alex@mail.com', 'password123', 'user', 'avatar3.jpg', 10, 1, 1),
(6, 'maria', 'maria@mail.com', 'password123', 'user', 'avatar4.jpg', 70, 2, 4),
(7, 'anna', 'anna@mail.com', 'password123', 'user', 'avatar1.jpg', 15, 1, 3),
(8, 'chris', 'chris@mail.com', 'password123', 'user', 'avatar2.jpg', 20, 1, 2),
(9, 'josh', 'josh@mail.com', 'password123', 'user', 'avatar3.jpg', 90, 3, 6),
(10, 'kyle', 'kyle@mail.com', 'password123', 'user', 'avatar1.jpg', 25, 1, 1),
(11, 'sam', 'sam@mail.com', 'password123', 'user', 'avatar1.jpg', 110, 3, 5),
(12, 'jane', 'jane@mail.com', 'password123', 'user', 'avatar4.jpg', 35, 1, 2),
(13, 'joy', 'joy@mail.com', 'password123', 'user', 'avatar2.jpg', 15, 1, 1),
(14, 'ray', 'ray@mail.com', 'password123', 'user', 'avatar3.jpg', 5, 1, 1),
(15, 'luis', 'luis@mail.com', 'password123', 'user', 'avatar2.jpg', 75, 2, 3),
(16, 'jam', 'jam@mail.com', 'password123', 'user', 'avatar4.jpg', 65, 2, 3),
(17, 'ron', 'ron@mail.com', 'password123', 'user', 'avatar1.jpg', 30, 1, 2),
(18, 'leo', 'leo@mail.com', 'password123', 'user', 'avatar3.jpg', 20, 1, 1),
(19, 'kim', 'kim@mail.com', 'password123', 'user', 'avatar2.jpg', 90, 3, 4),
(20, 'bea', 'bea@mail.com', 'password123', 'user', 'avatar4.jpg', 10, 1, 1),
(21, 'ashley', 'ashley@mail.com', 'password123', 'user', 'avatar3.jpg', 12, 1, 1);


INSERT INTO subject (id, user_id, name, goal_type, goal_minutes)
VALUES
(2, 3, 'Science', 'weekly', 240),
(3, 4, 'English', 'daily', 60),
(4, 5, 'History', 'weekly', 180),
(5, 6, 'Programming', 'weekly', 400),
(6, 7, 'PE', 'daily', 30),
(7, 8, 'Biology', 'weekly', 200),
(8, 9, 'Chemistry', 'weekly', 250),
(9, 10, 'Literature', 'weekly', 150),
(10, 11, 'Algebra', 'daily', 45),
(11, 12, 'Calculus', 'weekly', 300),
(12, 13, 'Art', 'weekly', 120),
(13, 14, 'Music', 'daily', 20),
(14, 15, 'Physics', 'weekly', 250),
(15, 16, 'Statistics', 'weekly', 200),
(16, 17, 'Geography', 'daily', 30),
(17, 18, 'Economics', 'weekly', 150),
(18, 19, 'Coding', 'weekly', 300),
(19, 20, 'Reading', 'daily', 40),
(20, 9, 'Filipino', 'weekly', 180),
(21, 12, 'Math', 'weekly', 300);

INSERT INTO study_log (id, subject, minutes, date, user_id, subject_id)
VALUES
(2, 'Science', 45, '2025-12-02', 3, 2),
(3, 'English', 20, '2025-12-03', 4, 3),
(4, 'History', 60, '2025-12-04', 5, 4),
(5, 'Programming', 90, '2025-12-05', 6, 5),
(6, 'PE', 15, '2025-12-06', 7, 6),
(7, 'Biology', 30, '2025-12-07', 8, 7),
(8, 'Chemistry', 40, '2025-12-08', 9, 8),
(9, 'Literature', 25, '2025-12-09', 10, 9),
(10, 'Algebra', 35, '2025-12-10', 11, 10),
(11, 'Calculus', 50, '2025-12-11', 12, 11),
(12, 'Art', 20, '2025-12-12', 13, 12),
(13, 'Music', 15, '2025-12-13', 14, 13),
(14, 'Physics', 45, '2025-12-14', 15, 14),
(15, 'Statistics', 30, '2025-12-15', 16, 15),
(16, 'Geography', 10, '2025-12-16', 17, 16),
(17, 'Economics', 40, '2025-12-17', 18, 17),
(18, 'Coding', 60, '2025-12-18', 19, 18),
(19, 'Reading', 20, '2025-12-19', 20, 19),
(20, 'Filipino', 75, '2025-12-20', 9, 20),
(21, 'Math', 30, '2025-12-21', 21, 21);


SELECT id, username, email, role 
FROM user;

UPDATE user
SET email = REPLACE(email, '@mail.com', '@gmail.com')
WHERE email LIKE '%@mail.com';

INSERT INTO study_log (subject, minutes, date, user_id, subject_id)
VALUES ('Biology', 50, '2025-12-12', 8, 7);

UPDATE user
SET saved_xp = saved_xp + 20
WHERE id = 2;

DELETE FROM study_log
WHERE subject_id = 21;

DELETE FROM subject
WHERE id = 21;

