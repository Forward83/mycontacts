# mycontacts
Django web application for management contact information: Project has the following functionalities: user object: login, logout, sign-up, password reset. Contact object: adding, editing, deleting, loading/changing photo, custom validation phone number, exporting and importing all contacts for current user
## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.
### Installation requirements
If you are using Linux OS:
```
pip install -r requirements.txt (Python 2), or pip3 install -r requirements.txt (Python 3)
```
If you are using Windows OS:
```
python -m pip install -U pip setuptools
```
### Installing
To install application follow the following steps:  
1. Clone this repository to local machine
2. Install packages from requirements.txt
3. Import contacts.sql file to sql server
```
mysql.exe -u root -p contacts < contacts.sql
```
3. Create mysql user and grant all permission for database "contacts". On mysql shell type the following command:
```
CREATE USER 'mycontact'@'localhost' IDENTIFIED BY 'p@ssw0rd';
GRANT ALL PRIVILEGES ON contacts.* TO 'mycontact'@'localhost';
FLUSH PRIVILEGES;
```
You can change parameters db_name, mysql user_name and password in contact\settings.py file.  

4. Create superuser, if you need access to admin part of project. From project directory run:
```
python manage.py createsuperuser
```
5. Run built-in web server:
```
python manage.py runserver server:port  # localhost:8000 - default parameters
```
## Deployment
To start application open your browser and enter: http://localhost:8000. You will be redirected to login/sign-up form, because your user database is empty (if you don't create superuser) and all content of the application requires authenticated user. You can create new user by this form or by using administration tool. Admin part of the app is available by: http://localhost:8000/admin.  

After you authenticate, you will be able to make all actions to manage your contacts.  
If you forgot your password, you can change it by reset password link on login form. There will be generated massage with instructions __to your console with url you should follow__.

## Deployed version at GAE:

https://my-contacts-205212.appspot.com

https://my-contacts-205212.appspot.com/api/

