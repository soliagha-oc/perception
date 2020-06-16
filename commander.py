from globals import Globals
import utils as utils

import os
import json
import fnmatch
import csv
import datetime as datetime
import urllib.parse
import threading
import subprocess
from multiprocessing import Pool, TimeoutError
import time
import logging
from io import BytesIO

from pdf_audit import PDFAudit as PDFA
from selenium import webdriver
from selenium import common as sc
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.edge.options import Options
from axe_selenium_python import Axe
from threading import Thread, Event

stop_event = Event()


class CMDWriter:
    def __init__(self, report_name, url, email,
                 SEOInternal, SEOExternal, PDFAudit, LighthouseMOBILE, LighthouseDESKTOP,
                 AXEChrome, AXEFirefox, AXEEdge):
        self.thread_sleep = 8
        self.base_folder = Globals.base_folder
        self.report_folder = Globals.gbl_report_folder + report_name + '\\'
        global thread_limit
        thread_limit = 25
        # Create report folder
        # self.report_folder = self.base_folder + 'reports\\' + report_name + '\\'
        if not os.path.exists(self.report_folder):
            os.makedirs(self.report_folder)
        # Create report log folder
        self.log = self.report_folder + 'logs\\'
        if not os.path.exists(self.log):
            os.makedirs(self.log)
        # Set variable scope
        self.report_name = report_name
        self.url = url
        self.destination_folder = ''
        self.SEOInternal = SEOInternal
        self.SEOExternal = SEOExternal
        self.PDFAudit = PDFAudit
        self.AXEChrome = AXEChrome
        self.AXEFirefox = AXEFirefox
        self.AXEEdge = AXEEdge
        self.LighthouseMOBILE = LighthouseMOBILE
        self.LighthouseDESKTOP = LighthouseDESKTOP
        # Log
        msg = datetime.datetime.now().__str__()[:-7] + ' START ' + report_name
        print(msg)
        utils.logline(self.log + '_cmd_writer_log.txt', msg)
        # Request variables

        msg = (datetime.datetime.now().__str__()[:-7] +
               ' Request: ' + [['report_name', report_name], ['email', email], ['url', url],
                               ['SEOInternal', SEOInternal], ['SEOExternal', SEOExternal],
                               ['PDFAudit', PDFAudit],
                               ['AXEChrome', AXEChrome], ['AXEFirefox', AXEFirefox], ['AXEEdge', AXEEdge],
                               ['LighthouseMOBILE', LighthouseMOBILE], ['LighthouseDESKTOP']].__str__())
        # Log
        print(msg)
        if not url == 'RESTART':
            utils.logline(self.log + '_cmd_writer_log.txt', msg)
        # Start master_controller

        thread = Thread(target=self.master_controller)
        print('MAIN:before STARTING Spider thread: ' + thread.name + '\n')
        thread.daemon = True
        thread.start()

        # Create success email message
        msg = ('Please visit http://a11y-perception.ddns.net/report?report_name=' +
               self.report_name + ' to view your report. It may take several hours for your report to complete.')
        print(msg)
        # Send confirmation email
        utils.send_email(email, 'Audit for ' + self.report_name + ' is has started.', msg)
        utils.logline(self.log + '_cmd_writer_log.txt', msg)
        # Log request
        msg = datetime.datetime.now().__str__()[:-7] + ' END \n'
        print(msg)
        utils.logline(self.log + '_cmd_writer_log.txt', msg)

    def master_controller(self):
        # Create spider folder
        self.destination_folder = self.report_folder + 'SPIDER\\'
        # Check for restart and archive existing crawl
        # TODO: Archive all report data
        if self.url == 'RESTART':
            if self.SEOInternal or self.SEOExternal:
                if os.path.exists(self.destination_folder + '\\crawl.seospider'):
                    os.rename(self.destination_folder + '\\crawl.seospider',
                              self.destination_folder + '\\crawl.seospider' + '_' +
                              time.ctime(os.path.getctime(self.destination_folder + '\\crawl.seospider'))
                              .replace(' ', '_').replace(':', '_'))
                if os.path.exists(self.log + '_cmd_writer_log.txt'):
                    with open(self.log + '_cmd_writer_log.txt', 'r') as f:
                        lines = f.read().splitlines()
                        for line in reversed(lines):
                            if line.find('Request: ') > 0:
                                self.url = line[line.find('url') + 7:line.find('SEOInternal') - 6]

        if not os.path.exists(self.destination_folder + '\\crawl.seospider'):
            if not os.path.exists(self.destination_folder):
                os.makedirs(self.destination_folder)

            # RUN SPIDER!!
            msg = (datetime.datetime.now().__str__()[:-7] +
                   'New client folder created in COMPLETE: ' + self.destination_folder)
            # Create spider log
            utils.logline(self.log + '_spider_log.txt', msg)
            # Write base cmd
            cmd = (self.base_folder + 'cli-tools\\seo\\screamingfrogseospidercli.exe  --crawl ' + self.url +
                   ' --headless --save-crawl --output-folder ' + self.destination_folder + ' --overwrite ')
            # Write in/external
            if self.SEOInternal and self.SEOExternal:
                cmd += ('--config \"' + Globals.base_folder + '\\conf\\SEOConfig.seospiderconfig\" '
                                                              '--export-tabs '
                                                              '\"Internal:All, Internal:HTML, Internal:PDF, Internal:Flash, Internal:Other, Internal:Unknown, '
                                                              'External:All, External:HTML, External:PDF, Images:Missing ALT Text, Page Titles:All, '
                                                              'Page Titles:Missing, Page Titles:Duplicate, H1:All\" '
                                                              '--save-report ' + '\"Crawl Overview\"')
            # Write internal
            if self.SEOInternal and not self.SEOExternal:
                cmd += ('--config \"' + Globals.base_folder + '\\conf\\SEOConfig_Internal.seospiderconfig\" '
                                                              ' --export-tabs '
                                                              '\"Internal:All, Internal:HTML, Internal:PDF, Internal:Flash, Internal:Other, Internal:Unknown, '
                                                              'Images:Missing ALT Text, Page Titles:All, Page Titles:Missing, Page Titles:Duplicate, H1:All\" '
                                                              '--save-report ' + '\"Crawl Overview\"')
            # Write external
            if self.SEOExternal and not self.SEOInternal:
                cmd = ('--config \"' + Globals.base_folder + '\\conf\\SEOConfig_Internal.seospiderconfig\" '
                                                             '--export-tabs '
                                                             '\"External:All, External:HTML, External:PDF, Page Titles:All, '
                                                             'Page Titles:Missing, Page Titles:Duplicate, H1:All\" '
                                                             '--save-report ' + '\"Crawl Overview\"')
            # Call spider thread engine
            if self.SEOInternal or self.SEOExternal:
                CMDWriter.spider_thread(self, cmd)  # Not threaded and we need a wait
            # Wait for crawl to end before running the following
        # Start AXE CONTROLLER
        # TODO: Read config for all selections
        if self.AXEChrome or self.AXEFirefox or self.AXEEdge:
            threads = list()
            t = Thread(target=CMDWriter.axe_controller, args=(self,))
            t.daemon = True
            t.start()
        # Start Lighthouse CONTROLLER
        if self.LighthouseMOBILE or self.LighthouseDESKTOP:
            threads = list()
            t = Thread(target=self.lighthouse_controller)
            t.daemon = True
            t.start()
        # Start PDF CONTROLLER
        path = self.destination_folder + 'SPIDER\\'
        if self.PDFAudit:
            thread = Thread(target=CMDWriter.pdf, args=(self.destination_folder,))
            thread.daemon = True
            thread.start()

    def spider_thread(self, cmd):
        try:
            # Log start
            msg = datetime.datetime.now().__str__()[:-7] + ' Crawl started: ' + cmd
            utils.logline(self.log + '_spider_log.txt', msg)
            # RUN THE SPIDER AND WAIT
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
            # Log spider progress
            while True:
                line = p.stdout.readline()
                if str(line).rfind('mCompleted=') > 10:
                    print(line)
                    start = str(line).rfind('mCompleted=')
                    percentage = str(line)[start + 11: start + 17].replace(']\\', '').replace(']', '')
                    utils.logline(self.log + '_spider_progress_log.txt', percentage)
                    pass
                if not line:
                    break
            # Log spider completion
            msg = datetime.datetime.now().__str__()[:-7] + ' Crawl completed: ' + cmd
            utils.logline(self.log + '_spider_log.txt', msg)
        except Exception as e:
            msg = e.__str__() + ' SPIDER THREAD:01' + '\n'
            print(msg)
            utils.logline(self.log + '_spider_log.txt', msg)

    def axe_controller(self):
        # AXE count total links
        # TODO: Add switch for "external"
        first_line = True
        row_count = sum(1 for row in csv.reader(open(self.destination_folder + '\\internal_html.csv', 'r',
                                                     encoding='utf8'), delimiter=','))
        row_count_i = row_count - 1
        # Open HTML CSV list
        with open(self.destination_folder + '\\internal_html.csv', 'r', encoding='utf8') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            destination_folder = self.report_folder + 'AXE\\CHROME\\AXEChrome_REPORT.csv'
            # Check for completed URLs
            for row in csv_reader:
                if first_line:
                    first_line = False
                    continue
                # Compare AXE_REPORT to SPIDER_CSV
                elif os.path.exists(destination_folder):
                    with open(destination_folder, encoding='utf8') as completed_urls:
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
                                    utils.logline(self.log + '_axe_chrome_log.txt', msg)
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
                    while threading.active_count() > thread_limit:
                        # print(threading.active_count().__str__() + ' THREADS RUNNING >> LIGHTHOUSE >> TAKE 10')
                        time.sleep(5)

                    row_count_i -= 1
                    # CHROME THREAD
                    if self.AXEChrome:
                        thread = Thread(target=CMDWriter.axeChrome, args=(self, row[0]))
                        thread.daemon = True
                        thread.start()
                        thread_monitor = Thread(target=CMDWriter.thread_monitor, args=(self, 'AXEChrome', thread,))
                        thread_monitor.setDaemon(True)
                        thread_monitor.start()

                        # Log "Remaining URLs" to progress log
                        msg = (' >>> Remaining URLs for [AXE]: ' + row_count_i.__str__() +
                               ' out of ' + row_count.__str__() +
                               ' ' + (datetime.datetime.now().__str__()[:-7]))
                        print(msg)
                        utils.logline(self.log + '_axe_chrome_log.txt', msg)

                    # FIREFOX THREAD
                    if self.AXEFirefox:
                        thread = Thread(target=CMDWriter.axeFirefox, args=(self, row[0]))
                        thread.daemon = True
                        thread.start()
                        thread_monitor = Thread(target=CMDWriter.thread_monitor, args=(self, 'AXEFirefox', thread,))
                        thread_monitor.setDaemon(True)
                        thread_monitor.start()

                        # Log "Remaining URLs" to progress log
                        msg = (' >>> Remaining URLs for [AXE]: ' + row_count_i.__str__() +
                               ' out of ' + row_count.__str__() +
                               ' ' + (datetime.datetime.now().__str__()[:-7]))
                        print(msg)
                        utils.logline(self.log + '_axe_firefox_log.txt', msg)

                    # EDGE THREAD
                    if self.AXEEdge:
                        thread = Thread(target=CMDWriter.axeEdge, args=(self, row[0]))
                        thread.daemon = False
                        thread.start()
                        thread_monitor = Thread(target=CMDWriter.thread_monitor, args=(self, 'AXEEdge', thread,))
                        thread_monitor.setDaemon(True)
                        thread_monitor.start()

                    # Log "Remaining URLs" to progress log
                    msg = (' >>> Remaining URLs for [AXE]: ' + row_count_i.__str__() +
                           ' out of ' + row_count.__str__() +
                           ' ' + (datetime.datetime.now().__str__()[:-7]))
                    print(msg)
                    utils.logline(self.log + '_axe_edge_log.txt', msg)

                except Exception as e:
                    msg = e.__str__() + ' AXE CONTROLLER:01' + '\n'
                    # print(msg)
                    utils.logline(self.log + '_axe_log.txt', msg)

    def axeChrome(self, axe_url):
        try:
            # Create and log new folder, log
            # destination_folder = self.report_folder + 'AXEChrome_' + self.report_name + '\\'
            destination_folder = self.report_folder + 'AXE\\Chrome\\'
            if not os.path.exists(destination_folder):
                os.makedirs(destination_folder)
                msg = (datetime.datetime.now().__str__()[:-7] + ' ' +
                       'New folder created in COMPLETE: ' + destination_folder)
                utils.logline(self.log + '_axe_chrome_log.txt', msg)

            # Load driver CHROME
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument("--headless")
            driver = webdriver.Chrome(chrome_options=chrome_options)
            driver.get(axe_url)
            # Start thread
            threads = list()
            thread = Thread(target=CMDWriter.axe_runner,
                            args=(self, driver, axe_url, destination_folder, 'Chrome'))
            thread.daemon = True
            thread.start()
            i = 0
            thread_monitor = Thread(target=CMDWriter.thread_monitor,
                                    args=(self, 'AXE RUNNER CHROME', thread,))
            thread_monitor.setDaemon(True)
            thread_monitor.start()
            msg = 'AXE STARTED thread for Chrome ' + axe_url
            print(msg)

        except Exception as e:
            msg = e.__str__() + ' AXE/CHROME'
            print(msg)
            utils.logline(self.log + '_axe_chrome_log.txt', msg)

    def axeFirefox(self, axe_url):
        try:
            # Create and log new folder, log
            # destination_folder = self.report_folder + 'AXEFirefox_' + self.report_name + '\\'
            destination_folder = self.report_folder + 'AXE\\Firefox\\'
            if not os.path.exists(destination_folder):
                os.makedirs(destination_folder)
                msg = (datetime.datetime.now().__str__()[:-7] + ' ' +
                       'New folder created in COMPLETE: ' + destination_folder)
                utils.logline(self.log + '_axe_firefox_log.txt', msg)
            # Load driver FIREFOX
            options = webdriver.FirefoxOptions()
            options.set_headless(True)
            driver = webdriver.Firefox(executable_path='geckodriver', options=options)
            driver.get(axe_url)
            # Start thread
            thread = Thread(target=CMDWriter.axe_runner,
                            args=(self, driver, axe_url, destination_folder, 'Firefox'))
            thread.daemon = True
            thread.start()
            thread_monitor = Thread(target=CMDWriter.thread_monitor,
                                    args=(self, 'AXE RUNNER FIREFOX', thread,))
            thread_monitor.setDaemon(True)
            thread_monitor.start()
            msg = ' >>> Started AXE thread for Firefox ' + axe_url
            print(msg)

        except Exception as e:
            msg = e.__str__() + ' AXE/FIREFOX'
            print(msg)
            utils.logline(self.log + '_axe_firefox_log.txt', msg)

    def axeEdge(self, axe_url):
        try:
            # Create and log new folder, log
            # destination_folder = self.report_folder + '\\AXEEdge_' + self.report_name + '\\'
            destination_folder = self.report_folder + '\\AXE\\Edge\\'
            if not os.path.exists(destination_folder):
                os.makedirs(destination_folder)
                msg = (datetime.datetime.now().__str__()[:-7] + ' ' +
                       'New folder created in COMPLETE: ' + destination_folder)
                utils.logline(self.log + '_axeEdge_log.txt', msg)

            # Load driver EDGE
            options = webdriver.edge.options.DesiredCapabilities
            options.headless = True
            driver = webdriver.Edge()
            driver.get(axe_url)
            # Start thread
            threads = list()
            thread = Thread(target=CMDWriter.axe_runner,
                            args=(self, driver, axe_url, destination_folder, 'Edge'))
            thread.daemon = True
            thread.start()
            i = 0
            thread_monitor = Thread(target=CMDWriter.thread_monitor,
                                    args=(self, 'AXE RUNNER EDGE', thread,))
            thread_monitor.setDaemon(True)
            thread_monitor.start()
            msg = ' >>> Started AXE thread for Edge ' + axe_url + '\n'
            print(msg)

        except Exception as e:
            msg = e.__str__() + ' AXE/EDGE'
            print(msg)
            utils.logline(self.log + '_axeEdge_log.txt', msg)

    def axe_runner(self, driver, axe_url, destination_folder, browser):
        # Load AXE driver
        try:
            axe = Axe(driver)
            results = axe
            try:
                axe.inject()  # Inject axe-core javascript into page.
                results = axe.run()  # Run axe accessibility checks.
                # Write results to file
                axe.write_results(results, destination_folder + '\\' + urllib.parse.quote_plus(axe_url) + '.json')
            except Exception as e:
                msg = e.__str__() + ' AXE RUNNER:01'
                print(msg)
                utils.logline(self.log + browser + '_axe_log.txt', msg)
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
            if not os.path.exists(destination_folder + '\\AXE' + browser + '_REPORT.csv'):
                write_header = True
            else:
                write_header = False
            # Write AXE_REPORT
            with open(destination_folder + '\\AXE' + browser + '_REPORT.csv',
                      'a', encoding='utf8', newline='') as csv_file:
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
                        utils.logline(self.log + '_axe_log.txt', msg)
        except Exception as e:
            msg = e.__str__() + ' AXE RUNNER:02'
            utils.logline(self.log + browser + '_axe_log.txt', msg)
            print(msg)

    @staticmethod
    def pdf(cvs_path, scope=False):
        '''os.chdir(cvs_path)
        file_list = os.listdir('.')
        pattern = "*pdf*"'''

        # Default to internal
        file = 'internal_pdf.csv'
        if scope == 'external':
            file = 'external_pdf.csv'
        PDFA().pdf_csv(file, cvs_path, scope)
        '''for entry in file_list:
            if fnmatch.fnmatch(entry, pattern):
                print(entry)
                PDFA().pdf_csv(entry, cvs_path, scope)'''

    def lighthouse_controller(self):
        first_line = True
        row_count = sum(1 for row in csv.reader(open(self.destination_folder + '\\internal_html.csv', 'r',
                                                     encoding='utf8'), delimiter=','))
        row_count_i = row_count - 1
        # Open HTML list
        with open(self.destination_folder + '\\internal_html.csv', 'r', encoding='utf8') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            destination_folder = self.report_folder + 'LIGHTHOUSE\\LIGHTHOUSE_REPORT.csv'
            for row in csv_reader:
                if first_line:
                    first_line = False
                    continue
                # Compare LIGHTHOUSE_REPORT to SPIDER_CSV
                elif os.path.exists(destination_folder):
                    with open(destination_folder, encoding='utf8') as completed_urls:
                        completed_urls_reader = csv.reader(completed_urls, delimiter=',')
                        jump = True
                        fl = True
                        for completed_url in completed_urls_reader:
                            if fl:
                                jump = True
                                fl = False
                                continue
                            if row[0] in completed_url:
                                jump = True
                                fl = False
                                msg = (' >>> Remaining URLs for [Lighthouse]: ' + (row_count_i - 1).__str__() +
                                       ' out of ' + row_count.__str__() +
                                       ' ' + (datetime.datetime.now().__str__()[:-7]))
                                print(msg)
                                utils.logline(self.log + '_lighthouse_progress_log.txt', msg)
                                row_count_i -= 1
                                break
                            else:
                                jump = False
                                fl = False
                        # JUMP OUT OF LINE RUN
                        if jump:
                            jump = False
                            continue
                try:

                    # set number of threads
                    while threading.active_count() > thread_limit:
                        # print(threading.active_count().__str__() + ' THREADS RUNNING >> LIGHTHOUSE >> TAKE 10')
                        time.sleep(10)
                    thread = Thread(target=CMDWriter.lighthouse,
                                    args=(self, row[0]))
                    thread.daemon = True
                    thread.start()
                    thread_monitor = Thread(target=CMDWriter.thread_monitor,
                                            args=(self, 'LIGHTHOUSE', thread,))
                    thread_monitor.setDaemon(True)
                    thread_monitor.start()

                    msg = (' >>> Remaining URLs for [Lighthouse]: ' + (row_count_i - 1).__str__() +
                           ' out of ' + row_count.__str__() +
                           ' ' + (datetime.datetime.now().__str__()[:-7]))
                    print(msg)
                    utils.logline(self.log + '_lighthouse_progress_log.txt', msg)
                    row_count_i -= 1
                except Exception as e:
                    msg = e.__str__() + ' Lighthouse CONTROLLER:01'
                    print(msg)
                    utils.logline(self.log + '_lighthouse_log.txt', msg)

    def lighthouse(self, lighthouse_url):
        destination_folder = self.report_folder + 'LIGHTHOUSE\\'
        # Create \complete\client\report_folder
        if not os.path.exists(destination_folder):
            os.makedirs(destination_folder)
            utils.logline(self.log + '_lighthouse_log.txt', 'New client REPORTS folder created in COMPLETE: ' +
                          self.report_folder)
        if self.LighthouseMOBILE:
            try:
                # os.chdir(destination_folder)
                cmd = ('lighthouse --output=json --output=html  --chrome-flags=--headless --quiet ' +
                       '--output-path=' + destination_folder + urllib.parse.quote_plus(lighthouse_url) +
                       ' --emulated-form-factor=mobile ' + lighthouse_url)
                msg = cmd + ' LIGHTHOUSE:01 MOBILE STARTED: ' + lighthouse_url
                # print(msg)
                os.system('cmd /c ' + cmd)
                msg = cmd + ' LIGHTHOUSE:01 MOBILE FINISHED'
                # print(msg)
                utils.logline(self.log + '_lighthouse_log.txt', msg)
            except Exception as e:
                msg = e.__str__() + ' LIGHTHOUSE:01'
                print(msg)
                utils.logline(self.log + '_lighthouse_log.txt', msg)
        if self.LighthouseDESKTOP:
            try:
                cmd = ('lighthouse --output=json --output=html  --chrome-flags=--headless --quiet ' +
                       '--output-path=' + destination_folder + urllib.parse.quote_plus(lighthouse_url) +
                       ' --emulated-form-factor=desktop ' + lighthouse_url)
                msg = cmd + ' LIGHTHOUSE:01 DESKTOP STARTED: ' + lighthouse_url
                print(msg)
                os.system('cmd /c ' + cmd)
                msg = cmd + ' LIGHTHOUSE:01 DESKTOP FINISHED'
                print(msg)
                utils.logline(self.log + '_lighthouse_log.txt', msg)
            except Exception as e:
                msg = e.__str__() + ' LIGHTHOUSE:01'
                print(msg)
                utils.logline(self.log + '_lighthouse_log.txt', msg)
        try:
            # Look for JSON results
            list_json = []
            os.chdir(destination_folder)
            file_list = os.listdir('.')
            pattern = "*.json"
            for entry in file_list:
                if fnmatch.fnmatch(entry, pattern):
                    # print(entry)
                    list_json.append(entry)
            # Load JSON results
            with open(destination_folder + list_json[1], encoding="utf8") as readJSON:
                data_json = json.load(readJSON)
            # Define CSV
            csv_row = []

            dict_json = ['test', 'url', 'score', 'title', 'description']
            if not os.path.exists(destination_folder + 'LIGHTHOUSE_REPORT.csv'):
                csv_row.insert(0, dict_json)

            # Look for violations
            for key, value in data_json['audits'].items():
                if value['score'] == 0:
                    dict_json = ['lighthouse', lighthouse_url, value['score'].__str__(),
                                 value['title'], value['description']]
                    csv_row.insert(csv_row.__len__() + 1, dict_json)
            # Write violations report CSV
            with open(destination_folder + 'LIGHTHOUSE_REPORT.csv',
                      'a+', newline='', encoding="utf8") as csv_file:
                for i in range(csv_row.__len__()):
                    row = []
                    writer = csv.writer(csv_file, quoting=csv.QUOTE_ALL)
                    writer.dialect.lineterminator.replace('\n', '')
                    writer.writerow(csv_row[i])
            msg = csv_row.__str__() + ' LIGHTHOUSE:02'
            # print(msg)
            utils.logline(self.log + '_lighthouse_log.txt', msg)
            # print('COMPLETE - LIGHTHOUSE:02 ::: ')
        except Exception as e:
            msg = e.__str__() + ' LIGHTHOUSE:02'
            print(msg)
            utils.logline(self.log + '_lighthouse_log.txt', msg)

    @staticmethod
    def thread_monitor(self, process_name, thread):
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
