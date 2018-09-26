from pymongo import MongoClient

class MongoConnector():
    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        self.db = self.client.rankr
