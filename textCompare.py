# -*- coding: utf-8 -*-
"""
Created on Sun Apr 12 23:09:07 2020

@author: vttex
"""

import sys

def comp(f1, f2):
    line = 1
    while (True):
        l1 = f1.readline();
        l2 = f2.readline();
        if (l1 != l2):
            return line;
        if (l1 == ''):
            return 0;
        line = line + 1
        
if __name__ == '__main__':
    if (len(sys.argv) == 3):
        fp1 = sys.argv[1]
        fp2 = sys.argv[2]
    else:
        fp1 = input('input path1: ') 
        fp2 = input('input path2: ')     
    with open(fp1, 'r') as f1:
        with open(fp2, 'r') as f2: 
            line = comp(f1,f2)
            if (line == 0):
                print("\n equal")
            else:
                print("\n first different at line " + str(line))