from argparse import _SubParsersAction
import subprocess #สำำหรับรัน terminal command

if __name__ == "__main__":
    #basic terminal command
    subprocess.run(["ls","-ltr"])
    subprocess.run(["rm","-r","~/test"])
    subprocess.run(["cd"])