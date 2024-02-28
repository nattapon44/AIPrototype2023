from flask import Flask, request, render_template, make_response, send_file, send_from_directory
import json
import sys
import os


app = Flask(__name__)

@app.route('/request',methods=['POST'])
def web_service_API():

    payload = request.data.decode("utf-8")
    inmessage = json.loads(payload)

    print(inmessage)

    json_data = json.dumps({'y':'received!'})
    return json_data

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/web-page-project")
def webpage():
    return send_from_directory("/home/nattapon/codes/AIPrototype2023/time-table", "index.html")

@app.route("/LegalDoc/<path:filename>")
def static_files(filename):
    return send_from_directory("/home/nattapon/codes/AIPrototype2023/time-table/LegalDoc", filename)

@app.route("/about-us")
def aboutproject():
    return render_template("aboutus.html")

@app.route('/upload', methods=['GET', 'POST'])
def upload_file_csv():
    print(2222)
    if request.method == 'POST':
        print(1111)
        files = request.files.getlist('file')  
        for file in files:
            file.save(file.filename) 
    return render_template("upload.html", name='upload completed')

    

    
if __name__ == "__main__":
    app.run(host='0.0.0.0',debug=True,port=5001)
