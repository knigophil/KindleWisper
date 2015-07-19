from distutils.core import setup
import py2exe
import sys
import os

base_dir = os.path.abspath(os.path.dirname(sys.argv[0]))
sys.argv.append('py2exe')

try:
    shutil.rmtree(os.path.join(base_dir, 'build'))
except:
    pass
try:
    shutil.rmtree(os.path.join(base_dir, 'dist'))
except:
    pass
additional_files = [('', ['CharisSILModifiedLarger-B.ttf'])]


includes = []

dll_excludes = [
    'w9xpopen.exe'
]

excludes = [
    'pywin', 
    'pywin.debugger', 
    'pywin.debugger.dbgcon',
    'pywin.dialogs', 
    'pywin.dialogs.list', 
    'Tkconstants',
    'Tkinter',
    'tcl'
]

setup(
    options = {
        'py2exe': {
            'compressed': 1,
            'optimize': 2,
            'bundle_files': 1,
            'includes': includes,
            'excludes': excludes,
            'dll_excludes': dll_excludes
        }
    },
    console=['wispernetprep.py'],
    data_files=additional_files,
    zipfile=None
)

