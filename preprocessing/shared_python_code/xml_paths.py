from lxml import etree

magic_validator = etree.XMLParser(
    dtd_validation=False,
    resolve_entities=False,
    encoding='utf-8',
    recover=True)


def assg_xml_paths(grant_year):
    '''
    '''
    if grant_year >= 2005:
        prdn = "us-bibliographic-data-grant/publication-reference/document-id/doc-number"
        grant_date = "us-bibliographic-data-grant/publication-reference/document-id/date"
        app_date = "us-bibliographic-data-grant/application-reference/document-id/date"
        assg = "us-bibliographic-data-grant/assignees/"
        orgname = "addressbook/orgname"
        city = "addressbook/address/city"
        state = "addressbook/address/state"
        country = "addressbook/address/country"
        role = "addressbook/role"
    elif 2002 <= grant_year <= 2004:
        prdn = "SDOBI/B100/B110/DNUM/PDAT"
        grant_date = "SDOBI/B100/B140/DATE/PDAT"
        app_date = "SDOBI/B200/B220/DATE/PDAT"
        assg = "SDOBI/B700/B730"
        orgname = "./B731/PARTY-US/NAM/ONM/STEXT/PDAT"
        city = "./B731/PARTY-US/ADR/CITY/PDAT"
        state = "./B731/PARTY-US/ADR/STATE/PDAT"
        country = "./B731/PARTY-US/ADR/CTRY/PDAT"
        role = "./B732US/PDAT"
    elif grant_year <= 2001:
        prdn = "WKU"
        grant_date = ""  # just use grant_year_GBD
        app_date = "APD"
        assg = 'assignees/'
        orgname = "NAM"
        city = "CTY"
        state = "STA"
        country = "CNT"
        role = "COD"
    else:
        raise UserWarning("Incorrect grant year: " + str(grant_year))
    return prdn, grant_date, app_date, assg, orgname, city, state, country, role


def inv_xml_paths(grant_year):
    '''
    '''
    prdn, _, appl_date, assg, _, _, _, _, _ = assg_xml_paths(grant_year)
    inv_alt1 = ''
    inv_alt2 = ''
    if grant_year >= 2005:
        app_alt1 = 'us-bibliographic-data-grant/parties/applicants/'
        app_alt2 = 'us-bibliographic-data-grant/us-parties/us-applicants/'
        inv_alt1 = 'us-bibliographic-data-grant/parties/inventors/'
        inv_alt2 = 'us-bibliographic-data-grant/us-parties/inventors/'
    elif 2002 <= grant_year <= 2004:
        app_alt1 = 'SDOBI/B700/B720'
        app_alt2 = ''
    elif 1976 <= grant_year <= 2001:
        app_alt1 = 'inventors'
        app_alt2 = ''
    else:
        raise UserWarning('Incorrect grant year: ' + str(grant_year))
    return prdn, appl_date, app_alt1, app_alt2, inv_alt1, inv_alt2, assg


def inv_rel_xml_paths(grant_year):
    '''
    '''
    _, _, _, _, _, _, assg_state, _, _ = assg_xml_paths(grant_year)
    if grant_year >= 2005:
        app_ln = 'addressbook/last-name'
        app_fn = 'addressbook/first-name'
        app_city = 'addressbook/address/city'
        app_state = 'addressbook/address/state'
    elif 2002 <= grant_year <= 2004:
        app_ln = './B721/PARTY-US/NAM/SNM/STEXT/PDAT'
        app_fn = './B721/PARTY-US/NAM/FNM/PDAT'
        app_city = './B721/PARTY-US/ADR/CITY/PDAT'
        app_state = './B721/PARTY-US/ADR/STATE/PDAT'
    elif 1976 <= grant_year <= 2001:
        app_ln = 'LN'
        app_fn = 'FN'
        app_city = 'CTY'
        app_state = 'STA'
    else:
        raise UserWarning('Incorrect grant year: ' + str(grant_year))
    return app_ln, app_fn, app_city, app_state, assg_state


def metadata_xml_paths(grant_year):
    '''
    '''
    _, grant_date, _, _, _, _, _, _, _ = assg_xml_paths(grant_year)
    _, _, _, app_state, _ = inv_rel_xml_paths(grant_year)
    prdn, app_date, app_alt1, app_alt2, inv_alt1, inv_alt2, assg = inv_xml_paths(grant_year)
    return prdn, grant_date, app_date, app_alt1, app_alt2, inv_alt1, inv_alt2, assg, app_state
