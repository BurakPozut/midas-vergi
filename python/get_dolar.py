from db_connection import get_db_connection

def get_dolar(tarih):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        print(f"\n🔍 Looking up exchange rate for date: {tarih}")
        # Query to find the exchange rate for the given date
        query = "SELECT dovizAlis FROM Dolar WHERE gecerliOlduguTarih = %s"
        cursor.execute(query, (tarih,))
        
        result = cursor.fetchone()
        
        if result:
            rate = result['dovizAlis']
            print(f"💱 Exchange rate found: {rate}")
            return rate
        else:
            print(f"⚠️  No exchange rate found for date: {tarih}")
            return None
            
    except Exception as e:
        print(f"\n❌ Error getting exchange rate: {e}")
        return None
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()