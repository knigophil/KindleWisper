# -*- coding: utf-8 -*-
"""Transliterate Unicode text into plain 7-bit ASCII.

Example usage:
>>> from unidecode import unidecode:
>>> unidecode(u"\u5317\u4EB0")
"Bei Jing "

The transliteration uses a straightforward map, and doesn't have alternatives
for the same character based on language, position, or anything else.

In Python 3, a standard string object will be returned. If you need bytes, use:
>>> unidecode("Κνωσός").encode("ascii")
b'Knosos'
"""
import warnings
from sys import version_info
import x000
import x001
import x002
import x003
import x004
import x005
import x006
import x007
import x009
import x00a
import x00b
import x00c
import x00d
import x00e
import x00f
import x010
import x011
import x012
import x013
import x014
import x015
import x016
import x017
import x018
import x01d
import x01e
import x01f
import x020
import x021
import x022
import x023
import x024
import x025
import x026
import x027
import x028
import x029
import x02a
import x02c
import x02e
import x02f
import x030
import x031
import x032
import x033
import x04d
import x04e
import x04f
import x050
import x051
import x052
import x053
import x054
import x055
import x056
import x057
import x058
import x059
import x05a
import x05b
import x05c
import x05d
import x05e
import x05f
import x060
import x061
import x062
import x063
import x064
import x065
import x066
import x067
import x068
import x069
import x06a
import x06b
import x06c
import x06d
import x06e
import x06f
import x070
import x071
import x072
import x073
import x074
import x075
import x076
import x077
import x078
import x079
import x07a
import x07b
import x07c
import x07d
import x07e
import x07f
import x080
import x081
import x082
import x083
import x084
import x085
import x086
import x087
import x088
import x089
import x08a
import x08b
import x08c
import x08d
import x08e
import x08f
import x090
import x091
import x092
import x093
import x094
import x095
import x096
import x097
import x098
import x099
import x09a
import x09b
import x09c
import x09d
import x09e
import x09f
import x0a0
import x0a1
import x0a2
import x0a3
import x0a4
import x0ac
import x0ad
import x0ae
import x0af
import x0b0
import x0b1
import x0b2
import x0b3
import x0b4
import x0b5
import x0b6
import x0b7
import x0b8
import x0b9
import x0ba
import x0bb
import x0bc
import x0bd
import x0be
import x0bf
import x0c0
import x0c1
import x0c2
import x0c3
import x0c4
import x0c5
import x0c6
import x0c7
import x0c8
import x0c9
import x0ca
import x0cb
import x0cc
import x0cd
import x0ce
import x0cf
import x0d0
import x0d1
import x0d2
import x0d3
import x0d4
import x0d5
import x0d6
import x0d7
import x0f9
import x0fa
import x0fb
import x0fc
import x0fd
import x0fe
import x0ff
import x1d4
import x1d5
import x1d6
import x1d7



Cache = {}

def unidecode(string):
    """Transliterate an Unicode object into an ASCII string

    >>> unidecode(u"\u5317\u4EB0")
    "Bei Jing "
    """

    if version_info[0] < 3 and not isinstance(string, unicode):
        warnings.warn(  "Argument %r is not an unicode object. "
                        "Passing an encoded string will likely have "
                        "unexpected results." % (type(string),),
			RuntimeWarning, 2)

    retval = []

    for char in string:
        codepoint = ord(char)

        if codepoint < 0x80: # Basic ASCII
            retval.append(str(char))
            continue
        
        if codepoint > 0xeffff:
            continue # Characters in Private Use Area and above are ignored

        section = codepoint >> 8   # Chop off the last two hex digits
        position = codepoint % 256 # Last two hex digits

        try:
            table = Cache[section]
        except KeyError:
            try:
                mod = __import__('unidecode.x%03x'%(section), [], [], ['data'])
            except ImportError:
                Cache[section] = None
                continue   # No match: ignore this character and carry on.

            Cache[section] = table = mod.data

        if table and len(table) > position:
            retval.append( table[position] )

    return ''.join(retval)
