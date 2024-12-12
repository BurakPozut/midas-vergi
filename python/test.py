import pdfplumber
import pandas as pd
import os

# Directory containing the PDF files
directory_path = 'D:/midas-vergi/ekstre_test/'

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
                print(f"tables: {page.extract_tables()}")
                full_text += page.extract_text() + '\n'
                # print(f"File text: {full_text}")
        
        # Extract the "Yatırım İşlemleri" section
        start_keyword = "İşlem Tutarı"
        end_keyword = "HESAP İŞLEMLERİ"

        start_pos = full_text.find(start_keyword) + len(start_keyword)
        end_pos = full_text.find(end_keyword)

        if start_pos != -1 and end_pos != -1:
            yatirim_islemleri = full_text[start_pos:end_pos].strip()
            
            for line in yatirim_islemleri.split('\n'):
                parts = line.split()
                if len(parts) >= 13:  # Ensure the line has enough columns
                    # Combine the first two parts to reconstruct the timestamp
                    tarih = " ".join(parts[:2])
                    islem_turu = parts[2]
                    sembol = parts[3]
                    islem_tipi = parts[4]
                    islem_durumu = parts[5]
                    para_birimi = parts[6]
                    emir_adedi = parts[7]
                    emir_tutari = parts[8]
                    gerceklesen_adet = parts[9]
                    ortalama_islem_fiyati = parts[10]
                    islem_ucreti = parts[11]
                    islem_tutari = parts[12]

                    # Append the row with an additional column for the file name
                    all_rows.append([
                        tarih, islem_turu, sembol, islem_tipi, islem_durumu, para_birimi,
                        emir_adedi, emir_tutari, gerceklesen_adet, ortalama_islem_fiyati,
                        islem_ucreti, islem_tutari, filename
                    ])
        else:
            print(f"Yatırım İşlemleri section not found in {filename}")

# Define column names
columns = [
    "Tarih", "İşlem Türü", "Sembol", "İşlem Tipi", "İşlem Durumu", "Para Birimi",
    "Emir Adedi", "Emir Tutarı", "Gerçekleşen Adet", "Ortalama İşlem Fiyatı",
    "İşlem Ücreti", "İşlem Tutarı", "Source File"
]

# Create a DataFrame
df = pd.DataFrame(all_rows, columns=columns)

# Save all data to a single Excel file
output_path = 'yatirim_islemleri_combined.xlsx'
df.to_excel(output_path, index=False, engine='openpyxl')

print(f"Data from all files has been saved to {output_path}")

# import pdfplumber
# import pandas as pd
# import re

# # Directory containing the PDF files
# directory_path = 'D:/midas-vergi/ekstreler/'

# # Path to your PDF file
# file_path = 'D:/midas-vergi/Midas_Ekstre_Ekim.pdf'

# # Extract data from PDF
# with pdfplumber.open(file_path) as pdf:
#   full_text = ''
#   for page in pdf.pages:
#       full_text = page.extract_text() + '\n'
#       # print(full_text)

# # Extract the "Yatırım İşlemleri" section
# start_keyword = "İşlem Tutarı"
# end_keyword = "HESAP İŞLEMLERİ"

# # Find the start and end positions of the relevant section
# start_pos = full_text.find(start_keyword)+len(start_keyword)
# end_pos = full_text.find(end_keyword)

# if start_pos != -1 and end_pos != -1:
#     yatirim_islemleri = full_text[start_pos:end_pos].strip()
#     print(yatirim_islemleri)
#     rows = []
#     for line in yatirim_islemleri.split('\n'):
#         print("line: ",line)
#         parts = line.split()
#         # Combine the first three parts to reconstruct the timestamp
#         tarih = " ".join(parts[:2])
#         islem_turu = parts[2]
#         sembol = parts[3]
#         islem_tipi = parts[4]
#         islem_durumu = parts[5]
#         para_birimi = parts[6]
#         emir_adedi = parts[7]
#         emir_tutari = parts[8]
#         gerceklesen_adet = parts[9]
#         ortalama_islem_fiyati = parts[10]
#         islem_ucreti = parts[11]
#         islem_tutari = parts[12]

#         # Append as a row
#         rows.append([
#             tarih, islem_turu, sembol, islem_tipi, islem_durumu, para_birimi,
#             emir_adedi, emir_tutari, gerceklesen_adet, ortalama_islem_fiyati,
#             islem_ucreti, islem_tutari
#         ])

#     # # Define column names
#     columns = [
#         "Tarih", "İşlem Türü", "Sembol", "İşlem Tipi", "İşlem Durumu", "Para Birimi",
#         "Emir Adedi", "Emir Tutarı", "Gerçekleşen Adet", "Ortalama İşlem Fiyatı",
#         "İşlem Ücreti", "İşlem Tutarı"
#     ]
#     # # Create a DataFrame
#     df = pd.DataFrame(rows, columns=columns)

#     # # Save to Excel
#     output_path = 'yatirim_islemleri.xlsx'
#     df.to_excel(output_path, index=False, engine='openpyxl')

#     print(f"Data has been saved to {output_path}")
# else:
#     print("Yatırım İşlemleri section not found.")
