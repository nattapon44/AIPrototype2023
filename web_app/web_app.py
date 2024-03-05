from flask import Flask, request, render_template, make_response, send_file, send_from_directory, jsonify, redirect, url_for
import pandas as pd
import json
import sys
import os
from werkzeug.utils import secure_filename
from pyomo import environ as pe
from pyomo.environ import *
from pyomo.opt import SolverFactory
import numpy as np

app = Flask(__name__)

def solve_teaching_assignment_problem(course_file, room_file, professor_file, student_file):

    course = pd.read_excel(course_file)
    C = {}
    for idx, row in course.iterrows():
        teachers_dict = {}
        for i, teacher in enumerate(row['teachers'].split(','), start=1):
            teachers_dict[i] = teacher.strip()  # Strip whitespace from teacher names
        hours_per_week = [int(x) for x in row['hourPerWeek'].split(',')]
        course_type = row['type'].split(',')
        C[idx+1] = {
            "courseName": row['courseName'],
            "teachers": teachers_dict,
            "courseCapacity": row['courseCapacity'],
            "hoursPerWeek": hours_per_week,
            "type": course_type
        }

    room = pd.read_excel(room_file)
    R = {}
    for idx, row in room.iterrows():
        R[idx+1] = {
            "Name": row['Name'],
            "Capacity": row['Capacity'],
            "Type": row['Type']
        }

    professor = pd.read_excel(professor_file)
    professor.fillna('')
    P = {}
    for index, row in professor.iterrows():
        if pd.notna(row['Name']):
            prof_id = len(P) + 1
            P[prof_id] = {'Name': row['Name'], 'course': {}, 'weight': []}
        P[prof_id]['course'][index+1] = row['course']
        P[prof_id]['weight'].append(list(row[2:]))
    for prof_id in P:
        P[prof_id]['weight'] = [[float(w) if pd.notna(w) else w for w in sublist] for sublist in P[prof_id]['weight']]

    student = pd.read_excel(student_file)
    student.fillna('')
    S = {}
    for index, row in student.iterrows():
        if pd.notna(row['Major']):
            stud_id = len(S) + 1
            S[stud_id] = {'Major': row['Major'], 'Year': row['Year'], 'courseRegister': {}, 'Availability': []}
        S[stud_id]['courseRegister'][index+1] = row['courseRegister']
        S[stud_id]['Availability'].append(list(row[3:]))
    
    #define
    D = { 1: 'Monday',
          2: 'Tuesday',
          3: 'Wednesday',
          4: 'Thursday',
          5: 'Friday'
        }

    T = { 1: '8 am',
   	      2: '8:30 am',
	      3: '9 am',
	      4: '9:30 am',
   	      5: '10 am',
	      6: '10:30 am',
          7: '11 am',
          8: '11:30 am',
   	      9: '1 pm',
	     10: '1:30 pm',
	     11: '2 pm',
   	     12: '2:30 pm',
	     13: '3 pm',
         14: '3:30 pm',
         15: '4 pm',
   	     16: '4:30 pm',
	     17: '5 pm',
	     18: '5:30 pm'
        }

    def find_ucrdt(c, r, d, t):
        type_r = R[r]['Type']
        #print(type_r)
        type_c = C[c]['type']
        #print(type_c)
        if type_r == 'lecture' and 'lab' in type_c:
            #print("checking room")
            return 0
        else:
            Pp = list(C[c]['teachers'].keys())
            numteacher = len(Pp)
            if numteacher == 1:
                #print("Hello1")
                p_index = Pp[0]
                return P[p_index]['weight'][d-1][t-1]
            elif numteacher >= 2:
                #print("Hello>1", Pp)
                min_weight = []
                for p_index in Pp:
                    min_weight.append(P[p_index]['weight'][d-1][t-1])
                return min(min_weight)

    def hc(c):
        hours_per_week = C[c]["hoursPerWeek"]
        h_c = sum(hours_per_week)*2
        return h_c
    def capr(r):
        return R[r]['Capacity']
    def capc(c):
        return C[c]['courseCapacity']
    def kp(p):
        return 6
    def ks(s):
        return 6
    def kc(c):
        return len(C[c]['hoursPerWeek'])
    def a_sdt(s, d, t):
        return S[s]['Availability'][d-1][t-1]
    def tprime_tc(c, t):
        hc = C[c]["hoursPerWeek"]

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
    #Objective Funciton
    def Objective_rule(model):
        return sum([(find_ucrdt(c,r,d,t)/hc(c))*model.x_crdt[c,r,d,t] for c in model.C for r in model.R for d in model.D for t in model.T ])
    model.obj = Objective(rule=Objective_rule, sense=maximize)
    #Constraints
     # Constraint 1
    model.const1 = ConstraintList()
    for t in T:
        for d in D:
            for r in R:
                model.const1.add(sum(model.x_crdt[c, r, d, t] for c in model.C) <= 1)

    # Constraint 2
    model.const2 = ConstraintList()
    for p in P:
        for d in D:
            for t in T:
                model.const2.add(sum(model.x_crdt[c, r, d, t] for r in model.R for c in model.Cp) <= 1)

    # Constraint 3
    model.const3 = ConstraintList()
    for r in R:
        for c in C:
            for d in D:
                for t in T:
                    model.const3.add(sum(model.z_scrdt[s, c, r, d, t] for s in model.S) <= capr(r))

    # Constraint 4
    model.const4 = ConstraintList()
    for c in C:
        for r in R:
            for d in D:
                for t in T:
                    model.const4.add(sum(model.z_scrdt[s, c, r, d, t] for s in model.S) <= capc(c))
    
    # Constraint 6
    model.const6 = ConstraintList()
    for c in C:
        for r in R:
            for d in D:
                for t in T:
                    model.const6.add(model.x_crdt[c, r, d, 8]+ model.x_crdt[c, r, d, 9] <= 1)

    # Constraint 7
    model.const7 = ConstraintList()
    for c in C:
        model.const7.add(model.w_cd[c, 1] + model.w_cd[c, 2] <= 1)
        model.const7.add(model.w_cd[c, 2] + model.w_cd[c, 3] <= 1)
        model.const7.add(model.w_cd[c, 3] + model.w_cd[c, 4] <= 1)
        model.const7.add(model.w_cd[c, 4] + model.w_cd[c, 5] <= 1)

    # Constraint 9
    model.const9 = ConstraintList()
    for s in S:
        for c in C:
            for r in R:
                for d in D:
                    for t in T:
                        model.const9.add(model.x_crdt[c, r, d, t] <= model.z_scrdt[s, c, r, d, t])

    # Constraint 10
    model.const10 = ConstraintList()
    for p in P:
        for c in C:
            for r in R:
                for d in D:
                    for t in T:
                        model.const10.add(model.x_crdt[c, r, d, t] <= model.y_pdt[p, d, t])

    # Constraint 11
    model.const11 = ConstraintList()
    for p in P:
        model.const11.add(sum(model.y_pdt[p, d, t] for d in model.D for t in model.T) <= kp(p)  )

    # Constraint 12
    model.const12 = ConstraintList()
    for s in S:
        model.const12.add(sum(model.z_scrdt[s, c, r, d, t] for c in model.C for r in model.R) <= ks(s)  )

    # Constraint 13
    model.const13 = ConstraintList()
    for c in C:
        model.const13.add(sum(model.w_cd[c, d] for d in D) == kc(c))

    # Constatint 14
    model.const14 = ConstraintList()
    for s in S:
        for c in C:
            for r in R:
                model.const14.add(model.z_scrdt[s, c, r, d, t] <= a_sdt(s,d,t))

    twoucrdt = 2*find_ucrdt(c,r,d,t)
    print(twoucrdt)

    # Constraint 15
    model.const15 = ConstraintList()
    for c in C:
        for r in R:
            for d in D:
                for t in T:
                    model.const15.add(model.x_crdt[c, r, d, t] <= twoucrdt)
            
    # สร้างตัวแปรสำหรับเก็บผลลัพธ์และคืนค่า
    # solution = ...
    solver = pe.SolverFactory('glpk', executable='/usr/bin/glpsol')
    solution = solver.solve(model)

    from pyomo.opt import SolverFactory

    # กำหนด Solver
    opt = SolverFactory('glpk')
    opt.solve(model, tee=True)
    return solution

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
def upload_file_excel():
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

@app.route('/solve_ilp', methods=['GET', 'POST'])
def solve_ilp_endpoint():
    if request.method == 'POST':
        # รับไฟล์ CSV จาก request
        course_file = request.files['course_file']
        room_file = request.files['room_file']
        professor_file = request.files['professor_file']
        student_file = request.files['student_file']
        
        # เรียกใช้งานโมเดล Pyomo
        solution = solve_teaching_assignment_problem(course_file, room_file, professor_file, student_file)
        
        return redirect(url_for('show_solution', solution=solution))
    return render_template("solution.html")

@app.route('/solution')
def show_solution():
    # รับข้อมูล Solution จาก URL
    solution = request.args.get('solution')
    return render_template("solution.html", solution=solution)
    
if __name__ == "__main__":
    app.run(host='0.0.0.0',debug=True,port=5001)
