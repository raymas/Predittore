from flask import Flask, render_template
from dashboard.data import data


app = Flask(__name__)
app.register_blueprint(data, url_prefix='/data')

@app.route('/')
def index():
    return render_template('index.html')
