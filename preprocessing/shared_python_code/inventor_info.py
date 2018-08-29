import re
from .process_text import clean_up_inventor_name
from .process_text import split_first_name
from .process_text import split_name_suffix
from .xml_paths import inv_rel_xml_paths


def get_inventor_info(applicant, grant_year):
    '''
    '''
    app_ln, app_fn, app_city, app_state, _ = inv_rel_xml_paths(grant_year)
    try:
        city = clean_up_inventor_name(applicant, app_city)
    except Exception:
        city = ''
    try:
        state = applicant.find(app_state).text
        state = re.sub('[^a-zA-Z]+', '', state).upper()
    except Exception:  # not a US inventor
        state = ''
    try:  # to get all of the applicant data
        try:  # For 2005 and later patents
            sequence_num = applicant.get('sequence')
        except Exception:  # For pre-2005 patents
            sequence_num = None
        last_name = clean_up_inventor_name(applicant, app_ln)
        last_name, suffix = split_name_suffix(last_name)
        first_name = clean_up_inventor_name(applicant, app_fn)
        first_name, middle_name = split_first_name(first_name)
    except Exception:  # something's wrong
        sequence_num, last_name, suffix, first_name, middle_name = '', '', '', '', ''
    return city, state, sequence_num, last_name, suffix, first_name, middle_name
