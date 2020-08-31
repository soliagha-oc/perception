# PERCEPTION
This tool combines various open source tools to give insight into accessibility and performance metrics for a list of 
URLs. There are several parts that can be understood as such:

- This application requires a least one CSV wth a one column header labeled "Address" and one URL per line (ignores 
other comma delimited data).  
- A crawl can be also be executed (e.g. currently using a licenced version of ScreamingFrogSEO CLI tools 
https://www.screamingfrog.co.uk/seo-spider/) 
- Runs Deque AXE for all URLs and produces both a detailed and summary report (including updating the associated Google 
Sheet) See: https://pypi.org/project/axe-selenium-python/
- Runs Lighthouse CLI for all URLs and produces both a detailed and summary report (including updating the associated 
Google Sheet) See: https://github.com/GoogleChrome/lighthouse
- Runs a PDF audit for all PDF URLs and produces both a detailed and summary report (including updating the associated 
Google Sheet)

Get get started, follow the installation instructions below. Once complete:

1. Start the virtual environment.
2. Run <code>start app.py</code> or <code>python app.py</code>.
3. Navigate to http://127.0.0.1:5000/reports/ or http://localhost/reports/ where the sample "DRUPAL" report will be 
visible.
4. View the report by clicking on the report address or providing the link as such http://localhost/reports/?id=DRUPAL
5. Here is a link to the sample data Google Sheet report: 
<a href="https://docs.google.com/spreadsheets/d/1x_Chi2fzIpEDn9d2qsQrKZQ_lpwNPYhaujYgrEkRGlg">DRUPAL Google Sheet</a>

NOTE: At the moment, no database is used due to an initial interest in CSV DATA ONLY. The system creates one
 folder for each as follows (under /REPORTS/your_report_name): 
 
 - /AXE (used to store AXE data)
 - /LIGHTHOUSE (used to store Lighthouse data)
 - /logs (tracks progress and requests)
 - /PDF (used to store and process PDF files)
 - /SPIDER (used to store crawl data)
 
 At this point, a 
database would make more sense and adding a function to "Export to CSV", etc.

## Workflow
As mentioned, simply provide a CSV with a list of URLs (column header = "Address") and select the tests to run through the web form.

The application is configured through environment variables.  On startup, the application
will also read environment variables from a <code>.env</code> file.

- HOST (defaults to 127.0.0.1)
- PORT (defaults to 5000)
- SECRET_KEY (no default, used to sign the Flask session cookie.  Use a cryptographically
  strong sequence of characters, like you might use for a good password.)
- ALLOWED_EXTENSIONS (defaults to "csv", comma separated list)

## Installation
To get all tests running, the following steps are required: 

### Clone and install
<code>sudo apt update</code>

<code>sudo apt install git</code>

<code>sudo apt-get install python3-pip</code>

<code>sudo apt-get install python3-venv</code>

<code>sudo apt-get update</code>

<code>sudo apt-get install software-properties-common</code>

<code>sudo add-apt-repository ppa:deadsnakes/ppa</code>

<code>sudo apt-get install python3.6</code>

<code>git clone https://github.com/soliagha-oc/perception.git </code>

<code>sudo python -m venv venv</code>

<code>source venv/bin/activate</code>

<code>pip install -r requirements.txt</code>

<code>python app.py</code>

### CLI-TOOLS
Install the following CLI tools for your operating system:

#### chromedriver

1. Download and install the matching/required <code>chromedriver</code>

    https://chromedriver.chromium.org/downloads
    
2. Download latest version from official website and upzip it (here for instance, verson 2.29 to ~/Downloads)

    <code>wget https://chromedriver.storage.googleapis.com/2.29/chromedriver_linux64.zip </code>
  
3. Move to /usr/local/share (or any folder) and make it executable

    <code>sudo mv -f ~/Downloads/chromedriver /usr/local/share/</code>
        
    <code>sudo chmod +x /usr/local/share/chromedriver</code>
  
4. Create symbolic links

    <code>sudo ln -s /usr/local/share/chromedriver /usr/local/bin/chromedriver</code>
    
    <code>sudo ln -s /usr/local/share/chromedriver /usr/bin/chromedriver</code>

    OR

    <code>export PATH=$PATH:/path-to-extracted-file/</code>

    OR

    add to <code>.bashrc</code>

#### geckodriver

1. Go to the geckodriver releases page. Find the latest version of the driver for your platform and download it. For example:
    https://github.com/mozilla/geckodriver/releases
    
    <code>wget https://github.com/mozilla/geckodriver/releases/download/v0.24.0/geckodriver-v0.24.0-linux64.tar.gz </code>

2. Extract the file with:

    <code>tar -xvzf geckodriver* </code>

3. Make it executable:

    <code>chmod +x geckodriver</code>
 
4. Add the driver to your PATH so other tools can find it:

    <code>export PATH=$PATH:/path-to-extracted-file/</code>
    
    OR
    
    add to <code>.bashrc</code>
        
#### lighthouse

1. Install node

    https://nodejs.org/en/download/

    <code>curl -sL https://deb.nodesource.com/setup_14.x | sudo -E bash -</code>
    
    <code>sudo apt-get install -y nodejs</code>

2. Install npm

    <code>npm install npm@latest -g</code>
    
    <code>sudo npm install npm@latest -g</code>

3. Install lighthouse

    <code>npm install -g lighthouse</code>
    
    <code>sudo npm install -g lighthouse</code>

#### pdfimages

https://www.xpdfreader.com/download.html

To install this binary package:

1. Copy the executables (pdfimages, xpdf, pdftotext, etc.) to to /usr/local/bin.

2. Copy the man pages (*.1 and *.5) to /usr/local/man/man1 and
   /usr/local/man/man5.

3. Copy the sample-xpdfrc file to /usr/local/etc/xpdfrc.  You'll
   probably want to edit its contents (as distributed, everything is
   commented out) -- see xpdfrc(5) for details.
#### Google APIs

See this "Quick Start" guide to enable the Drive API: https://developers.google.com/drive/api/v3/quickstart/python

Complete the steps described in the rest of this page to create a simple Python command-line application that makes 
requests to the Drive API.

#### nginx (optional)

See: https://www.nginx.com/

### ScreamingFrog SEO
See: https://www.screamingfrog.co.uk/seo-spider/user-guide/general/#commandlineoptions

ScreamingFrog SEO CLI tools provide the following data sets (required listed is bold):
<strong>- crawl_overview.csv (used to create report DASHBOARD)</strong>
- external_all.csv
<strong>- external_html.csv (used to audit external URLs)</strong>
<strong>- external_pdf.csv (used to audit external PDFs)</strong>
- h1_all.csv
- images_missing_alt_text.csv
- internal_all.csv
- internal_flash.csv
<strong>- internal_html.csv (used to audit internal URLs)</strong>
- internal_other.csv
<strong>- internal_pdf.csv (used to audit internal PDFs)</strong>
- internal_unknown.csv
- page_titles_all.csv
- page_titles_duplicate.csv
- page_titles_missing.csv

Note: There are spider config files located in the /conf folder. You will require a licence to alter the configurations.

Note: If a licence is not available, simply provide a CSV where at least one column has the header "address". 
See DRUPAL example.

### Deque AXE

Installed via <code>pip install -r .\requirements.txt</code>

See: https://pypi.org/project/axe-selenium-python/ and https://github.com/dequelabs/axe-core

### Google Lighthouse

Lighthouse is an open-source, automated tool for improving the performance, quality, and correctness of your web apps. 

When auditing a page, Lighthouse runs a barrage of tests against the page, and then generates a report on how well the page did. From here you can use the failing tests as indicators on what you can do to improve your app.

* Quick-start guide on using Lighthouse:
https://developers.google.com/web/tools/lighthouse/

* View and share reports online:
https://googlechrome.github.io/lighthouse/viewer/

* Github source and details:
https://github.com/GoogleChrome/lighthouse

### Google APIs
#### Authentication

While there is a /reports/ dashboard, the system is enabled to write to a Google Sheets. To do this, set up credentials 
for Google API authentication here: https://console.developers.google.com/apis/credentials to get a valid 
"credentials.json" file.

#### Google Sheets Template

To facilitate branding and other report metrics, a "non-coder/sheet formula template" is used. Here is a 
<a href="https://docs.google.com/spreadsheets/d/1oPxGCc8gS1RhMhPqzDz-_SWSQANiPssoxFKgcRd5bsY/edit?usp=sharing">
sample template</a>. When a report is run from the /reports/ route, the template is loaded (template report and folder 
ID found in globals.py and need to be setup/updated once), and the Google Sheet is either created or updated (unique 
report ID auto generated and found in /REPORTS/your_report_name/logs/_gdrive_logs.txt). 

## Running with sample data

If you have a Screaming Frog SEO Spider licence be sure to add it to "CLI-TOOLS/seo". Even if Screaming Frog SEO Spider 
is not installed, a CSV can be provided to guide the report tools. Once installed, try to run the sample CSV. To do this:

Running a sample can be accomplished two ways, using the samples provided in the "/REPORTS/DRUPAL/" folder or by 
downloading and installing Screaming Frog SEO Spider and running a free crawl (500 URL limit and no configuration/CLI 
tool access). Once the crawl is completed or file created, create/save the following CSVs: 

- crawl_overview.csv (via "Reports >> Crawl Overview" in the ScreamingFrog menu) - used to create Report Overview. 
Without this CSV, the Report Overview will be missing (working on calculating the results to eliminate this report) 
- internal_html.csv (via "Export" button in the ScreamingFrog interface) - used to point the reporting tools to the 
desired URLs
- internal_pdf.csv (via "Export" button in the ScreamingFrog interface) - used to point the reporting tools to the 
desired URLs
- external_html.csv (via "Export" button in the ScreamingFrog interface) - used to point the reporting tools to the 
desired URLs
- external_pdf.csv (via "Export" button in the ScreamingFrog interface) - used to point the reporting tools to the 
desired URLs

If another method is used to crawl a base URL, be sure to include the results in a CSV file where at least one 
header (first row) reads "Address", provide one or more web or PDF URLs, and ensure that the filename(s) is the 
same as the one listed above and in "/REPORTS/your_report_name/SPIDER/" folder. At least one *_html.csv file is 
required and to be in the appropriate folder.

## Cautions
### Spider, scanning, and viruses

It is possible when crawling and scanning sites to encounter various security risks. Please be sure to have a virus 
scanner enabled to protect against JavaScript and other attacks or disable JavaScript in the configuration.
