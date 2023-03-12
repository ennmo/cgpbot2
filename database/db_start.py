from pymongo import MongoClient

mongo_client = MongoClient("mongodb://localhost:27017/")
db = mongo_client["main_db"]
users_collection = db["users"]
text = db["text"]
chatgpt_requests = db["chatgpt_requests"]