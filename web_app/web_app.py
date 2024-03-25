from flask import Flask, request, render_template, send_file, send_from_directory
import pandas as pd
import os
from werkzeug.utils import secure_filename
from pyomo import environ as pe
from pyomo.environ import *
import numpy as np

app = Flask(__name__)

UPLOAD_FOLDER = '/home/nattapon/codes/AIPrototype2023/web_app/static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def solve_teaching_assignment_problem(course_file, room_file, professor_file, student_file):
    course = pd.read_excel(course_file, engine='openpyxl')
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

    room = pd.read_excel(room_file, engine='openpyxl')
    R = {}
    for idx, row in room.iterrows():
        R[idx+1] = {
            "Name": row['Name'],
            "Capacity": row['Capacity'],
            "Type": row['Type']
        }

    professor = pd.read_excel(professor_file, engine='openpyxl')
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

    student = pd.read_excel(student_file, engine='openpyxl')
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

    def hcobj(c):
        hours_per_week = C[c]["hoursPerWeek"]
        h_c = sum(hours_per_week)
        return h_c

    def hc(c):
        hours_per_week = C[c]["hoursPerWeek"][0]
        return hours_per_week

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

    # สร้างโมเดล
    model = ConcreteModel()
    # Sets
    model.C = Set(initialize=C.keys())
    model.R = Set(initialize=R.keys())
    model.T = Set(initialize=T.keys())
    model.P = Set(initialize=P.keys())
    model.S = Set(initialize=S.keys())
    model.D = Set(initialize=D.keys())

    model.T_new = set(range(len(T) + 1))
    print(model.T_new)

    #Variables
    model.x_crdt = Var(model.C, model.R, model.D, model.T, within=Binary)
    model.z_scrdt = Var(model.S, model.C, model.R, model.D, model.T, within=Binary)
    model.w_c = Var(model.C, within=Binary)
    model.w_cd = Var(model.C, model.D, within=Binary)
    model.y_pdt = Var(model.P, model.D, model.T, within=Binary)
    model.v_crdt = Var(model.C, model.R, model.D, model.T_new, within=NonNegativeIntegers, bounds=(0,12))
    model.max_Vcrd = Var(model.C, model.R, model.D, within=NonNegativeIntegers, bounds=(0,12))
    model.b_crdt = Var(model.C, model.R, model.D, model.T, within=Binary)

    def Objective_rule(model):
        return sum([(find_ucrdt(c,r,d,t)/(2*hcobj(c)))*model.x_crdt[c,r,d,t] for c in model.C for r in model.R for d in model.D for t in model.T ])


    model.obj = Objective(rule=Objective_rule, sense=maximize)

    # Constraints
    # Constraint 1
    model.const1 = ConstraintList()
    for r in R:
        for d in D:
            for t in T:
                model.const1.add(sum(model.x_crdt[c, r, d, t] for c in model.C) <= 1)

    # Constraint 2
    model.const2 = ConstraintList()
    for p in P:
        for d in D:
            for t in T:
                model.const2.add(sum(model.x_crdt[c, r, d, t] for r in model.R for c in model.C) <= 1)

    # Constraint 3
    model.const3 = ConstraintList()
    for c in C:
        for r in R:
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

    # Constraints 5
    model.const5_1 = ConstraintList()
    model.const5_2 = ConstraintList()
    model.const5_3 = ConstraintList()
    model.const5_4 = ConstraintList()
    model.const5_5 = ConstraintList()
    model.const5_6 = ConstraintList()
    for c in C:
        for r in R:
            for d in D:
                model.const5_1.add(model.v_crdt[c, r, d, 0] == 0)
                for t in T:
                    model.const5_2.add(model.v_crdt[c, r, d, t] >= -t * model.x_crdt[c, r, d, t])
                    model.const5_3.add(model.v_crdt[c, r, d, t] <= t * model.x_crdt[c, r, d, t])
                    model.const5_4.add(model.v_crdt[c, r, d, t] >= 1 + model.v_crdt[c, r, d, t-1] - t * (1 - model.x_crdt[c, r, d, t]))
                    model.const5_5.add(model.v_crdt[c, r, d, t] <= 1 + model.v_crdt[c, r, d, t-1] + t * (1 - model.x_crdt[c, r, d, t]))
                    model.const5_6.add(model.max_Vcrd[c, r, d] >= model.v_crdt[c, r, d, t])

    # Constraints 6
    model.const6_1 = ConstraintList()
    model.const6_2 = ConstraintList()
    model.const6_3 = ConstraintList()
    for c in C:
        for r in R:
            for d in D:
                model.const6_1.add(model.max_Vcrd[c, r, d] == (sum(model.x_crdt[c, r, d, t] for t in model.T)))

    # Constraint 7
    model.const7 = ConstraintList()
    for c in C:
        for r in R:
            for d in D:
                for t in T:
                    model.const7.add(model.x_crdt[c, r, d, 8]+ model.x_crdt[c, r, d, 9] <= 1)

    # Constraint 8.1
    model.const8_1 = ConstraintList()
    for c in C:
        for d in D:
            model.const8_1.add(model.w_cd[c, d] <= (sum(model.x_crdt[c, r, d, t] for r in model.R for t in model.T)))

    # Constraint 8.2
    model.const8_2 = ConstraintList()
    for c in C:
        for d in D:
            model.const8_2.add((sum(model.x_crdt[c, r, d, t] for r in model.R for t in model.T)) <= (2*hc(c))*model.w_cd[c, d])

    # Constraint 9
    model.const9_1 = ConstraintList()
    model.const9_2 = ConstraintList()
    model.const9_3 = ConstraintList()
    model.const9_4 = ConstraintList()
    for c in C:
        model.const9_1.add(model.w_cd[c, 1] + model.w_cd[c, 2] <= 1)
        model.const9_2.add(model.w_cd[c, 2] + model.w_cd[c, 3] <= 1)
        model.const9_3.add(model.w_cd[c, 3] + model.w_cd[c, 4] <= 1)
        model.const9_4.add(model.w_cd[c, 4] + model.w_cd[c, 5] <= 1)

    # Constraint 10
    model.const10 = ConstraintList()
    for s in S:
        for c in C:
            for r in R:
                for d in D:
                    for t in T:
                        model.const10.add(model.x_crdt[c, r, d, t] <= model.z_scrdt[s, c, r, d, t])

    # Constraint 11
    model.const11 = ConstraintList()
    for p in P:
        for d in D:
            for t in T:
                model.const11.add(sum(model.x_crdt[c, r, d, t] for c in model.C for r in model.R) - model.y_pdt[p, d, t] == 0)

    # Constraint 12
    model.const12 = ConstraintList()
    for p in P:
        for d in D:
            model.const12.add(sum(model.y_pdt[p, d, t] for t in model.T) <= 2*kp(p)  )

    # Constraint 13
    model.const13 = ConstraintList()
    for s in S:
        for d in D:
            model.const13.add(sum(model.z_scrdt[s, c, r, d, t] for c in model.C for r in model.R) <= 2*ks(s)  )

    # Constraint 14
    model.const14 = ConstraintList()
    for c in C:
        model.const14.add(sum(model.w_cd[c, d] for d in D) == kc(c))

    # Constatint 15
    model.const15 = ConstraintList()
    for s in S:
        for c in C:
            for r in R:
                model.const15.add(model.z_scrdt[s, c, r, d, t] <= a_sdt(s,d,t))

    # Constraint 16
    model.const16 = ConstraintList()
    for c in C:
        for r in R:
            for d in D:
                for t in T:
                    model.const16.add(model.x_crdt[c, r, d, t] <= 2*find_ucrdt(c,r,d,t))

    from pyomo.opt import SolverFactory
    opt = SolverFactory('glpk')
    solution =  opt.solve(model, tee=True)


    list_of_x1 = []

    for c in C:
        for r in R:
            for d in D:
                for t in T:
                    val_x = pe.value(model.x_crdt[c, r, d, t])
                    if val_x != 0:
                        list_of_x1.append((c, r, d, t, int(val_x)))

    # พิมพ์ list_of_x1
    for x1 in list_of_x1:
        print("x_crdt({}, {}, {}, {}) = {}".format(x1[0], x1[1], x1[2], x1[3], x1[4]))

    list_of_z1 = []
    for s in S:
        for c in C:
            for r in R:
                for d in D:
                    for t in T:
                        val_z = pe.value(model.z_scrdt[s, c, r, d, t])
                    if val_z != 0:
                        list_of_z1.append((s, c, r, d, t, int(val_z)))
    # พิมพ์ list_of_x1
    for z1 in list_of_z1:
        print("z_scrdt({}, {}, {}, {}, {}) = {}".format(z1[0], z1[1], z1[2], z1[3], z1[4], z1[5]))

    list_of_w1 = []
    for c in C:
        for d in D:
            val_w = pe.value(model.w_cd[c, d])
            if val_w != 0:
                list_of_w1.append((c, d, int(val_w)))
    # พิมพ์ list_of_w1
    for y1 in list_of_w1:
        print("w_cd({}, {}) = {}".format(y1[0], y1[1], y1[2]))

    list_of_y1 = []
    for p in P:
        for d in D:
            for t in T:
                val_y = pe.value(model.y_pdt[p, d, t])
                if val_y != 0:
                    list_of_y1.append((p, d, t, int(val_y)))
    # พิมพ์ list_of_y1
    for y1 in list_of_y1:
        print("y_pdt({}, {}, {}) = {}".format(y1[0], y1[1], y1[2], y1[3]))

    list_of_v1 = []
    for c in C:
        for r in R:
            for d in D:
                for t in T:
                    val_v = pe.value(model.v_crdt[c, r, d, t])
                    list_of_v1.append((c, r, d, t, int(val_v)))
    # พิมพ์ list_of_x1
    for v1 in list_of_v1:
        print("v_crdt({}, {}, {}, {}) = {}".format(v1[0], v1[1], v1[2], v1[3], v1[4]))

    list_of_v1 = []
    for c in C:
        for r in R:
            for d in D:
                for t in T:
                    val_v = pe.value(model.v_crdt[c, r, d, t])
                    if val_v != 0:
                        list_of_v1.append((c, r, d, t, int(val_v)))
    # พิมพ์ list_of_x1
    for v1 in list_of_v1:
        print("v_crdt({}, {}, {}, {}) = {}".format(v1[0], v1[1], v1[2], v1[3], v1[4]))

    list_of_maxv1 = []
    for c in C:
        for r in R:
            for d in D:
                val_maxv1 = pe.value(model.max_Vcrd[c, r, d])
                if val_maxv1 != 0:
                    list_of_maxv1.append((c, r, d, int(val_maxv1)))
    # พิมพ์ list_of_maxv1
    for maxv1 in list_of_maxv1:
        print("maxv_crd({}, {}, {}) = {}".format(maxv1[0], maxv1[1], maxv1[2], maxv1[3]))

    # สร้างชื่อวันและเวลา
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    times = pd.date_range('08:30', '17:30', freq='30T').strftime('%H:%M')

    # สร้าง DataFrame โดยใช้ชื่อวันเป็น index และเวลาเป็น columns
    r1 = pd.DataFrame(index=days, columns=times)
    # เติมชื่อรายวิชาและผู้สอนลงในตาราง
    for x1 in list_of_x1:
        c, r, d, t, val_x = x1
        if r == 1:
            course_name = C[c]["courseName"]
            teachers = ', '.join(C[c]["teachers"].values())
            r1.at[days[d-1], times[t-1]] = course_name + '\n' + '(' + teachers + ')'
    # บันทึก DataFrame เป็นไฟล์ Excel
    r1.to_excel("r1.xlsx")

    # สร้าง DataFrame โดยใช้ชื่อวันเป็น index และเวลาเป็น columns
    r2 = pd.DataFrame(index=days, columns=times)
    # เติมชื่อรายวิชาและผู้สอนลงในตาราง
    for x1 in list_of_x1:
        c, r, d, t, val_x = x1
        if r == 2:
            course_name = C[c]["courseName"]
            teachers = ', '.join(C[c]["teachers"].values())
            r2.at[days[d-1], times[t-1]] = course_name + '\n' + '(' + teachers + ')'
    # บันทึก DataFrame เป็นไฟล์ Excel
    r2.to_excel("r2.xlsx")

    # สร้าง DataFrame โดยใช้ชื่อวันเป็น index และเวลาเป็น columns
    r3 = pd.DataFrame(index=days, columns=times)
    # เติมชื่อรายวิชาและผู้สอนลงในตาราง
    for x1 in list_of_x1:
        c, r, d, t, val_x = x1
        if r == 3:
            course_name = C[c]["courseName"]
            teachers = ', '.join(C[c]["teachers"].values())
            r3.at[days[d-1], times[t-1]] = course_name + '\n' + '(' + teachers + ')'
    # บันทึก DataFrame เป็นไฟล์ Excel
    r3.to_excel("r3.xlsx")

    # สร้าง DataFrame โดยใช้ชื่อวันเป็น index และเวลาเป็น columns
    r4 = pd.DataFrame(index=days, columns=times)
    # เติมชื่อรายวิชาและผู้สอนลงในตาราง
    for x1 in list_of_x1:
        c, r, d, t, val_x = x1
        if r == 4:
            course_name = C[c]["courseName"]
            teachers = ', '.join(C[c]["teachers"].values())
            r4.at[days[d-1], times[t-1]] = course_name + '\n' + '(' + teachers + ')'
    # บันทึก DataFrame เป็นไฟล์ Excel
    r4.to_excel("r4.xlsx")

    # สร้าง DataFrame โดยใช้ชื่อวันเป็น index และเวลาเป็น columns
    r5 = pd.DataFrame(index=days, columns=times)
    # เติมชื่อรายวิชาและผู้สอนลงในตาราง
    for x1 in list_of_x1:
        c, r, d, t, val_x = x1
        if r == 5:
            course_name = C[c]["courseName"]
            teachers = ', '.join(C[c]["teachers"].values())
            r5.at[days[d-1], times[t-1]] = course_name + '\n' + '(' + teachers + ')'
    # บันทึก DataFrame เป็นไฟล์ Excel
    r5.to_excel("r5.xlsx")

    # สร้าง DataFrame โดยใช้ชื่อวันเป็น index และเวลาเป็น columns
    r6 = pd.DataFrame(index=days, columns=times)
    # เติมชื่อรายวิชาและผู้สอนลงในตาราง
    for x1 in list_of_x1:
        c, r, d, t, val_x = x1
        if r == 6:
            course_name = C[c]["courseName"]
            teachers = ', '.join(C[c]["teachers"].values())
            r6.at[days[d-1], times[t-1]] = course_name + '\n' + '(' + teachers + ')'
    # บันทึก DataFrame เป็นไฟล์ Excel
    r6.to_excel("r6.xlsx")

    # สร้าง DataFrame โดยใช้ชื่อวันเป็น index และเวลาเป็น columns
    p1 = pd.DataFrame(index=days, columns=times)
    # เพิ่มข้อมูลรายวิชาและห้องเรียนลงในตาราง
    for y1 in list_of_y1:
        p, d, t, val_y = y1
        if p == 1:  # ตรวจสอบว่า p เท่ากับ 1 หรือไม่
            course_name = P[p]["course"].get(d)  # รหัสวิชาของวันนั้นๆ
            if course_name is not None:
                p1.at[days[d-1], times[t-1]] = f"{course_name}, {R[val_y]['Name']}"  # เพิ่มรหัสวิชาและชื่อห้องเรียน
    # บันทึก DataFrame เป็นไฟล์ Excel
    p1.to_excel("p1.xlsx")

    # สร้าง DataFrame โดยใช้ชื่อวันเป็น index และเวลาเป็น columns
    p2 = pd.DataFrame(index=days, columns=times)
    # เพิ่มข้อมูลรายวิชาและห้องเรียนลงในตาราง
    for y1 in list_of_y1:
        p, d, t, val_y = y1
        if p == 2:  # ตรวจสอบว่า p เท่ากับ 1 หรือไม่
            course_name = P[p]["course"].get(d)  # รหัสวิชาของวันนั้นๆ
            if course_name is not None:
                p2.at[days[d-1], times[t-1]] = f"{course_name}, {R[val_y]['Name']}"  # เพิ่มรหัสวิชาและชื่อห้องเรียน
    # บันทึก DataFrame เป็นไฟล์ Excel
    p2.to_excel("p2.xlsx")

    # สร้าง DataFrame โดยใช้ชื่อวันเป็น index และเวลาเป็น columns
    p3 = pd.DataFrame(index=days, columns=times)
    # เพิ่มข้อมูลรายวิชาและห้องเรียนลงในตาราง
    for y1 in list_of_y1:
        p, d, t, val_y = y1
        if p == 3:  # ตรวจสอบว่า p เท่ากับ 1 หรือไม่
            course_name = P[p]["course"].get(d)  # รหัสวิชาของวันนั้นๆ
            if course_name is not None:
                p3.at[days[d-1], times[t-1]] = f"{course_name}, {R[val_y]['Name']}"  # เพิ่มรหัสวิชาและชื่อห้องเรียน
    # บันทึก DataFrame เป็นไฟล์ Excel
    p3.to_excel("p3.xlsx")

    # สร้าง DataFrame โดยใช้ชื่อวันเป็น index และเวลาเป็น columns
    s1 = pd.DataFrame(index=days, columns=times)
    # เติมชื่อรายวิชาและห้องเรียนลงในตาราง
    for z1 in list_of_z1:
        s, c, r, d, t, val_z = z1
        if s == 1:
            if s in S and c in S[s]["courseRegister"] and r in R:
                course_name = S[s]["courseRegister"][c]
                room_name = R[r]["Name"]
                s1.at[days[d-1], times[t-1]] = course_name + '\n' + '(' + room_name + ')'
   # บันทึก DataFrame เป็นไฟล์ Excel
    s1.to_excel("p1.xlsx")

    return solution


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
        # รับไฟล์ excel จาก request
        course_file = request.files['course_file']
        room_file = request.files['room_file']
        professor_file = request.files['professor_file']
        student_file = request.files['student_file']
        
        # เรียกใช้งานโมเดล Pyomo
        solution = solve_teaching_assignment_problem(course_file, room_file, professor_file, student_file)
        
        return render_template("solution.html", solution=solution,)
    return render_template("solution.html")

@app.route('/download_solution/<filename>', methods=['GET'])
def download_solution(filename):
    # สร้าง path ไปยังไฟล์ solution ที่ต้องการให้ดาวน์โหลด
    solution_path = "/home/nattapon/codes/AIPrototype2023/web_app/static/" + filename
    # ส่งไฟล์กลับไปยังผู้ใช้
    return send_file(solution_path, as_attachment=True)


@app.route('/download_file_1')
def download_file_1():
    file_path = '/home/nattapon/codes/AIPrototype2023/web_app/static/templetes excel/course_template.xlsx'
    return send_file(file_path, as_attachment=True)

@app.route('/download_file_2')
def download_file_2():
    file_path = '/home/nattapon/codes/AIPrototype2023/web_app/static/templetes excel/professor_template.xlsx'
    return send_file(file_path, as_attachment=True)

@app.route('/download_file_3')
def download_file_3():
    file_path = '/home/nattapon/codes/AIPrototype2023/web_app/static/templetes excel/room_template.xlsx'
    return send_file(file_path, as_attachment=True)

@app.route('/download_file_4')
def download_file_4():
    file_path = '/home/nattapon/codes/AIPrototype2023/web_app/static/templetes excel/student_template.xlsx'
    return send_file(file_path, as_attachment=True)


if __name__ == "__main__":
    app.run(host='0.0.0.0',debug=True,port=5001)