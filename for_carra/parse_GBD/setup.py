# -*- coding: utf-8 -*-

from distutils.core import setup
from Cython.Build import cythonize

setup(
    name='Parse GBD'
    , version='1.0'
    , description='Gets the Google Patent Bulk Download xml files ready for CARRA PIKing'
    , long_description="""
    This takes the Google Bulk Download patent data and gets it into the form
    CARRA needs to attach a PIK to each inventor.
    """
    , author='David W Dreisigmeyer'
    , author_email='david.wayne.dreisigmeyer@census.gov'
    , ext_modules=cythonize("parse_GBD/xmlParser.pyx")
    , platforms=['RHEL 6']
    , data_files=[('xml', ['ASCII_zip3_cities.xml'
        , 'cityMisspellings.xml'
        , 'inventors.xml'])]
)
