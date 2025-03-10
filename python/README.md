# Python Scripts

This directory contains Python scripts used by the application. Below is a description of the active scripts and their purposes.

## Active Scripts

### PDF Processing

- **extract_tables.py** - Extracts transaction and dividend data from PDF files uploaded by users. Called by the Node.js upload API.

### Database Operations

- **db_connection.py** - Provides database connection and utility functions for all Python scripts. Supports PostgreSQL database.
- **insert_test_data.py** - Utility script for inserting test data into the database (development only).

### Financial Calculations

- **tax_calculator_db.py** - Calculates tax obligations based on transaction data from the database.
- **get_commission_db.py** - Calculates commission fees based on transaction data.
- **get_dolar.py** - Retrieves USD/TRY exchange rates from the database.
- **inflation_calculator.py** - Calculates inflation adjustments for tax calculations.

## Database Configuration

The application now uses PostgreSQL as the primary database. The connection settings are configured in the `.env` file:

```
PG_HOST="127.0.0.1"
PG_PORT="5432"
PG_USER="postgres"
PG_PASSWORD="your_password"
PG_DATABASE="midas_tax"
```

## Usage

Most of these scripts are called from the Node.js application as child processes. The primary entry point is `extract_tables.py`, which is called when users upload PDF files.

## Development

To run these scripts directly for testing:

```bash
# Process a PDF file
python extract_tables.py /path/to/pdf user_id

# Test database connection
python test_pg_connection.py

# Install required packages
pip install -r requirements.txt
```

Note: Unused or deprecated scripts have been moved to an archive directory and excluded from the Git repository.
