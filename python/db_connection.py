# import mysql.connector
import psycopg2
from urllib.parse import urlparse
from datetime import datetime
import locale
import os
from dotenv import load_dotenv
import logging
import traceback

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(os.path.dirname(__file__), 'db_connection.log'), encoding='utf-8'),  # Add encoding='utf-8'
        logging.StreamHandler()
    ]
)
#logger = logging.get#logger('db_connection')

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
        # Load environment variables
        load_dotenv()
        
        #logger.info("Attempting to establish database connection")
        
        # Get DATABASE_URL from .env
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            #logger.error("Missing DATABASE_URL environment variable")
            raise ValueError("Missing required environment variable: DATABASE_URL")
        
        # Parse the PostgreSQL URL
        parsed_url = urlparse(database_url)
        if parsed_url.scheme != 'postgresql':
            #logger.error(f"Invalid database scheme: {parsed_url.scheme}, expected 'postgresql'")
            raise ValueError("DATABASE_URL must use 'postgresql://' scheme")
        
        host = parsed_url.hostname or 'localhost'
        user = parsed_url.username
        password = parsed_url.password
        database = parsed_url.path[1:]  # Remove leading "/"
        port = parsed_url.port or 5432
        
        # Validate parsed values
        missing_vars = []
        if not host: missing_vars.append('host')
        if not user: missing_vars.append('user')
        if not password: missing_vars.append('password')
        if not database: missing_vars.append('database')
        if missing_vars:
            #logger.error(f"Missing connection details: {', '.join(missing_vars)}")
            raise ValueError(f"Missing required connection details: {', '.join(missing_vars)}")
        
        #logger.info(f"Connecting to PostgreSQL database: {database} on {host}:{port} as {user}")
        
        # Create connection config
        config = {
            'host': host,
            'user': user,
            'password': password,
            'database': database,
            'port': port,
            'connect_timeout': 10
        }
        
        # Attempt connection
        try:
            connection = psycopg2.connect(**config)
            #logger.info("Database connection established successfully")
        except psycopg2.Error as conn_err:
            #logger.error(f"Connection error: {str(conn_err)}")
            raise
        
        if not connection:
            #logger.error("Connection object created but not connected")
            raise Exception("Connection object created but not connected")
        
        # Test the connection with a simple query
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT 1")
            cursor.fetchone()
            #logger.debug("Connection test query executed successfully")
        except psycopg2.Error as query_err:
            #logger.error(f"Connection test query failed: {str(query_err)}")
            raise
        finally:
            cursor.close()
        
        return connection
        
    except psycopg2.Error as err:
        if isinstance(err, psycopg2.OperationalError):
            if "authentication failed" in str(err):
                #logger.error("Authentication failed: Invalid username or password")
                raise ValueError("Access denied: Please check your username and password")
            elif "database" in str(err) and "does not exist" in str(err):
                #logger.error(f"Database does not exist: {str(err)}")
                raise ValueError("Database does not exist")
            elif "connection" in str(err):
                #logger.error(f"Connection error: {str(err)}")
                raise ValueError("Can't connect to PostgreSQL server. Check if: 1) PostgreSQL service is running 2) Host/port are correct 3) Firewall is not blocking")
        #logger.error(f"PostgreSQL error: {str(err)}")
        raise
        
    except Exception as e:
        #logger.error(f"Connection failed: {str(e)}")
        #logger.error(traceback.format_exc())
        raise ValueError(f"Connection failed: {str(e)}")

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
        #logger.info(f"Attempting to insert {len(transactions_df)} transactions for user {user_id}")
        connection = get_db_connection()
        
        # Check if connection is open using psycopg2's 'closed' attribute
        if connection.closed != 0:
            #logger.error("Database connection failed - not connected")
            return False
            
        cursor = connection.cursor()  # Remove prepared=True, psycopg2 handles parameterization by default
        #logger.debug("Cursor created successfully")

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
                #logger.debug(f"Processing transaction row {index + 1}")
                
                transaction_date = row["Tarih"]
                #logger.debug(f"Transaction date: {transaction_date}, type: {type(transaction_date)}")
                
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
                
                #logger.debug(f"Executing SQL query for row {index + 1}")
                cursor.execute(insert_query, values)
                #logger.debug(f"Row {index + 1} inserted successfully")
                
            except psycopg2.Error as err:
                #logger.error(f"PostgreSQL Error processing row {index + 1}: {str(err)}")
                #logger.error(f"Row data: {row.to_dict()}")
                success = False
                continue
            except Exception as e:
                #logger.error(f"Unexpected error processing row {index + 1}: {str(e)}")
                #logger.error(f"Row data: {row.to_dict()}")
                #logger.error(traceback.format_exc())
                success = False
                continue

        if success:
            #logger.info("Committing transaction...")
            connection.commit()
            #logger.info("Transaction committed successfully")
        else:
            #logger.warning("Rolling back due to errors...")
            connection.rollback()
            #logger.info("Transaction rolled back")
        
    except psycopg2.Error as err:
        #logger.error(f"PostgreSQL Error: {str(err)}")
        success = False
        if connection:
            connection.rollback()
            #logger.info("Transaction rolled back due to PostgreSQL error")
    except Exception as e:
        #logger.error(f"Unexpected error in insert_transactions: {str(e)}")
        #logger.error(traceback.format_exc())
        success = False
        if connection:
            connection.rollback()
            #logger.info("Transaction rolled back due to unexpected error")
    finally:
        #logger.debug("Closing database resources...")
        if cursor:
            cursor.close()
            #logger.debug("Cursor closed")
        if connection and not connection.closed:
            connection.close()
            #logger.debug("Connection closed")

    return success

def insert_dividends(dividends_df, user_id):
    #logger.info(f"Attempting to insert {len(dividends_df)} dividend records for user {user_id}")
    
    connection = None
    cursor = None
    success = True

    try:
        connection = get_db_connection()
        if not connection:
            #logger.error("Failed to get database connection")
            return False
            
        cursor = connection.cursor()
        #logger.debug("Database cursor created successfully")

        insert_query = """
        INSERT INTO Dividend (
            paymentDate, symbol, grossAmount, taxWithheld,
            netAmount, userId, createdAt, updatedAt
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s
        )
        """

        for index, row in dividends_df.iterrows():
            try:
                #logger.debug(f"Processing dividend row {index + 1}")
                
                try:
                    payment_date = datetime.strptime(row["Ödeme Tarihi"].strip(), "%d/%m/%y")
                except Exception as date_error:
                    #logger.error(f"Error parsing dividend payment date '{row['Ödeme Tarihi']}': {str(date_error)}")
                    payment_date = datetime.now()  # Fallback to current date
                
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
                
                #logger.debug(f"Executing SQL insert for dividend {index + 1}, symbol: {values[1]}")
                cursor.execute(insert_query, values)
                #logger.debug(f"Dividend {index + 1} inserted successfully")
                
            except Exception as e:
                #logger.error(f"Error inserting dividend row {index + 1}: {str(e)}")
                #logger.error(f"Row data: {row.to_dict() if hasattr(row, 'to_dict') else row}")
                #logger.error(traceback.format_exc())
                success = False
                continue

        if success:
            #logger.info("Committing dividend batch")
            connection.commit()
            #logger.info("Dividend batch committed successfully")
        else:
            #logger.warning("Rolling back dividend batch due to errors")
            connection.rollback()
            #logger.info("Dividend batch rolled back")
            
    except Exception as e:
        #logger.error(f"Unexpected error in insert_dividends: {str(e)}")
        #logger.error(traceback.format_exc())
        success = False
        if connection:
            #logger.info("Rolling back due to unexpected error")
            connection.rollback()
    finally:
        #logger.debug("Closing database resources")
        if cursor:
            cursor.close()
            #logger.debug("Cursor closed")
        if connection:
            connection.close()
            #logger.debug("Connection closed")

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