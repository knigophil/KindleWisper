import sys, os, inspect
import argparse
import unicodefix
from unidecode import unidecode

def draw(imgname, title, seqnum, position):
    if title==None:
        print "Drawing:", seqnum, "No title"
    else:
        try:
            print "Drawing:", seqnum, title
        except:
            print "Drawing:", seqnum, unidecode(title)
            pass
    txt2img(title, seqnum, imgname, imgname, position)

def resize(img_in):
    try:
        from PIL import Image
        img = Image.open(img_in)
        img = img.resize((250,400), Image.ANTIALIAS)
        img.save(img_in, "JPEG", quality=100)
    except ImportError as e:
        print "Error:", e
        print "Warning: Pillow is not installed - image not resized"

def txt2img(title, seqnum, img_in, img_out, position):
    try:
        from PIL import Image, ImageDraw, ImageFont
        img = Image.open(img_in)
        #prepare font
        font = 'CharisSILModifiedLarger-B.ttf'
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
            draw.text((xmask - 0.5 * textwidth, ymask - 0.5 * textheight), seqnum, font=fnt, fill=txtcolor)

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
                draw.line((xmask + 0.5*haxis, ymask, xmask + haxis + 0.7 * width, ymask),fill=bgcolor,width=int(1.4*haxis))
                margin = xmask + haxis
                titlelength = 15
            else:
                draw.line(( 0, ymask, width, ymask),fill=bgcolor,width=int(1.4*haxis))
                margin = 0.5*fnt2.getsize(text2)[1]
                titlelength = 20
            textwidth2, textheight2 = fnt2.getsize(text2)
            offset = ymask - 0.25*textheight2 if len(text2)<=20 else ymask - 0.6*textheight
            #
            #No wrap drawing
            #
            splits=[text2[x:x+titlelength] for x in range(0,len(text2),titlelength)]
            ystep = fnt2.getsize(text2)[1]
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

        img.save(img_out, "JPEG", quality=100)
        del draw
    except ImportError as e:
        print "Error:", e
        print "Warning: Pillow is not installed - image text not drawn"

def main(argv=sys.argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file', metavar='<input file>', help='Input file')
    parser.add_argument('-s', '--sequence-number',  nargs='?', help='A number to stamp on the cover')
    parser.add_argument('-t', '--title',  nargs='?', help='A text to stamp on the cover')

    args = parser.parse_args()
    print args

    resize(args.input_file)
    draw(args.input_file, args.title, args.sequence_number)


if __name__ == "__main__":
    sys.exit(main())
