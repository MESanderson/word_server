from flask import Flask, request, flash, redirect, jsonify
from flask.templating import render_template
from db import init as db_init
from basic_word_processing import create_word_list_from_doc
from werkzeug.utils import secure_filename
import os
import datetime


UPLOAD_FOLDER = r'/home/mike/PycharmProjects/word_server/temp_docs'
if not os.path.isdir(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

ALLOWED_EXTENSIONS = {'.txt', }

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'blahblah'

config_obj = {
    'db': 'sqlite',
    'db_host': r'/home/mike/PycharmProjects/word_server/word_db.db'
}

db = db_init(config_obj)


def format_epoch_time(epoch_time):
    return datetime.datetime.fromtimestamp(epoch_time).isoformat()


def store_document(file):
    if file.filename == '':
        return False, 'Please supply a file name'
    if not ('.' in file.filename and os.path.splitext(file.filename)[1] in ALLOWED_EXTENSIONS):
        return False, 'Only .txt files are currently supported'

    filename = secure_filename(file.filename)
    uploaded_file = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(uploaded_file)

    db.add_document(uploaded_file, config_obj)

    return True, "File Successfully Uploaded"


def process_document_words(doc_hash):
    doc = db.get_doc(config_obj, doc_hash)
    doc_text = doc['doc_body'].decode('utf-8')
    word_list = create_word_list_from_doc(doc_text)
    db.update_doc_word_list(config_obj, word_list)
    return word_list


@app.route('/')
def hello_world():
    return app.send_static_file('index.html')


@app.route('/document_index')
def doc_index():
    doc_data_raw = db.list_docs(config_obj)
    doc_data_dicts = [{
        'doc_id': r['doc_hash'],
        'doc_name': r['doc_name'],
        'update_time': format_epoch_time(r['update_epoch_time'])
    } for r in doc_data_raw]
    return render_template('document_index.html', doc_index=doc_data_dicts)


@app.route('/document_upload', methods=('GET', 'POST'))
def doc_upload():
    if request.method == 'GET':
        return app.send_static_file('upload_form.html')

    if request.method == 'POST':

        if 'file' not in request.files:
            flash('Please provide a file')
            return

        success, msg = store_document(request.files['file'])

        flash(msg)

        if success:
            return redirect('/{}'.format(request.files['file'].filename))
        else:
            return redirect('/document_upload')


@app.route('/documents/<doc_id>')
def document_page(doc_id):
    doc_data_raw = db.get_doc(config_obj, doc_id)
    if doc_data_raw is None:
        flash('No document with that id')
        return redirect('/document_index')

    else:
        doc_data = {
            "doc_body": doc_data_raw['doc_body'].decode('utf-8'),
            "doc_update_time": format_epoch_time(doc_data_raw["update_epoch_time"]),
            "doc_name": doc_data_raw["doc_name"],
            "doc_id": doc_id
        }
        return render_template('document_details.html', doc_data=doc_data)


@app.route('/api/documents/<doc_id>/process_words', methods=["POST"])
def process_document_words_api(doc_id):
    word_list = process_document_words(doc_id)

    return jsonify(word_list)


if __name__ == '__main__':
    app.run(debug=True)
