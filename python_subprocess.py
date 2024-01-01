import subprocess #สำหรับรัน terminal command
    
if __name__ == "__main__":
    #basic terminal command
    print("first run num=100 XX=90")
    subprocess.run(["python","firstpy.py","--num","100","--XX","90"])
    print("------------------------------------------------------------")
    print("second run num=-10 XX=-90")
    subprocess.run(["python","firstpy.py","--num","-10","--XX","-90"])
    print("------------------------------------------------------------")
    print("third run num=0")
    subprocess.run(["python","firstpy.py","--num","0"])
    print("------------------------------------------------------------")


#use output from other program
process_output = subprocess.Popen(["python","firstpy.py","--num","0"],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
out, err = process_output.communicate()
print(out.decode('utf-8'))
print(len(out.decode('utf-8')))

output1 = subprocess.Popen(["python","firstpy.py","--num","100","--XX","90"],stdout=subprocess.PIPE,stderr=subprocess.PIPE).decode('utf-8')
output2 = subprocess.Popen(["python","firstpy.py","--num","-10","--XX","-90"],stdout=subprocess.PIPE,stderr=subprocess.PIPE).decode('utf-8')
output3 = subprocess.Popen(["python","firstpy.py","--num","0"],stdout=subprocess.PIPE,stderr=subprocess.PIPE).decode('utf-8')
sum_output = output1 + output2 + output3
print("Subprocess sum output")
print(sum_output)

#Hw เขียน subprocess sum output ที่งหมดของ 3 อันข้างบน (ตัวเลขก่อน Hello World!)

