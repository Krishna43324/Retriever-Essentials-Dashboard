USE retriever_dashboard; -- Name of MySQL Server

CREATE TABLE IF NOT EXISTS departments(
    dep_id INT AUTO_INCREMENT PRIMARY KEY, --primary key means each one will be unique
    dep_name VARCHAR(100) NOT NULL UNIQUE, --must have name to be saved
    date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS users(
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    Password_Hash VARCHAR(255) NOT NULL, -- Store a password HASH

    permissions ENUM('Viewer', 'Department_Manager', 'Admin') NOT NULL DEFAULT 'Viewer',
    dep_id INT NULL,
    date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_users_department
    FOREIGN KEY (dep_id)
    REFERENCES departments(dep_id)
    ON DELETE SET NULL
);


CREATE TABLE `CSV_File`(
    csv_id INT AUTO_INCREMENT PRIMARY KEY,
    file_Name VARCHAR(255) NOT NULL,
    file_Path VARCHAR(500) NOT NULL,
    file_Size_KB INT UNSIGNED NOT NULL DEFAULT 0,
    row_count INT UNSIGNED NOT NULL DEFAULT 0,
    upload_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    uploader_id  INT UNSIGNED NOT NULL,
    shared BOOLEAN NOT NULL DEFAULT FALSE,


    Uploader_ID INT NOT NULL,

    CONSTRAINT fk_csv_uploader
        FOREIGN KEY (uploader_id)
        REFERENCES users(user_id)
        ON DELETE RESTRICT,

    CONSTRAINT fk_csv_department
        FOREIGN KEY (dep_id)
        REFERENCES departments(dep_id)
        ON DELETE RESTRICT,

    INDEX idx_csv_uploader (uploader_id),
    INDEX idx_csv_department (dep_id),
    INDEX idx_csv_upload_date (upload_date)
);

CREATE TABLE Figure (
    figure_ID INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    dep_ID INT UNSIGNED NOT NULL,
    csv_id INT UNSIGNED NULL,

    chart_Type enum('bar', 'line', 'scatter', 'pie', 'doughnut') NOT NULL,
    caption VARCHAR(500) NULL,

    -- Coordinates for the figure's position in the UI.
    location_x INT NOT NULL DEFAULT 0,
    location_y INT NOT NULL DEFAULT 0,

    x_axis_label VARCHAR(255) NULL,
    x_axis_label VARCHAR(255) NULL,
    
    date_created TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_figure_department
        FOREIGN KEY (dep_id)
        REFERENCES department(dep_id)
        ON DELETE RESTRICT,

    CONSTRAINT fk_figure_csv
        FOREIGN KEY (csv_id)
        REFERENCES `CSV_File`(csv_id)
        ON DELETE SET NULL,

    INDEX idx__figure_csv (csv_id)
    INDEX idx_figure_department (dep_id)
);

