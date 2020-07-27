import datetime as datatime
import os


class Globals:
    # Global
    base_folder = os.getcwd() + '\\'
    gbl_report_folder = base_folder + 'REPORTS\\'

    # n_watch = base_folder + "queue\\new\\"
    # p_watch = base_folder + "queue\\pipe\\"
    # c_watch = base_folder + "queue\\complete\\"
    template_id = '1oPxGCc8gS1RhMhPqzDz-_SWSQANiPssoxFKgcRd5bsY'
    report_folder_id = '1_spCa2YbGEpYf3Ck2AfpfGVjFWy4HzTE'
    # SORT_SITE = "C:\\Program Files (x86)\\PowerMapper Software\\SortSite 5\\SortSite.exe"
    # ADOBE = "C:\\Program Files (x86)\\Adobe\\Acrobat DC\\Acrobat\\acrobat.exe"

    # logs
    process_log = os.getcwd() + "\\logs\\process_log.txt"
    # watch_log = base_folder + "logs\\watch_log.txt"

    dt = datatime.datetime
    bod = dt.combine(dt.now().date(), dt.now().time())
