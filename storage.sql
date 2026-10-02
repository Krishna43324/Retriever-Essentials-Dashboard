

CREATE TABLE IF NOT EXISTS departments(
    dep_id INT AUTO_INCREMENT PRIMARY KEY, --primary key means each one will be unique
    dep_name VARCHAR(100) NOT NULL, --must have name to be saved
    dep_users INT AUTO_INCREMENT PRIMARY KEY,
    num_figs INT,
    date_created DATE
);

CREATE TABLE IF NOT EXISTS department_data( --a data file
    data_file_name NVARCHAR(255) NOT NULL, --the file name
    --data_file_extension NVARCHAR(10), --the file extension such as ".csv"
    dep_data_id INT AUTO_INCREMENT PRIMARY KEY, 
    user_id INT NOT NULL,
    department VARCHAR(100) NOT NULL, 
    shared BOOL DEFAULT FALSE, --will automatically become TINYINT(1). TRUE=1+, FALSE=0
    date_created DATETIME DEFAULT GETDATE(),
    collected_data = VARBINARY(MAX), --file contents
);

--EXAMPLE for formatting
INSERT INTO department_data (data_file_name, user_id, department, collected_data)
VALUES('Retriever_Essentials_Weekly_Report.csv', '0', 'Retriever_Essentials', (SELECT BulkColumn FROM OPENROWSET(BULK 'C:\Departments\Retriever_Essentials\Retriever_Essentials_Weekly_Report.csv', SINGLE_BLOB) AS x));
