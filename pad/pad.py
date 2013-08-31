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
    from tkinter.simpledialog import askstring
else:
    import Tkinter as tk
    import ttk
    from tkFileDialog import (askdirectory, askopenfilename,
         asksaveasfilename)
    from tkMessageBox import (showinfo, showwarning, showerror,
         askquestion, askokcancel, askyesno, askretrycancel)
    from tkSimpleDialog import askstring


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
        self.text.insert(tk.END, text)
#       self.text.mark_set(tk.INSERT, "1.0")
        self.text.focus()

    def setText(self, text=""):
        self.text.delete(1.0, tk.END)
        self.appendText(text)

    def getText(self):
        return self.text.get("1.0", tk.END+'-1c')

    def bind(self, event, handler, add=None):
        self.text.bind(event, handler, add)


class StatusBar(tk.Frame):
    def __init__(self, parent=None):
        tk.Frame.__init__(self, parent)

        self.labels = {}

    def setLabel(self, name=0, side=tk.LEFT, **kargs):
        label = tk.Label(self, bd=1, relief=tk.SUNKEN, anchor=tk.W, **kargs)
        label.pack(side=side)
        self.labels[name] = label

        return label

    def setText(self, text="", name=0):
        if name in self.labels:
            label = self.labels[name]
        else:
            label = self.setLabel(name)
            self.labels[name] = label

        label.config(text=text)


class Menu(tk.Menu):
#   def __init__(self, master=None, **options):
#       tk.Menu.__init__(self, master, **options)

    def add_command2(self, **options):
        tk.Menu.add_command(self, **options)

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
        menu.add_command2(command=self.onEditCut, label="Cut", accelerator="Ctrl+X", underline=1)
        menu.add_command2(command=self.onEditCopy, label="Copy", accelerator="Ctrl+C", underline=0)
        menu.add_command2(command=self.onEditPaste, label="Paste", accelerator="Ctrl+V", underline=0)
        menu.add_command(command=self.onEditDelete, label="Delete", underline=0)
        menu.add_separator()
        menu.add_command(command=self.onEditSelectAll, label="Select all", accelerator="Ctrl+A", underline=7)

        menu = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Search", menu=menu, underline=0)
        menu.add_command(command=self.onSearchFind, label="Find", accelerator="Ctrl+F", underline=0)
        menu.add_command(command=self.onSearchFind, label="Replace", accelerator="Ctrl+H", underline=0)
        menu.add_command2(command=self.onSearchFind, label="Find next", accelerator="F3", underline=0)
        menu.add_command(command=self.onSearchFind, label="Find previous", accelerator="Shift-F3", underline=0)

        menu = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Help", menu=menu, underline=0)
        menu.add_command(command=self.onHelpAbout, label="About", underline=0)

        self.config(menu=self.menubar)

        ### Widgets ###

        # Text Widget
        self.text = ScrolledText(self)
        self.text.pack(fill=tk.BOTH, expand=tk.YES)

        # Status Widget
        self.status = StatusBar(self)
        self.status.pack(fill=tk.X)

        self.status.setLabel("position", width=20)
        self.status.setLabel("symbol", width=10)
#       self.status.setLabel("highlight", width=10)
#       self.status.setLabel("eol", width=10)
#       self.status.setLabel("codepage", width=20)

        ### Bind ###

        self.protocol('WM_DELETE_WINDOW', self.onFileExit)
        self.text.bind('<Key>', self.onSelection)
        self.text.bind('<Button-1>', self.onSelection)
        self.text.bind('<Button-3>', self.onRButton)
        self.bind('<<Selection>>', self.onSelection)
        self.text.bind('<<Modified>>', self.onSelection)

        ### Initial ###

        self.cursorinfo()

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
        self.filename = ""
        self.filetype = None
        self.text.setText()
        self.status.setText(self.filename)

    def onFileSave(self, event=None):
        print('dummy')

    def onFileSaveAs(self, event=None):
        print('dummy')

    def onFileInfo(self, event=None):
        print('dummy')

    def onFilePrint(self, event=None):
        print('dummy')

    def onFilePrintSettings(self, event=None):
        print('dummy')

    def onFilePreview(self, event=None):
        print('dummy')

    def onFileExit(self, event=None):
        res = askokcancel("Exit", "Really quit?")
        if res:
            self.destroy()

    def onEditUndo(self, event=None):
        print('dummy')

    def onEditRedo(self, event=None):
        print('dummy')

    def onEditCut(self, event=None):
        if self.text.text.tag_ranges(tk.SEL):
            text = self.text.text.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.text.text.delete(tk.SEL_FIRST, tk.SEL_LAST)
            self.clipboard_clear()
            self.clipboard_append(text)

    def onEditCopy(self, event=None):
        if self.text.text.tag_ranges(tk.SEL):
            text = self.text.text.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.clipboard_clear()
            self.clipboard_append(text)

    def onEditPaste(self, event=None):
        text = self.selection_get(selection='CLIPBOARD')
        self.text.text.insert(tk.INSERT, text)

    def onEditDelete(self, event=None):
        if self.text.text.tag_ranges(tk.SEL):
            text = self.text.text.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.text.text.delete(tk.SEL_FIRST, tk.SEL_LAST)

    def onEditSelectAll(self, event=None):
#       self.text.text.tag_remove(tk.SEL, "1.0", tk.END)
        self.text.text.tag_add(tk.SEL, "1.0", tk.END)
        self.text.text.mark_set(tk.INSERT, "1.0")
        self.text.text.see(tk.INSERT)

    def onSearchFind(self, event=None):
        target = askstring("Find", "Enter string for searching")
        if target:
            start = self.text.text.search(target, tk.INSERT, tk.END)
            if start:
#               self.text.text.tag_remove(tk.SEL, "1.0", tk.END)
                stop = start + '+{0}c'.format(len(target))
                self.text.text.tag_add(tk.SEL, start, stop)
                self.text.text.mark_set(tk.INSERT, start)
                self.text.text.see(tk.INSERT)
                self.text.text.focus()

    def onHelpAbout(self, event=None):
        text = """{0}\n{1}\nVersion {2}\n
Python: {3}
Package: {4}
""".format(__pkgname__, __description__, __version__,
           sys.version, __package__)
        showinfo("About", text)

    def onRButton(self, event=None):
        print("Right")

    def onSelection(self, event=None):
        self.cursorinfo()

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
        self.cursorinfo()
        self.status.setText(filename)

    def cursorinfo(self):
        position = self.text.text.index(tk.CURRENT)

        symbol = self.text.text.get(position)
        self.status.setText(repr(symbol), "symbol")

        if self.text.text.tag_ranges(tk.SEL):
            start, stop = self.text.text.tag_ranges(tk.SEL)
            position += " [{0}:{1}]".format(start.string, stop.string)

        self.status.setText(position, "position")



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
