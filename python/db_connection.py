from pymongo import MongoClient

mongo_uri = "mongodb+srv://burakpozut88:Dx4HNRwrvf8GBfhK@cluster0.h0fnumk.mongodb.net/"
# Create a MongoClient instance
client = MongoClient(mongo_uri)
# Access a specific database
db = client['ExchangeRate']  # Replace 'my_database' with your database name
print(" \n ---Connected to the database--- \n")