import sys
import os
import argparse
import sqlite3
from collections import OrderedDict
import re
from bibConstants import *

#finds index of all iterations of a substring in a string
def find_all(a_str, sub):
    start = 0
    while True:
        start = a_str.find(sub, start)
        if start == -1: return
        yield start
        start += len(sub)

#loads file line by line into a list
def loadTextList(fileName):
    fileHandler = open(fileName, "rt")
    text = fileHandler.readlines()
    fileHandler.close()
    return text

#loads file into a chunk of text
def loadTextString(fileName):
    fileHandler = open(fileName, "rt")
    text = fileHandler.read()
    fileHandler.close()
    return text

#loads keys from file into list
def loadKeyList(fileName):
    fileHandler = open(fileName, "rt")
    text = fileHandler.readlines()
    fileHandler.close()
    keys = []
    for line in text:
        if (line != "\n"):
            if(line != text[len(text)-1]):
                keys.append(line[:-1])
            else:
                keys.append(line)
    return sorted(keys,key=str.lower)

##Puts bibtex file (as string) into an ordered dictionary of dictionaries where
##the key of outer dictionary is key of entry and maps to another dictionary of
##its fields and values in the order of the entries of the input
def bib2Dict(original):
    length = len(original)

    ##Check for non-ascii chars
    n = 1; text = ''
    for x in xrange(length):
        c = original[x]
        if (c=='\n'): n+=1
        try:
            c.decode('ascii')
            text = text+c
        except:
            return 'ASCII ENCODE ERROR at line '+str(n)

    text = text+" "

    text = text.encode('ascii','ignore')

    length = len(text)

    bibs = OrderedDict()
    i=0; c = text[0] ##Initial index and character
    n = 1 ##Line number
    if (c=='\n'): n+=1
    currField = ''; currKey = ''
    inEntry = False
    ##Reads the bibtex file character by character
    while (i<length-1):
        ##If the line is a comment, then ignore entire line
        if (c=="%"):
            while (c!='\n'):
                i+=1; c = text[i]
            n+=1
            ##Skipping '\n'
            i+=1; c = text[i]
        ##Beginning of new entry
        elif (c=="@"):
            if (inEntry==False):
                inEntry = True
            else:
                return ('\n\nINPUT FILE ERROR around line '+str(n)+\
                        '.\nERROR: Field entry braces mismatched.')
            i+=1; c = text[i]
            if (c=='\n'): n+=1
            entryType = ''
            while (c!='{'):
                ##Read in entry type until '{' is reached
                entryType = entryType+c.upper()
                i+=1; c = text[i]
                if (c=='\n'): n+=1
            ##Skipping '{'
            i+=1; c = text[i]
            while (c==' ' or c=='\t' or c=='\n'):
                ##Continue through blanks until BibTeX key is reached
                i+=1; c = text[i]
                if (c=='\n'): n+=1
            entryKey = ''
            while (c!=','):
                ##Read in entry key until ',' is reached
                entryKey = entryKey+c
                i+=1; c = text[i]
                if (c=='\n'): n+=1
            if (entryKey in bibs):
                return ('\n\nINPUT FILE ERROR at line '+str(n)+\
                        '.\nERROR: Multiple entries with '+\
                        'same BibTeX key.\n'+\
                        'The repeated key is '+entryKey+'.\n'+\
                        'Either rename the repeated key or '+\
                        'delete the extra entries.\n'+\
                        'No output will be created until '+\
                        'this is resolved.')
            i+=1; c = text[i] ##Skip ","
            if (c=='\n'): n+=1
            currKey = entryKey
            ##Initialize dictionary value for the entry key
            bibs[entryKey] = {'ENTRYTYPE':entryType}
        elif ((c.isalpha() or c.isdigit()) and inEntry==True): ##New field
            ##Fields
            field = ''
            ##Read in field name
            while (c!=' ' and c!='=' and c!='\t' and c!='\n'):
                field = field+c.upper()
                i+=1; c = text[i]
                if (c=='\n'): n+=1
            ##Ignore spaces between field name and "="
            while (c==' ' or c=='\t' or c=='\n'):
                i+=1; c = text[i]
                if (c=='\n'): n+=1
            ##Check if next non-space-y char is "="
            if (c!='='):
                return ('\n\nINPUT FILE ERROR at line '+str(n)+\
                        '.\nERROR: Line is formatted incorrectly.')
            i+=1; c = text[i] ##Skipping "="
            if (c=='\n'): n+=1
            field = field.strip()
            currField = field
            ##Spaces before the entry delimiter
            while (c==" " or c=="\t" or c=="\n"):
                i+=1; c = text[i]
                if (c=='\n'): n+=1
            delim = c ##Next nonspace char is delimiter
            string = ''
            fieldCap = field.upper()
            if (delim=="{"):
                i+=1; c = text[i] ##Skipping "{"
                if (c=='\n'): n+=1
                braces =1
                while (braces!=0):
                    ##Read value for the field
                    if (c=="{"):
                        braces+=1
                        string = string+c
                    elif (c=="}"):
                        braces-=1
                        if (braces==0): break ##End of argument
                        else: string = string+c
                    elif ((c=="\n" or c=="\t") and fieldCap!="HTMLCOMMENT"):
                        string = string+" "
                    else:
                        string = string+c
                    i+=1; c = text[i]
                    if (c=='\n'): n+=1
                i+=1; c = text[i] ##Skipping '}'
                if (c=='\n'): n+=1
                if (c==','):
                    i+=1; c = text[i]
                    if (c=='\n'): n+=1
            elif (delim=='"'):
                i+=1; c = text[i] ##Skipping '"'
                if (c=='\n'): n+=1
                while (c!='"'):
                    if (c=="\n" or c=="\t"): string = string+" "
                    else: string = string+c
                    i+=1; c = text[i]
                    if (c=='\n'): n+=1
                i+=1; c = text[i] ##Skipping '"'
                if (c=='\n'): n+=1
                if (c==','):
                    i+=1; c = text[i]
                    if (c=='\n'): n+=1
            else:
                ##There is no delimiter, then next char must be number
                if (not c.isdigit()):
                    return ('\n\nINPUT FILE ERROR at line '+str(n)+\
                            '.\nERROR: Invalid field entry delimiter')
                while (c!="," and c!="}"):
                    if (c=="\n" or c=="\t"): string = string+" "
                    else: string = string+c
                    i+=1; c = text[i]
                    if (c=='\n'): n+=1
                ##If no delimiter found, then entry can only be a number
                ##(such as year, or volume number)
                if (not string.isdigit()):
                    return ('\n\nINPUT FILE ERROR at line '+str(n)+\
                            '.\nERROR: Invalid field entry delimiter.')
                if (c==','):
                    i+=1; c = text[i]
                    if (c=='\n'): n+=1
            ##Get rid of excess spaces between words
            listWords = string.split(" ")
            value = ''
            for word in listWords:
                if (word!=''): value = value+word+" "
            bibs[currKey][currField] = value.strip()
        ##End of entry '}'
        elif (c=='}'):
            if (inEntry==True):
                inEntry = False
                i+=1; c = text[i] ##Skipping "}"
                if (c=='\n'): n+=1
            else:
                return ('\n\nINPUT FILE ERROR around line '+str(n)+\
                        '.\nERROR: Field entry braces mismatched.')
        else:
            i+=1; c = text[i]
            if (c=='\n'): n+=1

    ##File ended w/o entry ending
    if (inEntry==True):
        return ('\n\nINPUT FILE ERROR around line '+str(n)+\
                '.\nERROR: Field entry braces mismatched.')

    return bibs


#gets fields for a particular entry type from a file
def getTypeFields(entryType, lines):
    lines.append("\n")
    fields = []
    for l in xrange(len(lines)):
        if ((lines[l][0] == '@') and (lines[l][1:-1] == entryType.upper())):
            index = l+1
            while (lines[index][0] != '\n' and lines[index][0] != '@'):
                fields.append(lines[index][:-1].upper())
                index+=1
    return fields

#orders the fields of the entry
def orderKeys(fields, entryType, fieldText):
    orderedFields = ['AUTHOR', 'TITLE', 'BOOKTITLE', 'SCHOOL', 'EDITOR',
                     'JOURNAL', 'SERIES', 'MONTH', 'YEAR', 'VOLUME',
                     'NUMBER', 'EDITION', 'CHAPTER', 'PAGES', 'LOCATION', 
                     'PUBLISHER', 'HOWPUBLISHED', 'ORGANIZATION', 'OWNER',
                     'ADDRESS', 'TIMESTAMP', 'URL', 'MYNOTE', 'NOTE',
                     'COMMENT']    
    tempFields =['AUTHOR', 'TITLE', 'BOOKTITLE', 'SCHOOL', 'EDITOR',
                 'JOURNAL', 'SERIES', 'MONTH', 'YEAR', 'VOLUME',
                 'NUMBER', 'EDITION', 'CHAPTER', 'PAGES', 'LOCATION', 
                 'PUBLISHER', 'HOWPUBLISHED', 'ORGANIZATION', 'OWNER',
                 'ADDRESS', 'TIMESTAMP', 'URL', 'MYNOTE', 'NOTE', 'COMMENT']
    for field in tempFields:
        if (field not in fields):
            orderedFields.remove(field)
    #puts any non-typical fields at end
    for field in fields:
        if ((field.upper() not in orderedFields) and (field != 'ENTRYTYPE')):
            orderedFields.append(field.upper())
    return orderedFields

#adds new lines and spaces to value
def formatValue(value, spaceNum):
    spaceNum+=3
    valLen = (80 - spaceNum)
    newValue = ''
    count = 0
    while(value != ''):
        temp = value[0:valLen]
        if((len(temp.rsplit(' ')) == 1) or (len(value) < valLen)):
            newTemp = value
            value = ''
        else:
            [newTemp, temp] = temp.rsplit(' ', 1)
            value = temp + value[valLen:]
        if (count == 0):
            newValue = newTemp
        else:
            newValue = newValue + '\n' + (' '*spaceNum) + newTemp
        count+=1
    return newValue

#puts a different author n each line
def formatAuthors(value, spaceNum):
    spaceNum+=3
    breaks = list(find_all(value, ' and '))
    authors = ''
    i = 0
    for b in breaks:
        #don't add spaces or newline if first author
        if (i == 0):
            authors = authors+value[i:b]+' and'
        else:
            authors = authors+'\n'+(' '*spaceNum)+value[i:b]+' and'
        i = b+5
    #gets last author
    authors = authors+'\n'+(' '*spaceNum)+value[(breaks[-1]+5):]
    return authors

##Takes a bibtex key and dictionary for its entry info and
##returns a string of formated entry
def formatBib(bibKey, fieldDict, args):
    keys = fieldDict.keys()
    longestKey = 0
    typ = ''
    #finds longest key and type of article
    for key in keys:
        if (key == 'ENTRYTYPE'):
            typ = fieldDict[key]
        elif (len(key) > longestKey):
            longestKey = len(key)
    keys = orderKeys(keys, typ, args)
    longestKey+=1
    #start of entry
    text = '\n@' + typ + '{' + bibKey + ',\n'
    count = 1
    #formats each key and value
    for key in keys:
        #don't print 'key' as a field
        if(key.lower() != 'key'):
            value = str(fieldDict[key])
            #puts different author on each line if more than 3
            if (key.lower() == 'author' and value.count('and') > 2):
                value = formatAuthors(value, longestKey)
            #breaks up value if it's over 80 characters
            elif (len(value) > (80 - (longestKey + 5))):
                value = formatValue(value, longestKey)
            while (len(key) < longestKey):
                key = key + ' '
            #adds comma if it's not the last fields
            if (count == len(keys)):
                key = key + '= ' + '{' + value + '}' + '\n'
            else:
                key = key + '= ' + '{' + value + '}' + ',' + '\n'
            text = text + key
            count+=1
    text = text + '}\n'
    return text

def keyErrorHandler(key, bibDict):
    try: return bibDict[key]
    except: return None

#Takes a key's dictionary of fields
#returns a citation in the HTML format
def formatHTML(key, bibDict):
    htmlText = '<!----------------------------BIB ENTRY BEGIN---------------------------->\n'
    if(keyErrorHandler('AUTHOR', bibDict) != None):
        if(bibDict['AUTHOR'] != ''):
            htmlText = htmlText+'<LI> '+bibDict['AUTHOR']
    if(keyErrorHandler('YEAR', bibDict) != None):
        if(bibDict['YEAR'] != ''):
            htmlText = htmlText+' ('+bibDict['YEAR']+').\n'
    if(keyErrorHandler('TITLE', bibDict) != None):
        if(bibDict['TITLE'] != ''):
            htmlText = htmlText+'<BR>\n<STRONG> '+bibDict['TITLE']+'</STRONG>.\n<BR>'
    if(keyErrorHandler('EDITOR', bibDict) != None):
        if(bibDict['EDITOR'] != ''):
            htmlText = htmlText+'\nIn '+bibDict['EDITOR']+' (Ed.), '
    if(keyErrorHandler('JOURNAL', bibDict) != None):
        if(bibDict['JOURNAL'] != ''):
            htmlText = htmlText+'<I>'+bibDict['JOURNAL']+'</I>, '
    elif(keyErrorHandler('BOOKTITLE', bibDict) != None):
        if(bibDict['BOOKTITLE'] != ''):
            htmlText = htmlText+'<I>'+bibDict['BOOKTITLE']+'</I>, '
    if(keyErrorHandler('LOCATION', bibDict) != None):
        if(bibDict['LOCATION'] != ''):
            htmlText = htmlText+bibDict['LOCATION']+', '
    if(keyErrorHandler('MONTH', bibDict) != None):
        if(bibDict['MONTH'] != ''):
            htmlText = htmlText+bibDict['MONTH']+' '
    if(keyErrorHandler('YEAR', bibDict) != None):
        if(bibDict['YEAR'] != ''):
            htmlText = htmlText+bibDict['YEAR']+', '
    if(keyErrorHandler('SERIES', bibDict) != None):
        if(bibDict['SERIES'] != ''):
            htmlText = htmlText+bibDict['SERIES']+', '
    if(keyErrorHandler('VOLUME', bibDict) != None):
        if(bibDict['VOLUME'] != ''):
            htmlText = htmlText+'Vol. '+bibDict['VOLUME']+', '
    if(keyErrorHandler('NUMBER', bibDict) != None):
        if(bibDict['NUMBER'] != ''):
            htmlText = htmlText+'No. '+bibDict['NUMBER']+', '
    if(keyErrorHandler('EDITION', bibDict) != None):
        if(bibDict['EDITION'] != ''):
            htmlText = htmlText+bibDict['EDITION']+' Edition'+', '
    if(keyErrorHandler('CHAPTER', bibDict) != None):
        if(bibDict['CHAPTER'] != ''):
            htmlText = htmlText+'Chapter '+bibDict['CHAPTER']+', '
    if(keyErrorHandler('PAGES', bibDict) != None):
        if(bibDict['PAGES'] != ''):
            htmlText = htmlText+'pp. '+bibDict['PAGES']+', '
    if(keyErrorHandler('ORGANIZATION', bibDict) != None):
        if(bibDict['ORGANIZATION'] != ''):
            htmlText = htmlText+bibDict['ORGANIZATION']+', '
    if(keyErrorHandler('PUBLISHER', bibDict) != None):
        if(bibDict['PUBLISHER'] != ''):
            htmlText = htmlText+bibDict['PUBLISHER']+', '
    if(keyErrorHandler('ADDRESS', bibDict) != None):
        if(bibDict['ADDRESS'] != ''):
            htmlText = htmlText+bibDict['ADDRESS']+'.'
    else:
        htmlText = htmlText[:-2]+'.'
    htmlText = htmlText+'(<A href="'+key+'.pdf">PDF</A>)'
    if(keyErrorHandler('HTMLCOMMENT', bibDict) != None):
        if(bibDict['HTMLCOMMENT'] != ''):
            htmlText = htmlText+'''<P>
<!--COMMENT-BUTTON-->
<input type="button"
onClick="toggleMe('toggleAuthor-String05');"
value="Comments"/></p>
<p id="toggleAuthor-String05" style="display:none;">
<BR>----------------------<BR>'''+bibDict['COMMENT']+'''
<BR>----------------------<BR>
<BR>'''
    return (htmlText+'<BR>&nbsp;<BR>\n<!--BIB ENTRY END-->\n')

##Returns an ordered dictionary of all bib entries in the input table in dbFile
##in the order of the rows in the database
def DB2Dict(dbFile, table):
    conn = sqlite3.connect(dbFile)
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info("+table+")")
    f = cursor.fetchall()

    ##Store all the fields
    fields = []
    for tup in f:
        fields.append(str(tup[1]))
    nFields = len(fields)

    cursor.execute("SELECT * FROM "+table)
    info = cursor.fetchall()

    bibs = OrderedDict()
    for row in info:
        key = str(row[0])
        entry = {}
        for x in xrange(1,nFields):
            value = row[x]
            if (value!=None):
                ##Record only if value exists for corresponding field
                entry[str(fields[x])] = str(value)
        bibs[key] = entry
    return bibs

##Puts a list of keys a and returns an ordered dictionary with the same keys
##with only years as fields (keys are authors last names, then year)
##For converting format from list to dict
def keys2Dict(a):
    bibDict = OrderedDict()
    nKeys = len(a)
    breakYear = '30' ##Year break-point from 2000's and 1900's

    for i in xrange(nKeys):
        key = a[i]
        info = re.split('(\d+)',key)
        year = info[1]
        digits = len(year)
        bibDict[key] = {}

        if (digits==4):
            bibDict[key]['YEAR'] = year
        elif (digits==2):
            ##If last 2 digits of year is less than breakYear, then
            ##it is in the 2000's. Otherwise it is in the 1900's
            if (year<=breakYear):
                year = '20'+year
            else:
                year = '19'+year
            bibDict[key]['YEAR'] = year

    return bibDict

##Returns a list of sorted keys in input dictionary of bibtex entries
def sortKeys(bibDict):
    a = list(bibDict)
    kList = sorted(a,key=str.lower) ##Sort list of keys alphabetically
    nKeys = len(kList)

    keys = []
    i=0
    while (i<nKeys):
        ##Handle articles w/ same authors w/ year in different centuries
        ##Order chronologically
        ##This is for keys ending in only last 2 digits of year
        repeat = [] ##Repeats of same authors
        key = kList[i]
        auths = ''
        ##Gets all authors out of key (no digits left)
        tempKey = key
        auths = re.split('(\d+)',tempKey)[0]
        
        if (len(auths)>=len(key)-3):
            ##Key does not contain year in full 4 digits
            for k in kList:
                if (auths==k[:-2] or auths==k[:-3]):
                    ##Handle for multiple entries in same year w/ same authors
                    repeat.append(k)
        nRepeats = len(repeat)
        if (nRepeats>1):
            ##Store and sort repeats of same authors by year
            ks = []
            for key in repeat:
                ks.append(bibDict[key]['YEAR'])
            ks.sort()
            index = 0
            #adds matching key for each year
            for y in ks:
                key = repeat[0]
                while (bibDict[key]['YEAR'] != y):
                    key = repeat[index]
                    index+=1
                keys.append(key)
                repeat.remove(key)
                index = 0
            i = i+nRepeats
        else:
            keys.append(key)
            i+=1
    return keys

#finds the matching entries
def findEntries(keys, bibText, fieldOrders):
    entries = ''
    tempKeys = list(keys)
    bibDict = bib2Dict(bibText)
    #gets entries from .bib file
    for key in tempKeys:
        ##Try to call the key on the bibs dictionary
        ##If failed, then key is not in the file
        if (key in bibDict):
            temp = bibDict[key]
            entries = entries + formatBib(key, temp, fieldOrders)
        else:
            keys.remove(key)
    textContent = entries      
    return textContent

##Gets input Bibtex file and desired SQLite database file to edit
def bib2DB(bibs, dbFile, table):
    conn = sqlite3.connect(dbFile)
    cursor = conn.cursor()

    ##Destroy the table if it already exists, to try to re-write it
    try:
        cursor.execute("DROP TABLE "+table)
    except:
        pass

    cursor.execute("CREATE TABLE "+table+"(BIBTEXKEY text)")

    for key in bibs:
        entry = bibs[key]
        cursor.execute("SELECT EXISTS(SELECT * FROM "+table+" WHERE BIBTEXKEY='"
                       +key+"')")
        exists = cursor.fetchone()
        if (exists==(0,)):
            cursor.execute("INSERT INTO "+table+" (BIBTEXKEY) VALUES(?)",(key,))
        for field in entry:
            value = entry[field]
            try:
                cursor.execute("ALTER TABLE "+table+" ADD "+field+" text")
            except: pass
            cursor.execute("UPDATE "+table+" SET '"+field
                           +"'=? WHERE BIBTEXKEY='"+key+"'",(value,))
            conn.commit()

    conn.close()

##Returns list of unique keys cited in the latex file
def getKeys(latexFile):
    string = loadTextString(latexFile)
    length = len(string)

    cites = set([]) ##No duplicates

    ##Remove all the LaTeX comments from file text string
    text = string
    while ('\\begin{comment}' in text):
        x = text.index('\\begin{comment}', 0, length)
        y = text.index('\\end{comment}', x, length)
        text = text[0:x]+text[(y+13):length]
        length = len(text)

    while ('%' in text):
        x = text.index('%', 0, length)
        y = text.index('\n', x, length)
        text = text[0:x]+text[(y+1):length]
        length = len(text)

    ##Look for citations
    i = 0
    while (i<length):
        try:
            key = ''
            a = text.index('\\cite', i, length)+5
            i = a
            c = text[i]
            while (c!='{'):
                i+=1; c = text[i]
            i+=1; c = text[i]
            braces = 1
            while (braces!=0):
                ##Read until open braces for cited key is closed
                if (c=='{'): braces+=1
                elif (c=='}'): braces-=1

                if (braces==0): break

                key = key+c
                i+=1; c = text[i]
            keys = key.split(",")
            for k in keys:
                if (k!=''): cites.add(k.strip())
        except:
            ##No more citations
            break
        i+=1
    return sortKeys(keys2Dict(list(cites)))


#creates returns HTML text .bib text
def outHTML(bibText):
    htmText = '''
<meta http-equiv="Context-Type" content="text/html; charset=WINDOWS-1252">

<meta http-equiv="Context-Type" content="text/html; charset=WINDOWS-1252">

<meta http-equiv="Context-Type" content="text/html; charset=WINDOWS-1252">
<!--------------------------------------------------------------------------->

<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3c.org/TR/1999/REC-html401-19991224/loose.dtd">
<HTML>
<HEAD><TITLE>Keystroke Big Mama web page</TITLE>
<META http-equiv=Content-Type content="text/html; charset=windows-1252">
<META http-equiv=Pragma content=*no*-*cache*>

<!-- STYLE INFO -->

<script type="text/javascript" language="javascript">

function toggleMe(id)
{
    var element = document.getElementById(id);
    if(element.style.display == "none")
    {
        element.style.display = "block";
    }
    else
    {
        element.style.display = "none";
    }
}
</script>

<STYLE type=text/css>BODY {
	FONT-SIZE: 11pt; FONT-FAMILY: sans-serif
}
.TH {
	FONT-WEIGHT: bold; FONT-SIZE: 14pt; BACKGROUND-COLOR: #faebd7; TEXT-ALIGN: center
}
</STYLE>

<META content="MSHTML 6.00.2900.2873" name=GENERATOR>
</HEAD>

<BODY>
<HR color=#6699ff>

<a name="top">
Click on link:
<a href="#top">Top</a>
<a href="#A">A</a>
<a href="#B">B</a>
<a href="#C">C</a>
<a href="#D">D</a>
<a href="#E">E</a>
<a href="#F">F</a>
<a href="#G">G</a>
<a href="#H">H</a>
<a href="#I">I</a>
<a href="#J">J</a>
<a href="#K">K</a>
<a href="#L">L</a>
<a href="#M">M</a>
<a href="#N">N</a>
<a href="#O">O</a>
<a href="#P">P</a>
<a href="#Q">Q</a>
<a href="#R">R</a>
<a href="#S">S</a>
<a href="#T">T</a>
<a href="#U">U</a>
<a href="#V">V</a>
<a href="#W">W</a>
<a href="#X">X</a>
<a href="#Y">Y</a>
<a href="#Z">Z</a>
<a href="#Bottom">Bottom</a>

<H2>Keystroke Big Mama Papers</H2>
<!-- RED DAGGER -->
<LI>The <Font Size="5" color="red">&#9830;</FONT>
symbol indicates that we are missing the PDF file.</LI>
<!-- RED BULLET -->
<LI>The <Font Size="6" color="red">&#8226;</FONT>
symbol indicates that we are missing details for the citation.</LI>
</UL>
<P>
'''
    headingText = '''<P>
<a href="#top">Back to top</a>
<a href="#A">A</a>
<a href="#B">B</a>
<a href="#C">C</a>
<a href="#D">D</a>
<a href="#E">E</a>
<a href="#F">F</a>
<a href="#G">G</a>
<a href="#H">H</a>
<a href="#I">I</a>
<a href="#J">J</a>
<a href="#K">K</a>
<a href="#L">L</a>
<a href="#M">M</a>
<a href="#N">N</a>
<a href="#O">O</a>
<a href="#P">P</a>
<a href="#Q">Q</a>
<a href="#R">R</a>
<a href="#S">S</a>
<a href="#T">T</a>
<a href="#U">U</a>
<a href="#V">V</a>
<a href="#W">W</a>
<a href="#X">X</a>
<a href="#Y">Y</a>
<a href="#Z">Z</a>

<a name=%s>
<!-- HEADING BEGIN -->
<TABLE width="100%%">
  <TBODY>
  <TR>
    <TD class=TH>%s</TD></TR></TBODY></TABLE>
<!-- HEADING END -->
'''
    currentLetter = 'A'
    keyDict = bib2Dict(bibText)
    keys = sortKeys(keyDict)
    if (keys[0][0].upper() == currentLetter):
        htmText = htmText+(headingText%(currentLetter, currentLetter))
    for key in keys:
        if ((key[0].upper()) != currentLetter):
            currentLetter = (key[0]).upper()
            htmText = htmText+(headingText%(currentLetter, currentLetter))
        htmText = htmText+(formatHTML(key, keyDict[key]))
    htmText = htmText+'''<a name=Bottom>
<a href="#top">Back to top</a>'''
    return htmText


##Turns a dictionary of lists of fields into user-friendly text file format
def fields2Txt(fieldOrder):
    text = ''
    
    alphabetized = []
    for t in fieldOrder:
        alphabetized.append(t)
    alphabetized.sort()

    for t in alphabetized:
        text = text + "@" + t + "\n"
        for f in fieldOrder[t]:
            text = text + f + "\n"
        text = text + "\n"

    return text

