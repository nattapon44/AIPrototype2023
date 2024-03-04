from flask import Flask, request, render_template, make_response, send_file, send_from_directory, jsonify
import model
import json
import pandas as pd
import sys
import os


app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = '/home/nattapon/codes/AIPrototype2023/web_app/uploads' 
app.config['ALLOWED_EXTENSIONS'] = {'csv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/request',methods=['POST'])
def web_service_API():

    payload = request.data.decode("utf-8")
    inmessage = json.loads(payload)

    # ทำการประมวลผลข้อมูลที่ได้รับ เช่น เรียกใช้โมเดล
    result = ilpmodel.process_data(inmessage)

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

@app.route('/upload', methods=['POST'])
def upload_file_csv():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            return render_template("upload.html", name='No file part')
        file = request.files['file']
        if file.filename == '':
            return render_template("upload.html", name='No selected file')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            # Load data from CSV and set variables in the model
            C, R, T, P, S, D = load_data_from_csv(os.path.join(app.config['UPLOAD_FOLDER'], filename))  
            return render_template("upload.html", name='upload completed')

    return render_template("upload.html", name='upload failed') 

def process_file_with_model(file):
    # Read and process the file using your model
    # For example, you might read the file content and pass it to your model
    # Then return the result
    return {'result': 'Processed successfully'}

    

    
if __name__ == "__main__":
    app.run(host='0.0.0.0',debug=True,port=5001)
