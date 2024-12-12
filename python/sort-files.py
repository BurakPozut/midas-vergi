import os
import re  # Importing the regex module

# Directory containing the PDF files
directory_path = 'D:/midas-vergi/ekstreler/'

# Mapping of Turkish month names to their corresponding numbers
month_mapping = {
    "Ocak": "01",
    "Şubat": "02",
    "Mart": "03",
    "Nisan": "04",
    "Mayıs": "05",
    "Haziran": "06",
    "Temmuz": "07",
    "Ağustos": "08",
    "Eylül": "09",
    "Ekim": "10",
    "Kasım": "11",
    "Aralık": "12"
}

# Loop through all files in the directory
for filename in os.listdir(directory_path):
    if filename.endswith('.pdf'):
        # Check if the filename contains a month name
        for month, month_num in month_mapping.items():
            if month in filename:
                # Extract year from the filename (assuming it's present)
                year = re.search(r'\d{4}', filename).group(0)
                
                # Construct the new filename
                new_filename = f"{year}-{month_num}_{month}_Midas_Ekstre.pdf"
                
                # Rename the file
                old_path = os.path.join(directory_path, filename)
                new_path = os.path.join(directory_path, new_filename)
                os.rename(old_path, new_path)
                print(f"Renamed '{filename}' to '{new_filename}'")
                break

# import os

# # Directory containing the PDF files
# directory_path = 'D:/midas-vergi/ekstreler/'

# # Mapping of Turkish month names to their corresponding numbers
# month_mapping = {
#     "Ocak": "1",
#     "Şubat": "2",
#     "Mart": "3",
#     "Nisan": "4",
#     "Mayıs": "5",
#     "Haziran": "6",
#     "Temmuz": "7",
#     "Ağustos": "8",
#     "Eylül": "9",
#     "Ekim": "10",
#     "Kasım": "11",
#     "Aralık": "12"
# }

# # Loop through all files in the directory
# for filename in os.listdir(directory_path):
#     if filename.endswith('.pdf'):
#         # Check if the filename contains a month name
#         for month, number in month_mapping.items():
#             if month in filename:
#                 # Construct the new filename
#                 new_filename = f"{number}_{filename}"
                
#                 # Rename the file
#                 old_path = os.path.join(directory_path, filename)
#                 new_path = os.path.join(directory_path, new_filename)
#                 os.rename(old_path, new_path)
#                 print(f"Renamed '{filename}' to '{new_filename}'")
#                 break
