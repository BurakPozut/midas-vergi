import mysql.connector
from dotenv import load_dotenv
import os

def test_database_connection():
    # Load environment variables
    load_dotenv()
    
    # Get database configuration
    config = {
        'host': os.getenv('MYSQL_HOST', 'localhost'),
        'user': os.getenv('MYSQL_USER'),
        'password': os.getenv('MYSQL_PASSWORD'),
        'database': os.getenv('MYSQL_DATABASE'),
        'auth_plugin': 'mysql_native_password'
    }
    
    print("\n=== Database Configuration ===")
    print(f"Host: {config['host']}")
    print(f"User: {config['user']}")
    print(f"Database: {config['database']}")
    
    try:
        # Attempt to establish connection
        print("\n🔄 Attempting to connect to database...")
        connection = mysql.connector.connect(**config)
        
        if connection.is_connected():
            # Get server information
            db_info = connection.get_server_info()
            cursor = connection.cursor()
            
            # Get database name
            cursor.execute("SELECT DATABASE();")
            db_name = cursor.fetchone()[0]
            
            # Get MySQL version
            cursor.execute("SELECT VERSION();")
            version = cursor.fetchone()[0]
            
            print("\n✅ Connection successful!")
            print(f"Server version: {db_info}")
            print(f"Connected to database: {db_name}")
            print(f"MySQL version: {version}")
            
            # Test a simple query
            print("\n🔄 Testing simple query...")
            cursor.execute("SHOW TABLES;")
            tables = cursor.fetchall()
            
            print("\n=== Available Tables ===")
            for table in tables:
                print(f"- {table[0]}")
            
            cursor.close()
            connection.close()
            print("\n✅ Connection closed successfully")
            return True
            
    except mysql.connector.Error as err:
        print("\n❌ Database connection error!")
        if err.errno == mysql.connector.errorcode.ER_ACCESS_DENIED_ERROR:
            print("Access denied: Check your username and password")
        elif err.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(f"Error: {err}")
        return False
        
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        return False

if __name__ == "__main__":
    test_database_connection() 