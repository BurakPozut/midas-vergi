from pymongo import MongoClient
from datetime import datetime
import locale

# Set locale to handle Turkish characters
locale.setlocale(locale.LC_ALL, 'tr_TR.UTF-8')

# Use the same connection string as in .env
client = MongoClient("mongodb+srv://burakpozut88:1SQnz1bxMEkfEckU@cluster0.h0fnumk.mongodb.net/ExchangeRate?retryWrites=true&w=majority")
db = client.ExchangeRate

def safe_float(value):
    try:
        if value == '-' or value == '' or value is None:
            return 0.0
        # Remove any thousand separators and replace decimal comma with point
        if isinstance(value, str):
            value = value.replace('.', '').replace(',', '.')
        return float(value)
    except (ValueError, TypeError) as e:
        print(f"Error converting value '{value}': {e}")  # Debug print
        return 0.0

def insert_transactions(transactions_df, user_id, source_file):
    print("\n in the insert_transactions function")
    transactions_collection = db.Transaction

    for _, row in transactions_df.iterrows():
        try:
            transaction = {
                "date": datetime.strptime(row["Tarih"].strip(), "%d/%m/%y %H:%M:%S"),
                "transactionType": str(row["İşlem Türü"]).strip(),
                "symbol": str(row["Sembol"]).strip(),
                "operationType": str(row["İşlem Tipi"]).strip(),
                "status": str(row["İşlem Durumu"]).strip(),
                "currency": str(row["Para Birimi"]).strip(),
                "orderQuantity": safe_float(row["Emir Adedi"]),
                "orderAmount": safe_float(row["Emir Tutarı"]),
                "executedQuantity": safe_float(row["Gerçekleşen Adet"]),
                "averagePrice": safe_float(row["Ortalama İşlem Fiyatı"]),
                "transactionFee": safe_float(row["İşlem Ücreti"]),
                "transactionAmount": safe_float(row["İşlem Tutarı"]),
                "sourceFile": source_file,
                "userId": user_id,
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow()
            }
            
            print(f"\nProcessing transaction:")
            print(f"Symbol: {transaction['symbol']}")
            print(f"Average Price: {transaction['averagePrice']}")
            print(f"Raw Average Price: {row['Ortalama İşlem Fiyatı']}")
            
            transactions_collection.insert_one(transaction)
        except Exception as e:
            print(f"Error processing row: {e}")
            print(f"Row data: {row.to_dict()}")
            continue

def get_user_transactions(user_id):
    transactions_collection = db.Transaction
    transactions = list(transactions_collection.find({"userId": user_id}))
    return transactions