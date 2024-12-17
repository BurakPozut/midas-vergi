# main.py
from sort_files import sort_files
from extract_tables import extract_tables_and_save
from inflation_calculator import get_inflation,calculate_inflation


# # Directory containing the PDF files
# directory_path = 'D:/midas-vergi/ekstreler/'

# # Call the sorting script
# print("Starting file sorting...")
# sort_files(directory_path)

# # Call the extraction script
# output_path = 'yatirim_islemleri_extracted.xlsx'
# print("Starting table extraction...")
# extract_tables_and_save(directory_path, output_path)

# # Call the inflation calculator
inflation_value = calculate_inflation()
print(f"in main: {inflation_value}")
