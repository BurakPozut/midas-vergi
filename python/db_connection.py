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
            print("\n⚠️  Warning: Could not set Turkish locale")
            locale.setlocale(locale.LC_ALL, '')


def get_db_connection():
    try:
        # Load environment variables explicitly
        load_dotenv()
        
        # Get environment variables
        host = os.getenv('MYSQL_HOST', 'localhost')
        user = os.getenv('MYSQL_USER')
        password = os.getenv('MYSQL_PASSWORD')
        database = os.getenv('MYSQL_DATABASE')
        
        # Validate environment variables
        missing_vars = []
        if not host: missing_vars.append('MYSQL_HOST')
        if not user: missing_vars.append('MYSQL_USER')
        if not password: missing_vars.append('MYSQL_PASSWORD')
        if not database: missing_vars.append('MYSQL_DATABASE')
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        # Create connection config with timeout
        config = {
            'host': host,
            'user': user,
            'password': password,
            'database': database,
            'auth_plugin': 'mysql_native_password',
            'connect_timeout': 10,
            'connection_timeout': 10,
            'use_pure': True
        }
        
        # Attempt connection
        try:
            connection = mysql.connector.connect(**config)
        except mysql.connector.Error as conn_err:
            raise
        
        if not connection.is_connected():
            raise Exception("Connection object created but not connected")
        
        # Test the connection with a simple query
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        except mysql.connector.Error as query_err:
            raise
        finally:
            cursor.close()
        
        return connection
        
    except mysql.connector.Error as err:
        if err.errno == mysql.connector.errorcode.ER_ACCESS_DENIED_ERROR:
            raise ValueError("Access denied: Please check your username and password")
        elif err.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
            raise ValueError("Database does not exist")
        elif err.errno == 2003:
            raise ValueError("Can't connect to MySQL server. Check if: 1) MySQL service is running 2) Host/port are correct 3) Firewall is not blocking")
        raise
        
    except Exception as e:
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
    connection = None
    cursor = None
    success = True

    try:
        # print("\n=== Debug: Try to get db connection ===")
        connection = get_db_connection()
        # print(f"Connection ID: {connection}")
        if not connection.is_connected():
            # print("❌ Database connection failed!")
            return False
            
        cursor = connection.cursor(prepared=True)  # Use prepared statements for better security
        # print("✅ Cursor created successfully")

        insert_query = """
        INSERT INTO Transaction (
            date, transactionType, symbol, operationType, status, currency,
            orderQuantity, orderAmount, executedQuantity, averagePrice,
            transactionFee, transactionAmount, userId, createdAt, updatedAt
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        """

        for index, row in transactions_df.iterrows():
            try:
                # print(f"\n--- Processing row {index + 1} ---")
                # print("Date value:", row["Tarih"])
                # print("Date type:", type(row["Tarih"]))
                
                transaction_date = row["Tarih"]
                
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
                
                # print("\nPrepared values for insertion:")
                # for i, val in enumerate(values):
                #     print(f"- Value {i}: {val} (type: {type(val)})")
                
                # print("\nExecuting SQL query...")
                cursor.execute(insert_query, values)
                # print("✅ Row inserted successfully")
                
            except mysql.connector.Error as err:
                # print(f"\n❌ MySQL Error processing row {index + 1}:")
                # print(f"Error Code: {err.errno}")
                # print(f"Error Message: {err.msg}")
                # print("Row data:", row.to_dict())
                success = False
                continue
            except Exception as e:
                # print(f"\n❌ Unexpected error processing row {index + 1}: {str(e)}")
                # print("Row data:", row.to_dict())
                success = False
                continue

        if success:
            # print("\nCommitting transaction...")
            connection.commit()
            # print("✅ Transaction committed successfully")
        else:
            # print("\nRolling back due to errors...")
            connection.rollback()
            # print("✅ Transaction rolled back")
        
    except mysql.connector.Error as err:
        # print(f"\n❌ MySQL Error:")
        # print(f"Error Code: {err.errno}")
        # print(f"Error Message: {err.msg}")
        success = False
        if connection:
            connection.rollback()
    except Exception as e:
        # print(f"\n❌ Unexpected error: {str(e)}")
        success = False
        if connection:
            connection.rollback()
    finally:
        # print("\nClosing database resources...")
        if cursor:
            cursor.close()
            # print("Cursor closed")
        if connection:
            connection.close()
            # print("Connection closed")

    return success

def insert_dividends(dividends_df, user_id):
    # print("\n=== Debug: insert_dividends ===")
    # print(f"Received DataFrame with {len(dividends_df)} rows")
    # print("\nDataFrame columns:", dividends_df.columns.tolist())
    
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
        # print(f"Database error: {e}")
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