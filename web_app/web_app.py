from flask import Flask, request, render_template, make_response, send_file, send_from_directory
import json
import sys
import os


app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'static/uploads'


@app.route("/")
def home():
    return render_template("home.html")

@app.route("/web-page-project")
def webpage():
    # อ่านเนื้อหา HTML จากไฟล์ภายนอก
    with open("/home/nattapon/codes/AIPrototype2023/time-table/index.html", "r") as file:
        html_content = file.read()
    return html_content

@app.route("/about-us")
def aboutproject():
    return render_template("aboutus.html")

@app.route('/upload', methods=['GET', 'POST'])
def upload_file_csv():
    print(2222)
    if request.method == 'POST':
        print(1111)
        file_course = request.files['file_course']
        file_room = request.files['file_room']
        file_professor = request.files['file_professor']
        file_student = request.files['file_student']
        
        file_course.save(os.path.join(app.config['UPLOAD_FOLDER'], file_course.filename))
        file_room.save(os.path.join(app.config['UPLOAD_FOLDER'], file_room.filename))
        file_professor.save(os.path.join(app.config['UPLOAD_FOLDER'], file_professor.filename))
        file_student.save(os.path.join(app.config['UPLOAD_FOLDER'], file_student.filename))
        
    return render_template("upload.html", name='upload completed')


    

    
if __name__ == "__main__":
    app.run(host='0.0.0.0',debug=True,port=5001)
