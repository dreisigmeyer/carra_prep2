# -*- coding: utf-8 -*-

"""
Helper functions
"""

import unicodedata, urllib
from HTMLParser import HTMLParser

def keep_letters(x):
    """
    Only keeps unicode letters and numbers.
    """
    if unicodedata.category(x)[0] in ('L', 'N'):
        return x
    if x == u',':
        return x
    else:
        return u' '
    
def clean_it(in_str):
    """
    Removes any URL or HTML encoded characters, anything that isn't a unicode
    character or number and multiple whitespace.  Outputs as UTF-8.
    """    
    if isinstance(in_str, unicode): # make sure it's a str
        encoded_str = in_str.encode('utf8') 
    elif isinstance(in_str, str):
        encoded_str = in_str
    else:
        raise Exception("clean_it: Input string is not of type UTF-8 or str.")
        
    try: # replace %xx escapes  
        out_str = urllib.unquote(encoded_str).decode('utf8')
    except Exception:
        print "Encoding problems in clean_it : replace %xx escapes."
        return ""
        
    try: # replace &text;
        out_str = HTMLParser().unescape(out_str) 
    except Exception:
        print "Encoding problems in clean_it : replace &text;."
        return ""
        
    try: # filter
        out_str = ''.join(keep_letters(x) for x in out_str) 
    except Exception:
        print "Encoding problems in clean_it : keep_letters(x)."
        return ""
        
    try: # make it upper case
        out_str = out_str.upper() 
    except Exception:
        print "Encoding problems in clean_it : make it upper case."
        return ""
        
    try: # single spaces only
        out_str = ' '.join(out_str.split())     
    except Exception:
        print "Encoding problems in clean_it : single spaces only."
        return ""
        
    return out_str