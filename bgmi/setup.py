import os

import bgmi
from bgmi.config import (
    BGMI_PATH, FRONT_STATIC_PATH, IS_WINDOWS, SAVE_PATH, SCRIPT_PATH, TMP_PATH, TOOLS_PATH
)
from bgmi.lib import constants
from bgmi.lib.download import get_download_class
from bgmi.lib.models import get_kv_storage
from bgmi.sql import init_db
from bgmi.utils import (
    exec_command, get_web_admin, print_error, print_info, print_success, print_warning
)


def install_crontab():
    if os.getenv('BGMI_IN_DOCKER'):
        print_warning('env BGMI_IN_DOCKER exists, skip install crontab')
        return
    print_info('Installing crontab job')
    if IS_WINDOWS:
        base = os.path.join(os.path.dirname(__file__), 'others\\windows\\cron')
        exec_command(
            'SCHTASKS /Create /TN "bgmi calendar updater" /SC HOURLY /MO 2 '
            '/TR "{tr}" /F'.format(tr=os.path.join(base, 'cal.vbs'))
        )

        exec_command(
            'SCHTASKS /Create /TN "bgmi bangumi updater" /SC HOURLY /MO 12 '
            '/TR "{tr}" /F'.format(tr=os.path.join(base, 'update.vbs'))
        )
    else:
        path = os.path.join(os.path.dirname(__file__), 'others/crontab.sh')
        exec_command("bash '%s'" % path)


def create_dir():
    path_to_create = (BGMI_PATH, SAVE_PATH, TMP_PATH, SCRIPT_PATH, TOOLS_PATH, FRONT_STATIC_PATH)

    if not os.environ.get('HOME', os.environ.get('USERPROFILE', None)):
        print_warning('$HOME and $BGMI_PATH not set, use a tmp dir ' + BGMI_PATH)

    # bgmi home dir
    try:
        for path in path_to_create:
            if not os.path.exists(path):
                os.makedirs(path)
                print_success('%s created successfully' % path)
    except OSError as e:
        print_error('Error: {}'.format(str(e)))


def install(ret):
    print('Installing bgmi')
    if not os.path.exists(BGMI_PATH):
        print_warning('BGMI_PATH %s does not exist, installing' % BGMI_PATH)

    bgmi.setup.create_dir()
    bgmi.setup.install_crontab()
    init_db()

    get_download_class().install()

    if constants.kv.OLD_VERSION not in get_kv_storage():
        get_kv_storage()[constants.kv.OLD_VERSION] = bgmi.__version__
    if ret.install_web:
        get_web_admin()
    else:
        print_info('skip downloading web static files')
