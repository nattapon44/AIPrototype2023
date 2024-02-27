from flask import Flask, request, render_template, make_response, send_file, send_from_directory
import json
import sys

app = Flask(__name__)

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
def upload():
    uploaded_file = request.files['file']
    if uploaded_file.filename != '':
        uploaded_file.save(uploaded_file.filename)
        return 'File uploaded successfully.'
    else:
        return 'No file selected.'



if __name__ == "__main__":
    app.run(host='0.0.0.0',debug=True,port=5001)
