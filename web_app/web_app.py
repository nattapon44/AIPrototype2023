from flask import Flask, request, render_template, make_response, send_file, send_from_directory
import json
import sys

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        files = request.files.getlist('file')
        for file in files:
            file.save('uploads/' + file.filename)  # Save the uploaded file in 'uploads' folder
    return render_template("upload.html", name='upload completed')




if __name__ == "__main__":
    app.run(host='0.0.0.0',debug=True,port=5001)
