# -*- coding: utf-8 -*-
"""
Created on Sun Nov 17 20:52:01 2019

@author: wyr
"""

import re

rep_rule = {r' \$(.*?)\$': '',
            r' \$\$(.*?)\$\$': '',
            r' \\cite{.*?}': '',
            r' \\cite\[.*?}': '',
            r'\\citet{.*?}': 'Tom',
            r'\\citet\[.*?}': 'Tom',
            r'\\\w*? ': '',
            r'\\.*?{(.*?)}': lambda x:x.group(1)}

def tex2txt(tex, rep_rule):
    for p in rep_rule:
        tex = re.sub(p, rep_rule[p], tex)
    return tex

if __name__ == '__main__':
    tex = input('input latex code: ')     
    txt = tex2txt(tex, rep_rule)
    print('\n\n out:')
    print(txt)