# -*- coding: utf-8 -*-
"""
Created on Wed Apr 17 14:18:46 2019

@author: wyr
"""

from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage, PDFTextExtractionNotAllowed
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams
import StringIO
import os.path
import codecs
import re

cite_keywords = ['Removed Due to Privacy Concerns', 'Removed Due to Privacy Concerns']
author_keywords = ['Removed Due to Privacy Concerns', 'Removed Due to Privacy Concerns']
title_keywords = ['Removed Due to Privacy Concerns', 'Removed Due to Privacy Concerns']
keywords_tofind = ['Removed Due to Privacy Concerns', 'Removed Due to Privacy Concerns']
title_confirm = 'Removed Due to Privacy Concerns'
folder_spliter = '\\'
pdf_folder = 'papers\\'
txt_folder = 'text_result\\'
parse_folder = 'parse_result\\'
cite_folder = 'cite_result\\'

class FileFinder():
    def __init__(self):
        self.flist = []
    
    def add_file_list(self, file_dir, suffix=''):
        l = len(suffix)
        if (l>0):
            for root_path, dirs, files in os.walk(file_dir):
                for f in files:
                    if (f[-1*l:] == suffix):
                        self.flist.append(os.path.join(root_path, f))
        else:
             for root_path, dirs, files in os.walk(file_dir):
                for f in files:
                    self.flist.append(os.path.join(root_path, f))           
    
    def add_file(self, f):
        self.flist.append(f)
        
    def get_list(self):
        return self.flist[:]
    
    def clear(self):
        self.flist = []

class Pdf2txt():

    def __init__(self, flist):
        self.flist = flist
        self.errlist = []

    def convert(self, path):
        output = StringIO.StringIO()
        e = False
        with open(path, 'rb') as f:
            try:
                praser = PDFParser(f)
                doc = PDFDocument(praser)
                if not doc.is_extractable:
                    raise PDFTextExtractionNotAllowed
                pdfrm = PDFResourceManager()
                laparams = LAParams()
                device = PDFPageAggregator(pdfrm, laparams=laparams)
                interpreter = PDFPageInterpreter(pdfrm, device)
            except Exception as err:
                print(err)
                e = True
            if (not e):
                for page in PDFPage.create_pages(doc):
                    try:
                        interpreter.process_page(page)
                        layout = device.get_result()
                        for x in layout:
                            if hasattr(x, "get_text"):
                                content = x.get_text()
                                output.write(content)
                    except Exception as err:
                        print(err)
                        e = True                
        if (e):
            self.errlist.append(path)
        content = output.getvalue()
        output.close()
        return content

    def savefile(self, content, path):
        with codecs.open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        
    def jiaonigan(self, output_dir):
        for f in self.flist:
            filename = f.split(folder_spliter)[-1]
            print('converting ' + filename)
            string = self.convert(f)
            self.savefile(string, output_dir+filename[:-4]+".txt")
        
class TxtParser():
    def __init__(self, flist):
        self.flist = flist
        
    def parse(self, path):
        output = StringIO.StringIO()
        with codecs.open(path, 'r', encoding='utf-8') as fin:
            for line in fin:
                line = re.sub(r'[\s]', "", line)
                output.write(line.lower())
        return output.getvalue()
                    
    def savefile(self, content, path):
        with codecs.open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        
    def jiaonigan(self, output_dir):
        for f in self.flist:
            filename = f.split(folder_spliter)[-1]
            print('parsing ' + filename)
            string = self.parse(f)
            self.savefile(string, output_dir+filename[:-4]+".txt")
            
class CiteFinder():
    def __init__(self, flist):
        self.flist = flist
        self.errlist = []
        self.warninglist = []
        
    def find_index(self, path, author_keywords, title_keywords, title_confirm='', find_length=70):
        idx_list = []
        with codecs.open(path, 'r', encoding='utf-8') as fin:
            context = fin.readline()   
            for author in author_keywords:
                i = context.find(author)
                while (i != -1):
                    target = context[i:i+100]
                    if (target.find(title_confirm) == -1):
                        i = context.find(author, i+1)
                        continue
                    target = context[i:i-find_length:-1]
                    s = re.search(r'\][\d]+\[', target)
                    if (s != None):
                        idx_list.append(int(target[s.span()[0]+1:s.span()[1]-1][::-1]))
                    s = re.match(r'z\.?[\d]+', target)
                    if (s != None):
                        temp_idx = target[s.span()[0]+2:s.span()[1]][::-1]
                        if (len(temp_idx) <= 2):
                            idx_list.append(int(temp_idx))
                        elif (len(temp_idx) == 5):
                            idx_list.append(int(temp_idx[-1]))
                        elif (len(temp_idx) == 6):
                            idx_list.append(int(temp_idx[-2:]))
                    i = context.find(author, i+1)
            for title in title_keywords:
                i = context.find(title)
                while (i != -1):
                    target = context[i:i-find_length:-1]
                    s = re.search(r'\][\d]+\[', target)
                    if (s != None):
                        idx_list.append(int(target[s.span()[0]+1:s.span()[1]-1][::-1]))
                    s = re.match(r'h-?\.?z\.?[\d]+', target)
                    if (s != None):
                        temp_idx = target[s.span()[0]+2:s.span()[1]][::-1]
                        if (len(temp_idx) <= 2):
                            idx_list.append(int(temp_idx))
                        elif (len(temp_idx) == 5):
                            idx_list.append(int(temp_idx[-1]))
                        elif (len(temp_idx) == 6):
                            idx_list.append(int(temp_idx[-2:]))
                    i = context.find(title, i+1)
        return list(set(idx_list))         
    
    def find_cite(self, path, idx, cite_keywords, r_min_length=0, l_min_length=10):
        cite_sentense = []
        with codecs.open(path, 'r', encoding='utf-8') as fin:
            context = fin.readline()       
            if (len(idx) > 0):
                cite_keywords = []
                for i in idx:
                    keyword = '[' + str(i) + ']'
                    j = context.find(keyword)
                    while (j > 0):
                        rdot = context.find('.', j+r_min_length);
                        ldot = context.rfind('.', 0, j-l_min_length);
                        cite_sentense.append(context[ldot+1:rdot+1])
                        j = context.find(keyword, j+1)
                    cite_sentense = cite_sentense[:-1] # remove reference
                    cite_keywords.append(',' + str(i) + ']')
                    cite_keywords.append('[' + str(i) + ',')
                    cite_keywords.append(',' + str(i) + ',')
            for keyword in cite_keywords:
                i = context.find(keyword)
                while (i > 0):
                    rdot = context.find('.', i+r_min_length);
                    ldot = context.rfind('.', 0, i-l_min_length);
                    cite_sentense.append(context[ldot+1:rdot+1])
                    i = context.find(keyword, i+1)
        return cite_sentense                 
                
    def savefile(self, cite_type, sentenses, path):
        with codecs.open(path, 'w', encoding='utf-8') as f:
            f.write(str(cite_type) + '\n')
            for line in sentenses:
                f.write(line + '\n')
        
    def jiaonigan(self, output_dir):
        for f in self.flist:
            filename = f.split(folder_spliter)[-1]
            print('finding ' + filename)
            idx = self.find_index(f, author_keywords, title_keywords, title_confirm)
            cite_sentenses = self.find_cite(f, idx, cite_keywords)
            if (len(cite_sentenses) > 0):
                if (len(idx) == 1):
                    self.savefile(idx[0], cite_sentenses, output_dir+filename[:-4]+".txt")
                elif (len(idx) == 0):
                    self.savefile(0, cite_sentenses, output_dir+filename[:-4]+".txt")
                else:
                    self.savefile(-1, cite_sentenses, output_dir+filename[:-4]+".txt")
                    self.warninglist.append(f)
            else:
                self.errlist.append(f)
                
class KeywordFinder():
    def __init__(self, flist):
        self.flist = flist
        self.buffer = []
        
    def find_keywords(self, path, keywords):
        keywords_count = [0 for _ in range(len(keywords))]
        words_count = 0
        with codecs.open(path, 'r', encoding='utf-8') as fin:
            for line in fin:
                words_count = words_count + len(line)
                for i in range(0, len(keywords)):
                    keywords_count[i] = keywords_count[i] + len(re.findall(keywords[i], line))
        return words_count, keywords_count                       
    
    def chars_to_line(self, count, ch_sline=90, ch_dline=60):
        dl = int(count/ch_dline) + 1
        sl = int(count/ch_sline) + 1
        return dl, sl
     
    def jiaonigan(self, filename):
        fout = codecs.open(filename, 'w', encoding='utf-8')
        for f in self.flist:
            title = f.split(folder_spliter)[-1][:-4]
            print('keyword ' + title)
            w_count, k_count = self.find_keywords(f, keywords_tofind)
            fout.write(title + ', ' + str(self.chars_to_line(w_count))[1:-1] + 
                       ', ' + str(k_count)[1:-1] + '\n')
            self.buffer.append([title, self.chars_to_line(w_count), k_count])
        fout.close()
        
    def get_buffer(self):
        return self.buffer[:]
    
    def clear(self):
        self.buffer = []
        
def get_cite_stat(title_list, stat, filename):
    fname = [i[0] for i in stat]
    fout = codecs.open(filename, 'w', encoding='utf-8')
    for t in title_list:
        if (t in fname):
            i = fname.index(t)
            fout.write(re.sub(",","",t) + ', ' + str(stat[i][1])[1:-1] + 
                       ', ' + re.sub("0","",str(stat[i][2])[1:-1]) + '\n')
        else:
            fout.write(re.sub(",","",t) + '\n')
    fout.close()

if __name__ == '__main__':
    flist_generator = FileFinder();
#    flist_generator.add_file_list(pdf_folder, '.pdf');
#    pdf_converter = Pdf2txt(flist_generator.get_list());
#    pdf_converter.jiaonigan(txt_folder)
#    with open("err_converter.txt", "w") as f:
#        for line in pdf_converter.errlist:
#            f.write(line + "\n")
#    flist_generator.clear();
    
    flist_generator.add_file_list(txt_folder)
    txt_parser = TxtParser(flist_generator.get_list())
    txt_parser.jiaonigan(parse_folder)
    flist_generator.clear();
    
    flist_generator.add_file_list(parse_folder)
    cite_finder = CiteFinder(flist_generator.get_list())
    cite_finder.jiaonigan(cite_folder)
    with open("err_finder.txt", "w") as f:
        for line in cite_finder.errlist:
            f.write(line + "\n")
    with open("warning_finder.txt", "w") as f:
        for line in cite_finder.warninglist:
            f.write(line + "\n")
    flist_generator.clear();
    
    flist_generator.add_file_list(cite_folder)
    key_finder = KeywordFinder(flist_generator.get_list())
    key_finder.jiaonigan("keyword_count.txt")
    flist_generator.clear();
    
    flist_generator.add_file_list(pdf_folder)
    title_list = flist_generator.get_list()
    for i in range(0, len(title_list)):
        title_list[i] = title_list[i].split(folder_spliter)[-1][:-4]
    get_cite_stat(title_list, key_finder.get_buffer(), "paper_stat.csv")

