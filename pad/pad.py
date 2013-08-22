#!/usr/bin/env python
# coding=utf-8
# Stan 2013-08-21

from __future__ import ( division, absolute_import,
                         print_function, unicode_literals )

import sys, os, re, codecs, logging


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

        self.text = tk.Text(self, relief=tk.SUNKEN)
        self.text.pack(fill=tk.BOTH, side=tk.LEFT, expand=tk.YES)

        sbar = tk.Scrollbar(self)
        sbar.pack(fill=tk.Y, side=tk.RIGHT)
        sbar.config(command=self.text.yview)

        self.text.config(yscrollcommand=sbar.set)
        self.text.config(font=('Courier', 9, 'normal'))

    def appendText(self, text=""):
        self.text.insert(tk.INSERT, text)
        self.text.mark_set(tk.INSERT, '1.0')
        self.text.focus()

    def setText(self, text=""):
        self.text.delete(1.0, tk.END)
        self.appendText(text)

    def getText(self):
        return self.text.get('1.0', tk.END+'-1c')

    def bind(self, event, handler, add=None):
        self.text.bind(event, handler, add)


class Statusbar(tk.Frame):
    def __init__(self, parent=None):
        tk.Frame.__init__(self, parent)

        self.status = tk.StringVar()
        self.label = tk.Label(self, textvariable=self.status, anchor=tk.W)
        self.label.pack(fill=tk.X)

    def setText(self, text=""):
        self.status.set(text)


class Menu(tk.Menu):
    def __init__(self, master=None, **options):
        tk.Menu.__init__(self, master, **options)

    def add_command(self, **options):
        tk.Menu.add_command(self, **options)

        accelerator = options.get('accelerator')
        command = options.get('command')
        if accelerator:
            res = re.split('[+-]', accelerator)
            # Control, Ctrl, Option, Opt, Alt, Shift, Command, Cmd, Meta
            modifiers = [i.replace('Ctrl', 'Control').replace('Opt', 'Option').\
                         replace('Cmd', 'Command') for i in res[:-1]]
            modifiers = '-'.join(modifiers)
            key = res[-1]
            # Control, Option, Alt, Shift, Command, Meta
            if len(key) == 1:
                self.bind_all("<{0}-{1}>".format(modifiers, key.upper()), command)
                self.bind_all("<{0}-{1}>".format(modifiers, key.lower()), command)
            else:
                self.bind_all("<{0}-{1}>".format(modifiers, key), command)


class AppUI(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.title("tkPad")

        ### Vars ###

        self.filename = None
        self.filetype = None

        ### Menu ###

        self.menubar = tk.Menu(self)

        menu = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="File", menu=menu, underline=0)
        menu.add_command(command=self.onFileNew, label="New", accelerator="Ctrl+N", underline=0)
        menu.add_command(command=self.onFileLoad, label="Open", accelerator="Ctrl+O", underline=0)
        menu.add_command(command=self.onFileClose, label="Close", accelerator="Ctrl+F4", underline=0)
        menu.add_separator()
        menu.add_command(command=self.onFileSave, label="Save", accelerator="Ctrl+S", underline=0)
        menu.add_command(command=self.onFileSaveAs, label="Save As...")
        menu.add_separator()
        menu.add_command(command=self.onFileInfo, label="Info", underline=0)
        menu.add_separator()
        menu.add_command(command=self.onFilePrint, label="Print", accelerator="Ctrl+P", underline=0)
        menu.add_command(command=self.onFilePrintSettings, label="Print settings", accelerator="Alt+P")
        menu.add_command(command=self.onFilePreview, label="Preview", underline=3)
        menu.add_separator()
        menu.add_command(command=self.onFileExit, label="Exit", accelerator="Ctrl+Q", underline=1)

        menu = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Edit", menu=menu, underline=0)
        menu.add_command(command=self.onEditUndo, label="Undo", accelerator="Ctrl+Z", underline=0)
        menu.add_command(command=self.onEditRedo, label="Redo", accelerator="Ctrl+Shift-Z", underline=0)
        menu.add_separator()
        menu.add_command(command=self.onEditCut, label="Cut", accelerator="Ctrl+X", underline=1)
        menu.add_command(command=self.onEditCopy, label="Copy", accelerator="Ctrl+C", underline=0)
        menu.add_command(command=self.onEditPaste, label="Paste", accelerator="Ctrl+V", underline=0)
        menu.add_command(command=self.onEditDelete, label="Delete", underline=0)
        menu.add_separator()
        menu.add_command(command=self.onEditSelectAll, label="Select all", accelerator="Ctrl+A", underline=7)

        menu = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Help", menu=menu, underline=0)
        menu.add_command(command=self.onHelpAbout, label="About", underline=0)

        self.config(menu=self.menubar)

        ### Widgets ###

        # Text Widget
        self.text = ScrolledText(self)
        self.text.pack(fill=tk.BOTH, expand=tk.YES)

        # Status Widget
        self.status = Statusbar(self)
        self.status.pack(fill=tk.X)

        ### Bind ###

        self.protocol('WM_DELETE_WINDOW', self.onFileExit)
        self.text.bind("<Button-3>", self.onRButton)

        ### Initial ###

        self.update_idletasks()
        self.minsize(self.winfo_reqwidth(), self.winfo_reqheight())

    ### Events ###

    def onFileNew(self, event=None):
        self.filename = "New.txt"
        self.filetype = None
        self.text.setText()
        self.status.setText(self.filename)

    def onFileLoad(self, event=None):
        self.loadfileDialog()

    def onFileClose(self, event=None):
        self.filename = None
        self.filetype = None
        self.text.setText()
        self.status.setText(self.filename)

    def onFileSave(self, event=None):
        pass

    def onFileSaveAs(self, event=None):
        pass

    def onFileInfo(self, event=None):
        pass

    def onFilePrint(self, event=None):
        pass

    def onFilePrintSettings(self, event=None):
        pass

    def onFilePreview(self, event=None):
        pass

    def onFileExit(self, event=None):
        res = askokcancel("Exit", "Really quit?")
        if res:
            self.destroy()

    def onEditUndo(self, event=None):
        pass

    def onEditRedo(self, event=None):
        pass

    def onEditCut(self, event=None):
        pass

    def onEditCopy(self, event=None):
        pass

    def onEditPaste(self, event=None):
        pass

    def onEditDelete(self, event=None):
        pass

    def onEditSelectAll(self, event=None):
        pass

    def onRButton(self, event=None):
        print("Right")

    def onHelpAbout(self, event=None):
        text = """{0}\n{1}\nVersion {2}\n
Python: {3}
Package: {4}
""".format(__pkgname__, __description__, __version__,
           sys.version, __package__)
        showinfo("About", text)

    ### Dialogs ###

    def loadfileDialog(self):
        filename = askopenfilename(filetypes=[
                       ('All files', '*.*'),
                   ])
        if filename:
            self.loadfile(filename)

    ### Functions ###

    def loadfile(self, filename):
        if os.path.isfile(filename):
            with codecs.open(filename) as f:
                text = f.read()
                self.text.setText(text)

        self.filename = filename
        self.filetype = None
        self.status.setText(self.filename)



def main(args):
    root = AppUI()
    for i in args.files:
        root.loadfile(i)
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
