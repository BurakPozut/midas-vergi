import os
from dotenv import load_dotenv
import psycopg2
from urllib.parse import urlparse
import logging

# Configure logging (same as your script)
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(os.path.dirname(__file__), 'db_connection_test.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('db_connection_test')

# Load environment variables
load_dotenv()

def get_db_connection():
    try:
        # Load environment variables
        load_dotenv()
        
        # Get DATABASE_URL from .env
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            logger.error("Missing required environment variable: DATABASE_URL")
            raise ValueError("Missing required environment variable: DATABASE_URL")
        
        # Parse the PostgreSQL URL
        parsed_url = urlparse(database_url)
        if parsed_url.scheme != 'postgresql':
            logger.error(f"Invalid database scheme: {parsed_url.scheme}, must be postgresql")
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
            logger.error(f"Missing required connection details: {', '.join(missing_vars)}")
            raise ValueError(f"Missing required connection details: {', '.join(missing_vars)}")
        
        # Create connection config
        config = {
            'host': host,
            'user': user,
            'password': password,
            'database': database,
            'port': port,
            'connect_timeout': 10
        }
        
        logger.info(f"Attempting to connect to PostgreSQL at {host}:{port}/{database}")
        
        # Attempt connection
        try:
            connection = psycopg2.connect(**config)
            logger.info("Successfully connected to PostgreSQL database")
        except psycopg2.Error as conn_err:
            logger.error(f"Failed to connect to PostgreSQL: {str(conn_err)}")
            raise
        
        if not connection:
            logger.error("Connection object created but not connected")
            raise Exception("Connection object created but not connected")
        
        # Test the connection with a simple query
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            logger.debug(f"Connection test query result: {result}")
        except psycopg2.Error as query_err:
            logger.error(f"Connection test query failed: {str(query_err)}")
            raise
        finally:
            cursor.close()
        
        return connection
        
    except psycopg2.Error as err:
        if isinstance(err, psycopg2.OperationalError):
            error_msg = str(err)
            if "authentication failed" in error_msg:
                logger.error("Authentication failed: Please check username and password")
                raise ValueError("Access denied: Please check your username and password")
            elif "database" in error_msg and "does not exist" in error_msg:
                logger.error(f"Database does not exist: {error_msg}")
                raise ValueError("Database does not exist")
            elif "connection" in error_msg:
                logger.error(f"Connection error: {error_msg}")
                raise ValueError("Can't connect to PostgreSQL server. Check if: 1) PostgreSQL service is running 2) Host/port are correct 3) Firewall is not blocking")
        logger.error(f"PostgreSQL error: {str(err)}")
        raise
        
    except Exception as e:
        logger.error(f"Connection failed: {str(e)}")
        raise ValueError(f"Connection failed: {str(e)}")

# Test the connection
if __name__ == "__main__":
    connection = None
    try:
        logger.info("Starting database connection test...")
        connection = get_db_connection()
        print("✅ Database connection test passed!")
        logger.info("Database connection test passed")
    except Exception as e:
        print(f"❌ Database connection test failed: {str(e)}")
        logger.error(f"Database connection test failed: {str(e)}")
    finally:
        if connection and not connection.closed:
            connection.close()
            logger.debug("Connection closed")