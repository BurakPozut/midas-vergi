from db_connection import db

months = [
    "OCAK", "ŞUBAT", "MART", "NİSAN", "MAYIS", "HAZİRAN",
    "TEMMUZ", "AĞUSTOS", "EYLÜL", "EKİM", "KASIM", "ARALIK"
]

# Function to get previous month and year
def get_previous_month(year, month):
    if month == 0: # Handle case for January
        return year - 1, "ARALIK"
    else:
        return year, months[month]

# Function to get inflation for a specific year and month
def get_inflation(year, month):
    collection = db["YiUfe"]
    query = {"YIL": year}
    result = collection.find_one(query)
    if result:
        return result.get(month)
    print(f"No inflation data found for {month} {year}")
    return None


def calculate_inflation(first_year, first_month, second_year, second_month):
    # print(f"Calculating inflation between {months[first_month]} {first_year} and {months[second_month]} {second_year}...")
    inflation_start = get_inflation(first_year, months[first_month])
    inflation_end = get_inflation(second_year, months[second_month])
    
    if inflation_start and inflation_end:
        inflation_rate = (inflation_end - inflation_start) / inflation_start * 100
        # print(f"Inflation rate between {months[first_month]} {first_year} and {months[second_month]} {second_year}: {inflation_rate:.2f}%")
        return inflation_rate
    print("Inflation calculation failed.")
    return None
