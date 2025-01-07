import pdfplumber
import pandas as pd
import os
import sys
import locale
from db_connection import insert_transactions
import json

os.environ['PYTHONIOENCODING'] = 'utf-8'

# Force UTF-8 encoding
if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

def extract_tables_and_save(pdf_path, user_id, target_title_prefix="YATIRIM İŞLEMLERİ"):
    try:
        # Initialize a list to store all rows
        all_rows = []
        
        # Extract data from PDF
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                for table in tables:
                    if table and table[0][0] and target_title_prefix in table[0][0]:
                        print(f"Found matching table in {pdf_path}")
                        for row in table[2:]:  # Skip header rows
                            if len(row) >= 12:  # Ensure there are enough columns
                                # Check if row has any non-None and non-empty values
                                if any(cell and str(cell).strip() for cell in row):
                                    all_rows.append(row)

        # Define column names
        columns = [
            "Tarih", "İşlem Türü", "Sembol", "İşlem Tipi", "İşlem Durumu", "Para Birimi",
            "Emir Adedi", "Emir Tutarı", "Gerçekleşen Adet", "Ortalama İşlem Fiyatı",
            "İşlem Ücreti", "İşlem Tutarı"
        ]

        # Create DataFrame
        df = pd.DataFrame(all_rows, columns=columns)
        
        # If DataFrame is empty, it means no valid transactions were found
        if df.empty:
            print(f"No transactions found in {pdf_path}")
            return {
                "success": True,
                "message": f"No transactions found in {pdf_path}",
                "hasData": False
            }

        # Insert into MongoDB only if we have valid transactions
        insert_success = insert_transactions(df, user_id)
        if insert_success:
            print(f"Data extracted and saved successfully from {pdf_path}")
            return {
                "success": True,
                "message": f"Data extracted and saved successfully from {pdf_path}",
                "hasData": True
            }
        else:
            return {
                "success": False,
                "error": "Failed to insert transactions into database",
                "hasData": True
            }

    except Exception as e:
        error_msg = f"Error processing PDF: {str(e)}"
        print(error_msg)
        return {"success": False, "error": error_msg}

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python extract_tables.py <pdf_path> <user_id>")
        sys.exit(1)
        
    pdf_path = sys.argv[1]
    user_id = sys.argv[2]
    
    result = extract_tables_and_save(pdf_path, user_id)
    if not result["success"]:
        sys.exit(1)                        