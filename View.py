import Tkinter as tk
import tkMessageBox
import webbrowser
import os
import sys


class View(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master=master)
        self.controller = None
        self.grid()
        self.master.protocol('WM_DELETE_WINDOW', self.exit_app)
        self.master.title('StarCategorizer')
        self.master.iconbitmap(self.resource_path('logo.ico'))
        self.master.geometry('350x120')
        self.apiKeyLabel = tk.Label(self, text=" Steam API Key               ")
        self.steamIDLabel = tk.Label(self, text=" SteamID64     ")
        self.leftInfoLabel = tk.Label(self, text="")
        self.rightInfoLabel = tk.Label(self, text="")

        self.steamCategories = {}
        self.profilePublic = tk.BooleanVar()
        with open(self.resource_path('categories.txt'), 'r') as F:
            for line in F:
                k, v = line.strip().split('\t\t')
                self.steamCategories[int(k.strip())] = [v.strip(), tk.BooleanVar(False)]

        self.apiKeyEntry = tk.Entry(self, width=34)
        self.steamIDEntry = tk.Entry(self, width=18)
        self.cancelButton = tk.Button(self, text='Cancel', state='disabled')
        self.startButton = tk.Button(self, text='Start', state='normal')

        self.publicBox = tk.Checkbutton(self, text='public profile')
        self.apiKeyLabel.grid(row=0, column=0, sticky='W')
        self.steamIDLabel.grid(row=1, column=0, sticky='W')
        self.leftInfoLabel.grid(row=2, column=0)
        self.rightInfoLabel.grid(row=2, column=1)

        self.apiKeyEntry.grid(row=0, column=1, columnspan=2)
        self.steamIDEntry.grid(row=1, column=1, sticky='W')
        self.publicBox.grid(row=1, column=2)

        self.cancelButton.grid(row=3, column=1)
        self.startButton.grid(row=3, column=2)
        self.publicBox.configure(variable=self.profilePublic, command=self.box_switch_public)

        self.startButton.config(command=lambda: self.controller.button_start())
        self.cancelButton.config(command=lambda: self.controller.button_cancel())

        #menu
        self.menuBar = tk.Menu(self.master, tearoff=0)
        self.helpMenu = tk.Menu(self.menuBar, tearoff=0)
        self.settingMenu = tk.Menu(self.menuBar, tearoff=0)

        self.master.config(menu=self.menuBar)

        self.settingMenu.add_command(label='Categories', command=self.window_categories)
        self.settingMenu.add_separator()
        self.settingMenu.add_command(label='Exit', command=self.exit_app)
        self.menuBar.add_cascade(label="Settings", menu=self.settingMenu)
        self.helpMenu.add_command(label='About', command=self.window_about)
        self.menuBar.add_cascade(label="Help", menu=self.helpMenu)

    def box_switch_public(self):

        if self.profilePublic.get():
            self.leftInfoLabel.configure(text='')
            self.steamIDLabel.configure(text='CustomUrl/SteamID64')
            self.apiKeyEntry.configure(state='disabled')
        elif not self.profilePublic.get():
            self.leftInfoLabel.configure(text='')
            self.steamIDLabel.configure(text=' SteamID64     ')
            self.apiKeyEntry.configure(state='normal')

    def window_about(self):
        window = tk.Toplevel(self)
        window.geometry('300x100')
        window.resizable(width=False, height=False)
        window.resizable(width=False, height=False)
        window.title('About')
        window.iconbitmap(self.resource_path('logo.ico'))
        copyright_symbol = u"\u00A9"
        window.infoLabel = tk.Label(window, text="\nCopyright " + copyright_symbol + "2017 Mastercorp\n MIT License\n"
                                                                                     "Version 2.1")
        window.infoLabel.pack()
        window.infoLabel = tk.Label(window, text="https://github.com/Mastercorp/StarCategorizer",
                                    fg="blue", cursor="hand2")
        window.infoLabel.bind("<Button-1>", self.open_web)
        window.infoLabel.pack()

    def window_categories(self):
        window = tk.Toplevel(self)

        window.resizable(width=False, height=False)
        window.resizable(width=False, height=False)
        window.title('Categories')
        window.iconbitmap(self.resource_path('logo.ico'))
        for idx, keys in enumerate(sorted(self.steamCategories)):
            var = self.steamCategories[keys][1]
            chk = tk.Checkbutton(window, text=self.steamCategories[keys][0], variable=var)
            chk.grid(row=idx // 5, column=idx % 5, sticky='W')

    @staticmethod
    def open_web(event):
        webbrowser.open_new(r"https://github.com/Mastercorp/StarCategorizer")

    def exit_app(self):
            if tkMessageBox.askokcancel("Confirm Exit", "Are you sure you want to exit StarCategorizer?"):
                self.master.destroy()

    def register(self, controller):
        self.controller = controller

    def resource_path(self, relative_path):
        """ Get absolute path to resource, works for PyInstaller """
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)
