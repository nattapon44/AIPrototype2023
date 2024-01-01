import subprocess #สำหรับรัน terminal command
    
if __name__ == "__main__":
    #basic terminal command
    print("first run num=100 XX=90")
    output1 = subprocess.run(["python","firstpy.py","--num","100","--XX","90"])
    print(output1)
    print("------------------------------------------------------------")
    print("second run num=-10 XX=-90")
    output2 = subprocess.run(["python","firstpy.py","--num","-10","--XX","-90"])
    print(output2)
    print("------------------------------------------------------------")
    print("third run num=0")
    output3 = subprocess.run(["python","firstpy.py","--num","0"])
    print(output3)
    print("------------------------------------------------------------")


#use output from other program
process_output = subprocess.Popen(["python","firstpy.py","--num","0"],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
out, err = process_output.communicate()
print(out.decode('utf-8'))
print(len(out.decode('utf-8')))

total_sum = 0
# output1 = subprocess.check_output(["python", "firstpy.py", "--num", "100", "--XX", "90"]).decode('utf-8')
# ดึงค่าที่ต้องการบวก
sum_value1 = int(output1.split('\n')[3])  # ดึงค่าที่อยู่บรรทัดที่ 4
total_sum += sum_value1

# output2 = subprocess.check_output(["python", "firstpy.py", "--num", "-10", "--XX", "-90"]).decode('utf-8')
# ดึงค่าที่ต้องการบวก
sum_value2 = int(output2.split('\n')[3])  # ดึงค่าที่อยู่บรรทัดที่ 4
total_sum += sum_value2

# output3 = subprocess.check_output(["python", "firstpy.py", "--num", "0"]).decode('utf-8')
# ดึงค่าที่ต้องการบวก
sum_value3 = int(output3.split('\n')[3])  # ดึงค่าที่อยู่บรรทัดที่ 4
total_sum += sum_value3

print("Subprocess sum output")
print(total_sum)

#Hw เขียน subprocess sum output ที่งหมดของ 3 อันข้างบน (ตัวเลขก่อน Hello World!)

