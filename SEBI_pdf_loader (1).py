from bs4 import BeautifulSoup
import requests
import os
from urllib.parse import urlparse, parse_qs

# Read the list of URLs from the file
urls_file = 'urls.txt'

# Headers for the requests
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Referer': 'https://www.sebi.gov.in/',
    'Connection': 'keep-alive',
}

# Output directory for PDF files
output_dir_pdf = "downloaded_pdfs"
os.makedirs(output_dir_pdf, exist_ok=True)

session = requests.Session()
session.headers.update(headers)

# Process each URL from the list
with open(urls_file, 'r') as file:
    urls = file.readlines()

for url in urls:
    url = url.strip()
    if not url:
        continue

    print(f"Processing {url}...")

    try:
        response = session.get(url)
        if response.status_code != 200:
            print(f"Failed to fetch {url}, status code: {response.status_code}")
            continue

        soup = BeautifulSoup(response.content, 'html.parser')

        # Check for an embedded PDF file
        iframe = soup.find('iframe')
        if iframe and 'src' in iframe.attrs:
            embedded_pdf_url = requests.compat.urljoin(url, iframe['src'])

            # Extract the actual PDF URL from the query string
            parsed_url = urlparse(embedded_pdf_url)
            query_params = parse_qs(parsed_url.query)
            pdf_url = query_params.get('file', [None])[0]  # Extract the 'file' parameter

            if pdf_url:
                pdf_name = os.path.join(output_dir_pdf, os.path.basename(pdf_url))

                # Download the PDF
                print(f"Downloading PDF {pdf_url} to {pdf_name}...")
                pdf_response = session.get(pdf_url, stream=True)

                # Validate content type
                if pdf_response.headers.get('Content-Type') == 'application/pdf':
                    with open(pdf_name, 'wb') as f:
                        for chunk in pdf_response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    print(f"Downloaded {pdf_name}")
                else:
                    print(f"Unexpected content type for {pdf_url}: {pdf_response.headers.get('Content-Type')}")
            else:
                print(f"No valid PDF found in iframe URL: {embedded_pdf_url}")
        else:
            print(f"No embedded PDF found on {url}")
    except Exception as e:
        print(f"Error processing {url}: {e}")
