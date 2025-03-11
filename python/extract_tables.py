import pdfplumber
import pandas as pd
import os
import sys
import locale
from db_connection import insert_transactions, insert_dividends, get_db_connection, check_transactions_in_db
import json
from datetime import datetime
from logger import get_logger

# Initialize logger
logger = get_logger('extract_tables')

# Set UTF-8 encoding
os.environ['PYTHONIOENCODING'] = 'utf-8'
if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Set locale to handle Turkish characters
try:
    locale.setlocale(locale.LC_ALL, 'tr_TR.UTF-8')
    logger.info("Set locale to tr_TR.UTF-8")
except locale.Error:
    try:
        locale.setlocale(locale.LC_ALL, 'Turkish_Turkey.1254')
        logger.info("Set locale to Turkish_Turkey.1254")
    except locale.Error:
        try:
            locale.setlocale(locale.LC_ALL, 'tr_TR')
            logger.info("Set locale to tr_TR")
        except locale.Error:
            locale.setlocale(locale.LC_ALL, '')
            logger.warning("Failed to set Turkish locale, using default")

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
        logger.warning(f"Error converting value '{value}' to float: {str(e)}")
        return 0.0

def parse_date(date_str):
    try:
        return datetime.strptime(date_str.strip(), "%d/%m/%y %H:%M:%S")
    except Exception as e:
        logger.warning(f"Error parsing date '{date_str}': {str(e)}")
        return None

def parse_dividend_date(date_str):
    """Parse dividend date in format DD/MM/YY"""
    try:
        # Clean the date string
        date_str = date_str.strip()
        
        # Check if the date is in the format DD/MM/YY
        if len(date_str) == 8 and date_str[2] == '/' and date_str[5] == '/':
            day = int(date_str[0:2])
            month = int(date_str[3:5])
            year = int(date_str[6:8])
            
            # Adjust the year (assuming 20xx for years less than 50, 19xx otherwise)
            if year < 50:
                year += 2000
            else:
                year += 1900
                
            # Create a datetime object
            return datetime(year, month, day)
        else:
            # Try standard parsing as fallback
            return datetime.strptime(date_str, "%d/%m/%y")
    except Exception as e:
        logger.warning(f"Error parsing dividend date '{date_str}': {str(e)}")
        # Return the original string if parsing fails
        return date_str

def extract_tables_and_save(pdf_path, user_id, target_title_prefix="YATIRIM İŞLEMLERİ"):
    logger.info(f"Starting extraction for PDF: {pdf_path}, User ID: {user_id}")
    try:
        #logger.info(f"Starting extraction from PDF: {pdf_path} for user: {user_id}")
        
        # Validate PDF exists
        if not os.path.exists(pdf_path):
            logger.error(f"PDF file not found: {pdf_path}")
            return {
                "success": False,
                "error": f"PDF dosyası bulunamadı: {pdf_path}",
                "hasData": False
            }

        all_rows = []
        all_rows_dividend = []
        
        # Extract data from PDF
        try:
            logger.info(f"Opening PDF with pdfplumber: {pdf_path}")
            with pdfplumber.open(pdf_path) as pdf:
                logger.info(f"PDF opened successfully, processing {len(pdf.pages)} pages")
                for page_num, page in enumerate(pdf.pages, 1):
                    logger.debug(f"Processing page {page_num}")
                    tables = page.extract_tables()
                    logger.debug(f"Found {len(tables)} tables on page {page_num}")
                    
                    for table_num, table in enumerate(tables, 1):
                        if table and table[0] and len(table[0]) > 0 and table[0][0]:
                            logger.debug(f"Processing table {table_num} with header: '{table[0][0]}'")
                            
                            # Process investment transactions
                            if target_title_prefix in table[0][0]:
                                logger.info(f"Found investment transactions table: {table[0][0]}")
                                for row_idx, row in enumerate(table[2:], 2):
                                    if len(row) >= 12 and any(cell and str(cell).strip() for cell in row):
                                        cleaned_row = [
                                            parse_date(row[0]) if i == 0 else
                                            clean_number(row[i]) if i in [6,7,8,9,10,11] else
                                            str(row[i]).strip()
                                            for i in range(len(row))
                                        ]
                                        if cleaned_row[0]:
                                            all_rows.append(cleaned_row)
                                            logger.debug(f"Added transaction row {row_idx}: {cleaned_row[0]} - {cleaned_row[2]}")
                            
                            # Process dividend transactions
                            elif "TEMETTÜ İŞLEMLERİ" in table[0][0]:
                                logger.info(f"Found dividend transactions table: {table[0][0]}")
                                for row_idx, row in enumerate(table[2:], 2):
                                    if len(row) >= 5 and any(cell and str(cell).strip() for cell in row):
                                        cleaned_row = [
                                            parse_dividend_date(row[0]) if i == 0 else
                                            clean_number(row[i]) if i in [2,3,4] else
                                            str(row[i]).strip()
                                            for i in range(len(row))
                                        ]
                                        if cleaned_row[0]:
                                            all_rows_dividend.append(cleaned_row)
                                            logger.debug(f"Added dividend row {row_idx}: {cleaned_row[0]} - {cleaned_row[1]}")
        except Exception as pdf_error:
            logger.error(f"PDF reading error: {str(pdf_error)}", exc_info=True)
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

        logger.info(f"Extracted {len(df)} transaction rows and {len(df_dividend)} dividend rows")

        success_messages = []

        # Process regular transactions
        if not df.empty:
            try:
                logger.info(f"Inserting {len(df)} transactions into database")
                if not insert_transactions(df, user_id):
                    logger.error("Failed to insert transactions into database")
                    return {
                        "success": False,
                        "error": "Veritabanına işlemler kaydedilirken hata oluştu",
                        "hasData": True
                    }
                logger.info("Successfully inserted transactions into database")
                success_messages.append("işlemler")
            except Exception as db_error:
                logger.error(f"Database error (transactions): {str(db_error)}", exc_info=True)
                return {
                    "success": False,
                    "error": f"Veritabanı hatası (işlemler): {str(db_error)}",
                    "hasData": True
                }

        # Process dividend transactions
        if not df_dividend.empty:
            try:
                logger.info(f"Inserting {len(df_dividend)} dividend records into database")
                if not insert_dividends(df_dividend, user_id):
                    logger.error("Failed to insert dividend data into database")
                    return {
                        "success": False,
                        "error": "Veritabanına temettü verileri kaydedilirken hata oluştu",
                        "hasData": True
                    }
                logger.info("Successfully inserted dividend data into database")
                success_messages.append("temettü verileri")
            except Exception as db_error:
                logger.error(f"Database error (dividends): {str(db_error)}", exc_info=True)
                return {
                    "success": False,
                    "error": f"Veritabanı hatası (temettü): {str(db_error)}",
                    "hasData": True
                }
        
        # Handle no data case
        if df.empty and df_dividend.empty:
            logger.info(f"No transaction or dividend data found in {pdf_path}")
            return {
                "success": True,
                "message": f"{pdf_path} dosyasında işlem ve temettü verisi bulunamadı",
                "hasData": False
            }
        
        # Return success with appropriate message
        success_msg = f"{pdf_path} dosyasından {' ve '.join(success_messages)} başarıyla kaydedildi"
        logger.info(success_msg)
        return {
            "success": True,
            "message": success_msg,
            "hasData": True
        }
    except Exception as e:
        logger.error(f"PDF processing error: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": f"PDF işleme hatası: {str(e)}",
            "hasData": False
        }

if __name__ == "__main__":
    logger.info("Script started from command line")
    if len(sys.argv) < 3:
        logger.error("Insufficient arguments provided")
        sys.exit("Usage: python extract_tables.py <pdf_path> <user_id>")
    
    pdf_path = sys.argv[1]
    user_id = sys.argv[2]
    
    logger.info(f"Processing file: {pdf_path} for user: {user_id}")
    result = extract_tables_and_save(pdf_path, user_id)
    logger.info(f"Processing result: {json.dumps(result, ensure_ascii=False)}")
    
    # Output only the JSON result for the wrapper script to parse
    print(json.dumps(result, ensure_ascii=False))
    
    # After processing, check if the data was inserted correctly
    if result["success"] and result.get("hasData", False):
        logger.info("Checking if data was inserted correctly...")
        db_check = check_transactions_in_db(user_id)
        if db_check:
            logger.info(f"Database check result: {json.dumps(db_check)}")
        else:
            logger.warning("Database check failed")
    
    if not result["success"]:
        logger.error(f"Processing failed: {result.get('error', 'Unknown error')}")
        sys.exit(1)
    
    logger.info("Script completed successfully")                        