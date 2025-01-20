from db_connection import get_db_connection

months = [
    "ocak", "subat", "mart", "nisan", "mayis", "haziran",
    "temmuz", "agustos", "eylul", "ekim", "kasim", "aralik"
]

# Function to get previous month and year
def get_previous_month(year, month):
    if month == 0: # Handle case for January
        return year - 1, "aralik"
    else:
        return year, months[month]

# Function to get inflation for a specific year and month
def get_inflation(year, month):
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        print(f"\n🔍 Looking up inflation data for {month} {year}")
        # Query to get inflation data for the specific year and month
        query = f"SELECT {month} FROM YiUfe WHERE yil = %s"
        cursor.execute(query, (year,))
        
        result = cursor.fetchone()
        # Fetch any remaining results to avoid "unread result found" error
        while cursor.fetchone() is not None:
            pass
            
        if result:
            rate = result[month]
            print(f"📊 Inflation rate found: {rate}%")
            return rate
        else:
            print(f"⚠️  No inflation data found for {month} {year}")
            return None
            
    except Exception as e:
        print(f"\n❌ Error getting inflation data: {e}")
        return None
    finally:
        if cursor:
            try:
                # Fetch any remaining results before closing
                while cursor.fetchone() is not None:
                    pass
                cursor.close()
            except:
                pass
        if connection:
            connection.close()

def calculate_inflation(first_year, first_month, second_year, second_month):
    print(f"\n=== Calculating Inflation ===")
    print(f"From: {months[first_month]} {first_year}")
    print(f"To: {months[second_month]} {second_year}")
    
    inflation_start = get_inflation(first_year, months[first_month])
    if inflation_start is None:
        print("\n⚠️  Could not get starting inflation rate")
        return None
        
    inflation_end = get_inflation(second_year, months[second_month])
    if inflation_end is None:
        print("\n⚠️  Could not get ending inflation rate")
        return None
    
    try:
        inflation_rate = (inflation_end - inflation_start) / inflation_start * 100
        print(f"\n✅ Inflation rate calculated: {inflation_rate:.2f}%")
        return inflation_rate
    except Exception as e:
        print(f"\n❌ Error calculating inflation rate: {e}")
        return None
