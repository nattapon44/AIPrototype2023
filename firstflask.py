from flask import Flask, request, render_template, make_response 
import json

app = Flask(__name__)

@app.route("/")  
def helloworld():
    return "Hello, World!"

@app.route("/name")  
def hellonattapon():
    return "Hello, Nattapon!"

@app.route("/homefn")
def home2():
    return render_template("home.html",name='nattapon')

if __name__ == "__main__":
    app.run(host='0.0.0.0',debug=True,port=5001)