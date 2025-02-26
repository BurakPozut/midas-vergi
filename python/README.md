# Python Scripts

This directory contains Python scripts used by the application. Below is a description of the active scripts and their purposes.

## Active Scripts

### PDF Processing

- **extract_tables.py** - Extracts transaction and dividend data from PDF files uploaded by users. Called by the Node.js upload API.

### Database Operations

- **db_connection.py** - Provides database connection and utility functions for all Python scripts.
- **insert_test_data.py** - Utility script for inserting test data into the database (development only).

### Financial Calculations

- **tax_calculator_db.py** - Calculates tax obligations based on transaction data from the database.
- **get_commission_db.py** - Calculates commission fees based on transaction data.
- **get_dolar.py** - Retrieves USD/TRY exchange rates from the database.
- **inflation_calculator.py** - Calculates inflation adjustments for tax calculations.

## Usage

Most of these scripts are called from the Node.js application as child processes. The primary entry point is `extract_tables.py`, which is called when users upload PDF files.

## Development

To run these scripts directly for testing:

```bash
# Process a PDF file
python extract_tables.py /path/to/pdf user_id

# Test database connection
python test_db_connection.py
```

Note: Unused or deprecated scripts have been moved to an archive directory and excluded from the Git repository.
