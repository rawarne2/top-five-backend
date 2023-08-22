# top-five-backend

## Backend service for Top Five dating app

### How to run:

- create virtual environment: `python3 -m venv topfive_env`
- activate virtual environment: `source ./topfive_env/bin/activate`
- install dependencies: `pip install -r requirements.txt`
- create .env file in topfive directory and add the following:
```
SECRET_KEY=your_secret_key
DEBUG=True
```
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
- [x] Created Django users model and serializer
- [x] Created Django users views and urls for authentication
