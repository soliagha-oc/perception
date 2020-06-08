from globals import Globals

import os
import subprocess
import datetime as dt
from urllib import \
    request as request
# urlopen
from io import \
    StringIO, BytesIO
import string
import requests
import re
import csv
import threading
import utils as utils
import time
import datetime as datetime
import multiprocessing
from report import PDFItem
from PyPDF2 import PdfFileReader
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import resolve1
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.layout import LAParams  # , LTTextBox, LTTextLine
from threading import Thread, Event


stop_event = Event()
global document

class PDFAudit:

    def __init__(self):
        self.report_folder = ''
        self.document_folder = ''
        self.pdf_path = ''
        self.report_name = ''
        # self.line_count = 0
        self.csv_header = []
        self.gbl_report_folder = Globals.gbl_report_folder + self.report_folder
        self.log = self.gbl_report_folder + 'logs\\'
        self.document_t = PDFDocument
        self.parser = PDFParser
        self.url = ''
        self.line_count = 1

    def load_pdf(self, PDFDocument, password):
        i = 0
        while threading.currentThread().is_alive():
            i += 1
            report_path = self.report_folder + self.report_name
            print('LOADING: ' + i.__str__())
            time.sleep(1)
            try:
                self.document_t = PDFDocument(self.parser)
            except Exception as e:
                print('PDF OBJECT FAILED ::::::::::::::::::::::::: ' + e.__str__())

            if stop_event.is_set():
                if i >= 90:
                    # print(self.parser.fp.name + ' FAILED (SEC): ' + i.__str__())
                    print('XXXXXXXXXXXXXXXXXXXXXXXX PDF LOAD STOP EVENT : 90')
                    row = [self.line_count, 'PDFDocument FAILED TO LOAD - 90 SEC TIMEOUT REACHED FOR: ' + self.url,
                           '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '',
                           '', ]
                    # self.line_count += 1
                    # 90 SECOND TIMEOUT or FAILED TO PARSER
                    with open(report_path, 'a', encoding='utf8', newline='') as csv_file:
                        writer = csv.writer(csv_file, quoting=csv.QUOTE_ALL)
                        writer.dialect.lineterminator.replace('\n', '')
                        writer.writerow(row)
                print('XXXXXXXXXXXXXXXXXXXXXXXX PDF LOAD STOP EVENT!!')
                break

    def thread_monitor(self, process_name, thread):
        i = 0
        while thread.is_alive():
            time.sleep(2)
            i += 2
            print(process_name + ' WORKING FOR ' + i.__str__() + ' seconds for: ' + thread.getName())
            print('ACTIVE COUNT: ' + str(threading.active_count()))
            if i == 120:
                print(thread.getName() + ' XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX> KILLED')
                report_path = self.report_folder + self.report_name
                row = [self.line_count, 'PDF THREAD FAILED TO PROCESS - 120 SEC TIMEOUT REACHED FOR: ' + self.url,
                       '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ]
                # self.line_count += 1
                # 120 SECOND TIMEOUT
                with open(report_path, 'a', encoding='utf8', newline='') as csv_file:
                    writer = csv.writer(csv_file, quoting=csv.QUOTE_ALL)
                    writer.dialect.lineterminator.replace('\n', '')
                    writer.writerow(row)
                break

        print(process_name + ':[COMPLETED IN ' + i.__str__() + ' seconds for: ' + thread.getName() + ']')

    def pdf_csv(self, csv_to_audit, source_folder, scope):
        # Define CSV
        self.csv_header = (['csvline', 'url', 'filename', 'local_path',
                            'encrypted', 'decrypt_pass', 'istagged', 'pages', 'toc', 'form', 'fields', 'tables',
                            'word_count', 'char_count', 'words_per_page', 'chars_per_word', 'image_count',
                            '%_img_per_page', 'ocr_risk', 'author', 'creator', 'producer', 'subject', 'title', 'text'])
        # root_path = os.path.split(source_folder)[0]
        self.report_folder = os.path.split(source_folder)[0].replace('SPIDER', '')

        # Set logs
        self.log = self.report_folder + 'logs\\'
        if not os.path.exists(self.log):
            os.makedirs(self.log)

        self.report_folder += 'PDF\\'
        if not os.path.exists(self.report_folder):
            os.makedirs(self.report_folder)

        # os.chdir(self.report_folder)
        if csv_to_audit.find('internal') >= 0 or scope == 'internal':
            self.log = self.log + '\\_pdf_internal_log.txt'
            self.report_name = csv_to_audit[:-4] + '_a.csv'
        if csv_to_audit.find('external') >= 0 or scope == 'external':
            self.log = self.log + '\\_pdf_external_log.txt'
            self.report_name = csv_to_audit[:-4] + '_a.csv'
        self.document_folder = self.report_folder
        if not os.path.exists(self.document_folder):
            os.makedirs(self.document_folder)
        try:
            write_header = False
            report_path = self.report_folder + self.report_name
            if not os.path.exists(report_path):
                write_header = True
            os.chdir(self.report_folder)
            with open(report_path, 'a', encoding='utf8', newline='') as csv_file:
                writer = csv.writer(csv_file, quoting=csv.QUOTE_ALL)
                if write_header:
                    writer.writerow(self.csv_header)

        except Exception as e:
            print('PDF I/O error: ' + e.__str__())

        row_count = sum(1 for row in csv.reader(open(source_folder + '\\' + csv_to_audit, 'r',
                                                     encoding='utf8'), delimiter=','))
        row_count_i = row_count - 2
        with open(source_folder + '\\' + csv_to_audit, encoding='utf8') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            # set number of threads
            thread_count = 1
            destination_folder = self.report_name
            # Get URL for PDF from row[1]
            # FOR EACH PDF
            first_line = True
            for row in csv_reader:
                pdf_url = row[0]
                skip = False
                if first_line:
                    first_line = False
                    print(' ::::::::::::::::::::::::::::: START ALL PDF ::::::::')
                    continue
                elif os.path.exists(destination_folder):
                    with open(destination_folder, encoding='utf8') as completed_urls:
                        completed_urls_reader = csv.reader(completed_urls, delimiter=',')
                        jump = True
                        fl = True
                        skip = False
                        for completed_url in completed_urls_reader:
                            if fl:
                                jump = True
                                fl = False
                                continue
                            if pdf_url in completed_url[1]:
                                msg = (' >>> Remaining PDFs: ' + row_count_i.__str__() + ' out of ' +
                                       row_count.__str__() + ' ' + (datetime.datetime.now().__str__()[:-7]))
                                row_count_i -= 1
                                # self.line_count += 1
                                utils.logline(self.log, msg)
                                print(msg)
                                fl = False
                                skip = True
                                break
                    # completed_urls.close()
                try:
                    '''thread = multiprocessing.Process(self.pdf_thread(line_count, row[0]))
                    thread.daemon = False
                    thread.start()
                    thread.join()
                    from concurrent.futures import ThreadPoolExecutor
                    from time import sleep
                    executor = ThreadPoolExecutor(50)
                    future = executor.submit(PDFAudit.pdf_thread(self, line_count, row[0]))
                    print(future.done().__str__())'''
                    if skip:
                        skip = False
                        continue
                    '''from concurrent.futures import ThreadPoolExecutor
                    from multiprocessing import Pool
                    p = Pool(5)
                    print('Pool row count ' + row_count_i.__str__())
                    p.map(self.pdf_thread(line_count, row[0]))
                    thread_pool = ThreadPoolExecutor(max_workers=10)
                    xyz = thread_pool.submit(self.pdf_thread(line_count, row[0]))'''
                    self.line_count = csv_reader.line_num
                    self.url = pdf_url
                    thread = Thread(target=self.pdf_thread,
                                    args=(pdf_url,))
                    thread.setDaemon(True)
                    while threading.active_count() > 35:
                        print('                                >> TAKE 5')
                        time.sleep(5)
                    print('AWAY FOR ::::::::::::: ' + pdf_url + ' ' + thread.getName())
                    thread.start()
                    i = 0
                    thread_monitor = Thread(target=self.thread_monitor,
                                            args=('PDF', thread))
                    thread_monitor.setDaemon(True)
                    thread_monitor.start()
                    time.sleep(5)
                    # PDFAudit.twatch(self, thread, i)

                    '''while thread.is_alive():
                        time.sleep(1)
                        i += 1
                        print('WORKING: ' + i.__str__() + '  ' + thread.getName())'''

                    # thread.join()

                    msg = (' >>> Remaining PDFs: ' + row_count_i.__str__() + ' out of ' +
                           row_count.__str__() + ' ' + (datetime.datetime.now().__str__()[:-7]))
                    row_count_i -= 1
                    utils.logline(self.log, msg)
                    print(msg)
                    '''while thread.is_alive():
                        time.sleep(1)
                        i += 1
                        print('WORKING: ' + i.__str__() + thread.getName())'''
                    # stop_event.set()
                    '''
                    # PDFAudit.pdf_thread(self, line_count, row[0])
                    msg = (' >>> Remaining PDFs: ' + row_count_i.__str__() + ' out of ' + row_count.__str__() + ' ' +
                            (datetime.datetime.now().__str__()[:-7]))
                    row_count_i -= 1
                    print(msg)
                    utils.logline(self.log, msg)
                    while threading.active_count() >= thread_count:
                        threads = threading.active_count()
                        string = (' !! PDF !! Excessive threads in PDF, pausing 5 secs - ' +
                                  str(threads) + ' active threads. \n')
                        print(string)
                        time.sleep(5)
                        status = threading.Thread(target=PDFAudit.status_update(str(threads)))
                        status.start()'''
                except Exception as e:
                    msg = e.__str__() + ' PDF:01' + '\n'
                    print(msg)
                    utils.logline(self.log, msg)

        # csv_file.close()

    def pdf_thread(self, url):

        pdf_name = ''
        exit_call = ''
        csv_row = []
        # save PDF to disk
        try:
            pdf_name = BytesIO(url.split("/")[-1].encode('UTF-8')).read().__str__()[2:-1]
            valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
            regex = re.compile(valid_chars)
            # First parameter is the replacement, second parameter is your input string
            # regex.sub('', pdf_name.__str__())
            # pdf_name = ''.join(c for c in pdf_name if c in valid_chars)
            pdf_name = regex.sub('', pdf_name.__str__())
            self.pdf_path = self.document_folder + regex.sub('', pdf_name)
            r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            # if not os.path.exists(self.pdf_path):
            with open(self.pdf_path, 'wb') as code:
                code.write(r.content)
            code.close()
            csv_row.insert(0, [self.csv_header[0], self.line_count.__str__()])
            csv_row.insert(1, [self.csv_header[1], url if url.__len__() > 0 else 'NULL'])
            csv_row.insert(2, [self.csv_header[2], pdf_name if pdf_name.__len__() > 0 else 'NULL'])
            csv_row.insert(3, [self.csv_header[3], self.pdf_path if self.pdf_path.__len__() > 0 else 'NULL'])
            print(' >>>> PDF START:[' + url + '] ' + self.line_count.__str__() + ' ' + (
                datetime.datetime.now().__str__()[:-7]))
        except Exception as e:
            csv_row.insert(0, [self.csv_header[0], self.line_count.__str__()])
            csv_row.insert(1, [self.csv_header[1], url if url.__len__() > 0 else 'NULL'])
            csv_row.insert(2, [self.csv_header[2], e.__str__()])
            csv_row.insert(3, [self.csv_header[3], self.pdf_path if self.pdf_path.__len__() > 0 else 'NULL'])
            print(e)
            pass

        my_file = os.path.join(self.document_folder + pdf_name)
        try:
            fp = open(my_file, 'rb')
            # self.pdf(fp, csv_row)
        except Exception as e:
            print('     PDF LOAD FAILED !!! LINE 290ish ' + self.line_count.__str__() + ' :  ' + self.pdf_path)
            csv_row.pop(3)
            csv_row.insert(3, [self.csv_header[3], 'PDF FAILED TO OPEN:' + self.pdf_path if self.pdf_path.__len__() > 0 else 'NULL'])
            # Write results
            row = []
            for i in range(csv_row.__len__()):
                row.append(csv_row[i][1])
            report_path = self.report_folder + self.report_name
            # OPEN FAILED
            with open(report_path, 'a', encoding='utf8', newline='') as csv_file:
                writer = csv.writer(csv_file, quoting=csv.QUOTE_ALL)
                writer.dialect.lineterminator.replace('\n', '')
                writer.writerow(row)
            return
        try:
            self.pdf(fp, csv_row)
        except Exception as e:
            print('PDF FAIL')

    def pdf(self, fp, csv_row):
        password = ''
        extracted_text = ''
        self.parser = PDFParser(fp)
        self.document_t = PDFDocument
        pf = PdfFileReader
        # isEncrypted
        try:
            i = 0
            try:
                thread = Thread(target=self.load_pdf,
                                args=(PDFDocument, password))
                thread.start()
                thread.join(timeout=90)
            except Exception as e:
                print('PDF I/O error: ' + e.__str__())
                row = [self.line_count, 'PDF DOCUMENT OBJECT FAILED TO LOAD - ' + e.__str__() + ': ' +
                       self.url, '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '',
                       '', ]
                # self.line_count += 1
                report_path = self.report_folder + self.report_name
                # 90 SECONDS or LOAD FAIL
                with open(report_path, 'a', encoding='utf8', newline='') as csv_file:
                    writer = csv.writer(csv_file, quoting=csv.QUOTE_ALL)
                    writer.dialect.lineterminator.replace('\n', '')
                    writer.writerow(row)

            stop_event.set()
            '''document = PDFDocument(parser)
            if not parser.doc:
                raise PDFTextExtractionNotAllowed
            else:
                document = PDFDocument(parser)'''
            document = PDFDocument
            document = self.document_t
            pf = PdfFileReader(BytesIO(open(self.pdf_path, 'rb').read()))
            # ENCRYPTION
            if self.parser.doc.encryption is not None:
                csv_row.insert(4, [self.csv_header[4], 'ENCRYPTED'])
                csv_row.insert(5, [self.csv_header[5], 'ENCRYPTED'])
                # exit_call = e.__str__() + ' is encrypted!!'
                # print exit_call
            else:
                csv_row.insert(4, [self.csv_header[4], 'FALSE'])
                csv_row.insert(5, [self.csv_header[5], 'NA'])
        except Exception as e:
            csv_row.insert(4, [self.csv_header[4], 'FAILED: ' + e.__str__()])
            csv_row.insert(5, [self.csv_header[5], 'NA'])
            exit_call = e.__str__() + ' document failed!!'
            print(exit_call)
            pass

        page_count = 0
        # istagged
        try:
            pages = PDFPage.get_pages(document)
            if not document.is_extractable:
                raise PDFTextExtractionNotAllowed
            rsrcmgr = PDFResourceManager()
            laparams = LAParams()
            page_no = 0
            istagged = 'FALSE'
            try:
                # document.catalog
                if document.catalog['MarkInfo']:
                    istagged = 'TRUE'
            except Exception as e:
                exit_call = e.__str__() + ' tagged info failed!!'
                print(exit_call)
            page_count = resolve1(document.catalog['Pages'])['Count']
            csv_row.insert(6, [self.csv_header[6], istagged])
            csv_row.insert(7, [self.csv_header[7], page_count])
        except Exception as e:
            csv_row.insert(6, [self.csv_header[6], 'IsTagged: ' + e.__str__()])
            csv_row.insert(7, [self.csv_header[7], 'Page Count: ' + e.__str__()])
            exit_call = e.__str__() + ' tagged info failed!!'
            print(exit_call)
        # TOC
        try:
            if pf.outlines:
                csv_row.insert(8, [self.csv_header[8], 'TRUE'])
                '''pdf_path_toc = self.document_folder + pdf_name + '_toc.txt'
                places_list = pf.outlines

                with open(pdf_path_toc, 'w') as filehandle:
                    filehandle.writelines("%s\n" % place for place in places_list)
                filehandle.close()'''
            else:
                csv_row.insert(8, [self.csv_header[8], 'FALSE'])
        except Exception as e:
            csv_row.insert(8, [self.csv_header[8], 'TOC FAILED: ' + e.__str__()])
            exit_call = e.__str__() + ' toc info failed!!'
            print(exit_call)
        # isForm, fields,
        try:
            if pf.getFields():
                csv_row.insert(9, [self.csv_header[9], 'TRUE'])
                csv_row.insert(10, [self.csv_header[10], pf.getFields().__len__()])
            else:
                csv_row.insert(9, [self.csv_header[9], 'FALSE'])
                csv_row.insert(10, [self.csv_header[10], 0])
        except Exception as e:
            csv_row.insert(9, [self.csv_header[9], 'FORMS: ' + e.__str__()])
            csv_row.insert(10, [self.csv_header[10], 'FIELDS: ' + e.__str__()])
            exit_call = e.__str__() + ' forms failed!!'
            print(exit_call)
        # tables
        csv_row.insert(11, [self.csv_header[11], 'NOT RUN'])
        write_clip = ''
        word_count = 0
        words_per_page = 0
        char_count = 0
        chars_per_word = 0
        image_count = 0
        # TODO: write 3 page sample and word count
        try:
            if pf.getNumPages() < 50:
                for page in range(pf.getNumPages()):
                    p = pf.getPage(page)
                    text_clip = p.extractText().encode('UTF-8')
                    text_clip = BytesIO(text_clip).read().__str__()[2:]
                    count_clip = re.findall(r"[^\W_]+", text_clip, re.MULTILINE)
                    word_count += len(count_clip)
                    char_count += len(text_clip)
                    if page <= 3:
                        write_clip += '[ PAGE ' + (page + 1).__str__() + ' START ] '
                        write_clip += text_clip.replace('\n', '').replace(',', ' ').replace('"', '')
                        write_clip += '[ PAGE ' + (page + 1).__str__() + ' END ]'
            else:
                write_clip = 'OVER 50 PAGES - SAMPLE SKIPPED'
        except Exception as e:
            exit_call = e.__str__() + ' :: TEXT sample failed!!'
            write_clip = exit_call
            word_count = exit_call
            char_count = exit_call
            print(exit_call)
        # TODO: Words/chars per page
        try:
            if not word_count == 0:
                chars_per_word = char_count / word_count
            else:
                chars_per_word = 0
            if not page_count == 0:
                words_per_page = word_count / page_count
            else:
                words_per_page = 0
        except Exception as e:
            exit_call = e.__str__() + ' :: WORD METRICS failed!!'
            chars_per_word = exit_call
            words_per_page = exit_call
            print(exit_call)
        # TODO: Add to row
        i = 12
        try:
            csv_row.insert(i, [self.csv_header[i], word_count.__str__()])
        except Exception as e:
            csv_row.insert(i, [self.csv_header[i], 'WORD_COUNT: ' + e.__str__()])
        i = 13
        try:
            csv_row.insert(i, [self.csv_header[i], char_count.__str__()])
        except Exception as e:
            csv_row.insert(i, [self.csv_header[i], 'CHAR_COUNT: ' + e.__str__()])
        i = 14
        try:
            csv_row.insert(i, [self.csv_header[i], words_per_page.__str__()])
        except Exception as e:
            csv_row.insert(i, [self.csv_header[i], 'WPP: ' + e.__str__()])
        i = 15
        try:
            csv_row.insert(i, [self.csv_header[i], chars_per_word.__str__()])
        except Exception as e:
            csv_row.insert(i, [self.csv_header[i], 'CPP: ' + e.__str__()])

        # TODO: IMAGES
        i = 16
        try:
            '''pdf_path_image = self.document_folder + pdf_name[:-4] + '_images.txt'
            self.pdf_path_imgfolder = self.document_folder + pdf_name[:-4] + '_img' '''
            pdfImages = Globals.base_folder + 'cli-tools\\pdfimages.exe'

            img_folder = self.document_folder + 'images\\'  # + pdf_name[:-4] + '\\'
            if not os.path.exists(img_folder):
                os.makedirs(img_folder)
            # cmd = pdfImages + ' -list ' + '\"' + pdf_path + '\"'
            # output = subprocess.Popen(cmd, stdout=subprocess.PIPE).communicate()[0].split(b'\n')
            # save images to disk
            cmd = pdfImages + ' -list \"' + self.pdf_path + '\" \"' + ' ' + '\"'
            # subprocess.Popen(cmd, stdout=subprocess.PIPE)
            os.chdir(img_folder)
            image_list = subprocess.Popen(cmd, stdout=subprocess.PIPE).communicate()[0].split(b'\r\n')
            # os.remove(img_folder)
            # image_count = output.count('\n')
            image_count = image_list.__len__()
            if image_count > 2:
                # target = open(pdf_path_image, 'w')
                # target.write(image_list)
                # target.close()
                csv_row.insert(i, [self.csv_header[i], (image_count - 2).__str__()])
            elif image_count == 0:
                csv_row.insert(i, [self.csv_header[i], 0])
            else:
                csv_row.insert(i, [self.csv_header[i], 0])
        except Exception as e:
            csv_row.insert(i, [self.csv_header[i], e.__str__() + ' image info failed!!'])
            exit_call = e.__str__() + ' image info failed!!'
            print(exit_call)
        # TODO: IMAGES per page
        i = 17
        percent_img_per_page = float
        try:
            if not image_count == 0 or page_count == 0:
                percent_img_per_page = (float(image_count) / float(page_count)) * 100
            else:
                percent_img_per_page = 0
            csv_row.insert(i, [self.csv_header[i], percent_img_per_page])
        except Exception as e:
            csv_row.insert(i, [self.csv_header[i], 'IMG: ' + e.__str__()])
        # TODO: OCR risk
        i = 18
        try:
            if words_per_page == 0 or percent_img_per_page > 3000:
                ocr_risk = 5
            elif words_per_page < 15 or percent_img_per_page > 2000:
                ocr_risk = 4
            elif words_per_page < 40 or percent_img_per_page > 1000:
                ocr_risk = 3
            elif words_per_page < 70 or percent_img_per_page > 425:
                ocr_risk = 2
            elif words_per_page < 80 or percent_img_per_page > 200:
                ocr_risk = 1
            else:
                ocr_risk = 0
            csv_row.insert(i, [self.csv_header[i], ocr_risk])
        except Exception as e:
            csv_row.insert(i, [self.csv_header[i], 'OCR: ' + e.__str__()])
        # author, creator, producer, subject, title,
        di = pf
        try:
            di = pf.documentInfo
        except Exception as e:
            exit_call = e.__str__() + ' :: DOCUMENT INFO LOAD failed!!'
            print(exit_call)

        # Document info
        if di:
            # Author
            try:
                i = 19
                if di.author:
                    csv_row.insert(i, [self.csv_header[i], di.author.encode('UTF-8')])
                else:
                    csv_row.insert(i, [self.csv_header[i], 'NULL'])
            except Exception as e:
                csv_row.insert(i, [self.csv_header[i], 'AUTHOR: ' + e.__str__()])
                exit_call = e.__str__() + ' doc info failed!!'
                print(exit_call)
            # Creator
            try:
                i = 20
                if di.creator:
                    csv_row.insert(i, [self.csv_header[i], di.creator.encode('UTF-8')])
                else:
                    csv_row.insert(i, [self.csv_header[i], 'NULL'])
            except Exception as e:
                csv_row.insert(i, [self.csv_header[i], 'CREATOR: ' + e.__str__()])
                print(exit_call)
                print('#5.1')
            # Producer
            try:
                i = 21
                if di.producer:
                    csv_row.insert(i, [self.csv_header[i], di.producer.encode('UTF-8')])
                else:
                    csv_row.insert(i, [self.csv_header[i], 'NULL'])
            except Exception as e:
                csv_row.insert(i, [self.csv_header[i], 'PRODUCER: ' + e.__str__()])
                print(exit_call)
            # Subject
            try:
                i = 22
                if di.subject:
                    csv_row.insert(i, [self.csv_header[i], di.subject.encode('UTF-8')])
                else:
                    csv_row.insert(i, [self.csv_header[i], 'NULL'])
            except Exception as e:
                csv_row.insert(i, [self.csv_header[i], 'SUBJECT: ' + e.__str__()])
                print(exit_call)
            # Title
            try:
                i = 23
                if di.title:
                    csv_row.insert(i, [self.csv_header[i], di.title.encode('UTF-8')])
                else:
                    csv_row.insert(i, [self.csv_header[i], 'NULL'])
            except Exception as e:
                csv_row.insert(i, [self.csv_header[i], 'TITLE: ' + e.__str__()])
                print(exit_call)
        # Document clip
        i = 24
        try:
            csv_row.insert(i, [self.csv_header[i], write_clip])
        except Exception as e:
            csv_row.insert(i, [self.csv_header[i], e.__str__()])
        # Write results
        row = []
        for i in range(csv_row.__len__()):
            row.append(csv_row[i][1])
        report_path = self.report_folder + self.report_name
        # COPLETE WRITE
        with open(report_path, 'a', encoding='utf8', newline='') as csv_file:
            writer = csv.writer(csv_file, quoting=csv.QUOTE_ALL)
            writer.dialect.lineterminator.replace('\n', '')
            writer.writerow(row)
        # csv_file.close()
        fp.close()
        os.remove(self.pdf_path)

        # Log close
        msg = (' >>>> PDF complete:[' + self.url + '] ' + self.line_count.__str__() + ' ' +
               (datetime.datetime.now().__str__()[:-7]))
        print(msg)
        utils.logline(self.log, msg)
