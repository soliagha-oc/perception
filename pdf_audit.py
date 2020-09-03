import os
import subprocess
from io import BytesIO
import string
import requests
import re
import csv
import threading
import utils as utils
import time
import datetime as datetime
from flask import Flask
from PyPDF2 import PdfFileReader
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import resolve1
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from threading import Thread, Event

stop_event = Event()


# App config
app = Flask(__name__)
app.config.from_object('config.Config')
PROCESS_LOG = app.config['PROCESS_LOG']
BASE_FOLDER = app.config['BASE_FOLDER']
REPORTS_FOLDER = app.config['REPORTS_FOLDER']
GMAIL_USER = app.config['GMAIL_USER']
GMAIL_PASSWORD = app.config['GMAIL_PASSWORD']
SENT_FROM = app.config['SENT_FROM']

class PDFAudit:
    def __init__(self):
        self.pdf_folder = ''
        self.document_folder = ''
        self.pdf_path = ''
        self.pdf_report = ''
        self.csv_header = []
        self.log = ''  # os.path.join(REPORTS_FOLDER, 'logs')
        self.pdf_document = PDFDocument
        self.parser = PDFParser
        self.url = ''
        self.line_count = 1

    def pdf_csv(self, so, csv_file_path):

        """ # Get the URL from the log file
        if os.path.exists(so.request_log):
            with open(so.request_log, 'r') as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                for row in csv_reader:
                    if row == 'url':
                        # TODO:
                        continue """

        # Define CSV header
        self.csv_header = (['csvline', 'url', 'filename', 'local_path',
                            'encrypted', 'decrypt_pass', 'istagged', 'pages', 'toc', 'form', 'fields', 'tables',
                            'word_count', 'char_count', 'words_per_page', 'chars_per_word', 'image_count',
                            '%_img_per_page', 'ocr_risk', 'author', 'creator', 'producer', 'subject', 'title', 'text'])
        # root_path = os.path.split(source_folder)[0]
        # self.report_folder = os.path.split(source_folder)[0].replace('SPIDER', '')

        # Set logs
        if not os.path.exists(so.logs):
            os.makedirs(so.logs)
        self.log = os.path.join(so.logs, '_pdf_log.txt')
        self.pdf_folder = os.path.join(so.report_folder, 'PDF')
        if not os.path.exists(self.pdf_folder):
            os.makedirs(self.pdf_folder)
        self.pdf_report = os.path.join(self.pdf_folder, 'PDF_REPORT.csv')
        self.document_folder = os.path.join(self.pdf_folder, 'PDFs')
        if not os.path.exists(self.document_folder):
            os.makedirs(self.document_folder)

        try:
            write_header = False
            # report_path = os.path.join(self.report_folder, self.report_name)
            if not os.path.exists(self.pdf_report):
                write_header = True
            os.chdir(self.pdf_folder)
            with open(self.pdf_report, 'a', encoding='utf8', newline='') as csv_file:
                writer = csv.writer(csv_file, quoting=csv.QUOTE_ALL)
                if write_header:
                    writer.writerow(self.csv_header)
        except Exception as e:
            print('PDF I/O error:', str(e))

        # csv_source = os.path.join(source_folder, csv_to_audit)
        row_count = sum(1 for row in csv.reader(open(csv_file_path, 'r',
                                                     encoding='utf8'), delimiter=','))

        row_count_i = row_count - 2
        with open(csv_file_path, encoding='utf8') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            # set number of threads
            # Get URL for PDF from row[1]
            # FOR EACH PDF
            first_line = True
            for row in csv_reader:
                pdf_url = row[0]
                skip = False
                if first_line:
                    first_line = False
                    print(' ::: START ALL PDF :::')
                    continue
                elif os.path.exists(self.pdf_report):
                    with open(self.pdf_report, encoding='utf8') as completed_urls:
                        completed_urls_reader = csv.reader(completed_urls, delimiter=',')
                        fl = True
                        skip = False
                        for completed_url in completed_urls_reader:
                            if fl:
                                fl = False
                                continue
                            if pdf_url in completed_url[1]:
                                msg = (' >>> Remaining PDFs: ', str(row_count_i), ' out of ',
                                       str(row_count), (str(datetime.datetime.now())[:-7]))
                                row_count_i -= 1
                                utils.log_line(self.log, ''.join(msg))
                                print(''.join(msg))
                                fl = False
                                skip = True
                                break
                try:
                    if skip:
                        skip = False
                        continue
                    self.line_count = csv_reader.line_num
                    self.url = pdf_url
                    t = Thread(target=self.pdf_thread, args=(pdf_url,))
                    t.setDaemon(True)
                    while threading.active_count() > 35:
                        print(' !! TAKE 5 !!')
                        time.sleep(5)
                    print('RUN AUDIT FOR ::',  pdf_url, t.getName())
                    t.start()
                    thread_monitor = Thread(target=self.thread_monitor,
                                            args=('PDF', t))
                    thread_monitor.setDaemon(True)
                    thread_monitor.start()
                    time.sleep(5)
                    msg = (' >>> Remaining PDFs:', str(row_count_i), ' out of ',
                           str(row_count), str(datetime.datetime.now())[:-7])
                    row_count_i -= 1
                    utils.log_line(self.log, ''.join(msg))
                    print(''.join(msg))

                except Exception as e:
                    msg = (str(e), ' PDF:01')
                    print(''.join(msg))
                    utils.log_line(self.log, ''.join(msg))

    def pdf_thread(self, url):
        pdf_name = ''
        csv_row = []
        # save PDF to disk
        try:
            pdf_name = str(BytesIO(url.split("/")[-1].encode('UTF-8')).read())[2:-1]
            valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
            regex = re.compile(valid_chars)
            pdf_name = regex.sub('', str(pdf_name))
            self.pdf_path = os.path.join(self.document_folder, regex.sub('', str(pdf_name)))
            r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            with open(self.pdf_path, 'wb') as code:
                code.write(r.content)
            code.close()
            csv_row.insert(0, [self.csv_header[0], str(self.line_count)])
            csv_row.insert(1, [self.csv_header[1], url if url.__len__() > 0 else 'NULL'])
            csv_row.insert(2, [self.csv_header[2], pdf_name if pdf_name.__len__() > 0 else 'NULL'])
            csv_row.insert(3, [self.csv_header[3], self.pdf_path if self.pdf_path.__len__() > 0 else 'NULL'])
            print(' >>>> PDF START:[',  url,  '] ', str(self.line_count), str(datetime.datetime.now())[:-7])
        except Exception as e:
            csv_row.insert(0, [self.csv_header[0], str(self.line_count)])
            csv_row.insert(1, [self.csv_header[1], url if url.__len__() > 0 else 'NULL'])
            csv_row.insert(2, [self.csv_header[2], str(e)])
            csv_row.insert(3, [self.csv_header[3], self.pdf_path if self.pdf_path.__len__() > 0 else 'NULL'])
            print(str(e))
            pass

        try:
            fp = open(self.pdf_path, 'rb')
            # self.pdf(fp, csv_row)
        except Exception:
            print('PDF LOAD FAILED !!!', str(self.line_count), ':', self.pdf_path)
            csv_row.pop(3)
            csv_row.insert(3, [self.csv_header[3], 'PDF FAILED TO OPEN:' + self.pdf_path if self.pdf_path.__len__() > 0 else 'NULL'])
            # Write results
            row = []
            for i in range(csv_row.__len__()):
                row.append(csv_row[i][1])
            row_append = ['', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '']
            index = 4
            for ii in row_append:
                row.insert(index, ii)
                index += 1
            # OPEN FAILED
            with open(self.pdf_report, 'a', encoding='utf8', newline='') as csv_file:
                writer = csv.writer(csv_file, quoting=csv.QUOTE_ALL)
                writer.dialect.lineterminator.replace('\n', '')
                writer.writerow(row)
            return
        try:
            self.pdf(fp, csv_row)
        except Exception as e:
            print('PDF FAIL', str(e))

    def pdf(self, fp, csv_row):
        password = ''
        self.parser = PDFParser(fp)
        # self.document_t = PDFDocument
        pf = PdfFileReader
        # isEncrypted
        try:
            try:
                t = Thread(target=self.load_pdf, args=(password,))
                t.start()
                # 90 SECONDS or LOAD FAIL
                t.join(timeout=90)
            except Exception as e:
                print('PDF I/O error: ' + str(e))
                row = [self.line_count, 'PDF DOCUMENT OBJECT FAILED TO LOAD - ' + str(e) + ': ' +
                       self.url, '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '',
                       '', ]
                with open(self.pdf_report, 'a', encoding='utf8', newline='') as csv_file:
                    writer = csv.writer(csv_file, quoting=csv.QUOTE_ALL)
                    writer.dialect.lineterminator.replace('\n', '')
                    writer.writerow(row)

            stop_event.set()
            # document = PDFDocument
            # pdf_document = self.document_t
            pf = PdfFileReader(BytesIO(open(self.pdf_path, 'rb').read()))

            # ENCRYPTION
            if self.parser.doc.encryption is not None:
                csv_row.insert(4, [self.csv_header[4], 'ENCRYPTED'])
                csv_row.insert(5, [self.csv_header[5], 'ENCRYPTED'])
            else:
                csv_row.insert(4, [self.csv_header[4], 'FALSE'])
                csv_row.insert(5, [self.csv_header[5], 'NA'])
        except Exception as e:
            csv_row.insert(4, [self.csv_header[4], 'FAILED: ' + str(e)])
            csv_row.insert(5, [self.csv_header[5], 'NA'])
            exit_call = str(e) + ' document failed!!'
            print(exit_call)
            pass

        page_count = 0
        # is_tagged
        try:
            if not self.pdf_document.is_extractable:
                raise PDFTextExtractionNotAllowed
            is_tagged = 'FALSE'
            try:
                # document.catalog
                if self.pdf_document.catalog['MarkInfo']:
                    istagged = 'TRUE'
            except Exception as e:
                exit_call = str(e) + ' tagged info failed!!'
                print(exit_call)
            page_count = resolve1(self.pdf_document.catalog['Pages'])['Count']
            csv_row.insert(6, [self.csv_header[6], is_tagged])
            csv_row.insert(7, [self.csv_header[7], page_count])
        except Exception as e:
            csv_row.insert(6, [self.csv_header[6], 'IsTagged: ' + str(e)])
            csv_row.insert(7, [self.csv_header[7], 'Page Count: ' + str(e)])
            exit_call = str(e) + ' tagged info failed!!'
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
            csv_row.insert(8, [self.csv_header[8], 'TOC FAILED: ' + str(e)])
            exit_call = str(e) + ' toc info failed!!'
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
            csv_row.insert(9, [self.csv_header[9], 'FORMS: ' + str(e)])
            csv_row.insert(10, [self.csv_header[10], 'FIELDS: ' + str(e)])
            exit_call = str(e) + ' forms failed!!'
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
                    text_clip = str(BytesIO(text_clip).read())[2:]
                    count_clip = re.findall(r"[^\W_]+", text_clip, re.MULTILINE)
                    word_count += len(count_clip)
                    char_count += len(text_clip)
                    if page <= 3:
                        write_clip += '[ PAGE ' + str((page + 1)) + ' START ] '
                        write_clip += text_clip.replace('\n', '').replace(',', ' ').replace('"', '')
                        write_clip += '[ PAGE ' + str((page + 1)) + ' END ]'
            else:
                write_clip = 'OVER 50 PAGES - SAMPLE SKIPPED'
        except Exception as e:
            exit_call = str(e) + ' :: TEXT sample failed!!'
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
            exit_call = str(e) + ' :: WORD METRICS failed!!'
            chars_per_word = exit_call
            words_per_page = exit_call
            print(exit_call)
        # TODO: Add to row
        i = 12
        try:
            csv_row.insert(i, [self.csv_header[i], str(word_count)])
        except Exception as e:
            csv_row.insert(i, [self.csv_header[i], 'WORD_COUNT: ' + str(e)])
        i = 13
        try:
            csv_row.insert(i, [self.csv_header[i], str(char_count)])
        except Exception as e:
            csv_row.insert(i, [self.csv_header[i], 'CHAR_COUNT: ' + str(e)])
        i = 14
        try:
            csv_row.insert(i, [self.csv_header[i], str(words_per_page)])
        except Exception as e:
            csv_row.insert(i, [self.csv_header[i], 'WPP: ' + str(e)])
        i = 15
        try:
            csv_row.insert(i, [self.csv_header[i], str(chars_per_word)])
        except Exception as e:
            csv_row.insert(i, [self.csv_header[i], 'CPP: ' + str(e)])

        # TODO: IMAGES
        i = 16
        try:
            # pdfImages = os.path.join(BASE_FOLDER, 'cli-tools', 'pdfimages.exe')
            img_folder = os.path.join(self.document_folder, 'images')  # + pdf_name[:-4] + '\\'
            if not os.path.exists(img_folder):
                os.makedirs(img_folder)
            # cmd = pdfImages + ' -list ' + '\"' + pdf_path + '\"'
            # output = subprocess.Popen(cmd, stdout=subprocess.PIPE).communicate()[0].split(b'\n')
            # save images to disk
            # cmd = pdfImages + ' -list \"' + self.pdf_path + '\" \"' + ' ' + '\"'
            cmd = 'pdfimages -list \"' + self.pdf_path + '\" \"' + img_folder + '/\"'
            # subprocess.Popen(cmd, stdout=subprocess.PIPE)
            # os.chdir(img_folder)
            image_list = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True).communicate()[0].split(b'\r\n')
            # image_list = subprocess.Popen(cmd, shell=True)
            # os.remove(img_folder)
            # image_count = output.count('\n')
            image_count = image_list.__len__()
            # if image_count > 2:
                # target = open(pdf_path_image, 'w')
                # target.write(image_list)
                # target.close()
            csv_row.insert(i, [self.csv_header[i], str(image_count)])
            '''elif image_count == 0:
                csv_row.insert(i, [self.csv_header[i], 0])
            else:
                csv_row.insert(i, [self.csv_header[i], 0])'''
        except Exception as e:
            csv_row.insert(i, [self.csv_header[i], str(e) + ' image info failed!!'])
            exit_call = str(e) + ' image info failed!!'
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
            csv_row.insert(i, [self.csv_header[i], 'IMG: ' + str(e)])
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
            csv_row.insert(i, [self.csv_header[i], 'OCR: ' + str(e)])
        # author, creator, producer, subject, title,
        di = pf
        try:
            di = pf.documentInfo
        except Exception as e:
            exit_call = str(e) + ' :: DOCUMENT INFO LOAD failed!!'
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
                csv_row.insert(i, [self.csv_header[i], 'AUTHOR: ' + str(e)])
                exit_call = str(e) + ' doc info failed!!'
                print(exit_call)
            # Creator
            try:
                i = 20
                if di.creator:
                    csv_row.insert(i, [self.csv_header[i], di.creator.encode('UTF-8')])
                else:
                    csv_row.insert(i, [self.csv_header[i], 'NULL'])
            except Exception as e:
                csv_row.insert(i, [self.csv_header[i], 'CREATOR: ' + str(e)])
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
                csv_row.insert(i, [self.csv_header[i], 'PRODUCER: ' + str(e)])
                print(exit_call)
            # Subject
            try:
                i = 22
                if di.subject:
                    csv_row.insert(i, [self.csv_header[i], di.subject.encode('UTF-8')])
                else:
                    csv_row.insert(i, [self.csv_header[i], 'NULL'])
            except Exception as e:
                csv_row.insert(i, [self.csv_header[i], 'SUBJECT: ' + str(e)])
                print(exit_call)
            # Title
            try:
                i = 23
                if di.title:
                    csv_row.insert(i, [self.csv_header[i], di.title.encode('UTF-8')])
                else:
                    csv_row.insert(i, [self.csv_header[i], 'NULL'])
            except Exception as e:
                csv_row.insert(i, [self.csv_header[i], 'TITLE: ' + str(e)])
                print(exit_call)
        # Document clip
        i = 24
        try:
            csv_row.insert(i, [self.csv_header[i], write_clip])
        except Exception as e:
            csv_row.insert(i, [self.csv_header[i], str(e)])
        # Write results
        row = []
        for i in range(csv_row.__len__()):
            row.append(csv_row[i][1])
        # COPLETE WRITE
        with open(self.pdf_report, 'a', encoding='utf8', newline='') as csv_file:
            writer = csv.writer(csv_file, quoting=csv.QUOTE_ALL)
            writer.dialect.lineterminator.replace('\n', '')
            writer.writerow(row)
        # csv_file.close()
        fp.close()
        os.remove(self.pdf_path)

        # Log close
        msg = (' >>>> PDF complete:[' + self.url + '] ' + str(self.line_count) + ' ' +
               (str(datetime.datetime.now())[:-7]))
        print(msg)
        utils.log_line(self.log, msg)

    def load_pdf(self, password):
        i = 0
        while threading.currentThread().is_alive():
            i += 1
            print('LOADING: ' + str(i))
            time.sleep(1)
            # try:
            self.pdf_document = PDFDocument(self.parser)
            # except Exception as e:
            # print('PDFDocument(self.parser) FAILED ::::: ' + str(e))

            if stop_event.is_set():
                if i >= 120:
                    # print(self.parser.fp.name + ' FAILED (SEC): ' + str(i))
                    print(' >>> FAIL : PDF LOAD STOP EVENT : 120 SECONDS')
                    row = [self.line_count, 'PDFDocument FAILED TO LOAD - 90 SEC TIMEOUT REACHED FOR: ' + self.url,
                           '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '',
                           '', ]
                    # self.line_count += 1
                    # 90 SECOND TIMEOUT or FAILED TO PARSER
                    with open(self.pdf_report, 'a', encoding='utf8', newline='') as csv_file:
                        writer = csv.writer(csv_file, quoting=csv.QUOTE_ALL)
                        writer.dialect.lineterminator.replace('\n', '')
                        writer.writerow(row)
                break

    def thread_monitor(self, process_name, thread):
        i = 0
        while thread.is_alive():
            time.sleep(2)
            i += 2
            print(process_name + ' WORKING FOR ' + str(i) + ' seconds for: ' + thread.getName())
            print('ACTIVE COUNT: ' + str(threading.active_count()))
            if i == 180:
                print(thread.getName() + ' KILLED AT 180 SECONDS')
                row = [self.line_count, 'PDF THREAD FAILED TO PROCESS - 180 SEC TIMEOUT REACHED FOR: ' + self.url,
                       '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ]
                # self.line_count += 1
                # 120 SECOND TIMEOUT
                with open(self.pdf_report, 'a', encoding='utf8', newline='') as csv_file:
                    writer = csv.writer(csv_file, quoting=csv.QUOTE_ALL)
                    writer.dialect.lineterminator.replace('\n', '')
                    writer.writerow(row)
                break

        print(process_name + ':[COMPLETED IN ' + str(i) + ' seconds for: ' + thread.getName() + ']')