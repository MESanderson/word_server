from flask import Flask
from flask.templating import render_template
from db import init as db_init

app = Flask(__name__)

config_obj = {
    'db': 'sqlite',
    'db_host': r'/home/mike/PycharmProjects/word_server/word_db.db'
}

db = db_init(config_obj)


@app.route('/')
def hello_world():
    return app.send_static_file('index.html')


@app.route('/document_index')
def doc_index():
    doc_index = []
    return render_template('document_index.html', doc_index=doc_index)


@app.route('/document_upload')
def doc_upload():
    return app.send_static_file('upload_form.html')


if __name__ == '__main__':
    app.run(debug=True)
