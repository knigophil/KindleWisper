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

__version__ = '0.1'
__license__ = 'GPL-3'
__copyright__ = '2014, Pawel Jastrzebski <pawelj@vulturis.eu>'

import os,inspect
import sys
import argparse
import configparser
from tkinter import Tk, ttk, filedialog
from threading import Thread
from KindleButler import Interface
from KindleButler import File


class KindleButlerGUI:
    def __init__(self):
        self.root, self.pbar, self.label = self.draw_gui()

    def draw_gui(self):
        main = Tk()
        main.title('KindleButler ' + __version__)
        main.resizable(0, 0)
        main.wm_attributes('-toolwindow', 1)
        x = (main.winfo_screenwidth() - main.winfo_reqwidth()) / 2
        y = (main.winfo_screenheight() - main.winfo_reqheight()) / 2
        main.geometry('+%d+%d' % (x, y))
        progressbar = ttk.Progressbar(orient='horizontal', length=200, mode='determinate')
        progressbar.grid(row=0)
        style = ttk.Style()
        style.configure('BW.TLabel', foreground='red')
        label = ttk.Label(style='BW.TLabel')
        return main, progressbar, label

    def load_file(self, source):
        fname = filedialog.askopenfilename(title='Select cover', initialdir=os.path.split(source)[0],
                                           filetypes=(('Image files', '*.jpg;*.jpeg;*.png;*.gif'),))
        return fname


class KindleButlerWorker:
    def __init__(self, input_file, cover, ui, config, sequence_number, title, asin, position, mode, directory, getcover, cloud, cover_size):
        try:
            # looks for Kindle PW and checks it out
            kindle = Interface.Kindle(config, mode)
            file = File.MOBIFile(input_file, kindle, config, ui.pbar,sequence_number,title,asin,position,mode,cloud,cover_size)
            file.save_file(cover,directory,getcover,cloud,cover_size)
            ui.root.quit()
            #
            #next line removes progress bar window on Windows 8.1
            #
            ui.root.withdraw()

        except OSError as e:
            ui.label.grid(row=1)
            ui.label['text'] = e


if __name__ == '__main__':
    if getattr(sys, 'frozen', False):
        class FakeSTD(object):
            def write(self, string):
                pass

            def flush(self):
                pass
        sys.stdout = FakeSTD()
        sys.stderr = FakeSTD()
    parser = argparse.ArgumentParser(description=u'Application for extration covers from mobi/azw3 books to Kindle Paperwhite')
    parser.add_argument('-c', '--cover', dest='custom_cover', action='store_true',help='Issue request for external cover')
    parser.add_argument('input_file', type=str, help='Input mobi/azw3 book' )
    parser.add_argument('-s', '--sequence-number', help='A number to stamp on the cover ("auto" for first one-two numeric characters of the name of the file)')
    parser.add_argument('-t', '--title', default=None, help='A text to stamp on the cover ("auto" for the title from the metainfo of the book)')
    parser.add_argument('-a', '--asin', help='A text to put into ASIN metainfo field')
    parser.add_argument('-p', '--position', choices=['top', 'bottom'], default='bottom', help='Position of the stamp')
    parser.add_argument('-m', '--mode', choices=['pc', 'reader'], default='reader', help='Mode of operation: Write files to PC/to Paperwhite')
    parser.add_argument('-d', '--directory',help='Kindle Documents subdirectory')
    parser.add_argument('-e', '--getcover', choices=['search', 'extract'], default='search', help='Method of obtaining cover: Search/Extract')
    parser.add_argument('-cl', '--cloud',choices=['yes', 'no'], default='no', help='Process book for cloud?')
    parser.add_argument('-cs', '--cover_size',choices=['pw', 'kv'], default='pw', help='Set cover size: Paperwhite/Voyage')
    args = parser.parse_args()
    configFile = configparser.ConfigParser()
    scriptdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    path_to_ini = scriptdir + '\\KindleButler.ini'
    configFile.read(path_to_ini)
    if args.input_file != '':
        gui = KindleButlerGUI()
        if args.custom_cover:
            cover_file = gui.load_file(args.input_file)
            if cover_file == '':
                exit(0)
        else:
            cover_file = ''
        Thread(target=KindleButlerWorker, args=(args.input_file, cover_file, gui, configFile,args.sequence_number,
                         args.title,args.asin,args.position,args.mode, args.directory, args.getcover, args.cloud,
                         args.cover_size)).start()
        gui.root.mainloop()
