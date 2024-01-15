from flask import Flask, request, render_template, make_response 
import json

app = Flask(__name__)

@app.route("/")  
def helloworld():
    return "Hello, World!"

if __name__ == "__main__":
    app.run(host='0.0.0.0',debug=True,port=5001)#host='0.0.0.0',port=5001