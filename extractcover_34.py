import sys, os, glob
import mobiunpack32_34
import shutil

def extractThumbnail(infile, tmpdir):
    files = mobiunpack32_34.fileNames(infile, tmpdir)
    
    # Instantiate the mobiUnpack class    
    mu = mobiunpack32_34.mobiUnpack(files)
    metadata = mu.getMetaData()
    proc = mobiunpack32_34.processHTML(files, metadata)
    imgnames = proc.processImages(mu.firstimg, mu.sect)
    imgdir = os.path.join(tmpdir, "images")
    destdir = "images.$$$"
    os.mkdir(destdir)
    imageName = None
    if 'ThumbOffset' in metadata:
        imageNumber = int(metadata['ThumbOffset'][0])
        imageName = imgnames[imageNumber]
        if imageName is None:
            print ("Error: Cover Thumbnail image %s was not recognized as a valid image" % imageNumber)
        else:
            print ('Cover ThumbNail Image "%s"' % imageName)
            copyCover(destdir, infile, os.path.join(imgdir, imageName), ".thumbnail")
    if 'CoverOffset' in metadata:
        imageNumber = int(metadata['CoverOffset'][0])
        imageName = imgnames[imageNumber]
        if imageName is None:
            print ("Error: Cover image %s was not recognized as a valid image" % imageNumber)
        else:
            print ('Cover Image "%s"' % imageName)
            copyCover(destdir, infile, os.path.join(imgdir, imageName), ".cover")
    if imageName is None:
        print ('Neither Cover nor ThumbNail found')
        imgpath = max(glob.glob(os.path.join(imgdir, "*")), key=os.path.getsize)
        if os.path.splitext(os.path.split(imgpath)[1])[1]=='.jpeg':
            print ('Fake Cover Image "%s"' % os.path.split(imgpath)[1])
            copyCover(destdir, infile, imgpath, ".cover")
        else:
            print ('No candidate for cover image found. Execution interrupted.')
            shutil.rmtree(tmpdir)
            shutil.rmtree(destdir)
            sys.exit(0)

def copyCover(destdir, infile, imgpath, suffix):
    infileName = os.path.splitext(infile)[0]
    imageExt = os.path.splitext(imgpath)[1]
    shutil.copy(imgpath, os.path.join(destdir, infileName + suffix+imageExt))

def processFile(infile):
    infileext = os.path.splitext(infile)[1].upper()
    if infileext not in ['.MOBI', '.PRC', '.AZW', '.AZW4', '.AZW3']:
        print ("Error: first parameter must be a Kindle/Mobipocket ebook or a Kindle/Print Replica ebook.")
        return 1

    try:
        print ('Extracting...')
        extractThumbnail(infile, "tmpdir.$$$");
        shutil.rmtree("tmpdir.$$$")
        print ('Completed')
        
    except ValueError as e:
        print ("Error: %s" % e)
        return 1
    return 0

def main(argv=sys.argv):
    if len(argv) != 2:
        print ("Usage:")
        print ("  extractcover.py infile")
        return 1
    else:  
        return processFile(argv[1])

if __name__ == "__main__":
    sys.exit(main())
