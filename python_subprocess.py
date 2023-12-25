import subprocess #สำหรับรัน terminal command

if __name__ == "__main__":
    #basic terminal command
    subprocess.run(["python","firstpy.py","--num","100","--XX","90"])
    subprocess.run(["python","firstpy.py","--num","-10","--XX","-90"])
    subprocess.run(["python","firstpy.py","--num","0"])
