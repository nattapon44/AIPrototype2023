from flask import Flask, request, render_template, make_response, send_file, send_from_directory
import json
import sys
import os


app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'static/files'
class UploadFileForm(FlaskForm):
    file = FileField("File", validators=[InputRequired()])
    submit = SubmitField("Upload File")

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
    form = UploadFileForm()
    if form.validate_on_submit():
        file = form.file.data
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename)))

    csv_file = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('upload.html', form=form, csv_file=csv_file)
    

    
if __name__ == "__main__":
    app.run(host='0.0.0.0',debug=True,port=5001)
