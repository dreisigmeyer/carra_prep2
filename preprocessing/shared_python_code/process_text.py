import html
import re
import urllib

dateFormat = '%Y%m%d'  # The dates are expected in %Y%m%d format
grant_year_re = grant_year_re = re.compile('i?pgb([0-9]{4})')
pat_num_re = re.compile(r'([A-Z]*)0*([0-9]+)')


def clean_patnum(patnum):
    '''
    Removes extraneous zero padding
    '''
    pat_num = patnum.strip().upper()
    hold_pat_num = pat_num_re.match(pat_num).groups()
    pat_num_len = len(hold_pat_num[0] + hold_pat_num[1])
    zero_padding = '0' * (7 - pat_num_len)
    pat_num = hold_pat_num[0] + zero_padding + hold_pat_num[1]
    zero_padding = '0' * (8 - pat_num_len)
    xml_pat_num = hold_pat_num[0] + zero_padding + hold_pat_num[1]
    return xml_pat_num, pat_num


def standardize_name(in_str):
    '''
    This cleans and standardizes strings, removing HTML and URL encodings.
    It keeps any UTF8 chracters and numbers and replaces all whitespace
    with a single space.  The returned string is not necessarily ASCII.
    '''
    in_str = urllib.parse.unquote_plus(in_str)  # replace %xx
    in_str = html.unescape(in_str)  # replace HTML entities
    in_str = ' '.join(in_str.split())  # single spaces only
    in_str = ''.join(c for c in in_str if c.isalnum() or c == ' ')  # alphanumeric and spaces only
    in_str = in_str.upper()  # all upper case
    return in_str.strip()  # no leading or trailing whitespace


def standardize_name_late_of(in_str):
    '''
    '''
    in_str = standardize_name(in_str)
    in_str = re.sub('\s*LATE\s*OF\s*', '', in_str)  # deceased inventors
    return in_str.strip()


def clean_up_inventor_name(applicant, xml_path):
    '''
    '''
    applicant_text = applicant.find(xml_path).text
    applicant_text = standardize_name_late_of(applicant_text)
    return applicant_text.strip()


def standardize_name_cdp(in_str):
    '''
    '''
    in_str = standardize_name(in_str)
    in_str = re.sub('\s*Census\s*Designated\s*Place\s*', '', in_str)
    return in_str.strip()


def split_first_name(in_name):
    '''
    Get middle name out of first name
    '''
    holder = in_name.split(' ', 1)
    if len(holder) > 1:
        return holder[0], holder[1]
    else:
        return in_name, ''


def split_name_suffix(in_name):
    '''
    Takes the suffix off the last name
    '''
    # These are the generational suffixes.
    suffix_list = [
        'SR', 'SENIOR', 'I', 'FIRST', '1ST',
        'JR', 'JUNIOR', 'II', 'SECOND', '2ND',
        'THIRD', 'III', '3RD',
        'FOURTH', 'IV', '4TH',
        'FIFTH', 'V', '5TH',
        'SIXTH', 'VI', '6TH',
        'SEVENTH', 'VII', '7TH',
        'EIGHTH', 'VIII', '8TH',
        'NINTH' 'IX', '9TH',
        'TENTH', 'X', '10TH'
    ]
    holder = in_name.rsplit(' ', 2)
    if len(holder) == 1:  # includes empty string
        return in_name, ''
    elif len(holder) == 2:
        if holder[1] in suffix_list:
            return holder[0], holder[1]
        else:
            return in_name, ''
    elif holder[2] in suffix_list:
        if holder[1] == 'THE':
            return holder[0], holder[2]
        else:
            last_nm = holder[0] + ' ' + holder[1]
            return last_nm, holder[2]
    else:
        return in_name, ''
