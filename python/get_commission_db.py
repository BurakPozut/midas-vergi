from db_connection import get_user_transactions
from get_dolar import get_dolar

def get_commissions_db(user_id):
    try:
        transactions = get_user_transactions(user_id)
        if not transactions:
            return 0.0
            
        total_commission = 0.0
        
        for transaction in transactions:
            commission = transaction.get('transactionFee', 0.0)
            if isinstance(commission, (int, float)):
                # Convert commission to TRY if the transaction is in USD
                if transaction.get('currency') == 'USD':
                    date = transaction.get('date')
                    formatted_date = date.strftime("%d.%m.%Y")
                    exchange_rate = get_dolar(formatted_date)
                    if exchange_rate:
                        commission = float(commission) * exchange_rate
                total_commission += float(commission)
        
        return total_commission
        
    except Exception as e:
        return 0.0

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python get_commission_db.py <user_id>")
        sys.exit(1)
        
    user_id = sys.argv[1]
    total_commission = get_commissions_db(user_id)
    print(f"Total commissions: {total_commission:.2f} TRY") 