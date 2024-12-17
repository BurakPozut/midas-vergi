# Provide the connection details
from pymongo import MongoClient

def get_dolar():
    # Provide the connection details
    mongo_uri = "mongodb+srv://burakpozut88:Dx4HNRwrvf8GBfhK@cluster0.h0fnumk.mongodb.net/"
    # Create a MongoClient instance
    client = MongoClient(mongo_uri)
    # Access a specific database
    db = client['ExchangeRate']  # Replace 'my_database' with your database name

    # Access a specific collection
    collection = db['Dolar']  # Replace 'my_collection' with your collection name
    # Query to find the document by "Gecerli Oldugu Tarih"
    query = {"Gecerli Oldugu Tarih": "04.01.2023"}
    result = collection.find_one(query, {"_id": 0, "Doviz Alis": 1})

    # Print the result
    if result:
        print("Document found:", result.get("Doviz Alis"))
    else:
        print("No document found with the specified 'Gecerli Oldugu Tarih'")