import locale
from datetime import datetime
from collections import deque
from get_dolar import get_dolar
from inflation_calculator import calculate_inflation
from db_connection import get_user_transactions
from get_commission_db import get_commissions_db
import json
import sys

inflation_threshold = 10

try:
    locale.setlocale(locale.LC_TIME, "tr_TR.UTF-8")  # For Unix/Linux systems
except locale.Error:
    locale.setlocale(locale.LC_TIME, "Turkish_Turkey.1254")  # For Windows systems

def tax_calculator_db(user_id):
    print("\n=== Starting Tax Calculation ===")
    # Get transactions from database
    transactions = get_user_transactions(user_id)
    
    if not transactions:
        # print("No transactions found for the user")
        return None

    print(f"\nFound {len(transactions)} total transactions")
    
    # Separate buy and sell transactions
    sell_transactions = [t for t in transactions if t['operationType'] == "Satış"]
    buy_transactions = [t for t in transactions if t['operationType'] == "Alış"]
    
    print(f"Buy transactions: {len(buy_transactions)}")
    print(f"Sell transactions: {len(sell_transactions)}")

    # Initialize tracking dictionaries
    fifo_queues = {}
    profit_loss = {}
    net_profit = 0.0
    net_loss = 0.0

    print("\n=== Processing Buy Transactions ===")
    # Process buy transactions
    for transaction in buy_transactions:
        symbol = transaction['symbol']
        quantity = float(transaction['executedQuantity'])
        date = transaction['date']
        price = float(transaction['averagePrice'])
        
        print(f"\nProcessing buy: {symbol}")
        print(f"Original price: {price} {transaction['currency']}")
        
        # Convert price to TRY if needed
        if transaction['currency'] == 'USD':
            formatted_date = date.strftime("%d.%m.%Y")
            exchange_rate = get_dolar(formatted_date)
            if exchange_rate:
                price *= exchange_rate
                print(f"Converted price: {price} TRY (rate: {exchange_rate})")

        if quantity > 0:
            if symbol not in fifo_queues:
                fifo_queues[symbol] = deque()
            fifo_queues[symbol].append({"quantity": quantity, "price": price, "date": date})
            print(f"Added to queue: {quantity} units at {price} TRY")

    print("\n=== Processing Sell Transactions ===")
    # Process sell transactions
    for transaction in sell_transactions:
        symbol = transaction['symbol']
        sell_quantity = float(transaction['executedQuantity'])
        sell_date = transaction['date']
        sell_price = float(transaction['averagePrice'])
        
        print(f"\nProcessing sell: {symbol}")
        print(f"Original sell price: {sell_price} {transaction['currency']}")
        
        # Convert sell price to TRY if needed
        if transaction['currency'] == 'USD':
            formatted_date = sell_date.strftime("%d.%m.%Y")
            exchange_rate = get_dolar(formatted_date)
            if exchange_rate:
                sell_price *= exchange_rate
                print(f"Converted sell price: {sell_price} TRY (rate: {exchange_rate})")

        if symbol not in fifo_queues or not fifo_queues[symbol]:
            print(f"No available purchases for symbol {symbol} to match the sale.")
            continue

        total_profit = 0.0
        remaining_sell_quantity = sell_quantity
        print(f"Need to sell: {remaining_sell_quantity} units")

        while remaining_sell_quantity > 0 and fifo_queues[symbol]:
            buy = fifo_queues[symbol][0]
            buy_quantity = buy["quantity"]
            buy_price = buy["price"]
            buy_date = buy["date"]

            print(f"\nMatching with buy: {buy_quantity} units at {buy_price} TRY")

            # Calculate inflation adjustment
            buy_year, buy_month = buy_date.year, buy_date.month - 1
            sell_year, sell_month = sell_date.year, sell_date.month - 1
            inflation_rate = calculate_inflation(buy_year, buy_month, sell_year, sell_month - 1)

            if inflation_rate and inflation_rate > inflation_threshold:
                print(f"Applying inflation adjustment: {inflation_rate}%")
                print(f"Price before adjustment: {buy_price}")
                buy_price *= (1 + inflation_rate / 100)
                print(f"Price after adjustment: {buy_price}")

            if buy_quantity <= remaining_sell_quantity:
                profit = (sell_price - buy_price) * buy_quantity
                total_profit += profit
                remaining_sell_quantity -= buy_quantity
                fifo_queues[symbol].popleft()
                print(f"Used entire buy lot. Profit: {profit:.2f} TRY")
                print(f"Remaining to sell: {remaining_sell_quantity}")
            else:
                profit = (sell_price - buy_price) * remaining_sell_quantity
                total_profit += profit
                buy["quantity"] -= remaining_sell_quantity
                remaining_sell_quantity = 0
                print(f"Used partial buy lot. Profit: {profit:.2f} TRY")
                print(f"Remaining in buy lot: {buy['quantity']}")

        print(f"\nTotal profit for this sale: {total_profit:.2f} TRY")

        # Update profit/loss tracking
        if symbol in profit_loss:
            profit_loss[symbol] += total_profit
        else:
            profit_loss[symbol] = total_profit

        if total_profit > 0:
            net_profit += total_profit
        else:
            net_loss += total_profit

    print("\n=== Final Calculations ===")
    print("\nProfit/Loss by Symbol:")
    for symbol, profit in profit_loss.items():
        print(f"{symbol}: {profit:.2f} TRY")

    total_pl = sum(profit_loss.values())
    print(f"\nTotal profit/loss before commissions: {total_pl:.2f} TRY")
    
    commission = get_commissions_db(user_id)
    print(f"Total commissions: {commission:.2f} TRY")
    
    final_pl = total_pl - commission
    print(f"Total profit/loss after commissions: {final_pl:.2f} TRY")

    results = {
        "profit_loss_by_symbol": profit_loss,
        "total_profit": net_profit,
        "total_loss": net_loss,
        "total_profit_loss": total_pl,
        "total_profit_loss_after_commissions": final_pl
    }

    # Print the JSON result for the Node.js endpoint to capture
    print(json.dumps(results))
    return results

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python tax_calculator_db.py <user_id>")
        sys.exit(1)
    
    user_id = sys.argv[1]
    results = tax_calculator_db(user_id)
    if results:
        print("\n=== Results as JSON ===")
        print(json.dumps(results, indent=2)) 