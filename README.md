# top-five-backend

## Backend service for Top Five dating app

### About
This is a backend service built using Django REST Framework, to handle the requests from the front-end of the Top Five dating app React Native project. This project is in progress and is being created entirely by Rashaun Warner. **Please do not steal any ideas from this project**

### Tech Stack:

- Django: Python web framework
- PostgreSQL: SQL database

### Fully Functional URLs with Custom Views (not including admin)
- api/signup
- api/login
- api/logout
- api/users/user_by_id/{id}/
- api/users/update_user/{id}/
- api/users/delete_user/{id}/
- api/users/get_profile/{id}/
- api/users/create_profile/{id}/
- api/users/update_profile/{id}/



### Recent Backend Progress (most recent --> oldest): 
- Created views for get profile, update profile, delete user
- Created Interests model and serializer
- Created Matches model and serializer
- Created Profile model and serializer
- **MAJOR CHANGE: I decided to switch from MongoDB to PostgreSQL! This big decision was decided after discovering that their compatibility is too limited for my needs. This was a great learning experience!**
- Blacklisting JWTs completely works. Login adds Outstanding Token and starts new session, new refresh and access with tokens/refresh, and logout blacklists and ends the session.
- ~~Prevented refresh tokens from  being used as access tokens on protected routes~~
- Implemented outstanding tokens on login and blacklisting refresh tokens on logout.
- Completed Login and Logout views with Django REST Framework Simple JWT 
- Created Django users views and urls for authentication
- Created Django users model and serializer
- Created admin login, logout, reset password, and register views
- Created MongoDB Atlas cluster and connect to Django project using PyMongo and djongo
- Created Django project and installed dependencies



### How to run:

- create virtual environment: `python3 -m venv topfive_env`
- activate virtual environment: `source ./topfive_env/bin/activate`
- install dependencies: `pip install -r requirements.txt`
- create .env file in topfive directory and add the following:
```
SECRET_KEY=your_secret_key
DATABASE_NAME=your_mongodb_url
DATABASE_USER=your_mongodb_username
DATABASE_DATABASE_PASSWORDPASSWORD=your_mongodb_password
DEBUG=True
IS_PRODUCTION=False
```
- run server: `python manage.py runserver`