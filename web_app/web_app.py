from flask import Flask, request, render_template, make_response, send_file, send_from_directory, jsonify
import json
import pandas as pd
import sys
import os


app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = '/home/nattapon/codes/AIPrototype2023/web_app/uploads'  # Change to your upload directory
app.config['ALLOWED_EXTENSIONS'] = {'csv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/request',methods=['POST'])
def web_service_API():

    payload = request.data.decode("utf-8")
    inmessage = json.loads(payload)

    # ทำการประมวลผลข้อมูลที่ได้รับ เช่น เรียกใช้โมเดล
    result = your_model.process_data(inmessage)

    # ส่งผลลัพธ์กลับไปยังลูกค้า
    return jsonify(result)

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
        files = request.files.getlist('file')
        for file in files:
            if file and allowed_file(file.filename):
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
                # เรียกใช้โมเดลหรือการประมวลผลที่ต้องการทำกับไฟล์ CSV ที่อัปโหลด
                result = your_model.process_uploaded_file(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
                return jsonify(result)
    return render_template("upload.html", name='upload completed')

    

    
if __name__ == "__main__":
    app.run(host='0.0.0.0',debug=True,port=5001)
