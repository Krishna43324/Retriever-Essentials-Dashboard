# Retriever-Essentials-Dashboard
Retriever Essentials is UMBC's basic needs hub. This project will help Retriever Essentials build a centralized dashboard to understand the impact of their collective work by replacing manual spreadsheet collection with a database and a dashboard.
This github page can be used as a central page to view frontend and backend code. We can also write notes here. 


Setting up the Database:

1. Download the MySQL version that works with your OS
2. Follow the setup instructions from the MySQL configurator and name your MySQL server 'retriever_dashboard'. Write down your username and password for the server, we'll need that to access it using MySQL workbench.
3. Download the MySQL Workbench version that works with your OS
4. Open the Workbench. Using your username and password from the server steup, enter the correct details/credentials to register/save the server in Workbench. 
5. Make sure your MySQL server is running. If the workbench shows it is inactive, start it using the following method according to your OS. 
    a. For Windows: use "windows_key + r" and type "services.msc". In this window, navigate to the section with a service named MySQL with some numbers following it, such as "MySQL2610". Right click it and and select "start" to run the server. You can also set the server to startup automatically when you start the computer.
    b. For Linux: use the command "sudo systemctl start mysql", or "mysqld" to start it directly.
    c. For MacOS: use the command "mysql.server start" or "brew services start mysql" if you installed it via Homebrew.
6. Now that your server is running in Workbench, double click on your server and you should see a "connected" status at the top of your screen. If you do NOT see that, double check that your server is running by going through step 5 again, followed by troubleshooting if that fails as well.
7. You should now see an empty SQL file. To check your connection, write the following statements in the file: "USE retriever_dashboard;", go to the next line and write "SHOW TABLES;". If this displays 5 tables, you have setup the database!
8. Follow the Flask instructions to setup your Python environment to connect the program with the database.


To execute Flask, you need to go into backend/ folder. 

Create a venv: python3 -m venv venv
Turn on the venv: .\venv\Scripts\Activate.ps1  (on Windows)
Install pip if you haven't using online instructions (py -m ensurepip --upgrade or python -m ensurepip --upgrade on Windows) and do 'pip install Flask' and 'pip install bcrypt. Then run ./flask_start. It should be capable of bringing up the login page and allowing authentication for administrators and a lot of other functionalities. Flask will enable us to communicate between frontend and backend. Right now, the setup steps seem complex, so maybe we should also use Docker for all of this so that we can just run 'docker run build' or something like that and it'll create the venv and everything we want. We'll see.

