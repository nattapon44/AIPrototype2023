from flask import Flask, request, render_template, make_response, send_file, send_from_directory, jsonify
import pandas as pd
import json
import sys
import os
from werkzeug.utils import secure_filename
from pyomo import environ as pe
from pyomo.environ import *
from pyomo.opt import SolverFactory

app = Flask(__name__)

def process_csv(file_path):
    data = pd.read_csv(UPLOAD_FOLDER)
    return data

def solve_ilp(data):
    # สร้างโมเดล
    model = ConcreteModel()
    # Sets
    model.C = Set(initialize=C.keys())
    model.R = Set(initialize=R.keys())
    model.T = Set(initialize=T.keys())
    model.P = Set(initialize=P.keys())
    model.S = Set(initialize=S.keys())
    model.D = Set(initialize=D.keys())
    model.Cp = Set(initialize=C.keys())
    model.Cs = Set(initialize=S.keys())
    model.Rc = Set(initialize=C.keys())
    model.Tp = Set(initialize=P.keys())
    model.Tprime_tc = Set(initialize=T.keys())
    #Variables
    model.x_crdt = Var(model.C, model.R, model.D, model.T, within=Binary)
    model.z_scrdt = Var(model.S, model.C, model.R, model.D, model.T, within=Binary)
    model.w_c = Var(model.C, within=Binary)
    model.w_cd = Var(model.C, model.D, within=Binary)
    model.y_pdt = Var(model.P, model.D, model.T, within=Binary)

    def Objective_rule(model):
        return sum([(find_ucrdt(c,r,d,t)/hc(c))*model.x_crdt[c,r,d,t] for c in model.C for r in model.R for d in model.D for t in model.T ])
    model.obj = Objective(rule=Objective_rule, sense=maximize)


UPLOAD_FOLDER = '/home/nattapon/codes/AIPrototype2023/web_app/static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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
    print("File not upload")
    if request.method == 'POST':
        print("Files Upload Completed")
        files = ['course_file', 'room_file', 'professor_file', 'student_file']
        for filename in files:
            file = request.files.get(filename)
            if file:
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
        return render_template("upload.html", name='upload completed')
    return render_template("upload.html")

@app.route('/solve_ilp', methods=['POST'])
def solve_ilp_endpoint():
    if request.method == 'POST':
        # ตรวจสอบว่ามีไฟล์ CSV ถูกส่งมาหรือไม่
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        # ตรวจสอบว่าไฟล์ถูกส่งมาหรือไม่
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        # บันทึกไฟล์ CSV ไว้ในโฟลเดอร์ที่กำหนดไว้
        file_path = 'uploaded_file.csv'
        file.save(file_path)

        # ประมวลผลข้อมูลจากไฟล์ CSV
        data = process_csv(file_path)

        # แก้ปัญหา ILP ด้วยข้อมูลที่ได้จากไฟล์ CSV
        solution = solve_ilp(data)

        # ส่งผลลัพธ์กลับไปให้ผู้ใช้
        return jsonify(solution)
    else:
        return jsonify({'error': 'Method not allowed'}), 405


    
if __name__ == "__main__":
    app.run(host='0.0.0.0',debug=True,port=5001)
