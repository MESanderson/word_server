import sqlite3


def _init_sqlite_db(file):
    conn = sqlite3.connect(file)
    curs = conn.cursor()

    curs.execute('Create table if not exists raw_documents (doc_name text, doc_hash text, doc_body text);')

    conn.commit()


def init(config):
    file = config['db_host']
    _init_sqlite_db(file)

