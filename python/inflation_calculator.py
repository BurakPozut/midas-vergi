from pymongo import MongoClient

def get_inflation(year, month):
    # Connect to MongoDB
  mongo_uri = "mongodb+srv://burakpozut88:Dx4HNRwrvf8GBfhK@cluster0.h0fnumk.mongodb.net/"
  client = MongoClient(mongo_uri)

  # Access the database and collection
  db = client["ExchangeRate"]  # Replace with your database name
  collection = db["YiUfe"]  # Replace with your collection name

  # Find the document with the given year
  query = {"YIL": year}
  result = collection.find_one(query)

  # Extract the value for the specified month
  if result:
      month_value = result.get(month)  # Use .get() to safely access the month field
      if month_value is not None:
          return month_value
        #   print(f"The value for {month} in {year} is: {month_value}")
      else:
          print(f"The month '{month}' does not exist in the document.")
  else:
      print(f"No document found for the year {year}.")


def calculate_inflation():
    # Get the inflation values for March 2021 and March 2022
    inflation_2021 = get_inflation(2024, "ŞUBAT")
    inflation_2022 = get_inflation(2024, "MART")
    
    # Calculate the inflation rate
    inflation_rate = (inflation_2022 - inflation_2021) / inflation_2021 * 100
    
    # Print the inflation rate
    print(f"The inflation rate between March 2021 and March 2022 is: {inflation_rate:.2f}%")
