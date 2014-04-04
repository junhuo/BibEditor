import os

class Default(object):
    def __init__(self):
        self.fieldText = "@ARTICLE\n"+\
                         "AUTHOR\n"+\
                         "TITLE\n"+\
                         "JOURNAL\n"+\
                         "YEAR\n"+\
                         "VOLUME\n"+\
                         "NUMBER\n"+\
                         "PAGES\n"+\
                         "MONTH\n"+\
                         "NOTE\n"+\
                         "MISSING\n"+\
                         "\n"+\
                         "@BOOK\n"+\
                         "AUTHOR\n"+\
                         "EDITOR\n"+\
                         "TITLE\n"+\
                         "PUBLISHER\n"+\
                         "YEAR\n"+\
                         "VOLUME\n"+\
                         "NUMBER\n"+\
                         "SERIES\n"+\
                         "ADDRESS\n"+\
                         "EDITION\n"+\
                         "MONTH\n"+\
                         "NOTE\n"+\
                         "MISSING\n"+\
                         "\n"+\
                         "@BOOKLET\n"+\
                         "AUTHOR\n"+\
                         "TITLE\n"+\
                         "HOWPUBLISHED\n"+\
                         "ADDRESS\n"+\
                         "MONTH\n"+\
                         "YEAR\n"+\
                         "NOTE\n"+\
                         "MISSING\n"+\
                         "\n"+\
                         "@CONFERENCE\n"+\
                         "AUTHOR\n"+\
                         "TITLE\n"+\
                         "BOOKTITLE\n"+\
                         "YEAR\n"+\
                         "MISSING\n"+\
                         "\n"+\
                         "@INBOOK\n"+\
                         "AUTHOR\n"+\
                         "EDITOR\n"+\
                         "TITLE\n"+\
                         "CHAPTER\n"+\
                         "PAGES\n"+\
                         "PUBLISHER\n"+\
                         "YEAR\n"+\
                         "MISSING\n"+\
                         "\n"+\
                         "@INCOLLECTION\n"+\
                         "AUTHOR\n"+\
                         "TITLE\n"+\
                         "BOOKTITLE\n"+\
                         "PUBLISHER\n"+\
                         "YEAR\n"+\
                         "MISSING\n"+\
                         "\n"+\
                         "YEAR\n"+\
                         "@INPROCEEDINGS\n"+\
                         "AUTHOR\n"+\
                         "TITLE\n"+\
                         "EDITOR\n"+\
                         "BOOKTITLE\n"+\
                         "VOLUME\n"+\
                         "NUMBER\n"+\
                         "SERIES\n"+\
                         "PAGES\n"+\
                         "ADDRESS\n"+\
                         "MONTH\n"+\
                         "YEAR\n"+\
                         "ORGANIZATION\n"+\
                         "PUBLISHER\n"+\
                         "NOTE\n"+\
                         "MISSING\n"+\
                         "\n"+\
                         "@MANUAL\n"+\
                         "AUTHOR\n"+\
                         "TITLE\n"+\
                         "ORGANIZATION\n"+\
                         "ADDRESS\n"+\
                         "EDITION\n"+\
                         "MONTH\n"+\
                         "YEAR\n"+\
                         "NOTE\n"+\
                         "MISSING\n"+\
                         "\n"+\
                         "@MASTERTHESIS\n"+\
                         "AUTHOR\n"+\
                         "TITLE\n"+\
                         "SCHOOL\n"+\
                         "TYPE\n"+\
                         "ADDRESS\n"+\
                         "MONTH\n"+\
                         "YEAR\n"+\
                         "NOTE\n"+\
                         "MISSING\n"+\
                         "\n"+\
                         "@MISC\n"+\
                         "AUTHOR\n"+\
                         "TITLE\n"+\
                         "HOWPUBLISHED\n"+\
                         "MONTH\n"+\
                         "YEAR\n"+\
                         "NOTE\n"+\
                         "MISSING\n"+\
                         "\n"+\
                         "@PHDTHESIS\n"+\
                         "AUTHOR\n"+\
                         "TITLE\n"+\
                         "SCHOOL\n"+\
                         "TYPE\n"+\
                         "ADDRESS\n"+\
                         "MONTH\n"+\
                         "YEAR\n"+\
                         "NOTE\n"+\
                         "MISSING\n"+\
                         "\n"+\
                         "@PROCEEDINGS\n"+\
                         "EDITOR\n"+\
                         "TITLE\n"+\
                         "VOLUME\n"+\
                         "NUMBER\n"+\
                         "SERIES\n"+\
                         "ADDRESS\n"+\
                         "MONTH\n"+\
                         "YEAR\n"+\
                         "PUBLISHER\n"+\
                         "ORGANIZATION\n"+\
                         "NOTE\n"+\
                         "MISSING\n"+\
                         "\n"+\
                         "@TECHREPORT\n"+\
                         "AUTHOR\n"+\
                         "TITLE\n"+\
                         "INSTITUTION\n"+\
                         "TYPE\n"+\
                         "NUMBER\n"+\
                         "ADDRESS\n"+\
                         "MONTH\n"+\
                         "YEAR\n"+\
                         "NOTE\n"+\
                         "MISSING\n"+\
                         "\n"+\
                         "@UNPUBLISHED\n"+\
                         "AUTHOR\n"+\
                         "TITLE\n"+\
                         "MONTH\n"+\
                         "YEAR\n"+\
                         "NOTE\n"+\
                         "MISSING\n"

        self.allEntryTypes = ('ARTICLE', 'BOOK', 'BOOKLET', 'CONFERENCE',
                              'INBOOK', 'INCOLLECTION', 'INPROCEEDINGS',
                              'MANUAL', 'MASTERTHESIS', 'MISC', 'PHDTHESIS',
                              'PROCEEDINGS', 'TECHREPORT', 'UNPUBLISHED')

        self.allFields = ['ADDRESS', 'AUTHOR', 'BOOKTITLE', 'CHAPTER',
                          'COMMENT', 'CROSSREF', 'EDITION', 'EDITOR',
                          'EPRINT', 'HOWPUBLISHED', 'HTMLCOMMENT',
                          'INSTITUTION', 'JOURNAL', 'MISSING', 'NOTE', 'OWNER',
                          'PAGES', 'PUBLISHER', 'SCHOOL', 'SERIES', 'TITLE',
                          'URL', 'YEAR']
        
        self.entriesDefault = {'ARTICLE':['AUTHOR','TITLE','JOURNAL','YEAR',
                                          'VOLUME','NUMBER','PAGES','MONTH',
                                          'NOTE','MISSING'],
                               'BOOK':['AUTHOR','EDITOR','TITLE','PUBLISHER',
                                       'YEAR','VOLUME','NUMBER','SERIES',
                                       'ADDRESS','EDITION','MONTH','NOTE',
                                       'MISSING'],
                               'BOOKLET':['AUTHOR','TITLE','HOWPUBLISHED',
                                          'ADDRESS','MONTH','YEAR','NOTE',
                                          'MISSING'],
                               'CONFERENCE':['AUTHOR','TITLE','BOOKTITLE',
                                             'YEAR','MISSING'],
                               'INBOOK':['AUTHOR','EDITOR','TITLE','CHAPTER',
                                         'PAGES','PUBLISHER','YEAR','MISSING'],
                               'INCOLLECTION':['AUTHOR','TITLE','BOOKTITLE',
                                               'PUBLISHER','YEAR','MISSING'],
                               'INPROCEEDINGS':['AUTHOR','TITLE','EDITOR',
                                                'BOOKTITLE','VOLUME','NUMBER',
                                                'SERIES','PAGES','ADDRESS',
                                                'MONTH','YEAR','ORGANIZATION',
                                                'PUBLISHER','NOTE','MISSING'],
                               'MANUAL':['AUTHOR','TITLE','ORGANIZATION',
                                         'ADDRESS','EDITION','MONTH','YEAR',
                                         'NOTE','MISSING'],
                               'MASTERTHESIS':['AUTHOR','TITLE','SCHOOL',
                                               'TYPE','ADDRESS','MONTH','YEAR',
                                               'NOTE','MISSING'],
                               'MISC':['AUTHOR','TITLE','HOWPUBLISHED','MONTH',
                                       'YEAR','NOTE','MISSING'],
                               'PHDTHESIS':['AUTHOR','TITLE','SCHOOL','TYPE',
                                            'ADDRESS','MONTH','YEAR','NOTE',
                                            'MISSING'],
                               'PROCEEDINGS':['EDITOR','TITLE','VOLUME',
                                              'NUMBER','SERIES','ADDRESS',
                                              'MONTH','YEAR','PUBLISHER',
                                              'ORGANIZATION','NOTE','MISSING'],
                               'TECHREPORT':['AUTHOR','TITLE','INSTITUTION',
                                             'TYPE','NUMBER','ADDRESS','MONTH',
                                             'YEAR','NOTE','MISSING'],
                               'UNPUBLISHED':['AUTHOR','TITLE','MONTH','YEAR',
                                              'NOTE','MISSING']
                               }
        
        self.entriesOptional = {'ARTICLE':['VOLUME','NUMBER','PAGES','MONTH',
                                           'NOTE','KEY'],
                                'BOOK':['VOLUME','NUMBER','SERIES','ADDRESS',
                                        'EDITION','MONTH','NOTE','KEY'],
                                'BOOKLET':['AUTHOR','HOWPUBLISHED','ADDRESS',
                                           'MONTH','YEAR','NOTE','KEY'],
                                'CONFERENCE':['EDITOR','VOLUME','NUMBER',
                                              'SERIES','PAGES','ADDRESS',
                                              'MONTH','ORGANIZATION',
                                              'PUBLISHER','NOTE','KEY'],
                                'INBOOK':['VOLUME','NUMBER','SERIES','TYPE',
                                          'ADDRESS','EDITION','MONTH','NOTE',
                                          'KEY'],
                                'INCOLLECTION':['EDITOR','VOLUME','NUMBER',
                                                'SERIES','TYPE','CHAPTER',
                                                'PAGES','ADDRESS','EDITION',
                                                'MONTH','NOTE','KEY'],
                                'INPROCEEDINGS':['EDITOR','VOLUME','NUMBER',
                                                 'SERIES','PAGES','ADDRESS',
                                                 'MONTH','ORGANIZATION',
                                                 'PUBLISHER','NOTE','KEY'],
                                'MANUAL':['AUTHOR','ORGANIZATION','ADDRESS',
                                          'EDITION','MONTH','YEAR','NOTE',
                                          'KEY'],
                                'MASTERSTHESIS':['TYPE','ADDRESS','MONTH',
                                                 'NOTE','KEY'],
                                'MISC':['AUTHOR','TITLE','HOWPUBLISHED','MONTH',
                                        'YEAR','NOTE','KEY'],
                                'PHDTHESIS':['TYPE','ADDRESS','MONTH','NOTE',
                                             'KEY'],
                                'PROCEEDINGS':['EDITOR','VOLUME','NUMBER',
                                               'SERIES','ADDRESS','MONTH',
                                               'PUBLISHER','ORGANIZATION',
                                               'NOTE','KEY'],
                                'TECHREPORT':['TYPE','NUMBER','ADDRESS','MONTH',
                                              'NOTE','KEY'],
                                'UNPUBLISHED':['MONTH','YEAR','KEY']
                                }

        self.helpMessage = """
File Menu:
    Import
        -- Open existing .db or .bib file to edit
    Export as .bib
        -- Exports text as .bib file
    Export as .htm
        -- Converts text to HTML format and outputs .htm file
    Export as .db
        -- Creates a database with all entries listed in the text
    Exit
        -- Exits BibTeX Editor

Edit Menu: 
    Undo
        -- Undoes the last edit to the text
    Redo
        -- Reverses the effect of Undo
    Insert Bib Entry
        -- Opens separate menu to insert individual entries
    Pull Keys
        -- Displays list of bibTeX keys currently in text
        -- Select keys for entries to keep in text and hit 'Load Keys'
            to pull out those entries
        -- 'Import from File' will pull a list of keys from any .txt file
            and pull and matching entries out of the current text
    Format
        -- Formats text in display
    Sort
        -- Sorts entries alphabetically by key and formats text
    
Options Menu:
    Change Default Field Order
        -- Import a text file with a list of fields for each entry type to
            change the fields displayed by the 'Insert Entry' menu

Help Menu:
    BibTeX Editor Help
        -- Display this screen

'Find' bar:
    highlights any matching phrase in the text and jumps to first instance
    - turns pink if no matching phrase is found
"""
        
    def _fieldText(self):
        return self.fieldText

    ##All available entry types
    def _allEntryTypes(self):
        return self.allEntryTypes

    ##Default prompted entry fields 
    def _entriesDefault(self):
        return self.entriesDefault

    def _allFields(self):
        return self.allFields

    def _helpMessage(self):
        return self.helpMessage

    def _dummy(self):
        pass



class Constants(object):
    def __init__(self):
        self.Default = Default()
        self.fieldText = self.Default._fieldText()
        self.allEntryTypes = self.Default._allEntryTypes()
        self.entriesDefault = self.Default._entriesDefault()
        self.allFields = self.Default._allFields()
        self.helpMessage = self.Default._helpMessage()

        currdir = os.path.dirname(os.path.realpath(__file__))
        if (currdir[-4:]==u'.zip'):
            path = currdir.split('\\')
            path.pop()
            currdir = '\\'.join(path)
        self.currdir = currdir

        try:
            fileHandler = open(self.currdir+'\\fieldOrderDefault.txt', "rt")
            text = fileHandler.read()
            fileHandler.close()
            self.fieldText = text
            self.entriesDefault = self.txt2Fields(text)
            for k in self.entriesDefault:
                for i in self.entriesDefault[k]:
                    if i not in self.allFields:
                        self.allFields.append(i)
            self.allFields.sort()
        except:
            pass

    def txt2Fields(self, text):
        textList = text.split('\n')
        entries = {}

        n = len(textList)
        i = -1
        while (i<n-1):
            i+=1; line = textList[i]
            if (line==''):
                continue
            elif (line[0]=="@"):
                key = line[1:]
                temp = []
                i+=1; line = textList[i]
                while (line!=''):
                    temp.append(line)
                    i+=1; line = textList[i]
                entries[key] = temp

        return entries
    
    def _fieldText(self):
        return self.fieldText

    ##All available entry types
    def _allEntryTypes(self):
        return self.allEntryTypes

    ##Default prompted entry fields 
    def _entriesDefault(self):
        return self.entriesDefault

    def _allFields(self):
        return self.allFields

    def _helpMessage(self):
        return self.helpMessage

    
