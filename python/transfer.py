import os
from dotenv import load_dotenv
import mysql.connector
import psycopg2
from urllib.parse import urlparse

def get_mysql_connection():
    try:
        load_dotenv()
        config = {
            'host': os.getenv('MYSQL_HOST', 'localhost'),
            'user': os.getenv('MYSQL_USER'),
            'password': os.getenv('MYSQL_PASSWORD'),
            'database': os.getenv('MYSQL_DATABASE'),
            'connect_timeout': 10
        }
        missing = [key for key, value in config.items() if not value]
        if missing:
            raise ValueError(f"Missing MySQL env vars: {', '.join(missing)}")
        connection = mysql.connector.connect(**config)
        if not connection.is_connected():
            raise Exception("MySQL connection failed")
        return connection
    except mysql.connector.Error as e:
        raise Exception(f"MySQL connection error: {str(e)}")

def get_postgres_connection():
    try:
        load_dotenv()
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            raise ValueError("Missing DATABASE_URL")
        parsed_url = urlparse(database_url)
        config = {
            'host': parsed_url.hostname or 'localhost',
            'user': parsed_url.username,
            'password': parsed_url.password,
            'database': parsed_url.path[1:],
            'port': parsed_url.port or 5432,
            'connect_timeout': 10
        }
        missing = [key for key, value in config.items() if not value]
        if missing:
            raise ValueError(f"Missing PostgreSQL connection details: {', '.join(missing)}")
        connection = psycopg2.connect(**config)
        if not connection:
            raise Exception("PostgreSQL connection failed")
        return connection
    except psycopg2.Error as e:
        raise Exception(f"PostgreSQL connection error: {str(e)}")

def transfer_table(mysql_conn, pg_conn, mysql_table, pg_table, column_mapping):
    try:
        # Fetch data from MySQL
        mysql_cursor = mysql_conn.cursor()
        mysql_cursor.execute(f"SELECT * FROM {mysql_table}")
        rows = mysql_cursor.fetchall()
        mysql_columns = [desc[0] for desc in mysql_cursor.description]
        
        if not rows:
            print(f"No data found in MySQL table '{mysql_table}'")
            return
        
        # Map MySQL columns to PostgreSQL columns (ensure quotes)
        pg_columns = [f'"{column_mapping[col]}"' for col in mysql_columns]  # Explicitly quote each column
        placeholders = ', '.join(['%s'] * len(pg_columns))
        insert_query = f'INSERT INTO "{pg_table}" ({", ".join(pg_columns)}) VALUES ({placeholders})'
        
        # Debug: Print the query to verify
        print(f"Generated INSERT query: {insert_query}")
        
        # Insert data into PostgreSQL
        pg_cursor = pg_conn.cursor()
        pg_cursor.executemany(insert_query, rows)
        pg_conn.commit()
        
        print(f"Transferred {len(rows)} rows from MySQL '{mysql_table}' to PostgreSQL '{pg_table}'")
        
    except mysql.connector.Error as e:
        raise Exception(f"MySQL error during transfer: {str(e)}")
    except psycopg2.Error as e:
        pg_conn.rollback()
        raise Exception(f"PostgreSQL error during transfer: {str(e)}")
    finally:
        mysql_cursor.close()
        pg_cursor.close()

def main():
    mysql_conn = None
    pg_conn = None
    try:
        mysql_conn = get_mysql_connection()
        pg_conn = get_postgres_connection()
        
        # Column mappings (MySQL -> PostgreSQL, exact camelCase match)
        dolar_mapping = {
            "id": "id",
            "gecerliOlduguTarih": "gecerliOlduguTarih",
            "dovizAlis": "dovizAlis"
        }
        yiufe_mapping = {
            "id": "id",
            "yil": "yil",
            "ocak": "ocak",
            "subat": "subat",
            "mart": "mart",
            "nisan": "nisan",
            "mayis": "mayis",
            "haziran": "haziran",
            "temmuz": "temmuz",
            "agustos": "agustos",
            "eylul": "eylul",
            "ekim": "ekim",
            "kasim": "kasim",
            "aralik": "aralik"
        }
        
        transfer_table(mysql_conn, pg_conn, "dolar", "Dolar", dolar_mapping)
        transfer_table(mysql_conn, pg_conn, "yiufe", "YiUfe", yiufe_mapping)
        
        print("Data transfer completed successfully!")
        
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        if mysql_conn and mysql_conn.is_connected():
            mysql_conn.close()
        if pg_conn and not pg_conn.closed:
            pg_conn.close()

if __name__ == "__main__":
    main()