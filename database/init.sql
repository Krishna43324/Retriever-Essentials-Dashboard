-- Retriever Essentials Dashboard
-- MySQL 8.x initial schema.
--
-- Executed automatically by the MySQL Docker image the first time its data
-- directory is initialized (mounted into /docker-entrypoint-initdb.d).
-- Safe to re-run manually: every statement is idempotent.

CREATE DATABASE IF NOT EXISTS retriever_dashboard
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_0900_ai_ci;
USE retriever_dashboard;

-- NOTE: in MySQL, "--" only starts a comment when followed by a space.

CREATE TABLE IF NOT EXISTS departments (
    dep_id       INT UNSIGNED NOT NULL AUTO_INCREMENT,
    dep_name     VARCHAR(100) NOT NULL,
    date_created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (dep_id),
    UNIQUE KEY uq_departments_dep_name (dep_name)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS users (
    user_id       INT UNSIGNED NOT NULL AUTO_INCREMENT,
    username      VARCHAR(100) NOT NULL,
    email         VARCHAR(255) NULL,
    password_hash VARCHAR(255) NOT NULL, -- bcrypt hash, never plaintext
    role          ENUM('viewer', 'staff', 'admin') NOT NULL DEFAULT 'viewer',
    dep_id        INT UNSIGNED NULL,
    date_created  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (user_id),
    UNIQUE KEY uq_users_username (username),
    UNIQUE KEY uq_users_email (email),
    KEY idx_users_dep_id (dep_id),

    CONSTRAINT fk_users_department
        FOREIGN KEY (dep_id)
        REFERENCES departments (dep_id)
        ON UPDATE CASCADE
        ON DELETE SET NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS csv_files (
    csv_id          INT UNSIGNED NOT NULL AUTO_INCREMENT,
    dataset_name    VARCHAR(255) NOT NULL,  -- name the user typed in the UI
    file_name       VARCHAR(255) NOT NULL,  -- original uploaded filename
    file_path       VARCHAR(500) NOT NULL,  -- where it is stored on disk
    file_size_bytes INT UNSIGNED NOT NULL DEFAULT 0,
    row_count       INT UNSIGNED NOT NULL DEFAULT 0,
    upload_date     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    uploader_id     INT UNSIGNED NOT NULL,
    dep_id          INT UNSIGNED NULL,
    shared          BOOLEAN NOT NULL DEFAULT FALSE,

    PRIMARY KEY (csv_id),
    UNIQUE KEY uq_csv_files_file_path (file_path),
    UNIQUE KEY uq_csv_files_dataset_name (dataset_name),
    KEY idx_csv_files_uploader (uploader_id),
    KEY idx_csv_files_department (dep_id),
    KEY idx_csv_files_upload_date (upload_date),

    CONSTRAINT fk_csv_uploader
        FOREIGN KEY (uploader_id)
        REFERENCES users (user_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT fk_csv_department
        FOREIGN KEY (dep_id)
        REFERENCES departments (dep_id)
        ON UPDATE CASCADE
        ON DELETE SET NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS figures (
    figure_id    INT UNSIGNED NOT NULL AUTO_INCREMENT,
    dep_id       INT UNSIGNED NOT NULL,
    created_by   INT UNSIGNED NULL, -- NULL allowed so ON DELETE SET NULL works
    chart_type   ENUM('bar', 'line', 'scatter', 'pie', 'doughnut') NOT NULL,
    caption      VARCHAR(500) NULL,
    date_created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Coordinates for the figure's position in the UI.
    location_x   INT NOT NULL DEFAULT 0,
    location_y   INT NOT NULL DEFAULT 0,
    x_axis_label VARCHAR(255) NULL,
    y_axis_label VARCHAR(255) NULL,

    PRIMARY KEY (figure_id),
    KEY idx_figures_department (dep_id),
    KEY idx_figures_created_by (created_by),

    CONSTRAINT fk_figures_department
        FOREIGN KEY (dep_id)
        REFERENCES departments (dep_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT fk_figures_creator
        FOREIGN KEY (created_by)
        REFERENCES users (user_id)
        ON UPDATE CASCADE
        ON DELETE SET NULL
) ENGINE=InnoDB;

-- Many-to-many link between figures and csv_files.
CREATE TABLE IF NOT EXISTS figure_datasets (
    figure_id     INT UNSIGNED NOT NULL,
    csv_id        INT UNSIGNED NOT NULL,
    display_order INT UNSIGNED NOT NULL DEFAULT 1,

    PRIMARY KEY (figure_id, csv_id),
    KEY idx_figure_datasets_csv (csv_id),

    CONSTRAINT fk_figure_datasets_figure
        FOREIGN KEY (figure_id)
        REFERENCES figures (figure_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT fk_figure_datasets_csv
        FOREIGN KEY (csv_id)
        REFERENCES csv_files (csv_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
) ENGINE=InnoDB;

-- Seed the primary department. Re-running this statement is safe.
INSERT INTO departments (dep_name)
VALUES ('Retriever Essentials')
ON DUPLICATE KEY UPDATE dep_name = VALUES(dep_name);
