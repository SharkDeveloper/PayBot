import imp
import pymongo
from config import MONGODB_TOKEN 


client = pymongo.MongoClient(MONGODB_TOKEN )
db = client.telegrambot

collection = db.BotUsers

def set(id,value):
    a=dict(value)   
    collection.update_one({"id":id},{"$set":a},True)



receipts = db.receipts

def get(key):
    return receipts.find_one(key)
def get_many(key):
    return receipts.find(key)


def set_dish(receipt):
    receipts.insert_one(receipt)

def delete_dish(data):
    receipts.delete_many(data)

