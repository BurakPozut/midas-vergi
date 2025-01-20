from db_connection import get_db_connection
from datetime import datetime

def insert_test_data():
    connection = get_db_connection()
    cursor = connection.cursor()
    
    # Use the existing user ID
    user_id = "c4e4a95e-322e-444e-b230-e1bb4190ccc3"

    try:
        print("\n=== Inserting Test Data ===")
        print(f"\n👤 Using existing user ID: {user_id}")

        # Insert test exchange rates
        print("\n📈 Adding exchange rates...")
        dolar_query = """
        INSERT INTO Dolar (gecerliOlduguTarih, dovizAlis) VALUES (%s, %s)
        """
        dolar_data = [
            ("20.12.2023", 29.50),
            ("21.12.2023", 29.55),
            ("22.12.2023", 29.60),
        ]
        for rate in dolar_data:
            try:
                cursor.execute(dolar_query, rate)
                print(f"✅ Added exchange rate for {rate[0]}: {rate[1]}")
            except Exception as e:
                print(f"⚠️  Skipping duplicate exchange rate for {rate[0]}")

        # Insert test inflation data
        print("\n📊 Adding inflation data...")
        yiufe_query = """
        INSERT INTO YiUfe (yil, ocak, subat, mart, nisan, mayis, haziran, 
                          temmuz, agustos, eylul, ekim, kasim, aralik) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        yiufe_data = [
            (2023, 100.0, 101.0, 102.0, 103.0, 104.0, 105.0, 106.0, 107.0, 108.0, 109.0, 110.0, 111.0),
            (2024, 112.0, 113.0, 114.0, 115.0, 116.0, 117.0, 118.0, 119.0, 120.0, 121.0, 122.0, 123.0),
        ]
        for year_data in yiufe_data:
            try:
                cursor.execute(yiufe_query, year_data)
                print(f"✅ Added inflation data for year {year_data[0]}")
            except Exception as e:
                print(f"⚠️  Skipping duplicate inflation data for year {year_data[0]}")

        # Insert test transactions
        print("\n💰 Adding test transactions...")
        transaction_query = """
        INSERT INTO Transaction (
            date, transactionType, symbol, operationType, status, currency,
            orderQuantity, orderAmount, executedQuantity, averagePrice,
            transactionFee, transactionAmount, userId, createdAt, updatedAt
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        """
        
        # Test transactions for THYAO
        transactions = [
            # Buy THYAO
            (datetime(2023, 12, 20, 10, 30), "Hisse", "THYAO", "Alış", "Gerçekleşti", "TRY",
             100, 25000, 100, 250, 25, 25025, user_id, datetime.now(), datetime.now()),
            # Sell THYAO
            (datetime(2023, 12, 22, 14, 45), "Hisse", "THYAO", "Satış", "Gerçekleşti", "TRY",
             100, 27000, 100, 270, 27, 26973, user_id, datetime.now(), datetime.now()),
        ]

        for tx in transactions:
            try:
                cursor.execute(transaction_query, tx)
                print(f"✅ Added {tx[3]} transaction for {tx[2]}")
            except Exception as e:
                print(f"⚠️  Error adding transaction: {e}")

        # Commit all changes
        connection.commit()
        print("\n✅ All test data inserted successfully!")

    except Exception as e:
        print(f"\n❌ Error inserting test data: {e}")
        connection.rollback()
    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    insert_test_data() 