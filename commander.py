import utils as utils
import os
import json
import fnmatch
import csv
import datetime as datetime
import urllib.parse
import threading
import subprocess
import sys
import time
from flask import Flask
from pdf_audit import PDFAudit as PDFA
from selenium import webdriver
from shutil import copyfile
from axe_selenium_python import Axe
from threading import Thread, Event

# App config
app = Flask(__name__)
app.config.from_object('config.Config')
PROCESS_LOG = app.config.get('PROCESS_LOG')
BASE_FOLDER = app.config.get('BASE_FOLDER')
REPORTS_FOLDER = app.config.get('REPORTS_FOLDER')
GMAIL_USER = app.config.get('GMAIL_USER')
GMAIL_PASSWORD = app.config.get('GMAIL_PASSWORD')
SENT_FROM = app.config.get('SENT_FROM')
stop_event = Event()

class CMDWriter:
    def __init__(self, report_name, url, email,
                 SEOInternal, SEOExternal, CSVUpload, PDFAudit,
                 LighthouseMOBILE, LighthouseDESKTOP, AXEChrome, AXEFirefox, AXEEdge):
        # Set variable scope
        self.spider_file = None
        self.base_folder = BASE_FOLDER
        self.report_folder = os.path.join(REPORTS_FOLDER, report_name)
        # Create report folder
        if not os.path.exists(self.report_folder):
            os.makedirs(self.report_folder)
        # Create report log folder
        self.logs = os.path.join(self.report_folder, 'logs')
        if not os.path.exists(self.logs):
            os.makedirs(self.logs)
        self.request_log = os.path.join(self.logs, '_request_log.csv')
        self.report_name = report_name
        self.url = url
        self.destination_folder = ''
        self.spider_folder = ''
        self.CSVFile = CSVUpload
        self.SEOInternal = SEOInternal
        self.SEOExternal = SEOExternal
        self.PDFAudit = PDFAudit
        self.AXEChrome = AXEChrome
        self.AXEFirefox = AXEFirefox
        self.AXEEdge = AXEEdge
        self.LighthouseMOBILE = LighthouseMOBILE
        self.LighthouseDESKTOP = LighthouseDESKTOP
        self.thread_limit = 25
        self.thread_sleep = 8

        # Request variables
        request_tuple = [('date', str(datetime.datetime.now())[:-7]), ('report_name', report_name),
                         ('email', str(email)), ('url', url),
                         ('SEOInternal', str(SEOInternal)),
                         ('SEOExternal', str(SEOExternal)),
                         ('CSVUpload', str(CSVUpload)),
                         ('PDFAudit', str(PDFAudit)),
                         ('AXEChrome',  str(AXEChrome)),
                         ('AXEFirefox', str(AXEFirefox)),
                         ('AXEEdge', str(AXEEdge)),
                         ('LighthouseMOBILE', str(LighthouseMOBILE)),
                         ('LighthouseDESKTOP', str(LighthouseDESKTOP))]

        if not url == 'RESTART':
            utils.log_line(self.request_log, request_tuple)

        # Start master_controller
        thread = Thread(target=self.master_controller)
        print('MAIN:before STARTING Spider thread: ' + thread.name + '\n')
        thread.daemon = True
        thread.start()

        # Create success email message
        msg = ('Email was sent to ' + str(email) + '. Please visit http://a11y-perception.ddns.net/reports?report_name=' +
               self.report_name + ' to view your report. It may take several hours for your report to complete.' + '\n')
        print(msg)

        # Send confirmation email
        try:
            utils.send_email(email, 'Audit for ' + self.report_name + ' is has started.', msg)
            utils.log_line(os.path.join(self.logs, '_email_log.txt'), msg)
        except Exception as e:
            msg = str(e) + ' EMAIL' + '\n'
            print('PERCEPTION ' + msg)
            utils.log_line(os.path.join(self.logs, '_email_log.txt'), msg)

    def master_controller(self):
        # Create spider folder
        self.spider_folder = os.path.join(self.report_folder, 'SPIDER')

        # Check for restart and archive existing crawl
        # TODO: Archive all report data
        spider_file = os.path.join(self.spider_folder, 'crawl.seospider')
        if self.url == 'RESTART':
            if self.SEOInternal or self.SEOExternal:
                if os.path.exists(spider_file):
                    os.rename(spider_file,
                              spider_file + '_' +
                              time.ctime(os.path.getctime(spider_file))
                              .replace(' ', '_').replace(':', '_'))
                # Get the URL from the log file
                if os.path.exists(self.request_log):
                    with open(self.request_log, 'r') as csv_file:
                        csv_reader = csv.reader(csv_file, delimiter=',')
                        for row in csv_reader:
                            if row == 'url':
                                continue

        if not os.path.exists(spider_file) and not self.url == '':
            if self.SEOInternal or self.SEOExternal:
                CMDWriter.spider_controller(self)

        for root, dirs, files in os.walk(os.path.join(self.report_folder, 'CSV')):
            for file in files:
                # Wait for crawl to end before running the following
                # Start AXE CONTROLLER
                # TODO: Add file
                # TODO: Read config for all selections
                self.CSVFile = os.path.join(self.report_folder, 'CSV', file)
                if self.AXEChrome or self.AXEFirefox or self.AXEEdge:
                    t = Thread(target=CMDWriter.axe_controller, args=(self,))
                    t.daemon = True
                    t.start()
                # Start Lighthouse CONTROLLER
                if self.LighthouseMOBILE or self.LighthouseDESKTOP:
                    t = Thread(target=self.lighthouse_controller)
                    t.daemon = True
                    t.start()
                # Start PDF CONTROLLER
                if self.PDFAudit or self.CSVFile.find('__pdf__'):
                    self.CSVFile = os.path.join(self.report_folder, 'PDF', file)
                    t = Thread(target=self.pdf, args=self.destination_folder)
                    t.daemon = True
                    t.start()

    def spider_controller(self):
        # TODO: Move the check
        if not os.path.exists(self.spider_folder):
            os.makedirs(self.spider_folder)

        if self.SEOInternal or self.SEOExternal and not os.path.exists(os.path.join(
                self.spider_folder, 'crawl.seospider')):  # Default crawl

            # RUN SPIDER!!
            msg = (str(datetime.datetime.now())[:-7], 'New client folder created in COMPLETE:',
                   self.spider_folder)
            # Create spider log
            utils.log_line(os.path.join(self.logs, '_spider_log.txt'), msg)

            # TODO: Check for upload
            # Write base cmd
            cmd = ('screamingfrogseospidercli --crawl ' + self.url +
                   ' --headless --save-crawl --output-folder \"' + self.spider_folder + '\" --overwrite ')
            # Write in/external
            if self.SEOInternal and self.SEOExternal:
                cmd += ('--config \"' + os.path.join(BASE_FOLDER, 'conf', 'SEOConfig.seospiderconfig') + '\" '
                        '--export-tabs \"Internal:All,Internal:HTML,Internal:PDF,Internal:Flash,Internal:Other,Internal:Unknown,'
                        'External:All,External:HTML,External:PDF,Images:Missing ALT Text,Page Titles:All,Page Titles:Missing,'
                        'Page Titles:Duplicate,H1:All\" --save-report \"Crawl Overview\"')
            # Write internal
            if self.SEOInternal and not self.SEOExternal:
                cmd += ('--config \"' + os.path.join(BASE_FOLDER, 'conf', 'SEOConfig_Internal.seospiderconfig') + '\" ' 
                        '--export-tabs \"Internal:All,Internal:HTML,Internal:PDF,Internal:Flash,Internal:Other,'
                        'Internal:Unknown,Images:Missing ALT Text,Page Titles:All,Page Titles:Missing,'
                        'Page Titles:Duplicate,H1:All\" --save-report \"Crawl Overview\"')
            # Write external
            if self.SEOExternal and not self.SEOInternal:
                cmd = ('--config \"' +
                       os.path.join(BASE_FOLDER, 'conf', 'SEOConfig_External.seospiderconfig') + '\" ' 
                       '--export-tabs \"External:All,External:HTML,External:PDF,Page Titles:All,'
                       'Page Titles:Missing,Page Titles:Duplicate,H1:All\" --save-report \"Crawl Overview\"')
            # Call spider thread engine
            if self.SEOInternal or self.SEOExternal:
                CMDWriter.spider_thread(self, cmd)  # Not threaded and we need a wait

    def spider_thread(self, cmd):
        try:
            # Log start
            msg = datetime.datetime.now().__str__()[:-7] + ' Crawl started: ' + cmd
            # utils.log_line(os.path.join(self.logs, '_spider_log.txt'), msg)
            # RUN THE SPIDER AND WAIT
            if 'linux' in sys.platform:
                p = subprocess.run(cmd, stdout=subprocess.PIPE)
            else:
                p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
            # on exit

            # Log spider progress
            while True:
                line = p.stdout.readline()
                if str(line).rfind('mCompleted=') > 10:
                    print(line)
                    start = str(line).rfind('mCompleted=')
                    percentage = str(line)[start + 11: start + 17].replace(']\\', '').replace(']', '')
                    utils.log_line(os.path.join(self.logs, '_spider_progress_log.txt'), percentage)
                    pass
                if not line:
                    break

            # Once complete...
            file_list = ['internal_html.csv', 'internal_pdf.csv', 'external_html.csv', 'external_pdf.csv']
            for file in file_list:
                if os.path.exists(os.path.join(self.spider_folder, file)):
                    if not os.path.exists(os.path.join(self.report_folder, 'CSV')):
                        os.makedirs(os.path.join(self.report_folder, 'CSV'))

                    path = os.path.join(self.report_folder, 'CSV', file)
                    # check for whether PDF
                    if file.find('_pdf.csv') > -1:
                        path = os.path.join(self.report_folder, 'CSV', '__pdf__' + file)
                    copyfile(os.path.join(self.spider_folder, file), path)

            # Log spider completion
            msg = datetime.datetime.now().__str__()[:-7] + ' Crawl completed: ' + cmd
            utils.log_line(os.path.join(self.logs, '_spider_log.txt'), msg)
        except Exception as e:
            msg = e.__str__() + ' SPIDER THREAD:01' + '\n'
            print(msg)
            utils.log_line(os.path.join(self.logs, '_spider_log.txt'), msg)

    def axe_controller(self):
        # AXE count total links
        # TODO: Add switch for "external"
        first_line = True
        # csv_path = os.path.join(self.destination_folder, 'internal_html.csv')
        csv_path = self.CSVFile
        row_count = sum(1 for row in csv.reader(open(csv_path, 'r',
                                                     encoding='utf8'), delimiter=','))
        row_count_i = row_count - 1
        # Open HTML CSV list
        with open(csv_path, 'r', encoding='utf8') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            dest_file = os.path.join(self.report_folder, 'AXE', 'CHROME', 'AXE_CHROME_DETAILS.csv')
            # Check for completed URLs
            for row in csv_reader:
                if first_line:
                    first_line = False
                    continue
                # Compare AXE_REPORT to SPIDER_CSV
                elif os.path.exists(dest_file):
                    with open(dest_file, encoding='utf8') as completed_urls:
                        completed_urls_reader = csv.reader(completed_urls, delimiter=',')
                        jump = True
                        fl = True
                        for completed_url in completed_urls_reader:
                            if fl:
                                jump = True
                                fl = False
                                continue
                            # If match found:
                            if row[0] in completed_url:
                                row_count_i -= 1
                                jump = True
                                fl = False
                                msg = (' >>> Remaining URLs for [AXE]: ' + row_count_i.__str__() +
                                       ' out of ' + row_count.__str__() +
                                       ' ' + (datetime.datetime.now().__str__()[:-7]))
                                if row_count_i >= 0:
                                    utils.log_line(os.path.join(self.logs, '_axe_chrome_log.txt'), msg)
                                print(msg)
                                break
                            else:
                                jump = False
                                fl = False
                        if jump:
                            jump = False
                            continue
                try:
                    # Start AXE
                    # Set number of threads
                    while threading.active_count() > self.thread_limit:
                        # print(threading.active_count().__str__() + ' THREADS RUNNING >> LIGHTHOUSE >> TAKE 10')
                        time.sleep(5)

                    row_count_i -= 1
                    # CHROME THREAD
                    if self.AXEChrome:
                        # TODO: Add if .pdf call pdf_audit
                        thread = Thread(target=CMDWriter.axeChrome, args=(self, row[0]))
                        thread.daemon = True
                        thread.start()
                        thread_monitor = Thread(target=CMDWriter.thread_monitor, args=('AXEChrome', thread,))
                        thread_monitor.setDaemon(True)
                        thread_monitor.start()

                        # Log "Remaining URLs" to progress log
                        msg = (' >>> Remaining URLs for [AXE]: ' + row_count_i.__str__() +
                               ' out of ' + row_count.__str__() +
                               ' ' + (datetime.datetime.now().__str__()[:-7]))
                        print(msg)
                        utils.log_line(os.path.join(self.logs, '_axe_chrome_log.txt'), msg)

                    # FIREFOX THREAD
                    if self.AXEFirefox:
                        thread = Thread(target=CMDWriter.axeFirefox, args=(self, row[0]))
                        thread.daemon = True
                        thread.start()
                        thread_monitor = Thread(target=CMDWriter.thread_monitor, args=('AXEFirefox', thread,))
                        thread_monitor.setDaemon(True)
                        thread_monitor.start()

                        # Log "Remaining URLs" to progress log
                        msg = (' >>> Remaining URLs for [AXE]: ' + row_count_i.__str__() +
                               ' out of ' + row_count.__str__() +
                               ' ' + (datetime.datetime.now().__str__()[:-7]))
                        print(msg)
                        utils.log_line(os.path.join(self.logs, '_axe_firefox_log.txt'), msg)

                    # EDGE THREAD
                    if self.AXEEdge:
                        thread = Thread(target=CMDWriter.axeEdge, args=(self, row[0]))
                        thread.daemon = True
                        thread.start()
                        thread_monitor = Thread(target=CMDWriter.thread_monitor, args=('AXEEdge', thread,))
                        thread_monitor.setDaemon(True)
                        thread_monitor.start()

                    # Log "Remaining URLs" to progress log
                    msg = (' >>> Remaining URLs for [AXE]: ' + row_count_i.__str__() +
                           ' out of ' + row_count.__str__() +
                           ' ' + (datetime.datetime.now().__str__()[:-7]))
                    print(msg)
                    utils.log_line(os.path.join(self.logs, '_axe_edge_log.txt'), msg)

                except Exception as e:
                    msg = e.__str__() + ' AXE CONTROLLER:01' + '\n'
                    # print(msg)
                    utils.log_line(os.path.join(self.logs, '_axe_edge_log.txt'), msg)

    def axeChrome(self, axe_url):
        try:
            # Create and log new folder, log
            destination_folder = os.path.join(self.report_folder, 'AXE', 'CHROME')
            if not os.path.exists(destination_folder):
                os.makedirs(destination_folder)
                msg = (datetime.datetime.now().__str__()[:-7] + ' ' +
                       'New folder created in COMPLETE: ' + destination_folder)
                utils.log_line(os.path.join(self.logs, '_axe_chrome_log.txt'), msg)

            # Load driver CHROME
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument("--headless")
            driver = webdriver.Chrome(chrome_options=chrome_options)
            driver.get(axe_url)
            # Start thread
            t = Thread(target=CMDWriter.axe_runner,
                            args=(self, driver, axe_url, destination_folder, 'CHROME'))
            t.daemon = True
            t.start()
            thread_monitor = Thread(target=CMDWriter.thread_monitor,
                                    args=('AXE RUNNER CHROME', t,))
            thread_monitor.setDaemon(True)
            thread_monitor.start()
            msg = 'AXE STARTED thread for Chrome ' + axe_url
            print(msg)

        except Exception as e:
            msg = e.__str__() + ' AXE/CHROME'
            print(msg)
            utils.log_line(os.path.join(self.logs, '_axe_chrome_log.txt'), msg)

    def axeFirefox(self, axe_url):
        try:
            # Create and log new folder, log
            # destination_folder = self.report_folder + 'AXEFirefox_' + self.report_name + '\\'
            destination_folder = os.path.join(self.report_folder, 'AXE', 'FIREFOX')
            if not os.path.exists(destination_folder):
                os.makedirs(destination_folder)
                msg = (datetime.datetime.now().__str__()[:-7] + ' ' +
                       'New folder created in COMPLETE: ' + destination_folder)
                utils.log_line(os.path.join(self.logs, '_axe_firefox_log.txt'), msg)
            # Load driver FIREFOX
            options = webdriver.FirefoxOptions()
            options.set_headless(True)
            driver = webdriver.Firefox(executable_path='geckodriver', options=options)
            driver.get(axe_url)
            # Start thread
            t = Thread(target=CMDWriter.axe_runner,
                            args=(self, driver, axe_url, destination_folder, 'FIREFOX'))
            t.daemon = True
            t.start()
            thread_monitor = Thread(target=CMDWriter.thread_monitor,
                                    args=('AXE RUNNER FIREFOX', t,))
            thread_monitor.setDaemon(True)
            thread_monitor.start()
            msg = ' >>> Started AXE thread for Firefox ' + axe_url
            print(msg)

        except Exception as e:
            msg = e.__str__() + ' AXE/FIREFOX'
            print(msg)
            utils.log_line(os.path.join(self.logs, '_axe_firefox_log.txt'), msg)

    def axeEdge(self, axe_url):
        try:
            # Create and log new folder, log
            # destination_folder = self.report_folder + '\\AXEEdge_' + self.report_name + '\\'
            destination_folder = os.path.join(self.report_folder, 'AXE', 'EDGE')
            if not os.path.exists(destination_folder):
                os.makedirs(destination_folder)
                msg = (datetime.datetime.now().__str__()[:-7] + ' ' +
                       'New folder created in COMPLETE: ' + destination_folder)
                utils.log_line(os.path.join(self.logs, '_axeEdge_log.txt'), msg)

            # Load driver EDGE
            options = webdriver.Edge.desired_capabilities
            options.headless = True
            driver = webdriver.Edge()
            driver.get(axe_url)
            # Start thread
            t = Thread(target=CMDWriter.axe_runner,
                            args=(self, driver, axe_url, destination_folder, 'EDGE'))
            t.daemon = True
            t.start()
            thread_monitor = Thread(target=CMDWriter.thread_monitor,
                                    args=('AXE RUNNER EDGE', t,))
            thread_monitor.setDaemon(True)
            thread_monitor.start()
            msg = ' >>> Started AXE thread for Edge ' + axe_url + '\n'
            print(msg)

        except Exception as e:
            msg = e.__str__() + ' AXE/EDGE'
            print(msg)
            utils.log_line(os.path.join(self.logs, '_axe_Edge_log.txt'), msg)

    def axe_runner(self, driver, axe_url, destination_folder, browser):
        # Load AXE driver
        try:
            axe = Axe(driver)
            results = axe
            results_path = os.path.join(destination_folder, (urllib.parse.quote_plus(axe_url) + '.json'))
            try:
                axe.inject()  # Inject axe-core javascript into page.
                results = axe.run()  # Run axe accessibility checks.
                # Write results to file

                axe.write_results(results, results_path)
            except Exception as e:
                msg = e.__str__() + ' AXE RUNNER:01'
                print(msg)
                utils.log_line(os.path.join(self.logs, browser, '_axe_log.txt'), msg)
            finally:
                pass
            driver.close()
            # Assert no violations are found
            # assert len(results["violations"]) == 0, axe.report(results["violations"])
            # Define CSV
            csv_row = []
            dict_json = ['test', 'browser', 'url', 'score', 'title', 'description']
            csv_row.insert(0, dict_json)
            # Look for violations
            for violation in results['violations']:
                dict_json = ['axe', browser, axe_url, '0', violation['help'], violation['description']]
                csv_row.insert(csv_row.__len__() + 1, dict_json)
            # Write violations report CSV; create report folder/file; check for exists
            write_header = False
            report_path = os.path.join(destination_folder, ('AXE_' + browser + '_DETAILS.csv'))
            if not os.path.exists(report_path):
                write_header = True
            else:
                write_header = False
            # Write AXE_REPORT
            # os.chdir(os.path.join(destination_folder, 'AXE'))
            with open(report_path, 'a', encoding='utf8', newline='') as csv_file:
                for i in range(csv_row.__len__()):
                    writer = csv.writer(csv_file, quoting=csv.QUOTE_ALL)
                    writer.dialect.lineterminator.replace('\n', '')
                    if i == 0:
                        if write_header:
                            writer.writerow(csv_row[i])
                            write_header = False
                            continue
                    else:
                        writer.writerow(csv_row[i])
                        msg = datetime.datetime.now().__str__()[:-7] + ' ' + csv_row[i].__str__()
                        print(msg)
                        utils.log_line(os.path.join(self.logs, '_axe_log.txt'), msg)
            os.remove(results_path)
        except Exception as e:
            msg = e.__str__() + ' AXE RUNNER:02'
            utils.log_line(os.path.join(self.logs, browser, '_axe_log.txt'), msg)
            print(msg)

    @staticmethod
    def pdf(csv_path):
        PDFA().pdf_csv(csv_path, False, False)

    def lighthouse_controller(self):
        first_line = True
        csv_file = self.CSVFile
        row_count = sum(1 for row in csv.reader(open(csv_file, 'r',
                                                     encoding='utf8'), delimiter=','))
        row_count_i = row_count - 1
        # Open HTML list
        with open(csv_file, 'r', encoding='utf8') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            destination_file = os.path.join(self.report_folder, 'LIGHTHOUSE', 'LIGHTHOUSE_REPORT.csv')
            '''if not os.path.exists(destination_folder):
                os.makedirs(destination_folder)'''
            for row in csv_reader:
                if first_line:
                    first_line = False
                    continue
                # Compare LIGHTHOUSE_REPORT to SPIDER_CSV
                elif os.path.exists(destination_file):
                    with open(destination_file, encoding='utf8') as completed_urls:
                        completed_urls_reader = csv.reader(completed_urls, delimiter=',')
                        jump = True
                        fl = True
                        for completed_url in completed_urls_reader:
                            if fl:
                                jump = True
                                fl = False
                                continue
                            # If match found:
                            if row[0] in completed_url:
                                row_count_i -= 1
                                jump = True
                                fl = False
                                msg = (' >>> Remaining URLs for [Lighthouse]: ' + (row_count_i - 1).__str__() +
                                       ' out of ' + row_count.__str__() +
                                       ' ' + (datetime.datetime.now().__str__()[:-7]))
                                if row_count_i >= 0:
                                    utils.log_line(os.path.join(self.logs, '_lighthouse_chrome_log.txt'), msg)
                                print(msg)
                                break
                            else:
                                jump = False
                                fl = False
                        # JUMP OUT OF LINE RUN
                        if jump:
                            jump = False
                            continue
                try:
                    row_count_i -= 1
                    # set number of threads
                    while threading.active_count() > self.thread_limit:
                        # print(threading.active_count().__str__() + ' THREADS RUNNING >> LIGHTHOUSE >> TAKE 10')
                        time.sleep(5)
                    thread = Thread(target=CMDWriter.lighthouse,
                                    args=(self, row[0]))
                    thread.daemon = True
                    thread.start()
                    thread_monitor = Thread(target=CMDWriter.thread_monitor, args=('LIGHTHOUSE', thread,))
                    thread_monitor.setDaemon(True)
                    thread_monitor.start()

                    msg = (' >>> Remaining URLs for [Lighthouse]: ' + row_count_i.__str__() +
                           ' out of ' + row_count.__str__() +
                           ' ' + (datetime.datetime.now().__str__()[:-7]))
                    print(msg)
                    utils.log_line(os.path.join(self.logs, '_lighthouse_progress_log.txt'), msg)

                except Exception as e:
                    msg = e.__str__() + ' Lighthouse CONTROLLER:01'
                    print(msg)
                    utils.log_line(os.path.join(self.logs, '_lighthouse_log.txt'), msg)

    def lighthouse(self, lighthouse_url):
        destination_folder = os.path.join(self.report_folder, 'LIGHTHOUSE')
        # Create \complete\client\report_folder
        if not os.path.exists(destination_folder):
            os.makedirs(destination_folder)
            utils.log_line(os.path.join(self.logs, '_lighthouse_log.txt'),
                          'New client REPORTS folder created in COMPLETE: ' +
                           self.report_folder)

        output_path = os.path.join(destination_folder, urllib.parse.quote_plus(lighthouse_url))
        if self.LighthouseMOBILE:
            try:
                # os.chdir(destination_folder)
                cmd = ('lighthouse --output=json --output=html --chrome-flags=--headless --quiet ' +
                       '--output-path=\"' + output_path +
                       '\" --emulated-form-factor=mobile ' + lighthouse_url)
                msg = cmd + ' LIGHTHOUSE:01 MOBILE STARTED: ' + lighthouse_url
                # print(msg)
                # os.system('cmd /c ' + cmd)
                os.popen(cmd)
                msg = cmd + ' LIGHTHOUSE:01 :: MOBILE FINISHED :: '
                # print(msg)
                utils.log_line(os.path.join(self.logs, '_lighthouse_log.txt'), msg)
            except Exception as e:
                msg = e.__str__() + ' LIGHTHOUSE:01.1'
                print(msg)
                utils.log_line(os.path.join(self.logs, '_lighthouse_log.txt'), msg)

        if self.LighthouseDESKTOP:
            try:
                cmd = ('lighthouse --output=json --output=html --chrome-flags=--headless --quiet ' +
                       '--output-path=\"' + output_path +
                       '\" --emulated-form-factor=desktop ' + lighthouse_url)
                msg = cmd + ' LIGHTHOUSE:01 DESKTOP STARTED: ' + lighthouse_url
                print(msg)
                # os.system('cmd /c ' + cmd)
                os.popen(cmd)
                msg = ' LIGHTHOUSE:01 DESKTOP FINISHED' + cmd
                print(msg)
                utils.log_line(os.path.join(self.logs, '_lighthouse_log.txt'), msg)
            except Exception as e:
                msg = e.__str__() + ' LIGHTHOUSE:01.2'
                print(msg)
                utils.log_line(os.path.join(self.logs, '_lighthouse_log.txt'), msg)

        try:
            # Look for JSON results
            list_json = []
            # os.chdir(destination_folder)
            file_list = os.listdir(destination_folder)
            pattern = "*.json"
            for entry in file_list:
                if fnmatch.fnmatch(entry, pattern):
                    # print(entry)
                    list_json.append(entry)
            # Load JSON results
            with open(os.path.join(destination_folder, list_json[1]), encoding="utf8") as readJSON:
                data_json = json.load(readJSON)
            # Define CSV
            csv_row = []

            dict_json = ['test', 'url', 'score', 'title', 'description']
            lighthouse_path = os.path.join(destination_folder, 'LIGHTHOUSE_REPORT.csv')
            if not os.path.exists(lighthouse_path):
                csv_row.insert(0, dict_json)
            # Look for violations
            for key, value in data_json['audits'].items():
                if value['score'] == 0:
                    dict_json = ['lighthouse', lighthouse_url, value['score'].__str__(),
                                 value['title'], value['description']]
                    csv_row.insert(csv_row.__len__() + 1, dict_json)
            # Write violations report CSV
            with open(lighthouse_path, 'a+', newline='', encoding="utf8") as csv_file:
                for i in range(csv_row.__len__()):
                    writer = csv.writer(csv_file, quoting=csv.QUOTE_ALL)
                    writer.dialect.lineterminator.replace('\n', '')
                    writer.writerow(csv_row[i])
            msg = csv_row.__str__() + ' LIGHTHOUSE:02.0'
            # print(msg)
            utils.log_line(os.path.join(self.logs, '_lighthouse_log.txt'), msg)
            # print('COMPLETE - LIGHTHOUSE:02 ::: ')

        except Exception as e:
            msg = e.__str__() + ' LIGHTHOUSE:02.1'
            print(msg)
            utils.log_line(os.path.join(self.logs, '_lighthouse_log.txt'), msg)

        time.sleep(30)
        try:
            if os.path.exists(output_path[:-5] + '.report.html'):
                os.remove(output_path[:-5] + '.report.html')
                print('REMOVE LH HTML')
        except Exception as e:
            msg = e.__str__() + ' LIGHTHOUSE:02.2'
            print(msg)
            utils.log_line(os.path.join(self.logs, '_lighthouse_log.txt'), msg)

        try:
            if os.path.exists(output_path[:-5] + '.report.json'):
                os.remove(output_path[:-5] + '.report.json')
                print('REMOVE LH JSON')
        except Exception as e:
            msg = e.__str__() + ' LIGHTHOUSE:02.3'
            print(msg)
            utils.log_line(os.path.join(self.logs, '_lighthouse_log.txt'), msg)

    @staticmethod
    def thread_monitor(process_name, thread):
        i = 0
        while thread.is_alive():
            time.sleep(10)
            i += 10
            print(process_name + ' WORKING FOR ' + i.__str__() + ' seconds for: ' + thread.getName())
            # print('ACTIVE COUNT: ' + str(threading.active_count()))
            if i == 200:
                print(process_name + ' ' + thread.getName() +
                      ' X XX XXX XXXX XXXXX XXXXXXXXXXXXXXXXXXXXXXX> KILLED AFTER 200 SECONDS!!')
                break
        print(process_name + ':[COMPLETED IN ' + i.__str__() + ' seconds for: ' + thread.getName() + ']')
