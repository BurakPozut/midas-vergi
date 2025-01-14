import mysql.connector
from datetime import datetime
import locale
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set locale to handle Turkish characters
try:
    locale.setlocale(locale.LC_ALL, 'tr_TR.UTF-8')
except locale.Error:
    try:
        locale.setlocale(locale.LC_ALL, 'Turkish_Turkey.1254')
    except locale.Error:
        try:
            locale.setlocale(locale.LC_ALL, 'tr_TR')
        except locale.Error:
            print("Warning: Could not set Turkish locale")
            locale.setlocale(locale.LC_ALL, '')

def get_db_connection():
    try:
        return mysql.connector.connect(
            host=os.getenv('MYSQL_HOST', 'localhost'),
            user=os.getenv('MYSQL_USER'),
            password=os.getenv('MYSQL_PASSWORD'),
            database=os.getenv('MYSQL_DATABASE'),
            charset='utf8mb4',
            collation='utf8mb4_unicode_ci'
        )
    except mysql.connector.Error as err:
        print(f"Database connection error: {err}")
        raise

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
    connection = get_db_connection()
    cursor = connection.cursor()
    success = True

    insert_query = """
    INSERT INTO Transaction (
        date, transactionType, symbol, operationType, status, currency,
        orderQuantity, orderAmount, executedQuantity, averagePrice,
        transactionFee, transactionAmount, userId, createdAt, updatedAt
    ) VALUES (
        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
    )
    """

    try:
        for _, row in transactions_df.iterrows():
            try:
                transaction_date = datetime.strptime(row["Tarih"].strip(), "%d/%m/%y %H:%M:%S")
                values = (
                    transaction_date,
                    str(row["İşlem Türü"]).strip(),
                    str(row["Sembol"]).strip(),
                    str(row["İşlem Tipi"]).strip(),
                    str(row["İşlem Durumu"]).strip(),
                    str(row["Para Birimi"]).strip(),
                    safe_float(row["Emir Adedi"]),
                    safe_float(row["Emir Tutarı"]),
                    safe_float(row["Gerçekleşen Adet"]),
                    safe_float(row["Ortalama İşlem Fiyatı"]),
                    safe_float(row["İşlem Ücreti"]),
                    safe_float(row["İşlem Tutarı"]),
                    user_id,
                    datetime.utcnow(),
                    datetime.utcnow()
                )
                cursor.execute(insert_query, values)
            except Exception as e:
                print(f"Error processing transaction row: {e}")
                success = False
                continue

        connection.commit()
    except Exception as e:
        print(f"Database error: {e}")
        success = False
    finally:
        cursor.close()
        connection.close()

    return success

def insert_dividends(dividends_df, user_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    success = True

    insert_query = """
    INSERT INTO Dividend (
        paymentDate, symbol, grossAmount, taxWithheld,
        netAmount, userId, createdAt, updatedAt
    ) VALUES (
        %s, %s, %s, %s, %s, %s, %s, %s
    )
    """

    try:
        for _, row in dividends_df.iterrows():
            try:
                payment_date = datetime.strptime(row["Ödeme Tarihi"].strip(), "%d/%m/%y")
                values = (
                    payment_date,
                    str(row["Sermaya Piyasası Aracı"]).strip(),
                    safe_float(row["Brüt Temettü Tutarı"]),
                    safe_float(row["Stopaj*"]),
                    safe_float(row["Net Temettü Tutarı"]),
                    user_id,
                    datetime.utcnow(),
                    datetime.utcnow()
                )
                cursor.execute(insert_query, values)
            except Exception as e:
                print(f"Error processing dividend row: {e}")
                success = False
                continue

        connection.commit()
    except Exception as e:
        print(f"Database error: {e}")
        success = False
    finally:
        cursor.close()
        connection.close()

    return success

def get_user_dividends(user_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT * FROM Dividend WHERE userId = %s", (user_id,))
        dividends = cursor.fetchall()
        return dividends
    finally:
        cursor.close()
        connection.close()

def get_user_transactions(user_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT * FROM Transaction WHERE userId = %s", (user_id,))
        transactions = cursor.fetchall()
        return transactions
    finally:
        cursor.close()
        connection.close()