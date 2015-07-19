"""
Usage (Windows):
    python setup.py py2exe
"""
from sys import platform

NAME = "kindlewisper"
VERSION = "2.0.0"
MAIN = "kindlewisper.py"

if platform == "win32":
    # noinspection PyUnresolvedReferences
    import py2exe
    from distutils.core import setup
    additional_files = [('', ['LICENSE.txt',
                              'KindleButler.ini'])]
    mydata = [('', ['CharisSILModifiedLarger-B.ttf','FreeSansBold.ttf', 'FreeSansBoldOblique.ttf', 'default_banner.jpeg' ])]

    extra_options = dict(
        options={'py2exe': {"bundle_files": 2,
                            "dist_dir": "dist",
                            "compressed": True,
                            "optimize": 2}},
        windows=[{"script": "kindlewisper.py",
                  "dest_base": "kindlewisper",
                  "version": VERSION,
                  "copyright": "Pawel Jastrzebski 2014",
                  "legal_copyright": "GNU General Public License (GPL-3)",
                  "product_version": VERSION,
                  "product_name": "kindlewisper",
                  "file_description": "kindlewisper",
                  "icon_resources": [(1, "Assets\KindleButler.ico")]}],
        #zipfile='lib/library.zip',
        zipfile=None,
        data_files=mydata)
else:
    print('This script create only Windows releases.')
    exit()

#noinspection PyUnboundLocalVariable
setup(
    name=NAME,
    version=VERSION,
    author="Pawel Jastrzebski",
    author_email="pawelj@iosphe.re",
    description="kindlewisper",
    license="GNU General Public License (GPL-3)",
    url="https://github.com/AcidWeb/KindleButler/",
    **extra_options
)