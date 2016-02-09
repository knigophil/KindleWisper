# -*- coding: utf-8 -*-
#
# Copyright (c) 2014 Pawel Jastrzebski <pawelj@vulturis.eu>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

__license__ = 'GPL-3'
__copyright__ = '2014, Pawel Jastrzebski <pawelj@vulturis.eu>'

import sys, os, inspect, glob
from imghdr import what
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from uuid import uuid4
from tempfile import gettempdir
from subprocess import STDOUT, PIPE
from psutil import Popen
from . import DualMetaFix
from . import KindleUnpack
import mobiunpack32_34
import errno
import extractcover_34
import shutil
import textwrap

class MOBIFile:
    def __init__(self, path, kindle, config, progressbar,sequence_number,title,asin,position,mode,cloud,cover_size):
        self.mode = mode
        self.config = config
        self.path = path
        self.kindle = kindle
        self.seqnumber = sequence_number
        self.title = title
        self.asin = asin
        self.position = position
        self.write_thumb = True
        self.no_cover = False
        self.cover_size = cover_size
        # Do not write cover to Kindle/PC if asin is specified
        if asin != None:
            self.write_thumb = False
        # self.asin = str(uuid4())
        self.infilename = os.path.splitext(self.path)[0]
        self.infileext = os.path.splitext(self.path)[1]
        self.asin = self.infilename.replace("'","z") if asin is None else asin
        self.progressbar = progressbar
        # get title and seqnum
        section = KindleUnpack.Sectionizer(self.path)
        mhlst = [KindleUnpack.MobiHeader(section, 0)]
        mh = mhlst[0]
        metadata = mh.getmetadata()
        if self.title != None:
            self.title = self.get_booktitle2()
        self.author = self.get_bookauthor()
        self.seqnumber = self.get_seqnumber(self.infilename, self.seqnumber)
        self.check_file()

    def check_file(self):
        if not os.path.isfile(self.path):
            raise OSError('The specified file does not exist!')
        file_extension = os.path.splitext(self.path)[1].upper()
        if file_extension not in ['.MOBI', '.AZW', '.AZW3']:
            raise OSError('The specified file is not E-Book!')
        mobi_header = open(self.path, 'rb').read(100)
        palm_header = mobi_header[0:78]
        ident = palm_header[0x3C:0x3C+8]
        if ident != b'BOOKMOBI':
            raise OSError('The specified file is not E-Book!')

    def make_sure_path_exists(self,path):
        try:
            os.makedirs(path)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise

    def save_file(self,  cover,directory,getcover,cloud, cover_size):
        if(self.mode=='reader'):
            #  need.cover means that directory system/thumbnails has been found on the Kindle (this is Kindle PW)
            if self.kindle.need_cover:
                if cover != '':
                    try:
                        ready_cover = Image.open(cover)
                        # ready_cover.thumbnail((217, 330), Image.ANTIALIAS)
                        if self.cover_size =='pw':
                                ready_cover = ready_cover.resize((217, 330), Image.ANTIALIAS)
                        else:
                                ready_cover = ready_cover.resize((330, 470), Image.ANTIALIAS)
                        ready_cover = ready_cover.convert('L')
                        self.txt2img(self.title, self.seqnumber, ready_cover, self.position)
                    except:
                        raise OSError('Failed to load custom cover!')
                else:
                    if getcover=='search': # search for cover
                        try:
                           ready_cover = self.get_cover_image()
                        except:
                            if(self.write_thumb):
                                #raise OSError('Failed to extract cover!')
                                try:
                                    if sys.frozen or sys.importers:
                                          butler_dir = os.path.dirname(sys.executable)
                                except AttributeError:
                                          butler_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
                                path_to_cover = butler_dir + "\\default_banner.jpeg"
                                ready_cover = Image.open(path_to_cover)
                                if self.cover_size =='pw':
                                       ready_cover = ready_cover.resize((217, 330), Image.ANTIALIAS)
                                else:
                                       ready_cover = ready_cover.resize((330, 470), Image.ANTIALIAS)
                                ready_cover = ready_cover.convert('L')
                                self.txt2defaultcover(self.title, self.author, self.seqnumber, ready_cover, self.position )
                    else: # extract cover
                        try:
                            # ready_cover = self.get_cover_image()
                            extractcover_34.extractThumbnail(self.path, "tmpdir.$$$");
                            shutil.rmtree("tmpdir.$$$")
                            coverfile = 'images.$$$' + '\\' + self.infilename +'.cover' + '.jpeg'
                            ready_cover = Image.open(coverfile)
                            ready_cover = ready_cover.resize((217, 330), Image.ANTIALIAS)
                            ready_cover = ready_cover.convert('L')
                            self.txt2img(self.title, self.seqnumber, ready_cover, self.position)
                            shutil.rmtree("images.$$$")
                        except:
                            if(self.write_thumb):
                                #shutil.rmtree("images.$$$")
                                #raise OSError('Failed to extract cover!')
                                try:
                                    if sys.frozen or sys.importers:
                                          butler_dir = os.path.dirname(sys.executable)
                                except AttributeError:
                                          butler_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
                                path_to_cover = butler_dir + "\\default_banner.jpeg"
                                ready_cover = Image.open(path_to_cover)
                                if self.cover_size =='pw':
                                       ready_cover = ready_cover.resize((217, 330), Image.ANTIALIAS)
                                else:
                                       ready_cover = ready_cover.resize((330, 470), Image.ANTIALIAS)
                                ready_cover = ready_cover.convert('L')
                                self.txt2defaultcover(self.title, self.author, self.seqnumber, ready_cover, self.position)
                if self.kindle.ssh:
                    tmp_cover = os.path.join(gettempdir(), 'KindleButlerCover')
                    ready_cover.save(tmp_cover, 'JPEG')
                    ssh = Popen('"' + self.config['SSH']['PSCPPath'] + '" "' + tmp_cover + '" root@' + self.kindle.path +
                                ':/mnt/us/system/thumbnails/thumbnail_' + self.asin + '_EBOK_portrait.jpg',
                                stdout=PIPE, stderr=STDOUT, shell=True)
                    ssh_check = ssh.wait()
                    if ssh_check != 0:
                        raise OSError('Failed to upload cover!')
                    os.remove(tmp_cover)
                else:
                    if(self.write_thumb):
                        if(cloud=='no'):
                            ready_cover.save(os.path.join(self.kindle.path, 'system',
                                                  'thumbnails', 'thumbnail_' + self.asin + '_EBOK_portrait.jpg'), 'JPEG')
                        else:
                            # get ASIN from file
                            section = KindleUnpack.Sectionizer(self.path)
                            mhlst = [KindleUnpack.MobiHeader(section, 0)]
                            mh = mhlst[0]
                            metadata = mh.getmetadata()
                            assa = metadata.get('ASIN')
                            assassin = assa[0].decode("utf-8")
                            if assassin==None:
                                assassin='None'
                            ready_cover.save(os.path.join(self.kindle.path, 'system',
                                                  'thumbnails', 'thumbnail_' +  assassin + '_PDOC_portrait.jpg'), 'JPEG')

        # for all modes prepare processed file
        try:
            # noinspection PyArgumentList
            ready_file = DualMetaFix.DualMobiMetaFix(self.path, bytes(self.asin,'UTF-8'),cloud)
        except:
            raise OSError('E-Book modification failed!')
        ready_file, source_size = ready_file.getresult()

        # save processed file to reader
        if(self.mode=='reader'):
            if source_size < self.kindle.get_free_space():
                if self.kindle.ssh:
                    tmp_book = os.path.join(gettempdir(), os.path.basename(self.path))
                    open(tmp_book, 'wb').write(ready_file.getvalue())
                    ssh = Popen('"' + self.config['SSH']['PSCPPath'] + '" "' + tmp_book + '" root@' + self.kindle.path +
                                ':/mnt/us/documents/', stdout=PIPE, stderr=STDOUT, shell=True)
                    for line in ssh.stdout:
                        for inside_line in line.split(b'\r'):
                            if b'|' in inside_line:
                                inside_line = inside_line.decode('utf-8').split(' | ')[-1].rstrip()[:-1]
                                self.progressbar['value'] = int(inside_line)
                    ssh_check = ssh.wait()
                    os.remove(tmp_book)
                    if ssh_check != 0:
                        raise OSError('Failed to upload E-Book!')
                    Popen('"' + self.config['SSH']['PLinkPath'] + '" root@' + self.kindle.path +
                          ' "dbus-send --system /default com.lab126.powerd.resuming int32:1"',
                          stdout=PIPE, stderr=STDOUT, shell=True)
                else:
                    if cloud=='no':
                        saved = 0
                        if directory == None:
                            target = open(os.path.join(self.kindle.path, 'documents', os.path.basename(self.path)), 'wb')
                        else:
                            new_dir = self.kindle.path + 'documents' + '\\' + directory
                            self.make_sure_path_exists(new_dir)
                            target = open(new_dir + '\\' + os.path.basename(self.path), 'wb')
                            # target = open(os.path.join(self.kindle.path, 'documents' + '\\directory', os.path.basename(self.path)), 'wb')
                        while True:
                            chunk = ready_file.read(32768)
                            if not chunk:
                                break
                            target.write(chunk)
                            saved += len(chunk)
                            self.progressbar['value'] = int((saved/source_size)*100)
            else:
                raise OSError('Not enough space on target device!')

        # save cover and processed book to pc
        if(self.mode=='pc'):
            # prepare and save cover
            # if key -a asin then self.write_thumb=False and no need to save cover
            if cover != '': # means that cover was imported from external file
                try:
                    ready_cover = Image.open(cover)
                    if self.cover_size =='pw':
                             ready_cover = ready_cover.resize((217, 330), Image.ANTIALIAS)
                    else:
                             ready_cover = ready_cover.resize((330, 470), Image.ANTIALIAS)
                    ready_cover = ready_cover.convert('L')
                    self.txt2img(self.title, self.seqnumber, ready_cover, self.position)
                except:
                    raise OSError('Failed to load custom cover!')
            else: # search/extract cover from inside the book
                if(getcover=='search'): #search for cover
                    try:
                       ready_cover = self.get_cover_image()
                    except:
                        if(self.write_thumb):
                            #raise OSError('Failed to extract cover!')
                                self.no_cover = True
                                try:
                                    if sys.frozen or sys.importers:
                                          butler_dir = os.path.dirname(sys.executable)
                                except AttributeError:
                                          butler_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
                                path_to_cover = butler_dir + "\\default_banner.jpeg"
                                ready_cover = Image.open(path_to_cover)
                                if self.cover_size =='pw':
                                         ready_cover = ready_cover.resize((217, 330), Image.ANTIALIAS)
                                else:
                                         ready_cover = ready_cover.resize((330, 470), Image.ANTIALIAS)
                                ready_cover = ready_cover.convert('L')
                                self.txt2defaultcover(self.title, self.author, self.seqnumber, ready_cover, self.position)

                else: #extract the cover from the book
                    try:
                        # ready_cover = self.get_cover_image()
                        extractcover_34.extractThumbnail(self.path, "tmpdir.$$$");
                        shutil.rmtree("tmpdir.$$$")
                        coverfile = 'images.$$$' + '\\' + self.infilename +'.cover' + '.jpeg'
                        ready_cover = Image.open(coverfile)
                        if self.cover_size =='pw':
                                ready_cover = ready_cover.resize((217, 330), Image.ANTIALIAS)
                        else:
                                ready_cover = ready_cover.resize((330, 470), Image.ANTIALIAS)
                        ready_cover = ready_cover.convert('L')
                        self.txt2img(self.title, self.seqnumber, ready_cover, self.position)
                    except:
                        if(self.write_thumb):
                            # shutil.rmtree("images.$$$")
                            #raise OSError('Failed to extract cover!')
                                self.no_cover = True
                                try:
                                    if sys.frozen or sys.importers:
                                          butler_dir = os.path.dirname(sys.executable)
                                except AttributeError:
                                          butler_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
                                path_to_cover = butler_dir + "\\default_banner.jpeg"
                                ready_cover = Image.open(path_to_cover)
                                if self.cover_size =='pw':
                                         ready_cover = ready_cover.resize((217, 330), Image.ANTIALIAS)
                                else:
                                         ready_cover = ready_cover.resize((330, 470), Image.ANTIALIAS)
                                ready_cover = ready_cover.convert('L')
                                self.txt2defaultcover(self.title, self.author, self.seqnumber, ready_cover, self.position)
            if(self.write_thumb):
                if cloud=='no':
                     ready_cover.save('thumbnail_' + self.asin + '_EBOK_portrait.jpg', 'JPEG')
                else:
                    # get ASIN from file
                    section = KindleUnpack.Sectionizer(self.path)
                    mhlst = [KindleUnpack.MobiHeader(section, 0)]
                    mh = mhlst[0]
                    metadata = mh.getmetadata()
                    assa = metadata.get('ASIN')
                    assassin = assa[0].decode("utf-8")
                    if assassin==None:
                        assassin='None'
                    ready_cover.save('thumbnail_' + assassin + '_EBOK_portrait.jpg', 'JPEG')
                if getcover !='search' and cover == '' and self.no_cover == False:
                    shutil.rmtree("images.$$$")
                if cloud=='no':
                    #save processed file
                    saved = 0
                    # ready_file.seek(0)
                    target = open(self.infilename + '.processed' + self.infileext, 'wb')
                    while True:
                        chunk = ready_file.read(32768)
                        if not chunk:
                            break
                        target.write(chunk)
                        saved += len(chunk)
                        self.progressbar['value'] = int((saved/source_size)*100)


    def get_seqnumber(self,infilename, seqnumber):
        if seqnumber is None: return None
        result = seqnumber if seqnumber != 'auto' else infilename[0] + (infilename[1] if infilename[1].isdigit() else "")
        if not result.isdigit():
            print('Error: image text should be digits only')
            return None
        result = result[0:2]
        return result

    def get_booktitle(self):
        if self.title is None: return None
        title = self.title
        if self.title == 'auto':
            section = KindleUnpack.Sectionizer(self.path)
            mhlst = [KindleUnpack.MobiHeader(section, 0)]
            mh = mhlst[0]
            metadata = mh.getmetadata()
            title = mh.title.decode("utf-8")
        return title

    def get_booktitle2(self):
         section = KindleUnpack.Sectionizer(self.path)
         mhlst = [KindleUnpack.MobiHeader(section, 0)]
         mh = mhlst[0]
         metadata = mh.getmetadata()
         title = mh.title.decode("utf-8")
         return title


    def get_bookauthor(self):
        section = KindleUnpack.Sectionizer(self.path)
        mhlst = [KindleUnpack.MobiHeader(section, 0)]
        mh = mhlst[0]
        metadata = mh.getmetadata()
        author = mh.creator.decode("utf-8")
        return author


    def txt2defaultcover(self, title, author, seqnum, img, position):
        try:
            from PIL import Image, ImageDraw, ImageFont
            #font = 'PTC55F.ttf'
            font = 'FreeSansBold.ttf'

            font_size = 35 # sequence number font size
            try:
                if sys.frozen or sys.importers:
                   font_dir = os.path.dirname(sys.executable)
            except AttributeError:
                   font_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
            #prepare black/white text background
            width, height = img.size
            # number mask position
            xmask = 0.5*width
            ymask = 0.7* height
            haxis = font_size
            bgcolor = 'white'
            txtcolor = 'black'
            draw = ImageDraw.Draw(img)  # setup to draw on the main image
            fnt = ImageFont.truetype(os.path.join(font_dir, font), font_size)
            if seqnum is not None:
                #
                #draw sequence number
                #
                #draw number background
                draw.ellipse((xmask - haxis, ymask - haxis, xmask + haxis, ymask + haxis), fill=bgcolor)
                #draw number
                textwidth, textheight = fnt.getsize(seqnum)
                draw.text((xmask - 0.5 * textwidth, ymask - 0.85 * textheight), seqnum, font=fnt, fill=txtcolor)

            # draw author

            fonta = 'FreeSansBoldOblique.ttf'
#            fonta = 'CharisSILModifiedLarger-BI.ttf'
            font_size2 = 25# title & author font size
            fnta = ImageFont.truetype(os.path.join(font_dir, fonta), font_size2)
            text2 = author
            titlelength = 14
            textwidth2, textheight2 = fnta.getsize(text2)
            offset =  textheight2
            margin =  textheight2
            for line in textwrap.wrap(text2, width=titlelength, break_long_words=True):
                linewidth, lineheight = fnta.getsize(line)
                margin = (width - linewidth)/2.0
                draw.text((margin, offset), line, font=fnta, fill=txtcolor)
                offset += fnta.getsize(line)[1]
            offset += textheight2
            # draw title

            fontt = 'FreeSansBold.ttf'
#            fontt = 'CharisSILModifiedLarger-B.ttf'
            fntt = ImageFont.truetype(os.path.join(font_dir, fontt), font_size2)
            text2 = title
            margin =  textheight2

            for line in textwrap.wrap(text2, width=titlelength, break_long_words=True):
                linewidth, lineheight = fntt.getsize(line)
                margin = (width - linewidth)/2.0
                draw.text((margin, offset), line, font=fntt, fill=txtcolor)
                offset += fntt.getsize(line)[1]


            del draw
        except  ImportError as e:
             print ("Error:", e)
             print ("Warning: Pillow is not installed - image text not drawn")




    def txt2img(self,title, seqnum, img, position):
        try:
            from PIL import Image, ImageDraw, ImageFont
            # img = Image.open(img_in)
            #prepare font
            #font = 'PTC55F.ttf'
            font = 'CharisSILModifiedLarger-B.ttf'
            #font = 'ARIALBD.TTF'
            font_size = 35
            try:
                if sys.frozen or sys.importers:
                   font_dir = os.path.dirname(sys.executable)
            except AttributeError:
                   font_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
            #prepare black/white text background
            width, height = img.size
            # mask position
            xmask = 1.10 * font_size
            if position=="bottom":
                ymask = height - 1.10 * font_size
            else:
                ymask = 1.10 * font_size
            haxis = font_size
            #
            #Select colors
            #
            #bgcolor = 'white'
            #txtcolor = 'black'
            bgcolor = 'black'
            txtcolor = 'white'
            draw = ImageDraw.Draw(img)  # setup to draw on the main image
            fnt = ImageFont.truetype(os.path.join(font_dir, font), font_size)
            if seqnum is not None:
                #
                #draw sequence number
                #
                #draw number background
                draw.ellipse((xmask - haxis, ymask - haxis, xmask + haxis, ymask + haxis), fill=bgcolor)
                #draw number
                textwidth, textheight = fnt.getsize(seqnum)
                draw.text((xmask - 0.5 * textwidth, ymask - 0.7 * textheight), seqnum, font=fnt, fill=txtcolor)

            if title is not None:
                # this is to calculate vertical position of text bg based on text parameter in general used
                # for a sequence number (only textheight needed)
                fake_text = 'fake'
                # parameters of title text
                textwidth, textheight = fnt.getsize(fake_text)
                font_size2 = 15
                fnt2 = ImageFont.truetype(os.path.join(font_dir, font), font_size2)
                text2 = title.upper()
                if seqnum is not None:
                    if self.cover_size == "pw":
                        draw.line((xmask + 0.5*haxis, ymask, xmask + haxis + 0.7 * width, ymask),fill=bgcolor,width=int(1.4*haxis))
                        titlelength = 12
                    else:
                        draw.line((xmask + 0.5*haxis, ymask, xmask +1.6* haxis + 0.7 * width, ymask),fill=bgcolor,width=int(1.4*haxis))
                        titlelength = 22
                    margin = xmask + haxis
                else:
                    draw.line(( 0, ymask, width, ymask),fill=bgcolor,width=int(1.4*haxis))
                    margin = 0.5*fnt2.getsize(text2)[1]
                    if self.cover_size == "pw":
                        titlelength = 18
                    else:
                        titlelength = 28
                textwidth2, textheight2 = fnt2.getsize(text2)
                offset = ymask - 1.1*textheight2 if len(text2)<=20 else ymask - 0.7*textheight
                #
                #No wrap drawing
                #
                splits=[text2[x:x+titlelength] for x in range(0,len(text2),titlelength)]
                ystep = 1.1*fnt2.getsize(text2)[1]
                for i in range (len(splits) if len(splits)<3 else 3):
                    line = splits[i]
                    draw.text((margin, offset), line, font=fnt2, fill=txtcolor)
                    offset += ystep
                #
                # This is wrapping alternative
                #
                #for line in textwrap.wrap(text2, width=titlelength):
                #    draw.text((margin, offset), line, font=fnt2, fill=txtcolor)
                #    offset += fnt2.getsize(line)[1]

            del draw
        except ImportError as e:
            print ("Error:", e)
            print ("Warning: Pillow is not installed - image text not drawn")



    def get_cover_image(self):
        section = KindleUnpack.Sectionizer(self.path)
        mhlst = [KindleUnpack.MobiHeader(section, 0)]
        mh = mhlst[0]
        metadata = mh.getmetadata()
        coverid = int(metadata['CoverOffset'][0])
        beg = mh.firstresource
        end = section.num_sections
        imgnames = []
        for i in range(beg, end):
            data = section.load_section(i)
            tmptype = data[0:4]
            if tmptype in ["FLIS", "FCIS", "FDST", "DATP"]:
                imgnames.append(None)
                continue
            elif tmptype == "SRCS":
                imgnames.append(None)
                continue
            elif tmptype == "CMET":
                imgnames.append(None)
                continue
            elif tmptype == "FONT":
                imgnames.append(None)
                continue
            elif tmptype == "RESC":
                imgnames.append(None)
                continue
            if data == chr(0xe9) + chr(0x8e) + "\r\n":
                imgnames.append(None)
                continue
            imgtype = what(None, data)
            if imgtype is None and data[0:2] == b'\xFF\xD8':
                last = len(data)
                while data[last-1:last] == b'\x00':
                    last -= 1
                if data[last-2:last] == b'\xFF\xD9':
                    imgtype = "jpeg"
            if imgtype is None:
                imgnames.append(None)
            else:
                imgnames.append(i)
            if len(imgnames)-1 == coverid:
                cover = Image.open(BytesIO(data))
                if self.cover_size=='pw':
                    cover = cover.resize((217,330), Image.ANTIALIAS)
                else:
                    cover = cover.resize((330,470), Image.ANTIALIAS)
                cover = cover.convert('L')
                self.txt2img(self.title, self.seqnumber, cover, self.position)
                return cover
        raise OSError
