# KindleWisper

Sending Kindle books and optionally stamped covers to device via USB (based on **KindleButler version 0.1**).
If cover is missing from the book KindleWisper creates default cover and stamps it with 
author(s) name(s) and book title.

# Windows exe

Available [here](https://github.com/knigophil/KindleWisper/releases)


#Dependencies

    * Python 3.X
    * [Pillow](http://pypi.python.org/pypi/Pillow)
    * [Psutil](https://pypi.python.org/pypi/psutil)
    
#How to run:

    kindlewisper.cmd [--input-file]<INPUT_FILE> [keys]
     or
    kindlewisper.exe [--input-file]<INPUT_FILE> [keys]

    Optional keys:
	-h, --help 
    INPUT_FILE, --input-file INPUT_FILE 
        Input file 
    -s SEQUENCE_NUMBER, --sequence-number SEQUENCE_NUMBER 
        A one- or two-digit number to stamp on the cover ("auto" for first one-two numeric characters of the file name) 
    -t TITLE, --title TITLE 
        A text to stamp on the cover ("auto" for the title from the metainfo of the book) 
    -a ASIN, --asin ASIN 
        A text to put into ASIN metainfo field 
    -p {top, bottom}, --position {top, bottom} 
        Position of the stamp 
    -m {pc, reader} --mode[pc, reader] 
        Copy book either to PC or to e-reader 
    -d DIRECTORY,--directory DIRECTORY 
        Places book to Kindle Documents subdirectory 
    -e {search, extract}, --getcover {search, extract} 
        Method to obtain cover: Search or Extract 
    -c 
        Window opens to select external cover 
    -cl {yes, no}, --cloud {yes, no} 
        Process (add cover) to book on Kindle downloaded from cloud? yes or no

#COPYRIGHT

Copyright (c )2015 KindleWisper is released under GNU General Public License. See LICENSE.txt for further details.
This script includes and uses code from initial release of [KindleButler version 0.1](https://github.com/AcidWeb/KindleButler) by Pawel Jastrzebski.  
