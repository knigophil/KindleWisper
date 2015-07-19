#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai

import sys
import os
import getopt
import struct
import binascii
import locale
import codecs

iswindows = sys.platform.startswith('win')

# Because Windows (and Mac OS X) allows full unicode filenames and paths
# any paths in pure bytestring python 2.X code must be utf-8 encoded as they will need to
# be converted on the fly to full unicode for Windows platforms.  Any other 8-bit str 
# encoding would lose characters that can not be represented in that encoding

# these are simple support routines to allow use of utf-8 encoded bytestrings as paths in main program
# to be converted on the fly to full unicode as temporary un-named values to prevent
# the potential mixing of unicode and bytestring string values in the main program 

def pathof(s):
    if isinstance(s, unicode):
        try:
            print "Warning: pathof expects utf-8 encoded byestring: ", s
        except:
            pass
        if iswindows:
            return s
        return s.encode('utf-8')
    if iswindows:
        return s.decode('utf-8')
    return s

# force string to be utf-8 encoded whether unicode or bytestring
def utf8_str(p, enc='utf-8'):
    if isinstance(p, unicode):
        return p.encode('utf-8')
    if enc != 'utf-8':
        return p.decode(enc).encode('utf-8')
    return p


# get sys.argv arguments and encode them into utf-8
def utf8_argv():
    global iswindows
    if iswindows:
        # Versions 2.x of Python don't support Unicode in sys.argv on
        # Windows, with the underlying Windows API instead replacing multi-byte
        # characters with '?'.  So use shell32.GetCommandLineArgvW to get sys.argv 
        # as a list of Unicode strings and encode them as utf-8

        from ctypes import POINTER, byref, cdll, c_int, windll
        from ctypes.wintypes import LPCWSTR, LPWSTR

        GetCommandLineW = cdll.kernel32.GetCommandLineW
        GetCommandLineW.argtypes = []
        GetCommandLineW.restype = LPCWSTR

        CommandLineToArgvW = windll.shell32.CommandLineToArgvW
        CommandLineToArgvW.argtypes = [LPCWSTR, POINTER(c_int)]
        CommandLineToArgvW.restype = POINTER(LPWSTR)

        cmd = GetCommandLineW()
        argc = c_int(0)
        argv = CommandLineToArgvW(cmd, byref(argc))
        if argc.value > 0:
            # Remove Python executable and commands if present
            start = argc.value - len(sys.argv)
            return [argv[i].encode('utf-8') for i in
                    xrange(start, argc.value)]
        # this should never happen
        return None
    else:
        argv = []
        argvencoding = sys.stdin.encoding
        if argvencoding == None:
            argvencoding = sys.getfilesystemencoding()
        if argvencoding == None:
            argvencoding = 'utf-8'
        for arg in sys.argv:
            if type(arg) == unicode:
                argv.append(arg.encode('utf-8'))
            else:
                argv.append(arg.decode(argvencoding).encode('utf-8'))
        return argv


# Python 2.X is broken in that it does not recognize CP65001 as UTF-8
def add_cp65001_codec():
    try:
        codecs.lookup('cp65001')
    except LookupError:
        codecs.register(
            lambda name: name == 'cp65001' and codecs.lookup('utf-8') or None)
    return


# Almost all sane operating systems now default to utf-8 as the 
# proper default encoding so that all files and path names
# in any language can be properly represented.

def set_utf8_default_encoding():
    if sys.getdefaultencoding() in ['utf-8', 'UTF-8','cp65001','CP65001']:
        return

    # Regenerate setdefaultencoding.
    reload(sys)
    sys.setdefaultencoding('utf-8')

    for attr in dir(locale):
        if attr[0:3] != 'LC_':
            continue
        aref = getattr(locale, attr)
        try:
            locale.setlocale(aref, '')
        except locale.Error:
            continue
        try:
            lang = locale.getlocale(aref)[0]
        except (TypeError, ValueError):
            continue
        if lang:
            try:
                locale.setlocale(aref, (lang, 'UTF-8'))
            except locale.Error:
                os.environ[attr] = lang + '.UTF-8'
    try:
        locale.setlocale(locale.LC_ALL, '')
    except locale.Error:
        pass
    return

class DualMetaFixException(Exception):
    pass

# palm database offset constants
number_of_pdb_records = 76
first_pdb_record = 78

# important rec0 offsets
mobi_header_base = 16
mobi_header_length = 20
mobi_version = 36
title_offset = 84

def getint(data,ofs,sz='L'):
    i, = struct.unpack_from('>'+sz,data,ofs)
    return i

def writeint(data,ofs,n,len='L'):
    if len=='L':
        return data[:ofs]+struct.pack('>L',n)+data[ofs+4:]
    else:
        return data[:ofs]+struct.pack('>H',n)+data[ofs+2:]

def getsecaddr(datain,secno):
    nsec = getint(datain,number_of_pdb_records,'H')
    if (secno < 0) | (secno >= nsec):
        emsg = 'requested section number %d out of range (nsec=%d)' % (secno,nsec)
        raise DualMetaFixException(emsg)
    secstart = getint(datain,first_pdb_record+secno*8)
    if secno == nsec-1:
        secend = len(datain)
    else:
        secend = getint(datain,first_pdb_record+(secno+1)*8)
    return secstart,secend

def readsection(datain,secno):
    secstart, secend = getsecaddr(datain,secno)
    return datain[secstart:secend]

# overwrite section - must be exact same length as original
def replacesection(datain,secno,secdata): 
    secstart,secend = getsecaddr(datain,secno)
    seclen = secend - secstart
    if len(secdata) != seclen:
        raise DualMetaFixException('section length change in replacesection')
    datalst = []
    datalst.append(datain[0:secstart])
    datalst.append(secdata)
    datalst.append(datain[secend:])
    dataout = "".join(datalst)
    return dataout

def get_exth_params(rec0):
    ebase = mobi_header_base + getint(rec0,mobi_header_length)
    if rec0[ebase:ebase+4] != 'EXTH':
        raise DualMetaFixException('EXTH tag not found where expected')
    elen = getint(rec0,ebase+4)
    enum = getint(rec0,ebase+8)
    rlen = len(rec0)
    return ebase,elen,enum,rlen

def add_exth(rec0,exth_num,exth_bytes):
    ebase,elen,enum,rlen = get_exth_params(rec0)
    newrecsize = 8+len(exth_bytes)
    newrec0 = rec0[0:ebase+4]+struct.pack('>L',elen+newrecsize)+struct.pack('>L',enum+1)+\
              struct.pack('>L',exth_num)+struct.pack('>L',newrecsize)+exth_bytes+rec0[ebase+12:]
    newrec0 = writeint(newrec0,title_offset,getint(newrec0,title_offset)+newrecsize)
    # keep constant record length by removing newrecsize null bytes from end
    sectail = newrec0[-newrecsize:]
    if sectail != '\0'*newrecsize:
        raise DualMetaFixException('add_exth: trimmed non-null bytes at end of section')
    newrec0 = newrec0[0:rlen]
    return newrec0

def read_exth(rec0,exth_num):
    exth_values = []
    ebase,elen,enum,rlen = get_exth_params(rec0)
    ebase = ebase+12
    while enum>0:
        exth_id = getint(rec0,ebase)
        if exth_id == exth_num:
            # We might have multiple exths, so build a list.
            exth_values.append(rec0[ebase+8:ebase+getint(rec0,ebase+4)])
        enum = enum-1
        ebase = ebase+getint(rec0,ebase+4)
    return exth_values

def del_exth(rec0,exth_num):
    ebase,elen,enum,rlen = get_exth_params(rec0)
    ebase_idx = ebase+12
    enum_idx = 0
    while enum_idx < enum:
        exth_id = getint(rec0,ebase_idx)
        exth_size = getint(rec0,ebase_idx+4)
        if exth_id == exth_num:
            newrec0 = rec0
            newrec0 = writeint(newrec0,title_offset,getint(newrec0,title_offset)-exth_size)
            newrec0 = newrec0[:ebase_idx]+newrec0[ebase_idx+exth_size:]
            newrec0 = newrec0[0:ebase+4]+struct.pack('>L',elen-exth_size)+struct.pack('>L',enum-1)+newrec0[ebase+12:]
            newrec0 = newrec0 + '\0'*(exth_size)
            if rlen != len(newrec0):
                raise DualMetaFixException('del_exth: incorrect section size change')
            return newrec0
        enum_idx += 1
        ebase_idx = ebase_idx+exth_size
    return rec0


class DualMobiMetaFix:

    def __init__(self, infile, asin):
        self.datain = open(pathof(infile), 'rb').read()
        self.datain_rec0 = readsection(self.datain,0)

        # in the first mobi header
        # add 501 to "EBOK", add 113 as asin, add 504 as asin
        rec0 = self.datain_rec0
        rec0 = del_exth(rec0, 501)
        rec0 = del_exth(rec0, 113)
        rec0 = del_exth(rec0, 504)
        rec0 = add_exth(rec0, 501, "EBOK")
        rec0 = add_exth(rec0, 113, asin)
        rec0 = add_exth(rec0, 504, asin)
        self.datain = replacesection(self.datain, 0, rec0)

        ver = getint(self.datain_rec0,mobi_version)
        self.combo = (ver!=8)
        if not self.combo:
            return

        exth121 = read_exth(self.datain_rec0,121)
        if len(exth121) == 0:
            self.combo = False
            return
        else:
            # only pay attention to first exth121
            # (there should only be one)
            datain_kf8, = struct.unpack_from('>L',exth121[0],0)
            if datain_kf8 == 0xffffffff:
                self.combo = False
                return
        self.datain_kfrec0 =readsection(self.datain,datain_kf8)

        # in the second header
        # add 501 to "EBOK", add 113 as asin, add 504 as asin
        rec0 = self.datain_kfrec0
        rec0 = del_exth(rec0, 501)
        rec0 = del_exth(rec0, 113)
        rec0 = del_exth(rec0, 504)
        rec0 = add_exth(rec0, 501, "EBOK")
        rec0 = add_exth(rec0, 113, asin)
        rec0 = add_exth(rec0, 504, asin)
        self.datain = replacesection(self.datain, datain_kf8, rec0)

    def getresult(self):
        return self.datain


def usage(progname):
    print ""
    print "Description:"
    print "   Simple Program to add EBOK and ASIN Info to Meta on Dual Mobis"
    print "  "
    print "Usage:"
    print "  %s -h asin infile.mobi outfile.mobi" % progname
    print "  "
    print "Options:"
    print "    -h           print this help message"


def main(argv=utf8_argv()):
    print "DualMobiMetaFixer v003"
    progname = os.path.basename(argv[0])
    try:
        opts, args = getopt.getopt(argv[1:], "h")
    except getopt.GetoptError, err:
        print str(err)
        usage(progname)
        sys.exit(2)

    if len(args) != 3:
        usage(progname)
        sys.exit(2)

    for o, a in opts:
        if o == "-h":
            usage(progname)
            sys.exit(0)

    asin = args[0]
    infile = args[1]
    outfile = args[2]
    try:
        print "ASIN:   ", asin
        print "Input:  ", infile
        print "Output: ", outfile
    except:
        pass
    try:
        # make sure it is really a mobi ebook
        infileext = os.path.splitext(infile)[1].upper()
        if infileext not in ['.MOBI', '.PRC', '.AZW', '.AZW3','.AZW4']:
            raise DualMetaFixException('second parameter must be a Kindle/Mobipocket ebook.')
        mobidata = open(pathof(infile), 'rb').read(100)
        palmheader = mobidata[0:78]
        ident = palmheader[0x3C:0x3C+8]
        if ident != 'BOOKMOBI':
            raise DualMetaFixException('invalid file format not BOOKMOBI')

        dmf = DualMobiMetaFix(infile, asin)
        open(pathof(outfile),'wb').write(dmf.getresult())

    except Exception, e:
        print "Error: %s" % e
        return 1

    print "Success"
    return 0


if __name__ == '__main__':
    add_cp65001_codec()
    set_utf8_default_encoding()
    sys.exit(main())


