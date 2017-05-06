from pymongo import MongoClient

mongo_db = MongoClient().get_database('youtube')
