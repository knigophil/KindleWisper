#!/usr/bin/env python
#-*- coding: utf-8 -*-
import sys, os, inspect
import shutil
import extractcover, preparecover
import mobiunpack32
import glob, re
import subprocess
from subprocess import Popen, PIPE, STDOUT
import argparse
import unicodefix
from unidecode import unidecode
import dualmetafix

def escape_glob(path):
    transdict = {
            '[': '[[]',
            ']': '[]]',
            '*': '[*]',
            '?': '[?]',
            }
    rc = re.compile('|'.join(map(re.escape, transdict)))
    return rc.sub(lambda m: transdict[m.group(0)], path)

def processFile(infile, seqnumber, title, asin, position):
    infilename = os.path.splitext(infile)[0]
    infileext = os.path.splitext(infile)[1]
    inputdir = u"input.$$$"
    outputdir = u"output.$$$"
    os.mkdir(inputdir)
    os.mkdir(outputdir)
    shutil.copy(infile, os.path.join(inputdir, infilename+u".mobi"))
    for file in glob.glob(os.path.join(u"images.$$$", escape_glob(infilename)+u'.cover*')):
        imgname = u"thumbnail_" + unidecode(infilename).replace("'","z") + u"_EBOK_portrait.jpg"
        shutil.copy(file, imgname)
        try:
            preparecover.resize(imgname)
        except Exception as e:
            pass
    scriptdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    masin = unidecode(infilename).replace("'","z") if asin is None else asin
    pinfile = os.path.join(inputdir,infilename + u".mobi")
    poutfile = os.path.join(outputdir,infilename + u".mobi")
    cmd = u'python "' + os.path.join(scriptdir, u"dualmetafix.py") +u'" "%s" "%s" "%s"' % (masin, pinfile,poutfile)

    # Cyriilc file name fails here
    # subprocess.call(cmd)

    args = ["dualmetafix.py",masin,pinfile,poutfile]
    dualmetafix.main(args)

    # scriptdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    # cmd = u'java -cp "' + os.path.join(scriptdir, u"MobiMetaEditorV0.16.jar") +u'" cli.WhisperPrep "%s" "%s"' % (inputdir, outputdir)
    # print u"Running", cmd
    # process = Popen(cmd, stdin=PIPE, stdout=sys.stdout, stderr=STDOUT)
    # process.stdin.write(unidecode(infilename).replace("'","z") if asin is None else asin)
    # process.stdin.write("\n")
    # process.stdin.close()
    # process.wait()

    shutil.copy(os.path.join(outputdir, infilename+u".mobi"), infilename+u".processed"+infileext)
    shutil.rmtree(u"images.$$$")
    shutil.rmtree(inputdir)
    shutil.rmtree(outputdir)
    if asin!=None:
        sys.exit(0)
    title = get_booktitle(infile, title)
    if title==None:
        print "No title"
    else:
        try:
            print u'Title: "%s"' % title
        except:
            print u'Title: "%s"' % unidecode(title)
    seqnumber = get_seqnumber(infilename, seqnumber)
    print u'Seq number: "%s"' % seqnumber
    if title is not None or seqnumber is not None:
        preparecover.draw(u"thumbnail_" + unidecode(infilename).replace("'","z") + u"_EBOK_portrait.jpg", title, seqnumber, position)
    return 0

def get_booktitle(infile, title):
    if title is None: return None
    title = unicode(title, sys.stdin.encoding)
    if title == 'auto':
        files = mobiunpack32.fileNames(infile, "tmpdir2.$$$")
        mu = mobiunpack32.mobiUnpack(files)
        metadata = mu.getMetaData()
        title = unicode(mu.title, mu.codec)
        shutil.rmtree("tmpdir2.$$$")
    return title

def get_seqnumber(infilename, seqnumber):
    if seqnumber is None: return None
    result = seqnumber if seqnumber != 'auto' else infilename[0] + (infilename[1] if infilename[1].isdigit() else "")
    if not result.isdigit():
        print "Error: image text should be digits only"
        return None
    #result = result[0:2].zfill(2)
    result = result[0:2]
    return result


def main(argv=sys.argv):
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input-file', help='Input file')
    parser.add_argument('-s', '--sequence-number', help='A number to stamp on the cover ("auto" for first one-two characters of the name of the file)')
    parser.add_argument('-t', '--title', help='A text to stamp on the cover ("auto" for the title from the metainfo of the book)')
    parser.add_argument('-a', '--asin', help='A text to put into ASIN metainfo field')
    parser.add_argument('-p', '--position', choices=['top', 'bottom'], default='bottom', help='Position of the stamp')

    args, unknown = parser.parse_known_args()
    print args
    input_file = unicode(args.input_file, sys.stdin.encoding)

    extractcover.processFile(input_file,args.asin)
    return processFile(input_file, args.sequence_number, args.title, args.asin, args.position)

if __name__ == "__main__":
    sys.exit(main())