import pandas as pd
from datetime import datetime
from get_dolar import get_dolar

def get_commissions():
  # Load your Excel file
  file_path = "yatirim_islemleri_extracted.xlsx"
  df = pd.read_excel(file_path)

  commission = 0

  # Convert "Tarih" column to match the database format
  def format_date(date_string):
      # Parse the original date string into a datetime object
      date_object = datetime.strptime(date_string, "%d/%m/%y %H:%M:%S")
      # Reformat it to "DD.MM.YYYY"
      return date_object.strftime("%d.%m.%Y")

  # Apply the conversion to the "Tarih" column
  df["Formatted Tarih"] = df["Tarih"].apply(format_date)

  df["İşlem Ücreti"] = df["İşlem Ücreti"].str.replace(",", ".").astype(float)

  for _,row in df.iterrows():
      date = row["Formatted Tarih"]
      exchange_rate = get_dolar(date)
      if exchange_rate:
        commission += row["İşlem Ücreti"] * exchange_rate  # Convert to TRY
      else:
        raise ValueError(f"Exchange rate not found for date {date}")
      
  print(f"Total commission: {commission:.2f} TRY")
  return commission