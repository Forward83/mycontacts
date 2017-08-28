# mycontacts
Django web application for management contact information: Project has the following functionalities: user object: login, logout, sign-up, password reset. Contact object: adding, editing, deleting, loading/changing photo, custom validation phone number, exporting and importing all contacts for current user
## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.
### Prerequisites
* python3
* Django framework
* Django import-export lib 
* PIL lib
* zipfile lib
* mysql server 

### Installing
To install application follow the following steps:  
1. Clone this repository to local machine
2. Import contacts.sql file to sql server
```
mysql.exe -u root -p contacts < contacts.sql
```
3. Create mysql user and grant all permission for database "contacts". On mysql shell type the following command:
```
CREATE USER 'mycontact'@'localhost' IDENTIFIED BY 'p@ssw0rd';
GRANT ALL PRIVILEGES ON contacts.* TO 'mycontact'@'localhost';
FLUSH PRIVILEGES;
```
You can change parameters db_name, mysql user_name and password for it in contact\settings.py file.
4. Create superuser, if you need access to admin part of project.
```
mysql.exe -u root -p contacts < contacts.sql
```


