from flask import Flask, request, render_template, make_response, send_file, send_from_directory, redirect, url_for
import json
import pandas as pd
import sys
import os


app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = '/home/nattapon/codes/AIPrototype2023/web_app/static'  # Change to your upload directory
app.config['ALLOWED_EXTENSIONS'] = {'csv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

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

@app.route('/upload', methods=['POST'])
def upload_file_csv():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        # You can now use Pandas or another library to read the CSV file
        df = pd.read_csv(file_path)
        # Do something with the dataframe here
        # For example, print the dataframe to the console
        print(df)
        return render_template('upload_successful.html', filename=filename)
    else:
        flash('Allowed file type is csv')
        return redirect(request.url)

    

    
if __name__ == "__main__":
    app.run(host='0.0.0.0',debug=True,port=5001)
