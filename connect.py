# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import os
import time

def autologin(user, passwd, t):
    cmd = 'curl -d "username=' + user + '&password=' + passwd
    cmd = cmd + '" "http://p.nju.edu.cn/portal_io/login"'
    while True:
        result = os.system("ping www.baidu.com")
        if (result != 0):
            os.system(cmd)
        time.sleep(t)

if __name__ == '__main__':
    user = input("Student ID: ")
    passwd = input("Password: ")
    autologin(user, passwd, 600)