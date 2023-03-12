from pymongo import MongoClient

mongo_client = MongoClient("mongodb+srv://nesmerdik3:ItXb94Qbuu83GoDi@cluster0.7vnrtrk.mongodb.net/?retryWrites=true&w=majority")
db = mongo_client["main_db"]
users_collection = db["users"]
text = db["text"]
chatgpt_requests = db["chatgpt_requests"]