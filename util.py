﻿#!/usr/bin/env python
# coding=utf-8
# Author:  vavava

__author__ = 'vavava'

class test:
    pass

def parse_argvs(argvs):
    """
    usage:
        from sys import argv
        argv_dic=vavava.util.parse_argvs(argv)
        if argv_dic:
            if argv_dic.get('-ids'):  userTokens=argv_dic.get('-ids').split('|')
            if argv_dic.get('-d'):  httpdebuglevel=argv_dic.get('-d')
            if argv_dic.get('-t'):  socket_timeout=argv_dic.get('-t')
    """
    if len(argvs)<=1:
        return
    argv_dic={}
    key=None
    for each in argvs:
        if each[0] == '-':
            key=each
        else:
            if key is not None:
                argv_dic[key]=each
                key=None
    if key is not None:
        argv_dic[key]=key
    return argv_dic


def LogAdapter(log=None):
    import logging
    if log is None:
        log = logging.Logger("console")
        console = logging.StreamHandler()
        console.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
        console.setFormatter(formatter)
        log.addHandler(console)
    return log

def assure_path(path):
    import os.path
    if os.path.isdir(path) is not True:
        os.makedirs(path)

def initlog(logfile=None,level=None):
    import logging as logging
    if not level:
        level = logging.DEBUG
    logger = logging.getLogger()
    if logfile:
        hdlr = logging.FileHandler(logfile)
        hdlr.setLevel(level=level)
        formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
        hdlr.setFormatter(formatter)
        logger.addHandler(hdlr)
    console = logging.StreamHandler()
    console.setLevel(level)
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    console.setFormatter(formatter)
    logger.addHandler(console)

    logger.setLevel(level)
    return logger

class SynDict(object):
    from threading import Lock
    def __init__(self):
        self._dict = {}
        self._mt = Lock()

    def add(self,k,v):
        self._mt.acquire()
        self._dict[k]=v
        self._mt.release()

    def popitem(self):
        v = None
        self._mt.acquire()
        if len(self._dict) > 0:
            k,v = self._dict.popitem()
        self._mt.release()
        return v

import re
def reg_helper(text,reg_str="",mode=re.I|re.S):
    reg=re.compile(reg_str,mode)
    return reg.findall(text)

def importAny(name):
    try:
        return __import__(name,fromlist=[''])
    except:
        try:
            i = name.rfind('.')
            mod = __import__(name[:i],fromlist=[''])
            return getattr(mod,name[i+1:])
        except:
            raise RuntimeError('No module of: %s found'%(name))
def get_sufix(name):
    re = os.path.splitext(name)[1][1:]
    return re
def copy_dir(sourceDir, targetDir, types={}):
    sourceDir = os.path.abspath(sourceDir)
    targetDir = os.path.abspath(targetDir)
    for f in os.listdir(sourceDir):
        sourceF = os.path.join(sourceDir, f)
        targetF = os.path.join(targetDir, f)
        if os.path.isfile(sourceF):
            if not os.path.exists(targetDir):
                os.makedirs(targetDir)
            if types.has_key(get_sufix(f)):
                open(targetF, "wb").write(open(sourceF, "rb").read())
        if os.path.isdir(sourceF):
            copy_dir( sourceF, targetF, types )

##################################################################################################
def test_log():
    log = LogAdapter(log=None, name="test")
    log.info("%s%r%r", "1", "1", "1")
    log.info("alkdsaklads;fd")
    logger = initlog("./log/log_test.lg")
    log = LogAdapter(log=logger, name="test")
    log.info("%s%r%r", "1", "1", "1")
    log.info("alkdsaklads;fd")

def test_reg():
    import re
    m= re.findall(r'(^\s*$)','74.125.128.103  www.google.com.hk\n',re.MULTILINE)
    #m= re.findall(r'\s+(plus\.google\.com)\s*$','74.125.229.161  plus.google.com\n')
    if m:
        print m
    pass

try:
    import ctypes
    OutputDebugStringA = ctypes.windll.kernel32.OutputDebugStringA
    OutputDebugStringW = ctypes.windll.kernel32.OutputDebugStringW
except:pass

# time.clock() performance different on win and linux
import os
if os.name == "nt":
    from time import clock as _interval_timer
else:
    from time import time as _interval_timer

if __name__ == '__main__':
    test_log()

""" 如何判断平台类型
def TestPlatform():
    import platform
    #Windows will be : (32bit, WindowsPE)
    #Linux will be : (32bit, ELF)
    print(platform.architecture())

    #Windows will be : Windows-XP-5.1.2600-SP3 or Windows-post2008Server-6.1.7600
    #Linux will be : Linux-2.6.18-128.el5-i686-with-redhat-5.3-Final
    print(platform.platform())

    #Windows will be : Windows
    #Linux will be : Linux
    print(platform.system())

    #Windows and Linux will be : 3.1.1 or 3.1.3
    print(platform.python_version())

def UsePlatform():
    import platform
    sysstr = platform.system()
    if(sysstr =="Windows"):
        print ("Call Windows tasks")
    elif(sysstr == "Linux"):
        print ("Call Linux tasks")
    else:
        print ("Other System tasks")

"""
