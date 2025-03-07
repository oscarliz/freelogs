import os
import csv
import re
import zipfile
from concurrent.futures import ThreadPoolExecutor

LOG_FILE = "processed_zips.log"

def load_processed_files():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            return set(f.read().splitlines())
    return set()

def save_processed_file(filename):
    with open(LOG_FILE, "a") as f:
        f.write(filename + "\n")

def extract_zip_files(directory, extracted_folder):
    if not os.path.exists(extracted_folder):
        os.makedirs(extracted_folder)
    
    extracted_files = load_processed_files()
    
    for file in os.listdir(directory):
        if file.endswith('.zip') and file not in extracted_files:
            zip_path = os.path.join(directory, file)
            try:
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(extracted_folder)
                save_processed_file(file)
                print(f"[+] Extracted {file}")
            except zipfile.BadZipFile:
                print(f"[-] Failed to extract {file}, bad zip format.")
            except Exception as e:
                print(f"[-] Error extracting {file}: {e}")

def extract_data_from_txt(file_path, country):
    extracted_data = []
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    
        matches = re.findall(r'URL:\s*(.*?)\nUsername:\s*(.*?)\nPassword:\s*(.*?)\nApplication:\s*(.*?)\n', content, re.MULTILINE)
    
        for match in matches:
            extracted_data.append({
                'country': country,
                'url': match[0],
                'email': match[1],
                'password': match[2],
                'application': match[3]
            })
    except Exception as e:
        print(f"[-] Error processing file {file_path}: {e}")
    
    return extracted_data

def save_to_csv(data, output_file):
    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Country", "Email", "Password", "URL", "Application"])
            for entry in data:
                writer.writerow([entry['country'], entry['email'], entry['password'], entry['url'], entry['application']])
        print(f"[+] Report saved to {output_file}")
    except Exception as e:
        print(f"[-] Error writing to CSV: {e}")

def main(directory, extracted_folder, output_file):
    extract_zip_files(directory, extracted_folder)
    results = []
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        for root, _, files in os.walk(extracted_folder):
            country = os.path.basename(root).split('[')[0]  # Extraer país desde la carpeta
            for file in files:
                if file.lower().startswith("password") and file.lower().endswith(".txt"):
                    file_path = os.path.join(root, file)
                    futures.append(executor.submit(extract_data_from_txt, file_path, country))
        
        for future in futures:
            results.extend(future.result())
    
    save_to_csv(results, output_file)

if __name__ == "__main__":
    DIRECTORY = r"\\?\C:\Users\oencarnacion\Downloads\Telegram Desktop"  # Manejo de rutas largas
    EXTRACTED_FOLDER = r"\\?\C:\Users\oencarnacion\Downloads\Telegram Desktop\extracted_logs"
    OUTPUT_FILE = r"\\?\C:\Users\oencarnacion\Downloads\Telegram Desktop\filtered_logs.csv"
    
    main(DIRECTORY, EXTRACTED_FOLDER, OUTPUT_FILE)
