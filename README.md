# PERCEPTION
This tool combines various open source tools to give insight into accessibility and performance metrics for a list of 
URLs.

## Workflow
Simply provide a CSV with a list of URLs and select the tests to run. With a valid ScreamingFrog SEO licence, 
that list can be generated using a crawler. 

Once installed, run python requests.py
## Installation
### CLI-TOOLS
Install the following CLI tools for your operating system:
- chromedriver (add to $PATH)
- geckodriver (add to $PATH)
- nginx (optional)
- pdfimages

### ScreamingFrog SEO
ScreamingFrog SEO CLI tools provide the following data sets:
- crawl_overview.csv (used to create report DASHBOARD)
- external_all.csv
- external_html.csv (used to audit external URLs)
- external_pdf.csv (used to audit external PDFs)
- h1_all.csv
- images_missing_alt_text.csv
- internal_all.csv
- internal_flash.csv
- internal_html.csv (used to audit internal URLs)
- internal_other.csv
- internal_pdf.csv (used to audit internal PDFs)
- internal_unknown.csv
- page_titles_all.csv
- page_titles_duplicate.csv
- page_titles_missing.csv

See the RCMP example in the /REPORTS folder provided.

Note: There are spider config files located in the /conf folder. You will require a licence to alter the configurations.

Note: If a licence is not available, simply provide a CSV where at least one column has the header "address". 
See RCMP example.

### Deque AXE
Installed via "pip install -r .\requirements.txt" 

### Google Lighthouse
Installed via "pip install -r .\requirements.txt" 

### Google APIs
#### Authentication
While there is a /reports/ dashboard, the system is enabled to write to a Google Sheets. To do this, set up credentials 
for Google API authentication here: https://console.developers.google.com/apis/credentials to get a valid 
"credentials.json" file.

## Cautions
### Spider, scanning, and viruses
It is possible when crawling and scanning site to encounter various security risks. Please be sure to have a virus 
scanner enabled to protect against java script and other attacks.