import pdfplumber
import pandas as pd
import os
import sys
import locale
from db_connection import insert_transactions, insert_dividends, get_db_connection
import json
from datetime import datetime

# Set UTF-8 encoding
os.environ['PYTHONIOENCODING'] = 'utf-8'
if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Set locale to handle Turkish characters
try:
    locale.setlocale(locale.LC_ALL, 'tr_TR.UTF-8')
except locale.Error:
    try:
        locale.setlocale(locale.LC_ALL, 'Turkish_Turkey.1254')
    except locale.Error:
        try:
            locale.setlocale(locale.LC_ALL, 'tr_TR')
        except locale.Error:
            locale.setlocale(locale.LC_ALL, '')

def clean_number(value):
    try:
        if value == '-' or value == '' or value is None:
            return 0.0
            
        if isinstance(value, str):
            # Remove currency symbols and whitespace
            value = value.replace('TL', '').replace('USD', '').strip()
            
            # Handle Turkish number format (1.234,56 -> 1234.56)
            # First, remove thousand separators
            parts = value.split(',')
            if len(parts) == 2:
                # If there's a comma, treat it as decimal separator
                integer_part = parts[0].replace('.', '')
                decimal_part = parts[1]
                value = f"{integer_part}.{decimal_part}"
            else:
                # No comma found, just remove dots (thousand separators)
                value = value.replace('.', '')
                
        return float(value)
    except (ValueError, TypeError):
        return 0.0

def parse_date(date_str):
    try:
        return datetime.strptime(date_str.strip(), "%d/%m/%y %H:%M:%S")
    except Exception:
        return None

def extract_tables_and_save(pdf_path, user_id, target_title_prefix="YATIRIM İŞLEMLERİ"):
    try:
        # Validate PDF exists
        if not os.path.exists(pdf_path):
            return {
                "success": False,
                "error": f"PDF dosyası bulunamadı: {pdf_path}",
                "hasData": False
            }

        all_rows = []
        all_rows_dividend = []
        
        # Extract data from PDF
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    tables = page.extract_tables()
                    for table in tables:
                        if table and table[0] and len(table[0]) > 0 and table[0][0]:
                            # Process investment transactions
                            # print(f"\nTable {table[0][0]} header: '{table[0][0]}'")
                            if target_title_prefix in table[0][0]:
                                for row in table[2:]:
                                    if len(row) >= 12 and any(cell and str(cell).strip() for cell in row):
                                        cleaned_row = [
                                            parse_date(row[0]) if i == 0 else
                                            clean_number(row[i]) if i in [6,7,8,9,10,11] else
                                            str(row[i]).strip()
                                            for i in range(len(row))
                                        ]
                                        if cleaned_row[0]:
                                            all_rows.append(cleaned_row)
                            
                            # Process dividend transactions
                            elif "TEMETTÜ İŞLEMLERİ" in table[0][0]:
                                # print(f"\n=== Dividends ===")
                                # print(table)
                                for row in table[2:]:
                                    if len(row) >= 5 and any(cell and str(cell).strip() for cell in row):
                                        cleaned_row = [
                                            # parse_date(row[0]) if i == 0 else
                                            clean_number(row[i]) if i in [2,3,4] else
                                            str(row[i]).strip()
                                            for i in range(len(row))
                                        ]
                                        if cleaned_row[0]:
                                            all_rows_dividend.append(cleaned_row)
        except Exception as pdf_error:
            return {
                "success": False,
                "error": f"PDF okuma hatası: {str(pdf_error)}",
                "hasData": False
            }

        # Define column names
        columns = [
            "Tarih", "İşlem Türü", "Sembol", "İşlem Tipi", "İşlem Durumu", "Para Birimi",
            "Emir Adedi", "Emir Tutarı", "Gerçekleşen Adet", "Ortalama İşlem Fiyatı",
            "İşlem Ücreti", "İşlem Tutarı"
        ]
        columns_dividend = [
            "Ödeme Tarihi", "Sermaya Piyasası Aracı", "Brüt Temettü Tutarı", "Stopaj*", "Net Temettü Tutarı"
        ]

        # Create DataFrames
        df = pd.DataFrame(all_rows, columns=columns)
        df_dividend = pd.DataFrame(all_rows_dividend, columns=columns_dividend)

        # print(f"\n=== Result ===")
        # print(f"Transactions: {df.to_string()}")
        # print(f"Dividends: {df_dividend.to_string()}")

        success_messages = []

        # Process regular transactions
        if not df.empty:
            try:
                if not insert_transactions(df, user_id):
                    return {
                        "success": False,
                        "error": "Veritabanına işlemler kaydedilirken hata oluştu",
                        "hasData": True
                    }
                success_messages.append("işlemler")
            except Exception as db_error:
                return {
                    "success": False,
                    "error": f"Veritabanı hatası (işlemler): {str(db_error)}",
                    "hasData": True
                }

        # Process dividend transactions
        if not df_dividend.empty:
            try:
                if not insert_dividends(df_dividend, user_id):
                    return {
                        "success": False,
                        "error": "Veritabanına temettü verileri kaydedilirken hata oluştu",
                        "hasData": True
                    }
                success_messages.append("temettü verileri")
            except Exception as db_error:
                return {
                    "success": False,
                    "error": f"Veritabanı hatası (temettü): {str(db_error)}",
                    "hasData": True
                }
        
        # Handle no data case
        if df.empty and df_dividend.empty:
            return {
                "success": True,
                "message": f"{pdf_path} dosyasında işlem ve temettü verisi bulunamadı",
                "hasData": False
            }
        
        # Return success with appropriate message
        return {
            "success": True,
            "message": f"{pdf_path} dosyasından {' ve '.join(success_messages)} başarıyla kaydedildi",
            "hasData": True
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"PDF işleme hatası: {str(e)}",
            "hasData": False
        }

if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit("Usage: python extract_tables.py <pdf_path> <user_id>")
    
    pdf_path = sys.argv[1]
    user_id = sys.argv[2]
    
    result = extract_tables_and_save(pdf_path, user_id)
    # print(json.dumps(result, ensure_ascii=False, indent=2))
    if not result["success"]:
        sys.exit(1)                        