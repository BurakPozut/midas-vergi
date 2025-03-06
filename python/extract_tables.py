import pdfplumber
import pandas as pd
import os
import sys
import locale
from db_connection import insert_transactions, insert_dividends, get_db_connection
import json
from datetime import datetime
import logging
import traceback

# logging.basicConfig(
#     level=logging.DEBUG,
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#     handlers=[
#         logging.FileHandler(os.path.join(os.path.dirname(__file__), 'db_connection.log'), encoding='utf-8'),  # Add encoding='utf-8'
#         logging.StreamHandler()
#     ]
# )
# #logger = logging.get#logger('db_connection')

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
    except (ValueError, TypeError) as e:
        #logger.error(f"Error cleaning number value '{value}': {str(e)}")
        return 0.0

def parse_date(date_str):
    try:
        return datetime.strptime(date_str.strip(), "%d/%m/%y %H:%M:%S")
    except Exception as e:
        #logger.error(f"Error parsing date '{date_str}': {str(e)}")
        return None

def extract_tables_and_save(pdf_path, user_id, target_title_prefix="YATIRIM İŞLEMLERİ"):
    try:
        #logger.info(f"Starting extraction from PDF: {pdf_path} for user: {user_id}")
        
        # Validate PDF exists
        if not os.path.exists(pdf_path):
            #logger.error(f"PDF file not found: {pdf_path}")
            return {
                "success": False,
                "error": f"PDF dosyası bulunamadı: {pdf_path}",
                "hasData": False
            }

        all_rows = []
        all_rows_dividend = []
        
        # Extract data from PDF
        try:
            #logger.info("Opening PDF with pdfplumber")
            with pdfplumber.open(pdf_path) as pdf:
                #logger.info(f"PDF opened successfully. Total pages: {len(pdf.pages)}")
                
                for page_num, page in enumerate(pdf.pages, 1):
                    #logger.info(f"Processing page {page_num}/{len(pdf.pages)}")
                    tables = page.extract_tables()
                    #logger.info(f"Found {len(tables)} tables on page {page_num}")
                    
                    for table_num, table in enumerate(tables, 1):
                        if table and table[0] and len(table[0]) > 0 and table[0][0]:
                            #logger.info(f"Table {table_num} header: '{table[0][0]}'")
                            
                            # Process investment transactions
                            if target_title_prefix in table[0][0]:
                                #logger.info(f"Found investment transactions table with {len(table)} rows")
                                for row_idx, row in enumerate(table[2:], 3):
                                    if len(row) >= 12 and any(cell and str(cell).strip() for cell in row):
                                        try:
                                            cleaned_row = [
                                                parse_date(row[0]) if i == 0 else
                                                clean_number(row[i]) if i in [6,7,8,9,10,11] else
                                                str(row[i]).strip()
                                                for i in range(len(row))
                                            ]
                                            if cleaned_row[0]:
                                                all_rows.append(cleaned_row)
                                                #logger.debug(f"Added transaction row: {cleaned_row}")
                                            # else:
                                                #logger.warning(f"Skipped row {row_idx} due to invalid date: {row[0]}")
                                        except Exception as row_error:
                                            print(f"Error processing row {row_idx}: {str(row_error)}")
                                            #logger.error(f"Error processing row {row_idx}: {str(row_error)}")
                                            #logger.error(f"Row data: {row}")
                            
                            # Process dividend transactions
                            elif "TEMETTÜ İŞLEMLERİ" in table[0][0]:
                                #logger.info(f"Found dividend transactions table with {len(table)} rows")
                                for row_idx, row in enumerate(table[2:], 3):
                                    if len(row) >= 5 and any(cell and str(cell).strip() for cell in row):
                                        try:
                                            cleaned_row = [
                                                # parse_date(row[0]) if i == 0 else
                                                clean_number(row[i]) if i in [2,3,4] else
                                                str(row[i]).strip()
                                                for i in range(len(row))
                                            ]
                                            if cleaned_row[0]:
                                                all_rows_dividend.append(cleaned_row)
                                                #logger.debug(f"Added dividend row: {cleaned_row}")
                                            # else:
                                                #logger.warning(f"Skipped dividend row {row_idx} due to invalid data: {row[0]}")
                                        except Exception as row_error:
                                            print(f"Error processing dividend row {row_idx}: {str(row_error)}")
                                            #logger.error(f"Error processing dividend row {row_idx}: {str(row_error)}")
                                            #logger.error(f"Row data: {row}")
        except Exception as pdf_error:
            #logger.error(f"PDF reading error: {str(pdf_error)}")
            #logger.error(traceback.format_exc())
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

        #logger.info(f"Extracted {len(df)} transaction rows and {len(df_dividend)} dividend rows")
        
        success_messages = []

        # Process regular transactions
        if not df.empty:
            try:
                #logger.info(f"Inserting {len(df)} transactions into database")
                if not insert_transactions(df, user_id):
                    #logger.error("Failed to insert transactions into database")
                    return {
                        "success": False,
                        "error": "Veritabanına işlemler kaydedilirken hata oluştu",
                        "hasData": True
                    }
                #logger.info("Successfully inserted transactions into database")
                success_messages.append("işlemler")
            except Exception as db_error:
                #logger.error(f"Database error (transactions): {str(db_error)}")
                #logger.error(traceback.format_exc())
                return {
                    "success": False,
                    "error": f"Veritabanı hatası (işlemler): {str(db_error)}",
                    "hasData": True
                }

        # Process dividend transactions
        if not df_dividend.empty:
            try:
                #logger.info(f"Inserting {len(df_dividend)} dividend records into database")
                if not insert_dividends(df_dividend, user_id):
                    #logger.error("Failed to insert dividend data into database")
                    return {
                        "success": False,
                        "error": "Veritabanına temettü verileri kaydedilirken hata oluştu",
                        "hasData": True
                    }
                #logger.info("Successfully inserted dividend data into database")
                success_messages.append("temettü verileri")
            except Exception as db_error:
                #logger.error(f"Database error (dividends): {str(db_error)}")
                #logger.error(traceback.format_exc())
                return {
                    "success": False,
                    "error": f"Veritabanı hatası (temettü): {str(db_error)}",
                    "hasData": True
                }
        
        # Handle no data case
        if df.empty and df_dividend.empty:
            #logger.warning(f"No transaction or dividend data found in {pdf_path}")
            return {
                "success": True,
                "message": f"{pdf_path} dosyasında işlem ve temettü verisi bulunamadı",
                "hasData": False
            }
        
        # Return success with appropriate message
        #logger.info(f"Successfully processed PDF: {pdf_path}")
        return {
            "success": True,
            "message": f"{pdf_path} dosyasından {' ve '.join(success_messages)} başarıyla kaydedildi",
            "hasData": True
        }
    except Exception as e:
        #logger.error(f"PDF processing error: {str(e)}")
        #logger.error(traceback.format_exc())
        return {
            "success": False,
            "error": f"PDF işleme hatası: {str(e)}",
            "hasData": False
        }

if __name__ == "__main__":
    try:
        if len(sys.argv) < 3:
            #logger.error("Insufficient arguments provided")
            sys.exit("Usage: python extract_tables.py <pdf_path> <user_id>")
        
        pdf_path = sys.argv[1]
        user_id = sys.argv[2]
        
        #logger.info(f"Starting PDF extraction process for file: {pdf_path}, user: {user_id}")
        result = extract_tables_and_save(pdf_path, user_id)
        
        # Print result as JSON for the calling process
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
        if not result["success"]:
            #logger.error(f"Process failed: {result.get('error', 'Unknown error')}")
            sys.exit(1)
        # else:
            #logger.info("Process completed successfully")
    except Exception as e:
        #logger.critical(f"Unhandled exception: {str(e)}")
        #logger.critical(traceback.format_exc())
        print(json.dumps({
            "success": False,
            "error": f"Beklenmeyen hata: {str(e)}",
            "hasData": False
        }, ensure_ascii=False, indent=2))
        sys.exit(1)                        