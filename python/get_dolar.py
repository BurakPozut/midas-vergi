# Provide the connection details
from db_connection import db

def get_dolar(tarih):
    # Access a specific collection
    collection = db['Dolar']  # Replace 'my_collection' with your collection name
    # Query to find the document by "Gecerli Oldugu Tarih"
    query = {"Gecerli Oldugu Tarih": tarih}
    result = collection.find_one(query, {"_id": 0, "Doviz Alis": 1})

    # Print the result
    if result:
        # print("Document found:", result.get("Doviz Alis"))
        return result.get("Doviz Alis")
    else:
        print("No document found with the specified 'Gecerli Oldugu Tarih'")