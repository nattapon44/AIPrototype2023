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

process_output1 = subprocess.Popen(["python","firstpy.py","--num","100","--XX","90"],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
out, err = process_output1.communicate()
process_output2 = subprocess.Popen(["python","firstpy.py","--num","-10","--XX","-90"],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
out, err = process_output2.communicate()
process_output3 = subprocess.Popen(["python","firstpy.py","--num","0"],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
out, err = process_output3.communicate()
sum_output = process_output1 + process_output2 + process_output3
print("Subprocess sum output")
print(sum_output)

#Hw เขียน subprocess sum output ที่งหมดของ 3 อันข้างบน (ตัวเลขก่อน Hello World!)

