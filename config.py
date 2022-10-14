import pymongo
import certifi
import os

connection_string = os.environ.get('SERVER_CONNECTION_STRING')

client = pymongo.MongoClient(connection_string, tlsCAFile=certifi.where())

database = client.get_database("guild-bot")