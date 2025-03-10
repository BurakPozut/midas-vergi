#!/usr/bin/env python3
"""
Test script for PostgreSQL database connection
"""

from db_connection import get_db_connection
from logger import get_logger

logger = get_logger('test_pg_connection')

def test_connection():
    """Test the database connection and print available tables"""
    logger.info("Testing PostgreSQL database connection...")
    
    try:
        # Get connection
        connection = get_db_connection()
        
        if not connection:
            logger.error("Failed to establish database connection")
            return False
        
        logger.info("Database connection successful!")
        
        # Create cursor
        cursor = connection.cursor()
        
        # Check available tables
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        tables = cursor.fetchall()
        
        if tables:
            logger.info(f"Available tables: {[t[0] for t in tables]}")
        else:
            logger.warning("No tables found in the database")
        
        # Close cursor and connection
        cursor.close()
        connection.close()
        
        return True
    
    except Exception as e:
        logger.error(f"Error testing database connection: {str(e)}", exc_info=True)
        return False

if __name__ == "__main__":
    success = test_connection()
    
    if success:
        print("✅ PostgreSQL connection test successful!")
    else:
        print("❌ PostgreSQL connection test failed. Check logs for details.") 