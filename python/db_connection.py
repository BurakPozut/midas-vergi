import psycopg2  # Add PostgreSQL connector
import psycopg2.extras  # Add PostgreSQL extras for DictCursor
from datetime import datetime
import locale
import os
from dotenv import load_dotenv
from logger import get_logger

# Initialize logger
logger = get_logger('db_connection')

# Load environment variables
load_dotenv()
logger.info("Environment variables loaded")

# Set locale to handle Turkish characters
try:
    locale.setlocale(locale.LC_ALL, 'tr_TR.UTF-8')
    logger.info("Set locale to tr_TR.UTF-8")
except locale.Error:
    try:
        locale.setlocale(locale.LC_ALL, 'Turkish_Turkey.1254')
        logger.info("Set locale to Turkish_Turkey.1254")
    except locale.Error:
        try:
            locale.setlocale(locale.LC_ALL, 'tr_TR')
            logger.info("Set locale to tr_TR")
        except locale.Error:
            logger.warning("Could not set Turkish locale, using default")
            locale.setlocale(locale.LC_ALL, '')


def get_db_connection():
    try:
        # Load environment variables
        load_dotenv()
        
        # Get PostgreSQL environment variables
        host = os.getenv('PG_HOST', '127.0.0.1')
        user = os.getenv('PG_USER', 'postgres')
        password = os.getenv('PG_PASSWORD', '')
        database = os.getenv('PG_DATABASE', 'midas_tax')
        port = int(os.getenv('PG_PORT', '5432'))
        
        logger.debug(f"Connecting to PostgreSQL database: {database} on {host}:{port}")
        
        # Create PostgreSQL connection
        connection = psycopg2.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=port
        )
        
        logger.info("PostgreSQL database connection established")
        return connection
        
        # Comment out MySQL connection code
        """
        # Get MySQL environment variables
        host = os.getenv('MYSQL_HOST', 'localhost')
        user = os.getenv('MYSQL_USER', 'root')
        password = os.getenv('MYSQL_PASSWORD', '')
        database = os.getenv('MYSQL_DATABASE', 'taxdb')
        # port = int(os.getenv('MYSQL_PORT', '3306'))
        
        # logger.debug(f"Connecting to database: {database} on {host}:{port}")
        
        # Create connection
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            # port=port
        )
        
        logger.info("Database connection established")
        return connection
        """
    except psycopg2.Error as err:
        logger.error(f"PostgreSQL database connection error: {err}", exc_info=True)
        return None
    except Exception as err:
        logger.error(f"General database connection error: {err}", exc_info=True)
        return None

def safe_float(value):
    try:
        if value is None or (isinstance(value, str) and value.strip() == ''):
            return 0.0
        return float(value)
    except (ValueError, TypeError) as e:
        logger.warning(f"Error converting value '{value}' to float: {str(e)}")
        return 0.0

def insert_transactions(transactions_df, user_id):
    connection = None
    success = True
    
    logger.info(f"Inserting {len(transactions_df)} transactions for user {user_id}")
    
    try:
        connection = get_db_connection()
        if not connection:
            logger.error("Failed to establish database connection")
            return False
        
        cursor = connection.cursor()
        
        # Add diagnostic code to check tables
        try:
            logger.info("Checking available tables in the database...")
            # Modify for PostgreSQL syntax
            cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
            tables = cursor.fetchall()
            logger.info(f"Available tables: {[t[0] for t in tables]}")
            
        except Exception as e:
            logger.error(f"Error checking tables: {str(e)}", exc_info=True)
        
        # Define the SQL query
        insert_query = """
        INSERT INTO "Transaction" (
            date, "transactionType", symbol, "operationType", 
            status, currency, "orderQuantity", "orderAmount", 
            "executedQuantity", "averagePrice", "transactionFee", "transactionAmount",
            "userId", "createdAt", "updatedAt"
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        logger.debug("SQL query prepared")

        for index, row in transactions_df.iterrows():
            try:
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
                
                cursor.execute(insert_query, values)
                logger.debug(f"Inserted transaction: {transaction_date} - {row['Sembol']} - {row['İşlem Tipi']}")
                
            except psycopg2.Error as err:
                logger.error(f"PostgreSQL Error processing row {index}: {str(err)}")
                success = False
                continue
        
        if success:
            connection.commit()
            logger.info("All transactions committed to database")
        else:
            logger.warning("Some transactions failed to insert, partial commit performed")
            connection.commit()  # Commit successful ones
            
    except Exception as e:
        logger.error(f"Error in insert_transactions: {str(e)}", exc_info=True)
        success = False
        
    finally:
        if connection:
            if 'cursor' in locals():
                cursor.close()
            connection.close()
            logger.debug("Database connection closed")
        
        return success

def insert_dividends(dividends_df, user_id):
    logger.info(f"Inserting {len(dividends_df)} dividend records for user {user_id}")
    
    connection = None
    success = True
    
    try:
        connection = get_db_connection()
        if not connection:
            logger.error("Failed to establish database connection")
            return False
        
        cursor = connection.cursor()
        
        # Define the SQL query
        insert_query = """
        INSERT INTO "Dividend" (
            "paymentDate", symbol, "grossAmount", "taxWithheld",
            "netAmount", "userId", "createdAt", "updatedAt"
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        logger.debug("SQL query prepared for dividends")
        
        for index, row in dividends_df.iterrows():
            try:
                # Handle the payment date
                payment_date = row["Ödeme Tarihi"]
                
                # If payment_date is already a datetime object, use it directly
                if isinstance(payment_date, datetime):
                    logger.debug(f"Payment date is already a datetime: {payment_date}")
                else:
                    # Try to parse the date if it's a string
                    try:
                        # Check if the date is in the format DD/MM/YY
                        date_str = str(payment_date).strip()
                        if len(date_str) == 8 and date_str[2] == '/' and date_str[5] == '/':
                            day = int(date_str[0:2])
                            month = int(date_str[3:5])
                            year = int(date_str[6:8])
                            
                            # Adjust the year (assuming 20xx for years less than 50, 19xx otherwise)
                            if year < 50:
                                year += 2000
                            else:
                                year += 1900
                                
                            # Create a datetime object
                            payment_date = datetime(year, month, day)
                            logger.debug(f"Parsed payment date: {date_str} -> {payment_date}")
                        else:
                            # Try standard parsing as fallback
                            payment_date = datetime.strptime(date_str, "%d/%m/%y")
                            logger.debug(f"Parsed payment date with strptime: {date_str} -> {payment_date}")
                    except Exception as e:
                        logger.warning(f"Error parsing payment date '{payment_date}': {str(e)}")
                        # Use current date as fallback
                        payment_date = datetime.now()
                        logger.warning(f"Using current date as fallback: {payment_date}")
                
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
                logger.debug(f"Inserted dividend: {payment_date} - {row['Sermaya Piyasası Aracı']} - {row['Net Temettü Tutarı']}")
                
            except psycopg2.Error as err:
                logger.error(f"PostgreSQL Error processing dividend row {index}: {str(err)}")
                success = False
                continue
        
        if success:
            connection.commit()
            logger.info("All dividend records committed to database")
        else:
            logger.warning("Some dividend records failed to insert, partial commit performed")
            connection.commit()  # Commit successful ones
            
    except Exception as e:
        logger.error(f"Error in insert_dividends: {str(e)}", exc_info=True)
        success = False
        
    finally:
        if connection:
            if 'cursor' in locals():
                cursor.close()
            connection.close()
            logger.debug("Database connection closed")
        
        return success

def get_user_dividends(user_id):
    connection = get_db_connection()
    cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    try:
        cursor.execute('SELECT * FROM "Dividend" WHERE "userId" = %s', (user_id,))
        dividends = cursor.fetchall()
        return dividends
    finally:
        cursor.close()
        connection.close()

def get_user_transactions(user_id):
    connection = get_db_connection()
    cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    try:
        cursor.execute('SELECT * FROM "Transaction" WHERE "userId" = %s', (user_id,))
        transactions = cursor.fetchall()
        return transactions
    finally:
        cursor.close()
        connection.close()

def check_transactions_in_db(user_id):
    """Check if transactions for a user exist in the database and return details"""
    connection = None
    try:
        connection = get_db_connection()
        if not connection:
            logger.error("Failed to establish database connection")
            return False
        
        cursor = connection.cursor()
        
        # Check Transaction table
        try:
            logger.info("Checking Transaction table for user_id: " + user_id)
            cursor.execute('SELECT COUNT(*) FROM "Transaction" WHERE "userId" = %s', (user_id,))
            transaction_count = cursor.fetchone()[0]
            logger.info(f"Found {transaction_count} transactions for user {user_id}")
            
            if transaction_count > 0:
                # Get sample transactions
                cursor.execute("""
                    SELECT date, symbol, "operationType", "executedQuantity", "averagePrice", currency 
                    FROM "Transaction" 
                    WHERE "userId" = %s 
                    ORDER BY date DESC 
                    LIMIT 5
                """, (user_id,))
                
                sample_transactions = cursor.fetchall()
                logger.info("Sample transactions:")
                for tx in sample_transactions:
                    logger.info(f"  {tx[0]} - {tx[1]} - {tx[2]} - {tx[3]} {tx[1]} @ {tx[4]} {tx[5]}")
            
            # Check Dividend table
            cursor.execute('SELECT COUNT(*) FROM "Dividend" WHERE "userId" = %s', (user_id,))
            dividend_count = cursor.fetchone()[0]
            logger.info(f"Found {dividend_count} dividend records for user {user_id}")
            
            if dividend_count > 0:
                # Get sample dividends
                cursor.execute("""
                    SELECT "paymentDate", symbol, "grossAmount", "taxWithheld", "netAmount" 
                    FROM "Dividend" 
                    WHERE "userId" = %s 
                    ORDER BY "paymentDate" DESC 
                    LIMIT 5
                """, (user_id,))
                
                sample_dividends = cursor.fetchall()
                logger.info("Sample dividends:")
                for div in sample_dividends:
                    logger.info(f"  {div[0]} - {div[1]} - Gross: {div[2]}, Tax: {div[3]}, Net: {div[4]}")
            
            return {
                "transaction_count": transaction_count,
                "dividend_count": dividend_count
            }
            
        except Exception as e:
            logger.error(f"Error checking transactions: {str(e)}", exc_info=True)
            return False
            
    except Exception as e:
        logger.error(f"Error in check_transactions_in_db: {str(e)}", exc_info=True)
        return False
        
    finally:
        if connection:
            if 'cursor' in locals():
                cursor.close()
            connection.close()
            logger.debug("Database connection closed")