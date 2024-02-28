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
    if request.method == 'POST':
        file = request.files['file']
        file.save('filename')
        return render_template("upload.html",name='upload completed')

    return '''
    <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Upload page</title>
    <link rel="stylesheet" href="{{ url_for ('static', filename='css/upload.css') }}">
</head>
<body>
    <header>
        <h1>Upload Files page</h1>
    </header>
        <section class="upload-section">
            <form id="uploadForm" action="{{ url_for('upload_file_csv') }}" method="POST" enctype="multipart/form-data">
                <h2>Input Course (.csv file)</h2>
                <input type="file" name="file_course" accept=".csv">
                <h2>Input Room (.csv file)</h2>
                <input type="file" name="file_room" accept=".csv">
                <h2>Input Professor (.csv file)</h2>
                <input type="file" name="file_professor" accept=".csv">
                <h2>Input Student (.csv file)</h2>
                <input type="file" name="file_student" accept=".csv">
                <button type="submit">Upload</button>
            </form>       
    '''


    

    
if __name__ == "__main__":
    app.run(host='0.0.0.0',debug=True,port=5001)
