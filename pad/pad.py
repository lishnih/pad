#!/usr/bin/env python
# coding=utf-8
# Stan 2013-08-21

from __future__ import ( division, absolute_import,
                         print_function, unicode_literals )

import sys, os, logging


__pkgname__ = os.path.basename(os.path.dirname(os.path.abspath(__file__)))
__description__ = "Simple text editor based on Tk."
__version__ = "0.1"


if sys.version_info >= (3,):
    import tkinter as tk
    from tkinter import ttk
    from tkinter.filedialog import (askdirectory, askopenfilename,
         asksaveasfilename)
    from tkinter.messagebox import (showinfo, showwarning, showerror,
         askquestion, askokcancel, askyesno, askretrycancel)
else:
    import Tkinter as tk
    import ttk
    from tkFileDialog import (askdirectory, askopenfilename,
         asksaveasfilename)
    from tkMessageBox import (showinfo, showwarning, showerror,
         askquestion, askokcancel, askyesno, askretrycancel)


class ScrolledText(tk.Frame):
    def __init__(self, parent=None):
        tk.Frame.__init__(self, parent)             
        self.pack(fill=tk.BOTH, expand=tk.YES)

        self.text = tk.Text(self, relief=tk.SUNKEN)
        sbar = tk.Scrollbar(self)
        sbar.config(command=self.text.yview)                  
        self.text.config(yscrollcommand=sbar.set)           

        sbar.pack(fill=tk.Y, side=tk.RIGHT)                   
        self.text.pack(fill=tk.BOTH, side=tk.LEFT, expand=tk.YES)     

        self.text.config(font=('courier', 9, 'normal'))

    def appendText(self, text=""):
        self.text.insert(tk.INSERT, text)
        self.text.mark_set(INSERT, '1.0')              
        self.text.focus()                                

    def setText(self, text=""):
        self.text.delete(1.0, tk.END)
        self.appendText(text)

    def getText(self):                               
        return self.text.get('1.0', tk.END+'-1c')         

    def bind(self, event, handler, add=None):                               
        self.text.bind(event, handler, add)


class AppUI(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.title("tkPad")

        ### Menu ###

        self.menubar = tk.Menu(self)

        menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="File", menu=menu)
        menu.add_command(command=self.onFileNew, label="New")
        menu.add_command(command=self.onFileLoad, label="Load")
        menu.add_command(command=self.onFileClose, label="Close")
        menu.add_separator()
        menu.add_command(command=self.onFileSave, label="Save")
        menu.add_command(command=self.onFileSaveAs, label="Save As...")
        menu.add_separator()
        menu.add_command(command=self.onFileInfo, label="Info")
        menu.add_separator()
        menu.add_command(command=self.onFilePrint, label="Print")
        menu.add_command(command=self.onFilePrintSettings, label="Print settings")
        menu.add_command(command=self.onFilePreview, label="Preview")
        menu.add_separator()
        menu.add_command(command=self.onFileExit, label="Exit")

        menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Edit", menu=menu)
        menu.add_command(command=self.onEditUndo, label="Undo")
        menu.add_command(command=self.onEditRedo, label="Redo")
        menu.add_separator()
        menu.add_command(command=self.onEditCut, label="Cut")
        menu.add_command(command=self.onEditCopy, label="Copy")
        menu.add_command(command=self.onEditPaste, label="Paste")
        menu.add_command(command=self.onEditDelete, label="Delete")
        menu.add_separator()
        menu.add_command(command=self.onEditSelectAll, label="Select all")

        menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Help", menu=menu)
        menu.add_command(command=self.onHelpAbout, label="About")

        self.config(menu=self.menubar)

        ### Widgets ###

        # Text Widget
        self.text1 = ScrolledText()

        # Status Widget
        self.status = tk.StringVar()
        label1 = tk.Label(self, textvariable=self.status, anchor=tk.W)

        ### Grid widgets ###

        self.text1.pack(fill=tk.BOTH, expand=1)
        label1.pack(fill=tk.X)
    
        ### Bind ###

        self.protocol('WM_DELETE_WINDOW', self.onFileExit)
        self.text1.bind("<Button-3>", self.onRButton)

        ### Initial ###

        self.update_idletasks()
        self.minsize(self.winfo_reqwidth(), self.winfo_reqheight())

    def setStatus(self, text=""):
        self.status.set(text)

    ### Events ###

    def onFileNew(self):
        pass

    def onFileLoad(self):
        pass

    def onFileClose(self):
        pass

    def onFileSave(self):
        pass

    def onFileSaveAs(self):
        pass

    def onFileInfo(self):
        pass

    def onFilePrint(self):
        pass

    def onFilePrintSettings(self):
        pass

    def onFilePreview(self):
        pass

    def onFileExit(self):
        res = askokcancel("Exit", "Really quit?")
        if res:
            self.destroy()

    def onEditUndo(self):
        pass

    def onEditRedo(self):
        pass

    def onEditCut(self):
        pass

    def onEditCopy(self):
        pass

    def onEditPaste(self):
        pass

    def onEditDelete(self):
        pass

    def onEditSelectAll(self):
        pass

    def onRButton(self, event):
        print("Right")

    def onHelpAbout(self):
        text = """{0}\n{1}\nVersion {2}\n
Python: {3}
Package: {4}
""".format(__pkgname__, __description__, __version__,
           sys.version, __package__)
        showinfo("About", text)



def main(args):
    root = AppUI()
    for i in args.files:
        print(i)
    root.mainloop()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    import argparse

    parser = argparse.ArgumentParser(description=__description__)
    parser.add_argument('files', nargs='*',
                        help='files to open')

    if sys.version_info >= (3,):
        argv = sys.argv
    else:
        fse = sys.getfilesystemencoding()
        argv = [i.decode(fse) for i in sys.argv]

    args = parser.parse_args(argv[1:])

    sys.exit(main(args))
