from flask import Flask, request, render_template, make_response, send_file
import json
import sys

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")

@app.route('/web-page', methods=['GET', 'POST'])
def index():
    html_path = '/home/nattapon/outside/ubuntu/AIPrototype2023/time-table/index.html'
    return send_file(html_path)

@app.route('/upload', methods=['GET', 'POST'])
def upload_page():
    return render_template('upload.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        files = request.files.getlist('file')
        for file in files:
            file.save('filename')
    return render_template("upload.html",name='upload completed')




if __name__ == "__main__":
    app.run(host='0.0.0.0',debug=True,port=5001)
