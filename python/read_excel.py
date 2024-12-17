import pandas as pd
from collections import deque

# Load your Excel file
file_path = "yatirim_islemleri_extracted.xlsx"
df = pd.read_excel(file_path)

# Ensure numeric columns are properly converted
df["Ortalama İşlem Fiyatı"] = df["Ortalama İşlem Fiyatı"].str.replace(",", ".").astype(float)
df["İşlem Tutarı"] = df["İşlem Tutarı"].str.replace(",", ".").astype(float)
df["Emir Adedi"] = pd.to_numeric(df["Emir Adedi"], errors="coerce").fillna(0)

# Filter "Satış" and "Alış" transactions
sell_transactions = df[df["İşlem Tipi"] == "Satış"]
buy_transactions = df[df["İşlem Tipi"] == "Alış"]

# Initialize a dictionary to track FIFO queues and profit/loss for each symbol
fifo_queues = {}
profit_loss = {}

# Populate FIFO queues for each "Alış" (buy) transaction
for _, row in buy_transactions.iterrows():
    symbol = row["Sembol"]
    quantity = row["Emir Adedi"]  # Number of stocks bought
    price = row["Ortalama İşlem Fiyatı"]  # Price per stock
    
    if quantity > 0:
        if symbol not in fifo_queues:
            fifo_queues[symbol] = deque()  # Initialize a queue for the symbol
        fifo_queues[symbol].append({"quantity": quantity, "price": price})

# Process each "Satış" (sell) transaction using FIFO method
for _, row in sell_transactions.iterrows():
    symbol = row["Sembol"]
    sell_quantity = row["Emir Adedi"]  # Number of stocks sold
    sell_price = row["Ortalama İşlem Fiyatı"]  # Price per stock

    if symbol not in fifo_queues or not fifo_queues[symbol]:
        print(f"No available purchases for symbol {symbol} to match the sale.")
        continue

    total_profit = 0.0
    remaining_sell_quantity = sell_quantity

    # Match sell quantity using FIFO
    while remaining_sell_quantity > 0 and fifo_queues[symbol]:
        buy = fifo_queues[symbol][0]  # Get the oldest purchase
        buy_quantity = buy["quantity"]
        buy_price = buy["price"]

        if buy_quantity <= remaining_sell_quantity:
            # Fully consume this purchase
            profit = (sell_price - buy_price) * buy_quantity
            total_profit += profit
            remaining_sell_quantity -= buy_quantity
            fifo_queues[symbol].popleft()  # Remove fully consumed purchase
        else:
            # Partially consume this purchase
            profit = (sell_price - buy_price) * remaining_sell_quantity
            total_profit += profit
            buy["quantity"] -= remaining_sell_quantity  # Update remaining quantity in queue
            remaining_sell_quantity = 0

    # Store the profit/loss for this symbol
    if symbol in profit_loss:
        profit_loss[symbol] += total_profit
    else:
        profit_loss[symbol] = total_profit

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
