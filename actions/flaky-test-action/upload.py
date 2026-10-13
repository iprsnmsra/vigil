import os
import requests
import sys
import glob

def main():
    results_path = os.environ.get('RESULTS_PATH')
    api_url = os.environ.get('API_URL')
    
    if not results_path or not api_url:
        print("RESULTS_PATH and API_URL must be set.")
        sys.exit(1)
        
    xml_files = glob.glob(results_path, recursive=True)
    if not xml_files:
        print(f"No files found matching {results_path}")
        sys.exit(1)
        
    for file_path in xml_files:
        with open(file_path, 'rb') as f:
            print(f"Uploading {file_path} to {api_url}")
            try:
                response = requests.post(f"{api_url}/upload", files={'file': f})
                response.raise_for_status()
                print(f"Successfully uploaded {file_path}")
            except requests.exceptions.RequestException as e:
                print(f"Failed to upload {file_path}: {e}")
                sys.exit(1)

if __name__ == "__main__":
    main()
