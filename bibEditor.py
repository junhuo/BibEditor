from Tkinter import *
from Tkconstants import *
import tkFileDialog
import tkSimpleDialog
import tkMessageBox
import ScrolledText
import tkFont
import ctypes
import argparse
import unicodedata

import os
import Pmw
import ast
from editorLib import *
from bibConstants import *

##------------------------------------------------------------------------------
##  Raise error
##------------------------------------------------------------------------------

class RaiseError:
    def __init__(self, title, message):
        tkMessageBox.showwarning(title, message)

##------------------------------------------------------------------------------
##  Show message
##------------------------------------------------------------------------------

class RaiseMessage:
    def __init__(self, title, message):
        tkMessageBox.showinfo(title, message)


##------------------------------------------------------------------------------
##  Prompt database
##------------------------------------------------------------------------------

class PromptDB:
    def __init__(self, parent, tbox1, path, Constants):
        self.parent = parent
        self.Constants = Constants
        self.tbox1 = tbox1
        self.path = path

    def openFile(self):
        self.conn = sqlite3.connect(self.path)
        self.cursor = self.conn.cursor()
        
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        info = self.cursor.fetchall()

        self.allTables = []
        for t in info:
            self.allTables.append(str(t[0]))

        self.table = ''
        self.text = ''

        self.tbl = Pmw.SelectionDialog(self.parent, title='Select Table',
                                       buttons=('OK','Cancel'),
                                       defaultbutton='OK',
                                       scrolledlist_labelpos='n',
                                       label_text='Select table from file',
                                       scrolledlist_items=self.allTables,
                                       command=self.getTable)

        self.conn.close()
        self.tbl.withdraw()

    def saveFile(self):
        self.conn = sqlite3.connect(self.path)
        self.cursor = self.conn.cursor()
        
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        info = self.cursor.fetchall()

        self.allTables = []
        for t in info:
            self.allTables.append(str(t[0]))

        self.table = ''

        self.tbl = Pmw.ComboBoxDialog(self.parent, title='Update Table',
                                      buttons=('OK','Cancel'),
                                      defaultbutton='OK',
                                      combobox_labelpos='n',
                                      label_text=\
                                      'Enter a table to update/create: ',
                                      scrolledlist_items=self.allTables,
                                      command=self.setTable)

        self.conn.close()
        self.tbl.withdraw()

    def getTable(self, result):
        sel = self.tbl.getcurselection()
        if (result=='Cancel' or result==None):
            self.tbl.deactivate()
        elif (result=='OK'):
            if (len(sel)==0):
                message = "Please select a table before pressing 'OK'."
                RaiseError('No Selected Table', message)
            else:
                self.table=str(sel[0])
                bibs = DB2Dict(self.path, self.table)
                keys = sortKeys(bibs)
                for k in keys:
                    entry = bibs[k]
                    self.text = self.text+formatBib(k, entry,
                                                    self.Constants._fieldText())
                self.tbox1.settext(self.text)
                self.tbl.deactivate()

    def setTable(self, result):
        typ = str(self.tbl.get())
        sel = str(self.tbl.getcurselection())

        bibs = bib2Dict(self.tbox1.get())

        if (type(bibs)==str):
            RaiseError('BibTeX Error', bibs)
            return

        if (result=='Cancel' or result==None):
            self.tbl.deactivate()
        elif (result=='OK'):
            if (typ.strip(' \n\t')!=''):
                bib2DB(bibs, self.path, typ)
                RaiseMessage('File Saved', 'Table '+typ+' updated')
                self.tbl.deactivate()
            elif (sel.strip('\n\t ')!='()'):
                bib2DB(bibs, self.path, sel[0])
                RaiseMessage('File Saved', 'Table '+sel+' updated')
                self.tbl.deactivate()
            else:
                message = "Please enter table name or select an existing table."
                RaiseError("Invalid Table Name", message)
                self.saveFile()
                self.tbl.activate()


##------------------------------------------------------------------------------
##  Insert entry
##------------------------------------------------------------------------------
        
class InsertEntry(object):
    def __init__(self, parent, tbox1, entriesDefault, allFields, Constants):
        self.parent = parent
        self.Constants = Constants
        self.tbox1 = tbox1
        
        ##Get default fields from Main(),
        ##because user might have changed default options
        self.entriesDefault = entriesDefault
        self.allFields = allFields
        
        self.entry = ''

        self.allTypes = self.Constants._allEntryTypes()

        self.upload_opt = {'filetypes':[('Plain text files','.txt'),],
                           'parent': self.parent,
                           'title': 'Upload Fields Text',
                           'multiple': False
                           }

        self.dialog = Pmw.Dialog(parent, buttonboxpos='w', title='New Entry',
                                 buttons=('Clear All',
                                          'Import Field Orders\nfrom File',
                                          'Insert Entry',
                                          'Close',),
                                 command=self.execute)

        ##Options for entry types
        self.entryType = Pmw.OptionMenu(self.dialog.interior(), labelpos='w',
                                        label_text='Entry Type: ',
                                        items=self.allTypes,
                                        command=self.changeType)
        self.entryType.pack(anchor='w', padx=2, pady=2)

        self.key = Pmw.EntryField(self.dialog.interior(), labelpos='w',
                                  label_text='BibTeX Key: ', validate=None)
        self.key.pack(fill='x', expand=1, padx=2, pady=5)

        ##Scrollable frame for entry fields
        self.sf = Pmw.ScrolledFrame(self.dialog.interior(), usehullsize=1,
                                    hull_width=680, hull_height=580)

        self.promptFields('ARTICLE')

        self.sf.pack(side='bottom', padx=2, pady=1, fill='both', expand=1)        

        self.dialog.withdraw()

    ##Execute commands in main dialog frame
    def execute(self, result):
        if (result=='Close' or result==None):
            self.cancel(result)
        elif (result=='Clear All'):
            self.clearAll()
        elif (result=='Import Field Orders\nfrom File'):
            self.uploadFields()
        elif (result=='Insert Entry'):
            self.insertEntry()

    ##Clear all information in input fields
    def clearAll(self):
        self.key.clear() ##Clear key entry
        nFields = len(self.entries)
        for i in xrange(nFields):
            ##Clear all contents of all field entries
            self.entries[i].clearEntry()

    ##Insert into current text an entry with info in input fields
    def insertEntry(self):
        newEntry = ''
        key = self.key.get()
        if (key==''):
            RaiseError('Key Error', 'BibTeX Key cannot be empty.')
        else:
            entry = {'ENTRYTYPE':self.entryType.getcurselection()}
            i=0
            ##Create temp copy to check for updates in self.entries
            temp = []
            for e in self.entries:
                temp.append(e)
            for e in temp:
                ##Try to get label/entry
                ##If failed, then this label/entry doesn't exist anymore,
                ##so remove it from self.entries
                try:
                    e.getLabel()
                    e.getEntry()
                except:
                    ##Update self.entries
                    self.entries.remove(e)
            ##Set fields into entry dictionary
            for e in self.entries:
                entry[e.getLabel()] = e.getEntry()
            newEntry = formatBib(key, entry, self.Constants._fieldText())
            self.tbox1.appendtext(newEntry)
            ##Pop-up message of entry added
            RaiseMessage('Entry Added: '+key, 'Entry:\n'+newEntry+
                         '\nis added to text box.')
            #sets title of root menu
            if(self.parent.title()[:1] != '*'):
                self.parent.title("*"+self.parent.title())
            self.clearAll()


    ##Close dialog
    def cancel(self, result):
        self.dialog.deactivate(result)

    ##Entry type is changed
    def changeType(self, result):
        self.promptFields(result)

    ##Prompt for inputs for fields in scrollable box
    def promptFields(self, result):
        for w in self.sf.component('frame').winfo_children():
            w.destroy()
    
        self.fields = self.entriesDefault[result]

        self.entries = []
        self.r = 0
        for f in self.fields:
            self.entries.append(FieldRow(self.sf.interior(), self.r, f, ''))
            self.r+=1
            
        self.var = StringVar()
        self.var.set('ADDRESS')

        self.optRow()

        self.sf.interior().pack(padx=2, pady=1, fill='both', expand=1)

    ##Adding a field
    def addField(self):
        label = self.var.get() ##Get label
        text = self.addEnt.get() ##Get input
        ##Destroy all components of add entry
        self.addOpt.destroy()
        self.addEnt.destroy()
        self.addBut.destroy()
        ##Create newly added field
        self.entries.append(FieldRow(self.sf.interior(), self.r, label, text))
        self.r+=1

        ##Re-create add entry
        self.optRow()

    ##Create optional add row
    def optRow(self):
        self.addOpt = OptionMenu(self.sf.interior(), self.var, *self.allFields)
##        self.addEntry.config(width=15)
        self.addOpt.grid(row=self.r)
        self.addEnt = Entry(self.sf.interior(), width=80, takefocus=False)
        self.addEnt.grid(row=self.r, column=1)

        self.addBut = Button(self.sf.interior(), text='ADD', command=self.addField)
        self.addBut.grid(row=self.r, column=2)

    ##Upload fields from external .txt file
    ##Overrides previous fields default for entry types included in the file,
    ##keep old default otherwise
    def uploadFields(self):
        path = self.openFileName()
        if (path):
            fileList = loadTextList(path)
            for e in self.entriesDefault:
                try:
                    newFields = getTypeFields(e,fileList)
                    if (newFields!=[]):
                        self.entriesDefault[e] = newFields
                except:
                    pass
        self.promptFields('ARTICLE')

    ##Returns path of the file opened
    def openFileName(self):
        fileName = tkFileDialog.askopenfilename(**self.upload_opt)
        if (fileName): return fileName


##------------------------------------------------------------------------------
##  Field row
##------------------------------------------------------------------------------

##A packaged deal of field Label, Entry, and delete Button for class InsertEntry
class FieldRow:
    def __init__(self, parent, row, label, entry):
        self.parent = parent
        self.row = row
        self.label = label
        self.entry = entry

        self.l = Label(self.parent, text=self.label)
        self.l.grid(row=self.row, column=0)
        self.e = Entry(self.parent, width=80)
        self.e.insert(0,self.entry)
        self.e.grid(row=self.row, column=1)
        self.b = Button(self.parent, text='DEL', command=self.delete)
        self.b.grid(row=self.row, column=2)

    def getLabel(self):
        return self.label

    def getEntry(self):
        return self.e.get()

    def setEntry(self, text):
        self.e.delete(0, END)
        self.e.insert(0, text)

    def clearEntry(self):
        self.e.delete(0, END)

    ##Destroy all components of the packaged deal
    def delete(self):
        self.l.destroy()
        self.e.destroy()
        self.b.destroy()



##------------------------------------------------------------------------------
##  Key menu
##------------------------------------------------------------------------------

class KeyMenu(Frame):
    def __init__(self, parent, tbox1, fieldText):
        self.parent = parent
        self.tbox = tbox1
        self.fieldText = fieldText

        self.dialog = Pmw.Dialog(self.parent, buttonboxpos='s', title='Keys',
                                 buttons=('Close',), command=self.execute)
        
        self.bibText = self.tbox.get()
        self.bibs = bib2Dict(self.bibText)

        if (type(self.bibs)==str):
            RaiseError('BibTeX Error', self.bibs)
            return
        
        self.keys = sortKeys(self.bibs)
        self.selectedKeys = []

        self.keyList = Pmw.ScrolledListBox(self.dialog.interior(),
                                           items=(self.keys),
                                           labelpos='nw',
                                           listbox_height = 6,
                                           listbox_selectmode = 'multiple',
                                           selectioncommand=\
                                           self.selectionCommand,
                                           usehullsize = 1,
                                           hull_width = 200,
                                           hull_heigh = 300
                                           )
        self.keyList.pack(padx = 5, pady = 5)

        ##Options for importing a file
        self.imp_opt = {'defaultextension':'.txt',
                        'filetypes':[('LaTeX Files','.tex'),
                                     ('text files','.txt')],
                        'parent': self.parent, 'title': 'Import File'}

        self.buttons = Pmw.ButtonBox(self.dialog.interior(), labelpos='s')
        self.buttons.pack()
        self.buttons.add('Import from File', command=self.importKeys)
        self.buttons.add('Load Keys', command=self.loadKeys)
        self.buttons.alignbuttons()

    #gets selected keys
    def selectionCommand(self):
        selections = self.keyList.getcurselection()
        if (selections):
            self.selectedKeys = selections

    #gets keys from file
    def importKeys(self):
        path = self.openFileName()
        if (path):
            if (path[-4:] == '.txt'):
                self.original = findEntries(loadKeyList(path),
                                            self.bibText, self.fieldText)
            else:
                self.original = findEntries(getKeys(path),
                                            self.bibText, self.fieldText)
            self.tbox.settext(self.original)
            #sets title of root menu
            if(self.parent.title()[:1] != '*'):
                self.parent.title("*"+self.parent.title())
            self.cancel('Close')

    #loads entries for selected keys into editor
    def loadKeys(self):
        if(self.selectedKeys != []):
            self.original = findEntries(self.selectedKeys, self.bibText,
                                        self.fieldText)
            self.tbox.settext(self.original)
            #sets title of root menu
            if(self.parent.title()[:1] != '*'):
                self.parent.title("*"+self.parent.title())
        self.cancel('Close')

    ##Returns path of the file opened
    def openFileName(self):
        fileName = tkFileDialog.askopenfilename(**self.imp_opt)
        if (fileName): return fileName

    def execute(self, result):
        if (result=='Close' or result==None): self.cancel(result)

    ##Close dialog
    def cancel(self, result):
        self.dialog.deactivate(result)

##------------------------------------------------------------------------------
##  Field Menu
##------------------------------------------------------------------------------
        
class FieldMenu:
    def __init__(self, parent, fieldText, Constants):
        self.parent = parent
        self.Constants = Constants
        self.fieldText = fieldText
        self.entriesDefault = self.Constants._entriesDefault()
        
        self.dialog = Pmw.Dialog(self.parent,
                                 title='Change Default Field Order',
                                 buttonboxpos = 'w',
                                 command = self.buttonCommands,
                                 buttons=('Import field order\nfrom file',
                                          'Export current\nfield order to file',
                                          'Set current\nfield order as default',
                                          'Use default\norder',
                                          'Close'))

        self.fieldOrders = Pmw.ScrolledText(self.dialog.interior(),
                                            label_text='Current Field Order:',
                                            labelpos='nw',
                                            usehullsize = 1,
                                            hull_width = 200,
                                            hull_heigh = 500
                                            )
        self.fieldOrders.pack(padx = 5, pady = 5)
        self.fieldOrders.settext(self.fieldText)
        
        self.field_opt = {'defaultextension':'.txt',
                        'filetypes':[('text files','.txt')],
                        'parent': self.parent, 'title': 'Import File'}

    ##Returns path of the file opened
    def openFileName(self):
        fileName = tkFileDialog.askopenfilename(**self.field_opt)
        if (fileName): return fileName

    ##Returns path of file name to be saved
    def saveFileName(self):
        fileName = tkFileDialog.asksaveasfilename(**self.field_opt)
        if (fileName): return fileName

    def returnValue(self):
        return (self.fieldText, self.entriesDefault)

    #Upload fields from external .txt file
    def importFields(self):
        path = self.openFileName()
        if (path):
            self.fieldOrders.settext(loadTextString(path))

    #uploads field order from textbox to parent
    def uploadFields(self):
        text = self.fieldOrders.getvalue().encode('ascii','ignore').upper()
        self.fieldText = text
        tempList = text.split('\n')
        textList = []
        for l in tempList:
            textList.append(l+'\n')
        for e in self.entriesDefault:
            try:
                newFields = getTypeFields(e, textList)
                if (newFields!=[]):
                    self.entriesDefault[e] = newFields
            except:
                pass
        self.dialog.deactivate()

    def buttonCommands(self, button):
        if (button == 'Use default\norder'):
            self.entriesDefault = self.Constants._entriesDefault()
            self.fieldText = self.Constants._fieldText()
            self.dialog.deactivate()
        elif (button == 'Import field order\nfrom file'):
            self.importFields()
        elif (button == 'Export current\nfield order to file'):
            path = self.saveFileName()
            if (path):
                open(path, 'w+').write(self.fieldOrders.getvalue())
        elif (button == 'Set current\nfield order as default'):
            self.uploadFields()
        elif (button == 'Close' or button == None):
            self.dialog.deactivate()


##------------------------------------------------------------------------------
##  Main window
##------------------------------------------------------------------------------
        
class Main:
    def __init__(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('inputFile', nargs='?',
                            help="Input .bib or .db filename/path")
        self.args = parser.parse_args()

        self.Constants = Constants()
        
        self.entriesDefault = self.Constants._entriesDefault()
        self.fieldText = self.Constants._fieldText()
        self.allFields = self.Constants._allFields()
        self.currdir = self.Constants.currdir

        self.exported = True
        self.filepath = ''
        
        self.root = Pmw.initialise()
        self.root.protocol('WM_DELETE_WINDOW', self.checkSaved)

        ##Bind user key-presses
        self.root.bind("<KeyPress>", self.keyPressed)
      
        self.menuBar() ##Creates menu bar at top of window

        self.fontSize = 10

        self.root.title("BibTeX Editor") ##Window title
        dFont = tkFont.Font(family='Courier', size=self.fontSize) ##Default font


        ##Initialize text box, including size and font
        self.tbox1 = Pmw.HistoryText(self.root, usehullsize=1,
                                     hull_width=800, hull_height=500,
                                     text_wrap='none', text_font=dFont,
                                     rowheader=1,
                                     rowheader_width=4,
                                     Header_font=dFont,
                                     compresstail=1)
        self.tbox1.configure(Header_state = 'disabled')
        self.tbox1.tag_configure("highlight", background="#ffff00")
        self.lineNums = ''
        self.updateLineNums()
        self.addToHistory()

        self.findBar = Pmw.EntryField(self.root, labelpos='w',
                                      label_text='Find: ', entry_width=100,
                                      validate=self.validateFind)

        self.findBar.pack(fill='x', expand=0, padx=10, pady=5)

        self.tbox1.pack(side=LEFT, padx=2, pady=2, fill='both', expand=1)

        self.checkCommandLine()
    
        self.root.mainloop()

    ##Updates history whenever user presses a key
    def keyPressed(self, event):
        keysym = event.keysym
        
        self.addToHistory()
        self.exported = False
        self.checkExported()

        ##Check if ctrl and shift keys are down
        ctrl  = ((event.state & 0x0004) != 0)
        shift = ((event.state & 0x0001) != 0)

        ##Keyboard shortcuts
        if (ctrl):
            if ((keysym=='o' or keysym=='O') and shift==False):
                self.importFile()
            elif ((keysym=='s' or keysym=='S') and shift==False):
                self.saveFile()
            elif ((keysym=='i' or keysym=='I') and shift==False):
                self.insertEntry()
            elif ((keysym=='z' or keysym=='Z') and shift==False):
                self.goToPrev()
            elif ((keysym=='z' or keysym=='Z') and shift==True):
                self.goToNext()
            elif ((keysym=='a' or keysym=='A') and shift==False):
                self.selectAll()
            elif ((keysym=='p' or keysym=='P') and shift==False):
                self.editFormat()

    ##Highlights entire selection in text box
    def selectAll(self):
        self.tbox1.tag_add(SEL, "1.0", END)
        self.tbox1.mark_set(INSERT, "1.0")
        self.tbox1.see(INSERT)

    def menuBar(self):
        self.menubar = Menu(self.root)

        ##Create "File" menu
        menu = Menu(self.menubar, tearoff=0) ##Reset menu button commands
        self.menubar.add_cascade(label="File", menu=menu)
        menu.add_command(label="Import  (Ctrl+O)", command=self.importFile)
        menu.add_command(label="Save .bib (Ctr+S)", command=self.saveFile)
        menu.add_separator()
        menu.add_command(label="Save AS .bib", command=self.exportBibFile)
        menu.add_command(label="Save AS HTML", command=self.exportHTMLFile)
        menu.add_command(label="Save AS .db", command=self.exportDBFile)
        menu.add_separator()
        menu.add_command(label="Exit", command=self.root.destroy)

        ##Create "Edit" menu
        menu = Menu(self.menubar, tearoff=0) ##Reset menu button commands
        self.menubar.add_cascade(label="Edit", menu=menu)
        menu.add_command(label="Undo  (Ctrl+Z)", command=self.goToPrev)
        menu.add_command(label="Redo  (Ctrl+Shift+Z)", command=self.goToNext)
        menu.add_separator()
        menu.add_command(label="Insert Bib Entry  (Ctrl+I)",
                         command=self.insertEntry)
        menu.add_command(label="Pull Keys  (Ctrl+P)", command=self.pullKeys)
        menu.add_separator()
        menu.add_command(label="Unicode check", command=self.checkUnicode)
        menu.add_command(label="Format", command=self.editFormat)
        menu.add_command(label="Sort", command=self.sortEntries)

        ##Create "Options" menu        
        menu = Menu(self.menubar, tearoff=0) ##Reset menu button commands
        self.menubar.add_cascade(label="Options", menu=menu)
        menu.add_command(label="Change default\n field order",
                         command=self.changeFieldOrder)

        ##Create "Help" menu
        menu = Menu(self.menubar, tearoff=0) ##Reset menu button commands
        self.menubar.add_cascade(label="Help", menu=menu)
        menu.add_command(label="BibTeX Editor Help", command=self.helpMenu)

        ##Options for importing a file
        self.imp_opt = {'defaultextension':'.bib',
                        'filetypes':[('BibTeX files','.bib'),
                                     ('Database Files','.db')],
                        'parent': self.root, 'title': 'Import File',
                        'multiple':False}

        self.field_opt = {'defaultextension':'.txt',
                        'filetypes':[('text files','.txt')],
                        'parent': self.root, 'title': 'Import File'}

        ##Options for exporting a .bib file
        self.exp_bib_opt = {'defaultextension': '.bib', 'filetypes':
                        [('BibTeX file','.bib')], 'parent': self.root,
                        'title': 'Export BibTeX File'}

        #Options for exportiing a .htm file
        self.exp_htm_opt = {'defaultextension': '.htm', 'filetypes':
                        [('HTML file','.htm .html')], 'parent': self.root,
                        'title': 'Export HTML File'}

        #Options for exporting a .db file
        self.exp_db_opt = {'defaultextension': '.db', 'filetypes':
                        [('Database file', '.db')], 'parent': self.root,
                        'title': 'Export Database File'}

        self.root.config(menu=self.menubar)

    ##Returns path of the file opened
    def openFileName(self, imp_opt):
        fileName = tkFileDialog.askopenfilename(**imp_opt)
        if (fileName):
            return fileName

    ##Returns path of file name to be saved
    def saveFileName(self, exp_opt):
        fileName = tkFileDialog.asksaveasfilename(**exp_opt)
        if (fileName):
            return fileName

    ##Overwrite the .bib file with new version (save as is)
    def saveFile(self):
        if (self.filepath!='.bib'):
            new = self.tbox1.get(first=None, last=None)
            self.new = \
                unicodedata.normalize('NFKD',new).encode('ascii','ignore')
            try:
                open("temp.bib", 'w+').write(self.new)
                os.remove(self.filepath)
                os.rename("temp.bib", self.filepath)
                self.root.title('BibTeX Editor - '+self.filepath)
                self.loadText(self.filepath)
                self.exported = True
                self.checkExported()
            except:
                RaiseError('File Error', self.filepath+'\nCannot overwrite file.')
                os.remove("temp.bib")
        else:
            self.exportBibFile()

    ##Load the file into textbox
    def importFile(self):
        path = self.openFileName(self.imp_opt)
        if (path):
            self.loadText(path)

    #checks Command Line for an input file
    def checkCommandLine(self):
        if (self.args.inputFile):
            self.path = self.args.inputFile
            if (not os.path.isfile(self.args.inputFile)):
                RaiseError('File Error', self.args.inputFile+'\ncannot be found')
                self.path = ''
                self.importFile()
            else:
                self.loadText(self.args.inputFile)

    #Loads text into textbox
    def loadText(self, path):
        self.filepath = path
        if (path[-4:]==u'.bib'):
            self.original = loadTextString(path)
            self.tbox1.settext(self.original)
            self.root.title('BibTeX Editor - '+path)
            self.exported = False
            self.checkExported()
        elif (path[-3:]==u'.db'):
            a = PromptDB(self.root, self.tbox1, path, self.Constants)
            a.openFile()
            a.tbl.activate()
            self.root.title('BibTeX Editor - '+path)
            self.exported = False
            self.checkExported()
        else:
            RaiseError('File Error', path+'\nInvalid file extension')
            self.importFile()
        self.updateLineNums()
        self.addToHistory()

    ##Check for non-ascii characters in file and raise message
    def checkUnicode(self):
        text = self.tbox1.get(first=None,last=None)
        message = checkUnicode(text)

        RaiseMessage('Unicode check',message)

    ##Export all contents of text box to .bib file
    def exportBibFile(self):
        path = self.saveFileName(self.exp_bib_opt)
        if (path):
            if (os.path.exists(path)):
                self.filepath = path
                new = self.tbox1.get(first=None, last=None)
                self.new = \
                    unicodedata.normalize('NFKD',new).encode('ascii','ignore')
                try:
                    open("temp.bib", 'w+').write(self.new)
                    os.remove(self.filepath)
                    os.rename("temp.bib", self.filepath)
                    self.root.title('BibTeX Editor - '+self.filepath)
                    self.loadText(self.filepath)
                    self.exported = True
                    self.checkExported()
                except:
                    RaiseError('File Error', self.filepath+'\nCannot overwrite file.')
                    os.remove("temp.bib")
            else:
                self.filepath = path
                new = self.tbox1.get(first=None, last=None)
                self.new = \
                    unicodedata.normalize('NFKD',new).encode('ascii','ignore')
                try:
                    open("temp.bib", 'w+').write(self.new)
                    os.rename("temp.bib", self.filepath)
                    self.root.title('BibTeX Editor - '+self.filepath)
                    self.loadText(self.filepath)
                    self.exported = True
                    self.checkExported()
                except:
                    RaiseError('File Error', self.filepath+'\nCannot write file.')
                    os.remove("temp.bib")
                

    #Export to .htm file
    def exportHTMLFile(self):
        path = self.saveFileName(self.exp_htm_opt)
        if (path):
            self.filepath = path
            bibText = self.tbox1.get(first=None, last=None)
            try:
                self.new = outHTML(bibText)
            except:
                RaiseError('File Error', self.filepath+'\nText cannot be formatted to HTML.')
            if (os.path.exists(path)):
                self.filepath = path
                try:
                    open("temp.htm", 'w+').write(self.new)
                    os.remove(self.filepath)
                    os.rename("temp.htm", self.filepath)
                    self.root.title('BibTeX Editor - '+self.filepath)
                    self.exported = True
                    self.checkExported()
                except:
                    RaiseError('File Error', self.filepath+'\nCannot overwrite file.')
                    os.remove("temp.htm")
            else:
                self.filepath = path
                try:
                    open("temp.htm", 'w+').write(self.new)
                    os.rename("temp.htm", self.filepath)
                    self.root.title('BibTeX Editor - '+self.filepath)
                    self.exported = True
                    self.checkExported()
                except:
                    RaiseError('File Error', self.filepath+'\nCannot write file.')
                    os.remove("temp.htm")

    def exportDBFile(self):
        path = self.saveFileName(self.exp_db_opt)
        if (path):
            self.filepath = path
            a = PromptDB(self.root, self.tbox1, path, self.Constants)
            a.saveFile()
            a.tbl.activate()
            self.root.title('BibTeX Editor - '+path)
            self.exported = True

    ##Insert new entry into the current displayed BibTeX 
    def insertEntry(self):
        a = InsertEntry(self.root, self.tbox1, self.entriesDefault,
                        self.allFields, self.Constants)
        a.dialog.activate()
        self.updateLineNums()
        self.addToHistory()

    #displays list of keys in new window
    def pullKeys(self):
        a = KeyMenu(self.root, self.tbox1, self.fieldText)
        a.dialog.activate()
        self.updateLineNums()
        self.addToHistory()

    ##Change the format of the BibTeX to Maxion Style
    def editFormat(self):
        self.bibs = bib2Dict(self.tbox1.get(first=None, last=None))

        if (type(self.bibs)==str):
            RaiseError('BibTeX Error', self.bibs)
            return
        
        formatted = ''

        for key in self.bibs:
            formatted = formatted+formatBib(key, self.bibs[key], self.fieldText)

        self.tbox1.settext(formatted)
        self.updateLineNums()
        self.addToHistory()

    #sorts entries alphabetically by key
    def sortEntries(self):
        self.bibs = bib2Dict(self.tbox1.get(first=None,last=None))

        if (type(self.bibs)==str):
            RaiseError('BibTeX Error', self.bibs)
            return
        
        keys = sortKeys(self.bibs)
        sEntries = ''
        for key in keys:
            sEntries = sEntries+formatBib(key, self.bibs[key], self.fieldText)
        self.tbox1.settext(sEntries)
        self.updateLineNums()
        self.addToHistory()

    #creates pop-up with Information about bib editor
    def helpMenu(self):
        tkMessageBox.showinfo('Help', self.Constants._helpMessage())

    #updates root title if file has been changed
    def checkExported(self):
        if(not(self.exported) and self.root.title()[:1] != '*'):
            self.root.title("*"+self.root.title())
        elif(self.exported and self.root.title()[:1] == '*'):
            self.root.title(self.root.title()[1:])            

    #checks if file has been exported since last change
    def checkSaved(self):
        if(self.root.title()[:1] == "*"):
            reply = tkMessageBox.askquestion('Error',
                                        'Do you want to exit without saving?')
            if (reply == 'yes'):
                open(self.currdir+'\\fieldOrderDefault.txt', 'w+').write(
                    fields2Txt(self.entriesDefault))
                self.root.destroy()
        else:
            open(self.currdir+'\\fieldOrderDefault.txt', 'w+').write(
                fields2Txt(self.entriesDefault))
            self.root.destroy()

    #highlights all instances of the pattern
    def highlight_pattern(self, pattern, tag, start="1.0", end="end",
                          regexp=False):
        self.tbox1.mark_set("matchStart",start)
        self.tbox1.mark_set("matchEnd",start)
        self.tbox1.mark_set("searchLimit", end)

        count = IntVar()
        while True:
            index = self.tbox1.search(pattern, "matchEnd","searchLimit",
                                      nocase=True, count=count, regexp=regexp)
            if index == "": break
            self.tbox1.mark_set("matchStart", index)
            self.tbox1.mark_set("matchEnd", "%s+%sc" % (index,count.get()))
            self.tbox1.tag_add(tag, "matchStart", "matchEnd")

    #finds the first instance of the phrase and skips to it
    def find(self, phrase):
        self.tbox1.tag_delete("highlight")
        self.tbox1.tag_configure("highlight", background="#ffff00")
        first = self.tbox1.search(phrase, END, nocase=True)
        #goes to first instance of the phrase
        self.tbox1.see(first)
        self.highlight_pattern(phrase, "highlight")
        

    ##Check if phrase entered in find exists in current text
    def validateFind(self, phrase):
        text = self.tbox1.get(first=None, last=None)
        if (phrase.upper() in text.upper()):
            if(phrase != ''):
                self.find(phrase)
            else:
                self.tbox1.tag_delete("highlight")
                self.tbox1.tag_configure("highlight", background="#ffff00")
            return 1
        else:
            self.tbox1.tag_delete("highlight")
            return -1

    #get current line number
    def getLineNums(self):
        text = self.tbox1.get()
        lineNums = ''
        for l in xrange(1, text.count('\n')+1):
            if (l == 1):
                lineNums = (str(l))
            else:
                lineNums = lineNums+'\n'+(str(l))
        return lineNums

    #updates line numbers
    def updateLineNums(self):
        if (self.lineNums.count('\n') != (self.tbox1.get().count('\n')+1)):
            currentLineNums = self.getLineNums()
            if (self.tbox1.get().count('\n') > self.lineNums.count('\n')):
                self.tbox1.configure(Header_state='normal')
                self.tbox1.component('rowheader').insert(END,
                                        currentLineNums[len(self.lineNums):])
                self.tbox1.configure(Header_state='disabled')
            else:
                self.tbox1.configure(Header_state='normal')
                start = str(float(currentLineNums.count('\n'))+2)
                self.tbox1.component('rowheader').delete(start, END)
                self.tbox1.configure(Header_state='disabled')
            self.lineNums = currentLineNums

    #undo
    def goToPrev(self):
        self.tbox1.prev()
        self.updateLineNums()

    #redo
    def goToNext(self):
        self.tbox1.next()
        self.updateLineNums()

    def addToHistory(self):
        self.tbox1.addhistory()
        prev = self.tbox1.gethistory()[-1][1]
        if (self.tbox1.get() != prev):
            self.updateLineNums()

    #requests file to change field orders
    def changeFieldOrder(self):
        f = FieldMenu(self.root, self.fieldText, self.Constants)
        f.dialog.activate()
        (self.fieldText, self.entriesDefault) = f.returnValue()
        for k in self.entriesDefault:
            for i in self.entriesDefault[k]:
                if i not in self.allFields:
                    self.allFields.append(i)
        self.allFields.sort()
        


##------------------------------------------------------------------------------
##  run program
##------------------------------------------------------------------------------

Main()
