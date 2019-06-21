from flask import Flask
from flask.templating import render_template
app = Flask(__name__)


@app.route('/')
@app.route('/<greeting>')
def hello_world(greeting="Hello"):
    return render_template('hello.html', hello=greeting)


if __name__ == '__main__':
    app.run(debug=True)
