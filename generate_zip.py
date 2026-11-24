"""
Creates the complete ZIP submission archive for the project.
Generates: Cloud-Based-Student-Management-System.zip
"""
import os
import zipfile

PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))
ZIP_FILENAME = "Cloud-Based-Student-Management-System.zip"
ZIP_PATH = os.path.join(PROJECT_DIR, ZIP_FILENAME)

EXCLUDE_EXTENSIONS = {'.pyc', '.git', '.cache'}
EXCLUDE_DIRS = {'__pycache__', '.pytest_cache', '.git'}

def create_zip():
    print(f"Packaging project files from: {PROJECT_DIR}")
    files_added = 0
    with zipfile.ZipFile(ZIP_PATH, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(PROJECT_DIR):
            # Exclude unwanted directories
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
            
            for file in files:
                if file == ZIP_FILENAME:
                    continue
                if any(file.endswith(ext) for ext in EXCLUDE_EXTENSIONS):
                    continue
                
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, PROJECT_DIR)
                zipf.write(full_path, rel_path)
                files_added += 1
                print(f"  + Added: {rel_path}")

    print("==========================================================")
    print(f"Successfully generated ZIP: {ZIP_FILENAME}")
    print(f"Total files packaged: {files_added}")
    print(f"Archive Size: {os.path.getsize(ZIP_PATH) / 1024:.2f} KB")
    print("==========================================================")

if __name__ == "__main__":
    create_zip()
