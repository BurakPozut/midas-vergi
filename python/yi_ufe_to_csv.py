import pandas as pd

# Define the data as a dictionary
data = {
    "YIL": [2024, 2023, 2022, 2021, 2020],
    "OCAK": [3035.59, 2105.17, 1129.03, 583.38, 462.42],
    "ŞUBAT": [3149.03, 2138.04, 1210.60, 590.52, 464.64],
    "MART": [3252.79, 2147.44, 1321.90, 614.93, 468.69],
    "NİSAN": [3369.98, 2164.94, 1423.27, 641.63, 474.69],
    "MAYIS": [3435.96, 2179.02, 1548.01, 666.79, 482.02],
    "HAZİRAN": [3483.25, 2320.72, 1652.75, 693.54, 485.37],
    "TEMMUZ": [3550.88, 2511.75, 1738.21, 710.61, 490.33],
    "AĞUSTOS": [3610.51, 2659.60, 1780.05, 730.28, 501.85],
    "EYLÜL": [3659.84, 2749.98, 1865.09, 741.58, 515.13],
    "EKİM": [3707.10, 2803.29, 2011.13, 780.45, 533.44],
    "KASIM": [3731.43, 2882.04, 2026.08, 858.43, 555.18],
    "ARALIK": [None, 2915.02, 2021.19, 1022.25, 568.27],
}

# Create a DataFrame
df = pd.DataFrame(data)

# Path to save the Excel file
output_path = "yiUfe.csv"

# Save the DataFrame to Excel
df.to_csv(output_path, index=False, encoding='utf-8-sig')

print(f"Data has been saved to '{output_path}'")
