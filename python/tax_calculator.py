import pandas as pd
from datetime import datetime
import locale
from collections import deque
from get_dolar import get_dolar
from inflation_calculator import calculate_inflation, get_previous_month
import sys
from commission_calculator import get_commissions

inflation_threshold = 10

try:
    locale.setlocale(locale.LC_TIME, "tr_TR.UTF-8")  # For Unix/Linux systems
except locale.Error:
    locale.setlocale(locale.LC_TIME, "Turkish_Turkey.1254")  # For Windows systems

def tax_calculator():
    # Load your Excel file
    file_path = "yatirim_islemleri_extracted.xlsx"
    df = pd.read_excel(file_path)

    # Ensure numeric columns are properly converted
    df["Ortalama İşlem Fiyatı"] = df["Ortalama İşlem Fiyatı"].str.replace(",", ".").astype(float)
    df["Gerçekleşen Adet"] = df["Gerçekleşen Adet"].str.replace(",", ".").astype(float)

    # Convert "Tarih" column to match the database format
    def format_date(date_string):
        # Parse the original date string into a datetime object
        date_object = datetime.strptime(date_string, "%d/%m/%y %H:%M:%S")
        # Reformat it to "DD.MM.YYYY"
        return date_object.strftime("%d.%m.%Y")

    # Apply the conversion to the "Tarih" column
    df["Formatted Tarih"] = df["Tarih"].apply(format_date)

    # Convert "Ortalama İşlem Fiyatı" to TRY
    def convert_avg_price_to_try(row):
        formatted_date = row["Formatted Tarih"]  # Use the reformatted date
        exchange_rate = get_dolar(formatted_date)  # Fetch exchange rate using the formatted date
        if exchange_rate:
            return row["Ortalama İşlem Fiyatı"] * exchange_rate  # Convert to TRY
        else:
            raise ValueError(f"Exchange rate not found for date {formatted_date}")

    # Apply conversion to the "Ortalama İşlem Fiyatı" column
    df["Ortalama İşlem Fiyatı (TRY)"] = df.apply(convert_avg_price_to_try, axis=1)

    # Filter "Satış" and "Alış" transactions
    sell_transactions = df[df["İşlem Tipi"] == "Satış"]
    buy_transactions = df[df["İşlem Tipi"] == "Alış"]

    # Initialize a dictionary to track FIFO queues and profit/loss for each symbol
    fifo_queues = {}
    profit_loss = {}

    net_profit = 0.0
    net_loss = 0.0

    # Populate FIFO queues for each "Alış" (buy) transaction
    for _, row in buy_transactions.iterrows():
        symbol = row["Sembol"]
        quantity = row["Gerçekleşen Adet"]  # Number of stocks bought
        price = row["Ortalama İşlem Fiyatı (TRY)"]  # Price per stock
        buy_date = datetime.strptime(row["Tarih"], "%d/%m/%y %H:%M:%S")
        # price = row["Ortalama İşlem Fiyatı"]  # Price per stock
        
        if quantity > 0:
            if symbol not in fifo_queues:
                fifo_queues[symbol] = deque()  # Initialize a queue for the symbol
            fifo_queues[symbol].append({"quantity": quantity, "price": price, "date": buy_date})

    # Process each "Satış" (sell) transaction using FIFO method
    for _, row in sell_transactions.iterrows():
        symbol = row["Sembol"]
        sell_quantity = row["Gerçekleşen Adet"]  # Number of stocks sold
        sell_price = row["Ortalama İşlem Fiyatı (TRY)"]  # Price per stock
        sell_date = datetime.strptime(row["Tarih"], "%d/%m/%y %H:%M:%S")
        # sell_price = row["Ortalama İşlem Fiyatı"]  # Price per stock

        if symbol not in fifo_queues or not fifo_queues[symbol]:
            print(f"No available purchases for symbol {symbol} to match the sale.")
            continue

        total_profit = 0.0
        remaining_sell_quantity = sell_quantity
        print(f"Processing sale of {sell_quantity} stocks for symbol {symbol} at price {sell_price} TRY")

        # Match sell quantity using FIFO
        while remaining_sell_quantity > 0 and fifo_queues[symbol]:
            buy = fifo_queues[symbol][0]  # Get the oldest purchase
            buy_quantity = buy["quantity"]
            buy_price = buy["price"]
            buy_date = buy["date"]
            # print(f"buy date: {buy_date}")

            # Get inflation-adjusted buy price
            buy_year, buy_month = buy_date.year, buy_date.month - 1 # - 1 for index
            # print(f"--- /// Buy Year: {buy_year}, Buy Month: {buy_month}")
            sell_year, sell_month = sell_date.year, sell_date.month - 1

            # prev_sell_year, prev_sell_month = get_previous_month(sell_year, sell_month)

            inflation_rate = calculate_inflation(buy_year, buy_month, sell_year, sell_month - 1) # -1 for previous month

            if inflation_rate and inflation_rate > inflation_threshold:
                print(f"before inflation: {buy_price}")
                buy_price *= (1 + inflation_rate / 100)  # Adjust buy price
                print(f"after inflation: {buy_price}")

            if buy_quantity <= remaining_sell_quantity:
                # Fully consume this purchase
                profit = (sell_price - buy_price) * buy_quantity
                total_profit += profit
                remaining_sell_quantity -= buy_quantity
                fifo_queues[symbol].popleft()  # Remove fully consumed purchase
                print(f"-- {symbol} Matched purchase of {buy_quantity} stocks at price {buy_price} TRY")
            else:
                # Partially consume this purchase
                profit = (sell_price - buy_price) * remaining_sell_quantity
                total_profit += profit
                buy["quantity"] -= remaining_sell_quantity  # Update remaining quantity in queue
                remaining_sell_quantity = 0
                print(f"-- {symbol} Matched purchase of {remaining_sell_quantity} stocks at price {buy_price} TRY")
        if remaining_sell_quantity > 0:
            print(f"\n Remaining stocks: {remaining_sell_quantity} \n")
        # if remaining_sell_quantity > 0:
        print("\n")

        # Store the profit/loss for this symbol
        if symbol in profit_loss:
            profit_loss[symbol] += total_profit
        else:
            profit_loss[symbol] = total_profit

        if total_profit > 0:
            net_profit += total_profit
        else:
            net_loss += total_profit

    # Print profit/loss for each symbol
    for symbol, profit in profit_loss.items():
        print(f"{symbol}: {profit:.2f}")

    print(f"Total profit: {net_profit:.2f}")
    print(f"Total loss: {net_loss:.2f}")
    print(f"Total profit/loss: {sum(profit_loss.values()):.2f}")
    # Total Profit Loss after commissions
    print(f"Total Profit Loss after commissions: {sum(profit_loss.values()) - get_commissions():.2f}")
