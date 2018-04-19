#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Takes the Google Bulk Download patent data from pre-2002 patents
and converts it from the *.dat format into an XML format useable
by CARRA_201X/parse_GBD_201X/xmlParser.pyx.
"""

import codecs, glob, os, re, sys

#myre = re.compile(r'^([A-Z]*)([0-9]*)(.)([a-zA-Z]*)') # remove any trash at the end
#pat_num_re = re.compile(r'([A-Z]*)0*([0-9]+)')
def clean_patnum(patnum):
    """
    Removes extraneous zero padding
    """
    pat_num = patnum.strip().upper()
    # Anything after the first 8 digits must be a check digit.
    # It seems that all of the WKU for the pre-2002 patents are either 8 or 9.
    # characters long.  If they're 8 then the check digit seems to be missing.
    #pat_num = pat_num[:8] 
    #try: # removes any zero padding and rejoins the patent number
        #hold_pat_num = pat_num_re.match(pat_num).groups()
        #pat_num_len = len(hold_pat_num[0] + hold_pat_num[1])
        #zero_padding = '0' * (8 - pat_num_len)
        #xml_pat_num = hold_pat_num[0] + zero_padding + hold_pat_num[1]
    #except Exception:
        #pass
    #return xml_pat_num
    return pat_num[:8]
    
def clean_it(in_str):
    out_str = in_str.replace("&", "and")
    #out_str = re.sub('[^a-zA-Z0-9 ]+', '', out_str)
    return out_str.strip()

def convert_to_xml(in_file):
    """
    I know it is crap,
    It will only run one time.
    A nice haiku verse?
    """
    
    in_file_yr = in_file.split('/')[-1].split('.')[0]
    folder_path = 'abcd' + in_file_yr + '0101_wk00/' # fake name
    os.system('mkdir ' + folder_path)
    out_file_name = 'outData/abcd' + in_file_yr + '0101_wk00.xml' # fake name
    out_file = codecs.open(out_file_name, 'w', 'utf8')
    
    awk_cmd = "awk '/^PATN/{filename=NR\".dat\"; count=0;}; {count++; if (count > 1) print > \"" + folder_path + "\"filename}' "            
    os.system(awk_cmd + in_file)
    datSplit = glob.glob(folder_path + "*.dat")

    xml_line = '<?xml version="1.0" encoding="UTF-8"?>\n'
    for datFile in datSplit:
        # Some of the lines have a funcky encoding but it seems to be in the
        # references
        dat_file = codecs.open(datFile, 'r', encoding='utf8', errors='ignore')
        
        keyword = ''
        INVT_str = ''
        ASSG_str = ''
        WKU_str = ''
        APD_str = ''
        outer_line = ''
        while True:
        #for outer_line in dat_file:
            try:
                outer_line = dat_file.next()
            except StopIteration:
                break
            except Exception:
                print "Offending line is : " + dat_file.next()
                continue
            if outer_line.startswith(' '): # longer names etc are split across lines
                continue
            outer_line = clean_it(outer_line)
            try:
                outer_key, outer_val = map(unicode.strip, outer_line.split(' ', 1))
                if not keyword: # Only if in patent Bibliographic data
                    if outer_key == 'WKU':
                        #outer_val = myre.sub(r'\1\2\3', outer_val) # remove any trash at the end
                        #outer_val = outer_val[:-1] # trash character at end
                        outer_val = clean_patnum(outer_val)
                        WKU_str += '\t<WKU>' + outer_val + '</WKU>\n'
                        continue
                    if outer_key == 'APD':
                        APD_str += '\t<APD>' + outer_val + '</APD>\n'
                        continue
            except Exception: # This will be a keyword
                keyword = outer_line.strip()
                continue

            if keyword == 'INVT':
                keyword = ''
                INVT_str += '\t\t<INVT>\n'
                if outer_key == 'CTY':
                    INVT_str += '\t\t\t<CTY>' + outer_val + '</CTY>\n'
                elif outer_key == 'STA':
                    INVT_str += '\t\t\t<STA>' + outer_val + '</STA>\n'
                elif outer_key == 'CNT':
                    INVT_str += '\t\t\t<CNT>' + outer_val + '</CNT>\n'
                elif outer_key == 'NAM':
                    try:
                        ln, fn = map(unicode.strip, outer_val.split(';'))
                    except Exception:
                        INVT_str += '\t\t</INVT>\n'
                        continue # need to continue loop until we capture next keyword
                    INVT_str += '\t\t\t<LN>' + ln + '</LN>\n'
                    INVT_str += '\t\t\t<FN>' + fn + '</FN>\n'
                for inner_line in dat_file:
                    if inner_line.startswith(' '): # longer names etc are split across lines
                        continue
                    inner_line = clean_it(inner_line)
                    try:
                        inner_key, inner_val = map(unicode.strip, inner_line.split(' ', 1))
                    except Exception:# This should be a keyword
                        keyword = inner_line.strip()
                        break
                    if inner_key == 'CTY':
                        INVT_str += '\t\t\t<CTY>' + inner_val + '</CTY>\n'
                    elif inner_key == 'STA':
                        INVT_str += '\t\t\t<STA>' + inner_val + '</STA>\n'
                    elif inner_key == 'CNT':
                        INVT_str += '\t\t\t<CNT>' + inner_val + '</CNT>\n'
                    elif inner_key == 'NAM':
                        try:
                            ln, fn = map(unicode.strip, inner_val.split(';'))
                        except Exception:
                            continue # need to continue loop until we capture next keyword
                        INVT_str += '\t\t\t<LN>' + ln + '</LN>\n'
                        INVT_str += '\t\t\t<FN>' + fn + '</FN>\n'
                INVT_str += '\t\t</INVT>\n'
                continue # need to reset outer_key and outer_val
            if keyword == 'ASSG':
                keyword = ''
                ASSG_str += '\t\t<ASSG>\n'
                if outer_key == 'CTY':
                    ASSG_str += '\t\t\t<CTY>' + outer_val + '</CTY>\n'
                elif outer_key == 'STA':
                    ASSG_str += '\t\t\t<STA>' + outer_val + '</STA>\n'
                elif outer_key == 'CNT':
                    ASSG_str += '\t\t\t<CNT>' + outer_val + '</CNT>\n'
                elif outer_key == 'NAM':
                    ASSG_str += '\t\t\t<NAM>' + outer_val + '</NAM>\n'
                elif outer_key == 'COD':
                    ASSG_str += '\t\t\t<COD>' + outer_val + '</COD>\n'
                for inner_line in dat_file:
                    if inner_line.startswith(' '): # longer names etc are split across lines
                        continue
                    inner_line = clean_it(inner_line)
                    try:
                        inner_key, inner_val = map(unicode.strip, inner_line.split(' ', 1))
                    except Exception: # This should be a keyword
                        keyword = inner_line.strip()
                        break
                    if inner_key == 'CTY':
                        ASSG_str += '\t\t\t<CTY>' + inner_val + '</CTY>\n'
                    elif inner_key == 'STA':
                        ASSG_str += '\t\t\t<STA>' + inner_val + '</STA>\n'
                    elif inner_key == 'CNT':
                        ASSG_str += '\t\t\t<CNT>' + inner_val + '</CNT>\n'
                    elif inner_key == 'NAM':
                        ASSG_str += '\t\t\t<NAM>' + inner_val + '</NAM>\n'
                    elif inner_key == 'COD':
                        ASSG_str += '\t\t\t<COD>' + inner_val + '</COD>\n'
                ASSG_str += '\t\t</ASSG>\n'
                
        if INVT_str and ASSG_str and WKU_str and APD_str: # with assignee
            out_file.write(xml_line)
            out_file.write('<PATN>\n')
            out_file.write(WKU_str)
            out_file.write(APD_str)
            out_file.write('\t<INVTS>\n')
            out_file.write(INVT_str)
            out_file.write('\t</INVTS>\n')
            out_file.write('\t<ASSGS>\n')
            out_file.write(ASSG_str)
            out_file.write('\t</ASSGS>\n')
            out_file.write('</PATN>\n')
        elif INVT_str and WKU_str and APD_str: # self assigned
            out_file.write(xml_line)
            out_file.write('<PATN>\n')
            out_file.write(WKU_str)
            out_file.write(APD_str)
            out_file.write('\t<INVTS>\n')
            out_file.write(INVT_str)
            out_file.write('\t</INVTS>\n')
            out_file.write('</PATN>\n')
        
        dat_file.close()
        
    out_file.close()
    os.system('rm -rf ' + folder_path)

inDataFiles = glob.glob("./inData/*.dat")
for file_path in inDataFiles:
    convert_to_xml(file_path)
    
