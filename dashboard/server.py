from flask import Flask, render_template

from data import data

app = Flask(__name__)
app.register_blueprint(data, url_prefix='/data')


@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)