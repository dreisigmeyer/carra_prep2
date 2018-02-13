# -*- coding: utf-8 -*-

"""
"""

from lxml import etree
import codecs, os, re

file_dir = os.path.dirname(os.path.relpath(__file__))
os.chdir(file_dir)

synonyms = {}
syn_file = open('../userData/abbreviations.csv', 'r')
for line in syn_file:
    key_and_val = line.split(",")
    (key, val) = key_and_val[0].strip(), key_and_val[1].strip()
    synonyms[key] = val
syn_file.close()

def contains(context, hay, needle):
    haystack = hay[0]
    search_str = '^{0} | {0}$| {0} '.format(needle)
    if re.search(search_str, haystack):
        return True
    else:
        return False
        
def replace(context, needle, replacement, hay):
    haystack = hay[0]
    begin_str = '^{0} '.format(needle)
    end_str = ' {0}$'.format(needle)
    middle_str = ' {0} '.format(needle)
    if re.search(begin_str, haystack):
        repl = '{0} '.format(replacement)
        return re.sub(begin_str, repl, haystack)
    elif re.search(end_str, haystack):
        repl = ' {0}'.format(replacement)
        return re.sub(end_str, repl, haystack)
    elif re.search(middle_str, haystack):
        repl = ' {0} '.format(replacement)
        return re.sub(middle_str, repl, haystack)
    
ns = etree.FunctionNamespace('http://xslt_regex.org/myFunctions')
ns['contains'] = contains
ns['replace'] = replace

# A find/replace
def xslt_regex(patternStr, replaceStr):
    
    xslt_str = '''
    <xsl:stylesheet version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:fun="http://xslt_regex.org/myFunctions"
    exclude-result-prefixes="fun">
    <xsl:output method="xml" indent="yes" encoding="UTF-8"/>
    
    <xsl:variable name="pattern" select="'{pattern}'"/>
    <xsl:variable name="replace" select="'{replacement}'"/>
    
    <xsl:template match="states">
        <states><xsl:text>&#xa;</xsl:text>
        <xsl:apply-templates select="state"/>
        </states>
    </xsl:template>

    <xsl:template match="state">
        <state>
        <xsl:attribute name="abbrev">
            <xsl:value-of select="@abbrev"/>
        </xsl:attribute>
        <xsl:text>&#xa;</xsl:text>
        <xsl:apply-templates select="zip3"/>
        </state><xsl:text>&#xa;</xsl:text>
    </xsl:template>

    <xsl:template match="zip3">
        <xsl:choose>
        <xsl:when test="fun:contains(@city, $pattern)">
            <zip3>
            <xsl:attribute name="city">
                <xsl:value-of select="fun:replace($pattern, $replace, @city)"/>
            </xsl:attribute>
            <xsl:value-of select="."/> 
            </zip3><xsl:text>&#xa;</xsl:text>
        </xsl:when>
        </xsl:choose>
    </xsl:template>

    </xsl:stylesheet>
    '''.format(
    pattern = patternStr,
    replacement = replaceStr)
    return etree.XSLT(etree.XML(xslt_str))

# Removes duplicate entries
simplify_xml = '''
<xsl:stylesheet version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:output method="xml" indent="yes" encoding="UTF-8"/>
    <xsl:key name="keyStateAbbrev" match="state" use="@abbrev"/>    
        
    <xsl:template match="states">
    <xsl:comment>
    This comment is just to guarantee that this file is saved as UTF-8.  
    Without this it was continuously saved as ASCII even though it has 
    UTF-8 characters in it.
    A UTF-8 character: Ñ
</xsl:comment>
    <states>
        <xsl:apply-templates select=
        "state[generate-id(.)=generate-id(key('keyStateAbbrev', @abbrev)[1])]"
        />
    </states>
    </xsl:template>
    
    <xsl:template match="state">
    <state abbrev="{@abbrev}">
        <xsl:variable name="varAbbrev" select="@abbrev"/>
        <xsl:for-each select="/states/state[@abbrev=$varAbbrev]/zip3">
        <xsl:apply-templates select="."/>
        </xsl:for-each>
    </state>
    </xsl:template>
    
    <xsl:template match="zip3">
    <zip3 city="{@city}">
        <xsl:value-of select="current()"/>
    </zip3>
    </xsl:template>
            
</xsl:stylesheet>
'''
xslt_simplify = etree.XSLT(etree.XML(simplify_xml))

# Removes empty state nodes
clean_xml = '''
<xsl:stylesheet version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:output method="xml" indent="yes" encoding="UTF-8"/>
    
    <xsl:template match="states">
    <states>
        <xsl:for-each select="state">
        <xsl:if test="./*">
            <xsl:copy-of select="."/>
        </xsl:if>
        </xsl:for-each>
    </states>
    </xsl:template>
            
</xsl:stylesheet>
'''
remove_nodes = etree.XSLT(etree.XML(clean_xml))

encoding = 'utf-8'
xml_file = 'hold_zip3_cities.xml'
root = etree.parse(xml_file).getroot()
for k, v in synonyms.iteritems():
    
    xslt = xslt_regex(k, v)
    holder = root.getroottree()
    to_clean = xslt(holder)
    cleaned_xml = remove_nodes(to_clean)
    root.extend(cleaned_xml.getroot())
    
    xslt = xslt_regex(v, k)
    holder = root.getroottree()
    to_clean = xslt(holder)
    cleaned_xml = remove_nodes(to_clean)
    root.extend(cleaned_xml.getroot())

simplified_doc = xslt_simplify(root.getroottree())
out_file = codecs.open("zip3_cities.xml", "w")
simplified_doc.write(out_file
                    , xml_declaration=True
                    , pretty_print=True
                    , encoding='UTF-8'
                    )
