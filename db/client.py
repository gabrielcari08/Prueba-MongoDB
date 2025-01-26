from pymongo import MongoClient

#Base de datos local
#db_client = MongoClient()

#Base de datos remota
db_client = MongoClient(
    "mongodb+srv://test:test@cluster0.0h33f.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0").test
