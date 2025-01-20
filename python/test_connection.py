from db_connection import get_db_connection

def main():
    try:
        # Try to get a connection
        connection = get_db_connection()
        
        # If we get here, connection was successful
        print("\nTesting queries...")
        
        # Create a cursor
        cursor = connection.cursor()
        
        # Test some queries
        print("\nListing tables:")
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        for table in tables:
            print(f"- {table[0]}")
            
            # Show table structure
            print(f"\nStructure of {table[0]}:")
            cursor.execute(f"DESCRIBE {table[0]}")
            columns = cursor.fetchall()
            for column in columns:
                print(f"  - {column[0]}: {column[1]}")
        
        # Clean up
        cursor.close()
        connection.close()
        print("\n✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        raise

if __name__ == "__main__":
    main() 