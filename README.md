# PERCEPTION
This tool combines various open source tools to give insight into accessibility and performance metrics for a list of URLs. There are several parts that can be understood as such:

- This application requires a CSV wth a one column header labeled "Address" and one URL per line (ignore other comma delited data). 
- A crawl can be also be executed (e.g. currently using a licenced version of ScreamingFrogSEO CLI tools https://www.screamingfrog.co.uk/seo-spider/) 
- Runs Deque AXE for all URLs and produces both a detailed and summary report (including updating the associated Google Sheet) See: https://pypi.org/project/axe-selenium-python/
- Runs Lighthouse CLI for all URLs and produces both a detailed and summary report (including updating the associated Google Sheet) See: https://github.com/GoogleChrome/lighthouse
- Runs a PDF audit for all PDF URLs and produces both a detailed and summary report (including updating the associated Google Sheet) - more on this later...

<blockquote>NOTE: At the moment, no database is used due to an initial interest in CSV DATA ONLY . At this point, a database would make more sense and adding a function to "Export to CSV", etc.</blockquote>

## Workflow
As mentioned, simply provide a CSV with a list of URLs (column header = "Address") and select the tests to run through the web form.

Once installed, run <code>python app.py</code>

## Installation
To get all tests running, the following is required: 

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

<code>sudo python3 -m venv venv</code>

<code>source venv/bin/activate</code>

<code>pip install -r requirements.txt</code>

<code>python3 app.py</code>

### CLI-TOOLS
Install the following CLI tools for your operating system:
- chromedriver (add to $PATH)

    Download and install the matching/required <code>chromedriver</code>
    https://chromedriver.chromium.org/downloads

    1. Install unzip
        
        <code>sudo apt-get install unzip</code>
        
    2. Download latest version from official website and upzip it (here for instance, verson 2.29 to ~/Downloads)
       
        <code>wget https://chromedriver.storage.googleapis.com/2.29/chromedriver_linux64.zip</code>
        
    3. Move to /usr/local/share (or any folder) and make it executable

        <code>sudo mv -f ~/Downloads/chromedriver /usr/local/share/</code>
        
        <code>sudo chmod +x /usr/local/share/chromedriver</code>
        
    4. Create symbolic links

        <code>sudo ln -s /usr/local/share/chromedriver /usr/local/bin/chromedriver
        sudo ln -s /usr/local/share/chromedriver /usr/bin/chromedriver<code>

        OR

        <code>export PATH=$PATH:/path-to-extracted-file/</code>
    
        OR
    
        add to <code>.bashrc</code>
    
- geckodriver (add to $PATH)
    1. Go to the geckodriver releases page. Find the latest version of the driver for your platform and download it. For example:
        https://github.com/mozilla/geckodriver/releases
        wget https://github.com/mozilla/geckodriver/releases/download/v0.24.0/geckodriver-v0.24.0-linux64.tar.gz
  
    2. Extract the file with:

        tar -xvzf geckodriver*
        
    3. Make it executable:

        chmod +x geckodriver
     
    4. Add the driver to your PATH so other tools can find it:

        <code>export PATH=$PATH:/path-to-extracted-file/</code>
        OR
        add to <code>.bashrc</code>
        
- lighthouse

    <code>curl -sL https://deb.nodesource.com/setup_14.x | sudo -E bash -</code>
    
    <code>sudo apt-get install -y nodejs</code>
    
    <code>npm install npm@latest -g</code>
    
    <code>sudo npm install npm@latest -g</code>
    
    <code>npm install -g lighthouse</code>
    
    <code>sudo npm install -g lighthouse</code>

- pdfimages
    https://www.xpdfreader.com/download.html
    
    To install this binary package:

    1. Copy the executables (pdfimages, xpdf, pdftotext, etc.) to to /usr/local/bin.
    
    2. Copy the man pages (*.1 and *.5) to /usr/local/man/man1 and
       /usr/local/man/man5.
    
    3. Copy the sample-xpdfrc file to /usr/local/etc/xpdfrc.  You'll
       probably want to edit its contents (as distributed, everything is
       commented out) -- see xpdfrc(5) for details.
        
- nginx (optional)


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
