import pdfplumber
import pandas as pd
import re

# Path to your PDF file
file_path = 'D:/midas-vergi/Midas_Ekstre_Ekim.pdf'

# Extract data from PDF
with pdfplumber.open(file_path) as pdf:
  full_text = ''
  for page in pdf.pages:
      full_text = page.extract_text() + '\n'
      # print(full_text)

# Extract the "Yatırım İşlemleri" section
start_keyword = "İşlem Tutarı"
end_keyword = "HESAP İŞLEMLERİ"

# Find the start and end positions of the relevant section
start_pos = full_text.find(start_keyword)+len(start_keyword)
end_pos = full_text.find(end_keyword)

if start_pos != -1 and end_pos != -1:
    yatirim_islemleri = full_text[start_pos:end_pos].strip()
    print(yatirim_islemleri)
    rows = []
    for line in yatirim_islemleri.split('\n'):
        print("line: ",line)
        parts = line.split()
        # Combine the first three parts to reconstruct the timestamp
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

        # Append as a row
        rows.append([
            tarih, islem_turu, sembol, islem_tipi, islem_durumu, para_birimi,
            emir_adedi, emir_tutari, gerceklesen_adet, ortalama_islem_fiyati,
            islem_ucreti, islem_tutari
        ])
    # Regular expression to split each transaction into parts
    # pattern = r"(\d{2}/\d{2}/\d{2} \d{2}:\d{2}:\d{2})\s+([^\s]+)\s+([^\s]+)\s+([^\s]+)\s+([^\s]+)\s+([^\s]+)\s+([^\s]+)\s+([^\s]+)\s+([^\s]+)\s+([^\s]+)\s+([^\s]+)"
    # rows = re.findall(pattern, yatirim_islemleri)

    # # Define column names
    columns = [
        "Tarih", "İşlem Türü", "Sembol", "İşlem Tipi", "İşlem Durumu", "Para Birimi",
        "Emir Adedi", "Emir Tutarı", "Gerçekleşen Adet", "Ortalama İşlem Fiyatı",
        "İşlem Ücreti", "İşlem Tutarı"
    ]
    # # Create a DataFrame
    df = pd.DataFrame(rows, columns=columns)

    # # Save to Excel
    output_path = 'yatirim_islemleri.xlsx'
    df.to_excel(output_path, index=False, engine='openpyxl')

    print(f"Data has been saved to {output_path}")
else:
    print("Yatırım İşlemleri section not found.")
