PRAGMA foreign_keys = ON;

CREATE TABLE user (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('user', 'admin')),
    avatar TEXT,
    saved_xp INTEGER DEFAULT 0,
    saved_level INTEGER DEFAULT 1,
    saved_streak INTEGER DEFAULT 0
);
CREATE TABLE subject (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    goal_type TEXT NOT NULL CHECK(goal_type IN ('daily', 'weekly')),
    goal_minutes INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
);
CREATE TABLE study_log (
    id INTEGER PRIMARY KEY,
    subject TEXT NOT NULL,
    minutes INTEGER NOT NULL,
    date DATE NOT NULL,
    user_id INTEGER NOT NULL,
    subject_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES subject(id) ON DELETE CASCADE
);


