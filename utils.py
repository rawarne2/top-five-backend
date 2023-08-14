from pymongo import MongoClient
from dotenv import load_dotenv
from os import environ

load_dotenv()


def get_db_handle(db_name):
    db_url = environ['DATABASE_URL']
    client = MongoClient(db_url)
    db_handle = client[db_name]
    return db_handle
