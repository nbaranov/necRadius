from functions import readIPfromXLSX
from functions import logAndPrint
import os


listIP = readIPfromXLSX('NEnecDont.xlsx')
for ip in listIP:
    os.system(f"ping4 {ip} -c 5")