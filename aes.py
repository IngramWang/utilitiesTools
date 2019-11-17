# -*- coding: utf-8 -*-
"""
Created on Tue Oct  1 16:18:12 2019

@author: wyr

AES.PY: encrypt and decrypt files using AES128 cipher
Structure of output (encrypted):
-
|
| original file
| file size
|
-
|
| padding (random bits)
| (file size + padding size) % AES.block_size == 0
|
-
|
| random bits
| 2 * AES.block_size - 4 bits
|
-
| 
| padding size
| 4 bits
| 
-
| 
| padding size
| 32 bytes = 2 * AES.block_size
| 
-
"""

from Crypto import Random
from Crypto.Cipher import AES
import hashlib
import os
import sys

class aesEncrypter():
    def __init__(self, passwd, blocksize = 100000 * AES.block_size):
        # AES.block_size = 16
        sh = hashlib.sha256(passwd.encode('utf8'))
        sh = sh.digest()
        # len(sh) = 32
        self.key = sh[:16]
        self.iv = sh[16:]
        mode = AES.MODE_CBC
        self.cryptos = AES.new(self.key, mode, self.iv)
        if (blocksize % AES.block_size == 0):
            self.bs = blocksize
        else:
            raise Exception('invalid blocksize')

    @staticmethod        
    def __cal_padding_length(filesize):
        return (AES.block_size - (filesize - 1) % AES.block_size - 1)

    @staticmethod        
    def __get_padding_length(int4):
        int4 = int.from_bytes(int4, 'little', signed=False)
        return int4 & (AES.block_size - 1)

    @staticmethod        
    def __save_padding_length(int4, padding_length):
        int4 = int.from_bytes(int4, 'little', signed=False) & (~(AES.block_size - 1))
        return int(int4 | padding_length).to_bytes(4, 'little', signed=False)
            
    def encrypt(self, in_path, out_path, hashcheck = True):  
        if (hashcheck):
            sh = hashlib.sha256()             
        try:    
            filesize = os.path.getsize(in_path)
            if (filesize <= 0):
                return 1;  
            with open(in_path, 'rb') as fin, open(out_path, 'wb') as fout:                         
                while (filesize > self.bs):                      
                    chunk = fin.read(self.bs)
                    if (hashcheck):
                        sh.update(chunk)
                    chunk = self.cryptos.encrypt(chunk)
                    fout.write(chunk)
                    filesize = filesize - self.bs                                   
                chunk = fin.read(filesize)
                if (hashcheck):
                    sh.update(chunk)
                padding_length = self.__cal_padding_length(filesize)
                if (padding_length > 0):
                    chunk = chunk + Random.get_random_bytes(padding_length)
                chunk = self.cryptos.encrypt(chunk)
                fout.write(chunk)
                
                chunk = Random.get_random_bytes(2 * AES.block_size)
                chunk = chunk[:-4] + self.__save_padding_length(chunk[-4:], padding_length)
                if (hashcheck):
                    sh.update(chunk)
                    chunk = chunk + sh.digest()
                else:
                    chunk = chunk + Random.get_random_bytes(2 * AES.block_size)
                chunk = self.cryptos.encrypt(chunk)
                fout.write(chunk)
        except Exception:
            return 1
        return 0
    
    def decrypt(self, in_path, out_path, hashcheck = True):
        if (hashcheck):
            sh = hashlib.sha256()        
        try:
            filesize = os.path.getsize(in_path) - 4 * AES.block_size
            if (filesize <= 0):
                return 1
            with open(in_path, 'rb') as fin, open(out_path, 'wb') as fout:                       
                while (filesize > self.bs):                      
                    chunk = fin.read(self.bs)
                    chunk = self.cryptos.decrypt(chunk)
                    if (hashcheck):
                        sh.update(chunk)
                    fout.write(chunk)
                    filesize = filesize - self.bs                    
                chunk = fin.read(filesize)
                chunk = self.cryptos.decrypt(chunk)
                
                ctlchunk = fin.read(4 * AES.block_size)
                ctlchunk = self.cryptos.decrypt(ctlchunk)
                rand_bits = ctlchunk[:2 * AES.block_size]
                check_bits = ctlchunk[2 * AES.block_size:]
                padding_length = self.__get_padding_length(rand_bits[-4:])
                if (padding_length > 0):
                    chunk = chunk[:-1 * padding_length]
                if (hashcheck):
                    sh.update(chunk + rand_bits)
                fout.write(chunk)
        except Exception:
            return 1
        if (hashcheck and sh.digest() != check_bits):
            return 2
        return 0
                    
if __name__ == "__main__":
    if (len(sys.argv) == 5 and sys.argv[1] == 'encrypt'):
        cipher = aesEncrypter(sys.argv[4])
        cipher.encrypt(sys.argv[2], sys.argv[3])
    elif (len(sys.argv) == 5 and sys.argv[1] == 'decrypt'):
        cipher = aesEncrypter(sys.argv[4])
        cipher.decrypt(sys.argv[2], sys.argv[3])
    elif (len(sys.argv) == 1):
        print('AES.PY: encrypt and decrypt files using AES128 cipher')
        tp = input('D for decrypt, E for encrypt: ')        
        inpath = input('input file path: ')
        
        outpath = input('(optional, enter to skip) output file path: ')
        if (len(outpath) == 0):
            outpath = inpath + '.' + tp.lower() + 'cpt'
            print('outpath is: ' + outpath)
            
        passwd = input('password: ')
        
        bsize = input('(optional, enter to skip) blocksize: ')
        try:
            bsize = int(bsize)
        except Exception:            
            bsize = -1
            print('default blocksize is used')
            
        hcheck = input('(optional, T or F, enter to skip) need hash check: ')
        if (hcheck.lower() == 'f'):
            hcheck = False
            print('hash check will be skiped')
        else:
            hcheck = True
            print('hash check will be performed')
            
        if (tp.lower() == 'e' and bsize == -1):
            cipher = aesEncrypter(passwd)
            ret = cipher.encrypt(inpath, outpath, hcheck)
        elif (tp.lower() == 'e'):
            cipher = aesEncrypter(passwd, bsize)
            ret = cipher.encrypt(inpath, outpath, hcheck)
        elif (tp.lower() == 'd' and bsize == -1):
            cipher = aesEncrypter(passwd)
            ret = cipher.decrypt(inpath, outpath, hcheck)
        elif (tp.lower() == 'd'):
            cipher = aesEncrypter(passwd, bsize)
            ret = cipher.decrypt(inpath, outpath, hcheck)
        else:
            raise Exception('ERROR: invalid type')
        
        if (ret == 0):
            print('operation successful')
        elif (ret == 1):
            print('ERROR: empty file or can not open file')
        else:
            print('Warning: operation successful but hash check failed')
    else:
        print('AES.PY: encrypt and decrypt files using AES128 cipher')
        print('to encrypt files, using')
        print('python3 ase.py encrypt inputpath outputpath password')
        print('to decrypt files, using')
        print('python3 ase.py decrypt inputpath outputpath password')