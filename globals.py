import datetime as datatime
import os


class Globals:
    # Global
    base_folder = os.getcwd() + '\\'
    gbl_report_folder = base_folder + 'REPORTS\\'
    template_id = '1oPxGCc8gS1RhMhPqzDz-_SWSQANiPssoxFKgcRd5bsY'
    report_folder_id = '1_spCa2YbGEpYf3Ck2AfpfGVjFWy4HzTE'

    # logs
    process_log = os.getcwd() + "\\logs\\process_log.txt"
    dt = datatime.datetime
    bod = dt.combine(dt.now().date(), dt.now().time())
