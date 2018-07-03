#!/bin/bash

function clean_dtds {
    # The DTD files need to be modified for the modified XML files we deal with
    # The first one works for 2005-present (as of 2014)
    # The rest work for 2002-2004
    sed -i -r 's_(<!ELEMENT us-patent-grant.*>)_<!--\1-->\n<!ELEMENT us-patent-grant (us-bibliographic-data-grant , abstract*, sequence-list-doc?)>_' $1 
    sed -i -r 's_(<!ELEMENT PATDOC.*>)_<!--\1-->\n<!ELEMENT PATDOC (SDOBI,SDOAB?,SDODE,SDOCL*,SDODR?,SDOCR?)>_' $2
    sed -i -r 's_(FILE[ ]*ENTITY)[ ]*(#REQUIRED)(.*)_\1 #IMPLIED \3_g' $2
    sed -i -r 's_(<!ELEMENT CHEM-US.*>)_<!--\1-->\n<!ELEMENT CHEM-US \(CHEMCDX?,CHEMMOL?,EMI?\)>_' $2
    sed -i -r 's_(<!ELEMENT MATH-US.*>)_<!--\1-->\n<!ELEMENT MATH-US \(MATHEMATICA?,MATHML?,EMI?\)>_' $2
    sed -i -r 's_(<!ELEMENT BTEXT.*>)_<!--\1-->\n<!ELEMENT BTEXT \(H | PARA | CWU | IMG\)*>_' $2
}

./gbd_cleaner.pl
clean_dtds holdData/\*/\*.dtd holdData/\*/ST32-US-Grant-025xml.dtd
./xml_validator.py

HERE=`pwd`
for FILE in "$HERE"/holdData/*.zip; do
    FOLDER_PATH="$FILE/valid_well_formed_xml/"
    FILE_NAME=`basename $FILE`
    cd "$FOLDER_PATH"
    cp -r "$HERE"/DTDs/* "$FOLDER_PATH"
    clean_dtds ./\*.dtd ./ST32-US-Grant-025xml.dtd
    zip -q -r "$HERE/outData/$FILE_NAME" .
done

cd "$HERE"
rm -rf "$HERE"/holdData/*

cd outData
cp *.zip ../../CARRA_2014/inData
mv *.zip ../../patent_metadata/inData
cd ../inData
rm *.zip
cd ../