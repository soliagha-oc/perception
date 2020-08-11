# PERCEPTION
This tool combines various open source tools to give insight into accessibility and performance metrics for a list of 
URLs. There are several parts that can be understood as such:

- Runs a crawl or is provided a list of URLs
- Runs Deque AXE for all URLs and produces both a detailed and summary report (including updating the associated Google
Sheet) See: https://pypi.org/project/axe-selenium-python/
- Runs Lighthouse CLI for all URLs and produces both a detailed and summary report (including updating the associated Google
Sheet) See: https://github.com/GoogleChrome/lighthouse
- Runs a PDF audit for all PDF URLs and produces both a detailed and summary report (including updating the associated Google
Sheet) More on this later...

NOTE: At the moment, no database is used due to an initial interest in CSV ONLY DATA. At this point, a database would 
make more sense and adding a function to "Export to CSV", etc. 

## Workflow
Simply provide a CSV with a list of URLs and select the tests to run. With a valid ScreamingFrog SEO licence, 
that list can be generated using a crawler. 

Once installed, run python request.py

## Installation
### CLI-TOOLS
Install the following CLI tools for your operating system:
- chromedriver (add to $PATH)
- geckodriver (add to $PATH)
- nginx (optional)
- pdfimages

### ScreamingFrog SEO
See: https://www.screamingfrog.co.uk/seo-spider/user-guide/general/#commandlineoptions

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

See: https://pypi.org/project/axe-selenium-python/ and https://github.com/dequelabs/axe-core
  

### Google Lighthouse
Installed via "pip install -r .\requirements.txt" 

See: https://github.com/GoogleChrome/lighthouse

### Google APIs
#### Authentication
While there is a /reports/ dashboard, the system is enabled to write to a Google Sheets. To do this, set up credentials 
for Google API authentication here: https://console.developers.google.com/apis/credentials to get a valid 
"credentials.json" file.

#### Template
To facilitate branding and other report metrics, a "non-coder/sheet formula template" is used. Here is a 
<a href="https://docs.google.com/spreadsheets/d/1oPxGCc8gS1RhMhPqzDz-_SWSQANiPssoxFKgcRd5bsY/edit?usp=sharing">
sample template</a>: 

## Cautions
### Spider, scanning, and viruses
It is possible when crawling and scanning sites to encounter various security risks. Please be sure to have a virus 
scanner enabled to protect against JavaScript and other attacks or disable JavaScript in the configuration.
