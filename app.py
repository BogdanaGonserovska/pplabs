from flask import Flask

app = Flask(__name__)


@app.route('/api/v1/hello-world-3')
def hello():
    return 'Hello World 3'