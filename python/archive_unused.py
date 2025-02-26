import os
import shutil
from datetime import datetime

# Create archive directory with timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
archive_dir = os.path.join(os.path.dirname(__file__), f"unused_files_{timestamp}")
os.makedirs(archive_dir, exist_ok=True)

# List of files to archive
files_to_archive = [
    "test_connection.py",
    "test_db_connection.py",
    "yi_ufe_to_csv.py",
    "tax_calculator.py",
    "commission_calculator.py",
    "main.py",
    "sort_files.py",
    # Uncomment if you're sure these are unused
    # "insert_test_data.py",
]

# Move files to archive directory
moved_files = []
for filename in files_to_archive:
    source_path = os.path.join(os.path.dirname(__file__), filename)
    if os.path.exists(source_path):
        dest_path = os.path.join(archive_dir, filename)
        shutil.move(source_path, dest_path)
        moved_files.append(filename)
        print(f"Moved {filename} to {archive_dir}")
    else:
        print(f"File {filename} not found")

# Create a README in the archive directory
readme_content = f"""# Archived Python Files

These files were archived on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} because they were identified as unused or redundant in the project.

## Files Archived
{chr(10).join(['- ' + file for file in moved_files])}

## Reason for Archiving
These files were either:
- Test files not used in production
- Replaced by newer versions
- Functionality moved to Node.js API
- No longer referenced in the codebase

If you need to restore any of these files, they are preserved here for reference.
"""

with open(os.path.join(archive_dir, "README.md"), "w") as f:
    f.write(readme_content)

print(f"\nArchiving complete. {len(moved_files)} files moved to {archive_dir}")
print("Add this directory to .gitignore to exclude it from your repository") 