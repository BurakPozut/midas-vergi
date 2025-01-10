from pymongo import MongoClient
from datetime import datetime
import locale
from bson import ObjectId


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
            # Remove currency symbols and whitespace
            value = value.replace('TL', '').replace('USD', '').strip()
            # Remove thousand separators and convert decimal comma to point
            value = value.replace('.', '').replace(',', '.')
        return float(value)
    except (ValueError, TypeError) as e:
        return 0.0

def insert_transactions(transactions_df, user_id):
    # print("\n in the insert_transactions function")
    transactions_collection = db.Transaction
    
    transactions_to_insert = []
    
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
                "userId": ObjectId(user_id),
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow()
            }
            transactions_to_insert.append(transaction)
            
        except Exception as e:
            # print(f"Error processing row: {e}")
            # print(f"Row data: {row.to_dict()}")
            continue
    
    if transactions_to_insert:
        try:
            result = transactions_collection.insert_many(transactions_to_insert)
            # print(f"Successfully inserted {len(result.inserted_ids)} transactions")
            return True
        except Exception as e:
            #  print(f"Error during bulk insert: {e}")
            return False
    
    return False

def insert_dividends(dividends_df, user_id):
    dividends_collection = db.Dividend
    
    dividends_to_insert = []
    
    for _, row in dividends_df.iterrows():
        try:
            gross_amount = safe_float(row["Brüt Temettü Tutarı"])
            tax = safe_float(row["Stopaj*"])
            net_amount = safe_float(row["Net Temettü Tutarı"])
            
            dividend = {
                "paymentDate": datetime.strptime(row["Ödeme Tarihi"].strip(),  "%d/%m/%y"),
                "symbol": str(row["Sermaya Piyasası Aracı"]).strip(),
                "grossAmount": gross_amount,
                "taxWithheld": tax,
                "netAmount": net_amount,
                "userId": ObjectId(user_id),
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow()
            }
            dividends_to_insert.append(dividend)
            
        except Exception as e:
            continue
    
    if dividends_to_insert:
        try:
            result = dividends_collection.insert_many(dividends_to_insert)
            return True
        except Exception as e:
            return False
    
    return False

def get_user_dividends(user_id):
    dividends_collection = db.Dividend
    dividends = list(dividends_collection.find({"userId": user_id}))
    return dividends

def get_user_transactions(user_id):
    transactions_collection = db.Transaction
    transactions = list(transactions_collection.find({"userId": user_id}))
    return transactions