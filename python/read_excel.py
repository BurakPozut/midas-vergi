import pandas as pd

# Load your Excel file
file_path = "yatirim_islemleri_extracted.xlsx"
df = pd.read_excel(file_path)

# Ensure numeric columns are properly converted
df["Ortalama İşlem Fiyatı"] = df["Ortalama İşlem Fiyatı"].str.replace(",", ".").astype(float)
df["İşlem Tutarı"] = df["İşlem Tutarı"].str.replace(",", ".").astype(float)

# Replace non-numeric values in "Emir Adedi" with 0 (e.g., '-') and convert to numeric
df["Emir Adedi"] = pd.to_numeric(df["Emir Adedi"], errors="coerce").fillna(0)

# Filter rows where "İşlem Tipi" is "Satış"
filtered_df = df[df["İşlem Tipi"] == "Satış"]

# Initialize a dictionary to track profit/loss for each symbol
profit_loss = {}

# Loop through each "Satış" transaction
for _, row in filtered_df.iterrows():
    symbol = row["Sembol"]
    sell_quantity = row["Emir Adedi"]  # Number of stocks sold
    sell_amount = row["İşlem Tutarı"]  # Dollar amount from the sale
    sell_price = row["Ortalama İşlem Fiyatı"]  # Price per stock

    # Get all "Alış" transactions for the same symbol
    buy_transactions = df[(df["Sembol"] == symbol) & (df["İşlem Tipi"] == "Alış")]

    # Calculate total purchase quantity and total cost
    total_buy_quantity = buy_transactions["Emir Adedi"].sum()  # Total stocks purchased
    total_buy_amount = buy_transactions["İşlem Tutarı"].sum()  # Total dollars spent on purchases

    # Handle cases where "Emir Adedi" is 0 (fallback to "Emir Tutarı")
    if total_buy_quantity > 0:
        avg_buy_price = total_buy_amount / total_buy_quantity  # Average price per stock
        profit = (sell_price - avg_buy_price) * sell_quantity
    else:
        profit = sell_amount - total_buy_amount  # Fall back to dollar amount calculation

    # Store the profit/loss for this symbol
    if symbol in profit_loss:
        profit_loss[symbol] += profit  # Accumulate profit/loss
    else:
        profit_loss[symbol] = profit

# Print profit/loss for each symbol
for symbol, profit in profit_loss.items():
    print(f"{symbol}: {profit:.2f}")



# import pandas as pd

# # Path to the Excel file
# file_path = "yatirim_islemleri_extracted.xlsx"

# # Read the Excel file into a DataFrame
# df = pd.read_excel(file_path)
# filtered_df = df[df["İşlem Tipi"] == "Satış"]

# first_selled = filtered_df[0].get("Sembol")

# # Print the content of the DataFrame
# print(first_selled)
