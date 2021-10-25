from ctypes import *

import time

import os
import sys
import win32com.shell.shell as shell
ASADMIN = 'asadmin'

if sys.argv[-1] != ASADMIN:
    script = os.path.abspath(sys.argv[0])
    params = ' '.join([script] + sys.argv[1:] + [ASADMIN])
    shell.ShellExecuteEx(lpVerb='runas', lpFile=sys.executable, lpParameters=params)
    print ("I am root now.")

print (windll.shell32.IsUserAnAdmin ()) # determine whether administrator rights


user32 = windll.LoadLibrary("C:\\Windows\\System32\\user32.dll")
user32.BlockInput (True) # This function requires administrator privileges True disabled
time.sleep(5)
user32.BlockInput (False) # This function requires administrator privileges
time.sleep(5)
