import threading
from flask import Flask, render_template, flash, request
from wtforms import Form, TextField, validators, StringField
from commander import CMDWriter
from report import Table, Item, PDFItem, PDFTable, CommanderTable, CommanderItem, DashTable, DashItem
from globals import Globals

# App config
DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'


class ReusableForm(Form):
    print(">>> REPORT STARTED!")
    report_name = StringField('report_name:', validators=[validators.DataRequired()])
    email = StringField('Email:', validators=[validators.DataRequired(), validators.Length(min=6, max=35)])
    url = StringField('URL:', validators=[validators.DataRequired(), validators.Length(min=3, max=350)])


@app.route('/', methods=['GET', 'POST'])
def audit_request():
    form = ReusableForm(request.form)

    print(form.errors)
    if request.method == 'POST':
        # Get form
        form_response = request.form

        # Parse form response
        report_name = form_response['report_name'].replace(' ', '_')
        url = form_response['url']
        email = form_response['email']

        if form.validate():
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
                AXE = form_response['AXE']
            except Exception as e:
                AXE = False
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
            t = threading.Thread(target=CMDWriter, args=(report_name, url, email, SEOInternal, SEOExternal,
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
            if not url:
                msg += ' [URL] '
            flash(msg)
    return render_template('request_form.html', form=form)


@app.route('/action_restart/', methods=['GET', 'POST'])
def action_restart():
    sort = request.args.get('sort', 'id')
    report_name = request.args.get('id')
    report_type = request.args.get('report_type')
    if report_type == 'pdf_internal':
        CMDWriter.pdf(os.path.join(Globals.gbl_report_folder + report_name + '\\' + 'SPIDER\\', scope='internal')
    if report_type == 'pdf_external':
        CMDWriter.pdf(Globals.gbl_report_folder + report_name + '\\' + 'SPIDER\\', scope='external')
    if report_type == 'spider':
        url = 'RESTART'
        email = False
        SEOInternal = True
        SEOExternal = True
        PDFAudit = False
        LighthouseMOBILE = False
        LighthouseDESKTOP = False
        AXEChrome = False
        AXEFirefox = False
        AXEEdge = False
        thread = threading.Thread(target=CMDWriter, args=(report_name, url, email, SEOInternal, SEOExternal,
                                                          PDFAudit, LighthouseMOBILE, LighthouseDESKTOP,
                                                          AXEChrome, AXEFirefox, AXEEdge))
        thread.daemon = True
        thread.start()

    if report_type == 'axe':
        url = 'RESTART'
        email = False
        SEOInternal = False
        SEOExternal = False
        PDFAudit = False
        LighthouseMOBILE = False
        LighthouseDESKTOP = False
        AXEChrome = True
        AXEFirefox = True
        AXEEdge = False
        thread = threading.Thread(target=CMDWriter, args=(report_name, url, email, SEOInternal, SEOExternal,
                                                          PDFAudit, LighthouseMOBILE, LighthouseDESKTOP,
                                                          AXEChrome, AXEFirefox, AXEEdge))
        thread.daemon = True
        thread.start()

    if report_type == 'lighthouse':
        url = 'RESTART'
        email = False
        SEOInternal = False
        SEOExternal = False
        PDFAudit = False
        LighthouseMOBILE = True
        LighthouseDESKTOP = True
        AXEChrome = False
        AXEFirefox = False
        AXEEdge = False
        thread = threading.Thread(target=CMDWriter, args=(report_name, url, email, SEOInternal, SEOExternal,
                                                          PDFAudit, LighthouseMOBILE, LighthouseDESKTOP,
                                                          AXEChrome, AXEFirefox, AXEEdge))
        thread.daemon = True
        thread.start()
    return reports()


@app.route('/reports/', methods=['GET', 'POST'])
def reports():
    sort = request.args.get('sort', 'id')
    id = request.args.get('id')
    reverse = (request.args.get('direction', 'asc') == 'desc')
    report_name = request.args.get('report_name')
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

    dash = DashTable(DashItem.get_sorted_by(sort, 'dash', reverse), sort_by=sort, sort_reverse=reverse)
    lighthouse = Table(Item.get_sorted_by(sort, 'lighthouse', reverse), sort_by=sort, sort_reverse=reverse)
    axe_c = Table(Item.get_sorted_by(sort, 'axe_c', reverse), sort_by=sort, sort_reverse=reverse)
    axe_c_summary = Table(Item.get_sorted_by(sort, 'axe_c_summary', reverse), sort_by=sort, sort_reverse=reverse)
    pdf_internal = PDFTable(PDFItem.get_sorted_by(sort, 'pdf_internal', reverse), sort_by=sort, sort_reverse=reverse)
    pdf_external = PDFTable(PDFItem.get_sorted_by(sort, 'pdf_external', reverse), sort_by=sort, sort_reverse=reverse)

    return render_template("report.html",
                           report_name=report_name,
                           axe_u=axe_c_summary,
                           axe_u_title='Summary AXE errors:',
                           axe_u_desc='A summary AXE errors...',
                           pdf_internal=pdf_internal,
                           pdf_internal_title='Summary PDF errors (INTERNAL):',
                           pdf_internal_desc='A summary of PDF errors which are internally hosted.',
                           pdf_external=pdf_external,
                           pdf_external_title='Summary PDF errors (EXTERNAL):',
                           pdf_external_desc='A summary pf PDF errors for documents externally hosted.',
                           axe=axe_c,
                           axe_title='Full AXE Accessibility Results',
                           axe_desc='Full, unfiltered AXE results',
                           lighthouse=lighthouse,
                           lighthouse_title='Lighthouse Accessibility Results',
                           lighthouse_desc='Lighthouse is a ... '
                                           'The following violations were ...')


if __name__ == '__main__':
    # app.run(host='0.0.0.0', port=80)
    app.run(host='127.0.0.1', port=5000)
