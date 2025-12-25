CREATE DATABASE IF NOT EXISTS ProgressTracker;
USE ProgressTracker;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS daily_progress (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    date DATE NOT NULL,
    show_up VARCHAR(10),
    learn_thing VARCHAR(255),
    finish_small VARCHAR(255),
    avoid_quitting VARCHAR(10),
    idea_day VARCHAR(255),
    bible_study TEXT,
    thoughts TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE KEY user_date_unique (user_id, date)
);

CREATE TABLE IF NOT EXISTS counters (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    name VARCHAR(50) NOT NULL,
    value INT DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
