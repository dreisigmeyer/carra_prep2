import re
import unicodedata

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


# def keep_letters(x):
#     '''
#     Only keeps unicode letters and numbers along with the spaces.
#     '''
#     if unicodedata.category(x)[0] in ('L', 'N', 'Z'):  # alphanumeric
#         return x
#     else:  # crap
#         return u''


# def clean_it(in_str):
#     if isinstance(in_str, str):
#         encoded_str = in_str.decode('utf8')
#     else:
#         return ''
#     out_str = encoded_str
#     out_str = ''.join(keep_letters(x) for x in out_str)
#     out_str = out_str.upper()
#     out_str = ' '.join(out_str.split())
#     return out_str


# def clean_up(applicant, xml_path):
#     '''
#     Clean up the string
#     '''
#     applicant_text = applicant.find(xml_path).text
#     applicant_text = clean_it(applicant_text)
#     # Replace utf-8 characters with their closest ascii
#     applicant_text = unicodedata.normalize('NFKD', applicant_text)
#     applicant_text = applicant_text.encode('ascii', 'ignore')
#     applicant_text = re.sub('\s*LATE\s+OF\s*', '', applicant_text)
#     applicant_text = re.sub('[^a-zA-Z0-9 ]+', '', applicant_text).upper()
#     return applicant_text.strip()


def clean_up(applicant, xml_path):
    '''
    '''
    applicant_text = applicant.find(xml_path).text
    applicant_text = re.sub('[^a-zA-Z0-9 ]+', '', applicant_text)
    applicant_text = ' '.join(applicant_text.split())
    applicant_text = re.sub('\s*LATE\s+OF\s*', '', applicant_text)
    applicant_text = applicant_text.upper()
    return applicant_text.strip()


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
