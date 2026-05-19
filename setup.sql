-- Run this once as your MariaDB root user to set up the database and user.

CREATE DATABASE IF NOT EXISTS space_wordcloud
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

CREATE USER IF NOT EXISTS 'space_user'@'localhost' IDENTIFIED BY 'space_pass';

GRANT ALL PRIVILEGES ON space_wordcloud.* TO 'space_user'@'localhost';

FLUSH PRIVILEGES;

-- The application (db.py) creates the articles table automatically on startup.
-- You can also create it manually:

USE space_wordcloud;

CREATE TABLE IF NOT EXISTS articles (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  external_id INT UNIQUE,
  title       TEXT,
  summary     TEXT,
  source      VARCHAR(255),
  published   DATETIME,
  fetched_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
