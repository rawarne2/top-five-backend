# top-five-backend

## Backend service for Top Five dating app

### How to run:

- activate virtual environment: `source ./topfive_env/bin/activate`
- run server: `python manage.py runserver`

### Tech Stack:

- Django: Python web framework
- MongoDB Atlas: NoSQL cloud database
- PyMongo: Python driver for MongoDB
- djongo: MongoDB connector for Django


### Current Backend Progress:
- [x] Created Django project and installed dependencies
- [x] Created MongoDB Atlas cluster and connect to Django project using PyMongo and djongo
- [x] Created admin login, logout, reset password, and register views
- [x] Created Django users model and return list of user data from MongoDB at `/users`
