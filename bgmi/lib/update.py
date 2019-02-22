# coding=utf-8
import os
import sqlite3

from bgmi import __version__
from bgmi.config import DB_URL, BGMI_PATH, write_default_config
from bgmi.lib.models import db
from bgmi.sql import init_db
from bgmi.utils import print_error, print_info, print_warning

OLD = os.path.join(BGMI_PATH, 'old')


def exec_sql(sql, db=DB_URL):
    try:
        print_info('Execute {}'.format(sql))
        conn = sqlite3.connect(db)
        conn.execute(sql)
        conn.commit()
        conn.close()
    except sqlite3.OperationalError:  # pragma: no cover
        print_error('Execute SQL statement failed', exit_=False)


def update_database():
    if not os.path.exists(OLD):
        v = '0'
    else:
        with open(OLD, 'r+') as f:
            v = f.read()

    if v < '3.0.0':
        print_warning("can't simply upgrade from bgmi<3.0.0, database structure changed too much,\n"
                      "so bgmi must clear your database. type 'y' to continue")
        c = input()
        if c == 'y':
            db.close()
            os.remove(DB_URL)
            init_db()
            write_default_config()
        else:
            exit()

    with open(OLD, 'w') as f:
        f.write(__version__)
