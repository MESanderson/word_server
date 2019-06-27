import sqlite3
from hashlib import sha256
import os
import time


def _get_conn(config):
    conn = sqlite3.connect(config['db_host'])
    conn.row_factory = sqlite3.Row
    return conn


def add_document(file_path, config):
    m = sha256()
    with open(file_path, 'rb') as fi:
        doc_text = fi.read()
        m.update(doc_text)

    doc_hash = m.digest().hex()
    doc_name = os.path.split(file_path)[1]

    conn = _get_conn(config)

    try:
        conn.execute('''insert into raw_documents(doc_hash, doc_name, doc_body, update_epoch_time)
                    values (?, ?, ?, ?); ''', ((doc_hash, doc_name, doc_text, int(time.time()))))
    except sqlite3.IntegrityError as e:
        if 'UNIQUE' in e.args[0]:
            pass
        else:
            print(e)
            raise e
            conn.close()

    conn.commit()

    conn.close()

def list_docs(config):
    conn = _get_conn(config)
    curs = conn.cursor()

    curs.execute('''
    Select doc_name, doc_hash, update_epoch_time from raw_documents;
    ''')

    data = curs.fetchall()
    conn.close()
    return data

def get_doc(config, doc_id):
    conn = _get_conn(config)
    curs = conn.cursor()

    curs.execute('''
    Select * from raw_documents where doc_hash = (?);
    ''', (doc_id,))

    data = curs.fetchone()
    conn.close()
    return data


def init(config):
    conn = _get_conn(config)
    curs = conn.cursor()

    curs.execute('''Create table if not exists raw_documents 
    (doc_hash text primary key, doc_name text, doc_body text, update_epoch_time int);''')
    curs.execute('''Create table if not exists words (doc_hash text, word text, count int,
                 Foreign Key (doc_hash) references raw_doucments(doc_hash),
                 Constraint words_pk unique (doc_hash, word));''')
    #curs.execute('Create unique index words_pk on words(doc_hash, word);')

    conn.commit()
    conn.close()
