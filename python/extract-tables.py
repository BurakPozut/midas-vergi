import pdfplumber
import pandas as pd
import os

# Directory containing the PDF files
directory_path = 'D:/midas-vergi/ekstreler/'
target_title_prefix = "YATIRIM İŞLEMLERİ"

# Initialize a list to store all rows from all files
all_rows = []

# Loop through each PDF file in the directory
for filename in os.listdir(directory_path):
    if filename.endswith('.pdf'):
        file_path = os.path.join(directory_path, filename)
        print(f"Processing file: {filename}")
        
        # Extract data from PDF
        with pdfplumber.open(file_path) as pdf:
            full_text = ''
            for page in pdf.pages:
                tables = page.extract_tables()
                for table in tables:
                  if table and table[0][0] and target_title_prefix in table[0][0]:
                    print(f"Found matching table: {table[0][0]} in {filename}")
                    for row in table[2:]:
                       print(row)
                       if len(row) >= 12:  # Ensure there are enough columns
                        all_rows.append(row + [filename])  # Add filename for tracking

# Define column names
columns = [
    "Tarih", "İşlem Türü", "Sembol", "İşlem Tipi", "İşlem Durumu", "Para Birimi",
    "Emir Adedi", "Emir Tutarı", "Gerçekleşen Adet", "Ortalama İşlem Fiyatı",
    "İşlem Ücreti", "İşlem Tutarı", "Source File"
]

# Create a DataFrame from the collected rows
df = pd.DataFrame(all_rows, columns=columns)

# Save all data to an Excel file
output_path = 'yatirim_islemleri_extracted.xlsx'
# if os.path.exists(output_path):
#     os.remove(output_path)
#     print(f"Existing file '{output_path}' has been deleted.")

df.to_excel(output_path, index=False, engine='openpyxl')
print(f"Data from all matching tables has been saved to {output_path}")                        