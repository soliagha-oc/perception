from flask import Flask, render_template, flash, request
import os
import threading
from wtforms import Form
from commander import CMDWriter
from report import Table, Item, PDFItem, PDFTable, CommanderTable, CommanderItem

# App config
app = Flask(__name__)
app.config.from_object('config.Config')
BASE_FOLDER = app.config['BASE_FOLDER']
REPORTS_FOLDER = app.config['REPORTS_FOLDER']
SPIDER = app.config['SPIDER']


class ReusableForm(Form):
    print(">>> REPORT STARTED!")
    # report_name = StringField('report_name', validators=[validators.DataRequired(), validators.Length(min=6, max=35)])
    # email = StringField('email', validators=[validators.DataRequired(), validators.Length(min=6, max=35)])
    # url = StringField('url', validators=[validators.Length(min=-1, max=35)])

@app.route('/', methods=['GET', 'POST'])
def audit_request():
    global report_name, email, url
    form = ReusableForm(request.form)
    print(form.errors)
    if request.method == 'POST':
        # Get form
        form_response = request.form
        # Report name
        try:
            report_name = form_response['report_name'].replace(' ', '_')
        except Exception as e:
            print(e)
        # Email
        try:
            email = form_response['email']
        except Exception as e:
            print(e)
        # URL
        try:
            url = form_response['url']
        except Exception as e:
            print(e)

        # Handle form variables
        if form.validate():
            # SEO
            try:
                SEOInternal = form_response['SEOInternal']
            except Exception as e:
                SEOInternal = False
                print(e)
            try:
                SEOExternal = form_response['SEOExternal']
            except Exception as e:
                SEOExternal = False
                print(e)

            # CSV Upload
            CSVUpload = False
            try:
                # check if the post request has the file part
                if 'UploadCSV' not in request.files:
                    print('No file part')
                    # return redirect(request.url)
                file = request.files['UploadCSV']
                # if user does not select file, browser also
                # submit an empty part without filename
                if file.filename == '':
                    print('No selected file')
                    # return redirect(request.url)
                if file and allowed_file(file.filename):
                    app.config['UPLOAD_FOLDER'] = os.path.join(app.config['UPLOAD_FOLDER'], report_name, 'CSV')
                    if not os.path.exists(app.config['UPLOAD_FOLDER']):
                        os.makedirs(app.config['UPLOAD_FOLDER'])
                    os.chdir(REPORTS_FOLDER)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
                    CSVUpload = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                    # return redirect(url_for('uploaded_file',
                    #                         filename=filename))
            except Exception as e:
                print(e)
            try:
                PDFAudit = form_response['PDFAudit']
            except Exception as e:
                PDFAudit = False
                print(e)
            try:
                LighthouseMOBILE = form_response['lighthouse-mobile']
            except Exception as e:
                LighthouseMOBILE = False
                print(e)
            try:
                LighthouseDESKTOP = form_response['lighthouse-desktop']
            except Exception as e:
                LighthouseDESKTOP = False
                print(e)
            try:
                AXEChrome = form_response['AXEChrome']
            except Exception as e:
                AXEChrome = False
                print(e)
            try:
                AXEFirefox = form_response['AXEFirefox']
            except Exception as e:
                AXEFirefox = False
                print(e)
            try:
                AXEEdge = form_response['AXEEdge']
            except Exception as e:
                AXEEdge = False
                print(e)
            # Take off
            msg = ('Your request to run audits on ' + url + ' for ' + report_name + ' has been registered. ' +
                   'An email will be sent to ' + email + ' once the report is complete.')
            flash(msg)

            threads = list()
            t = threading.Thread(target=CMDWriter, args=(report_name, url, email, SEOInternal, SEOExternal, CSVUpload,
                                                         PDFAudit, LighthouseMOBILE, LighthouseDESKTOP,
                                                         AXEChrome, AXEFirefox, AXEEdge))
            print('REQUEST:before STARTING thread: ' + t.name + '\n')
            threads.append(t)
            t.daemon = True
            t.start()
        else:
            msg = 'Error: the following fields are required:'
            if not report_name:
                msg += ' [Report Name] '
            if not email:
                msg += ' [Email] '
            if SPIDER:
                if not url:
                    msg += ' [URL] '
            flash(msg)
    return render_template('request_form.html', form=form, spider=SPIDER)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/action_restart/', methods=['GET', 'POST'])
def action_restart():
    # Set vars
    # sort = request.args.get('sort', 'id')
    url = ''
    email = ''
    report_name = request.args.get('id')
    report_folder = os.path.join(REPORTS_FOLDER, report_name)
    request_log = os.path.join(report_folder, 'logs', '_request_log.tuple')
    report_type = request.args.get('report_type')

    # Check for request_log to get:
    if os.path.exists(request_log):
        with open(request_log, 'r') as file:
            reader = file.read()
            request_tuple = eval(reader)
            for tup in request_tuple:
                # get email
                if tup[0] == 'email':
                    report_email = tup[1]
                # get url
                if tup[0] == 'url':
                    report_url = tup[1]

    # csv_path = os.path.join(REPORTS_FOLDER, report_name, 'CSV')

    if report_type == 'spider':
        t = threading.Thread(target=CMDWriter, args=(report_name, url, email, True, True, False, False, False, False,
                                                     False, False, False))
        t.daemon = True
        t.start()

    if report_type == 'axe':
        t = threading.Thread(target=CMDWriter, args=(report_name, url, email, False, False, False, False, False, False,
                                                     True, True, False))
        t.daemon = True
        t.start()

    if report_type == 'lighthouse':
        t = threading.Thread(target=CMDWriter, args=(report_name, url, email, False, False, False, False, True, True,
                                                     False, False, False))
        t.daemon = True
        t.start()
    if report_type == 'pdf':
        t = threading.Thread(target=CMDWriter, args=(report_name, url, email, False, False, False, True, False, False,
                                                     False, False, False))
        t.daemon = True
        t.start()

    return reports()


@app.route('/reports/', methods=['GET', 'POST'])
def reports():
    sort = request.args.get('sort', 'id')
    id = request.args.get('id')
    reverse = (request.args.get('direction', 'asc') == 'desc')
    # report_name = request.args.get('report_name')
    if id:
        return index(id)
    else:
        reports_list = CommanderTable(CommanderItem.get_sorted_by(id, sort, 'report_list', reverse),
                                      sort_by=sort, sort_reverse=reverse)
        return render_template("report.html", reports_list=reports_list)


@app.route('/report/', methods=['GET', 'POST'])
@app.route('/report/<int:id>')
def index(id):
    sort = request.args.get('sort', 'id')
    reverse = (request.args.get('direction', 'asc') == 'desc')
    report_name = request.args.get('id')

    # dash = DashTable(DashItem.get_sorted_by(sort, 'dash', reverse), sort_by=sort, sort_reverse=reverse)
    lighthouse = Table(Item.get_sorted_by(sort, 'lighthouse', reverse), sort_by=sort, sort_reverse=reverse)
    axe_c = Table(Item.get_sorted_by(sort, 'axe_c', reverse), sort_by=sort, sort_reverse=reverse)
    axe_c_summary = Table(Item.get_sorted_by(sort, 'axe_c_summary', reverse), sort_by=sort, sort_reverse=reverse)
    pdf = PDFTable(PDFItem.get_sorted_by(sort, 'pdf', reverse), sort_by=sort, sort_reverse=reverse)
    # pdf_external = PDFTable(PDFItem.get_sorted_by(sort, 'pdf_external', reverse), sort_by=sort, sort_reverse=reverse)

    return render_template("report.html",
                           report_name=report_name,
                           axe_u=axe_c_summary,
                           axe_u_title='Summary AXE errors:',
                           axe_u_desc='A summary AXE errors...',
                           pdf=pdf,
                           pdf_title='Summary PDF errors (INTERNAL):',
                           pdf_desc='A summary of PDF errors which are internally hosted.',
                           # pdf_external=pdf_external,
                           # pdf_external_title='Summary PDF errors (EXTERNAL):',
                           # pdf_external_desc='A summary pf PDF errors for documents externally hosted.',
                           axe=axe_c,
                           axe_title='Full AXE Accessibility Results',
                           axe_desc='Full, unfiltered AXE results',
                           lighthouse=lighthouse,
                           lighthouse_title='Lighthouse Accessibility Results',
                           lighthouse_desc='Lighthouse is a ... '
                                           'The following violations were ...')


if __name__ == '__main__':
    app.run(host=app.config['HOST'],
            port=app.config['PORT'])
