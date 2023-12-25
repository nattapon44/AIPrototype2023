import subprocess #สำหรับรัน terminal command

if __name__ == "__main__":
    #basic terminal command
    subprocess.run(["ls","-ltr"])
    subprocess.run(["python","firstpy.py"])