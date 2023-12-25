import subprocess #สำหรับรัน terminal command

def firstrun():
    print("first run num=100 XX=90")
def secrun():
    print("first run num=-10 XX=-90")
def thirdrun():
    print("first run num=0")
def print():
    print("---------------------------------------")
    
if __name__ == "__main__":
    #basic terminal command
    firstrun()
    subprocess.run(["python","firstpy.py","--num","100","--XX","90"])
    print()
    secrun()
    subprocess.run(["python","firstpy.py","--num","-10","--XX","-90"])
    print()
    thirdrun()
    subprocess.run(["python","firstpy.py","--num","0"])
    print()
