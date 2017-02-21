import Tkinter as tk
import tkMessageBox
import webbrowser
import os
import shutil
import urllib2
import threading
import json
import time


def resource_path(relative_path):
    """ Get absolute path to resource, works for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class ViewLayout(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master=master)
        self.grid()

        self.master.title('StarCategorizer')
        self.master.iconbitmap(resource_path('logo.ico'))
        self.master.geometry('350x120')
        self.apiKeyLabel = tk.Label(self, text=" Steam API Key               ")
        self.steamIDLabel = tk.Label(self, text=" SteamID64     ")
        self.leftInfoLabel = tk.Label(self, text="")
        self.rightInfoLabel = tk.Label(self, text="")

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


    def set_label(self, labelname, label_text):
        labelname.configure(text=label_text)

    def get_user_input(self):
        return self.apiKeyEntry.get(), self.steamIDEntry.get()


class Controller(object):
    def __init__(self):
        self.view = ViewLayout()
        self.create_menu()
        self.steamcategories = {}
        self.gameTimer = 0
        self.gameamount = 0
        self.alive = False
        self.profilepublic = tk.BooleanVar()
        with open(resource_path('categories.txt'), 'r') as F:
            for line in F:
                k, v = line.strip().split('\t\t')
                self.steamcategories[int(k.strip())] = [v.strip(), tk.BooleanVar(False)]

        self.view.startButton.config(command=self.button_start)
        self.view.cancelButton.config(command=self.button_cancel)
        self.view.publicBox.configure(variable=self.profilepublic, command=self.box_switch_public)

        self.view.master.protocol('WM_DELETE_WINDOW', self.exit_app)

        self.view.mainloop()

    def create_menu(self):
        self.view.menuBar = tk.Menu(self.view.master, tearoff=0)
        self.view.helpMenu = tk.Menu(self.view.menuBar, tearoff=0)
        self.view.settingMenu = tk.Menu(self.view.menuBar, tearoff=0)

        self.view.master.config(menu=self.view.menuBar)

        # self.view.settingMenu.add_command(label='Genres')
        self.view.settingMenu.add_command(label='Categories', command=self.window_categories)
        self.view.settingMenu.add_separator()
        self.view.settingMenu.add_command(label='Exit', command=self.exit_app)
        self.view.menuBar.add_cascade(label="Settings", menu=self.view.settingMenu)

        self.view.helpMenu.add_command(label='About', command=self.window_about)
        self.view.menuBar.add_cascade(label="Help", menu=self.view.helpMenu)

    def window_categories(self):
        window = tk.Toplevel(self.view)
        # window.geometry('300x100')
        # release after, else no focus
        # window.grab_set()
        window.resizable(width=False, height=False)
        window.resizable(width=False, height=False)
        window.title('Categories')
        window.iconbitmap(resource_path('logo.ico'))

        for idx, keys in enumerate(sorted(self.steamcategories)):
            var = self.steamcategories[keys][1]
            chk = tk.Checkbutton(window, text=self.steamcategories[keys][0], variable=var)
            chk.grid(row=idx // 5, column=idx % 5, sticky='W')

    def window_about(self):
        window = tk.Toplevel(self.view)
        window.geometry('300x100')
        window.resizable(width=False, height=False)
        window.resizable(width=False, height=False)
        window.title('About')
        window.iconbitmap(resource_path('logo.ico'))
        copyright_symbol = u"\u00A9"
        window.infoLabel = tk.Label(window, text="\nCopyright " + copyright_symbol + "2017 Mastercorp\n MIT License\n"
                                                                                     "Version 2.0")
        window.infoLabel.pack()
        window.infoLabel = tk.Label(window, text="https://github.com/Mastercorp/StarCategorizer",
                                    fg="blue", cursor="hand2")
        window.infoLabel.bind("<Button-1>", self.open_web)
        window.infoLabel.pack()

    @staticmethod
    def open_web(event):
        webbrowser.open_new(r"https://github.com/Mastercorp/StarCategorizer")

    def box_switch_public(self):

        if self.profilepublic.get():
            self.view.set_label(self.view.leftInfoLabel, '')
            self.view.set_label(self.view.steamIDLabel, 'CustomUrl/SteamID64')
            self.view.apiKeyEntry.configure(state='disabled')
        elif not self.profilepublic.get():
            self.view.set_label(self.view.leftInfoLabel, '')
            self.view.set_label(self.view.steamIDLabel, ' SteamID64     ')
            self.view.apiKeyEntry.configure(state='normal')

    pass

    def button_start(self):
        self.view.cancelButton.config(state='normal')
        self.view.startButton.config(state='disabled')
        self.view.publicBox.config(state='disabled')
        self.view.set_label(self.view.leftInfoLabel, '')
        self.view.set_label(self.view.rightInfoLabel, '')

        self.alive = True

        def callback():

            apiKey, steamID = self.view.get_user_input()
            if len(apiKey) == 32 and len(steamID) == 17 or (self.profilepublic.get() and len(steamID) > 0):
                self.backup_file()

                # delete all set tags, only exception is favorite
                if os.path.isfile('sharedconfig.vdf'):
                    customconfig = ""

                    # begin and end curly bracket after "Apps"
                    curlybegin = 0
                    curlyend = 0
                    with open('sharedconfig.vdf') as F:
                        # count open curly brackets
                        opencurly = 0
                        # is the "Apps" tag found in the file?
                        foundapps = False
                        for idx, line in enumerate(F):
                            searchtags = str(line.strip())
                            if searchtags.lower() == '"apps"' and not foundapps:
                                foundapps = True
                            if foundapps:
                                if searchtags == '{':
                                    if opencurly is 0:
                                        curlybegin = idx
                                    opencurly += 1
                                elif searchtags == '}':
                                    opencurly -= 1
                                    if opencurly is 0:
                                        curlyend = idx
                                        foundapps = False
                                        break

                        if curlybegin == curlyend:
                            self.view.set_label(self.view.leftInfoLabel, '')
                            self.view.set_label(self.view.rightInfoLabel, 'No games found in vdf')
                            self.view.startButton.config(state='normal')
                            self.view.cancelButton.config(state='disabled')
                            self.view.publicBox.config(state='normal')
                            self.alive = False
                            return

                        # to reset read() to beginning, else it stays at the end
                        F.seek(0)
                        first = False
                        second = False
                        # delete all "Tags" with the exception of
                        # search only in the "Apps" tag
                        # add 2 markers "StarCategory1 and 2 to make it easier to find "Apps" tag later
                        for idx, line in enumerate(F):
                            if idx == curlybegin:
                                customconfig += line
                                customconfig += 'StarCategory1\n'
                            elif curlybegin < idx < curlyend:
                                searchtags = str(line.strip())
                                if searchtags.lower() == '"tags"':
                                    first = True
                                    continue
                                elif first and searchtags == '{':
                                    second = True
                                    continue
                                elif first and second and searchtags == '}':
                                    first = False
                                    second = False
                                    continue
                                elif searchtags == '':
                                    continue
                                elif searchtags == '"0"\t\t"favorite"':
                                    customconfig += '\t\t\t\t\t\t"tags"\n'
                                    customconfig += '\t\t\t\t\t\t{\n'
                                    customconfig += '\t\t\t\t\t\t\t"0"\t\t"favorite"\n'
                                    customconfig += '\t\t\t\t\t\t}\n'
                                    continue
                                elif first and second:
                                    continue
                                    customconfig += line
                            elif idx == curlyend:
                                customconfig += 'StarCategory2\n'
                                customconfig += line
                            else:
                                customconfig += line
                    if not self.alive:
                        self.view.set_label(self.view.leftInfoLabel, 'cancelled')
                        self.restore_backup()
                        return

                        # apps + { + linebreakes and tabs
                    if customconfig.find('StarCategory1') > -1:
                        curlybegin = customconfig.find('StarCategory1') + 14

                    startaddgames = customconfig[:curlybegin]
                    endaddgames = customconfig[curlybegin:]
                    gameids = ""
                    if not self.profilepublic.get():
                        try:
                            responseinjson = urllib2.urlopen(
                                'https://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={}'
                                '&steamid={}&format=json'.format(apiKey, steamID))
                        except urllib2.HTTPError as e:
                            if e.code == 403:
                                self.view.set_label(self.view.leftInfoLabel, 'wrong key or id')
                                self.view.startButton.config(state='normal')
                                self.view.cancelButton.config(state='disabled')
                                self.view.publicBox.config(state='normal')
                                self.restore_backup()
                                return
                            else:
                                self.view.set_label(self.view.leftInfoLabel, 'http error')
                                self.view.startButton.config(state='normal')
                                self.view.cancelButton.config(state='disabled')
                                self.view.publicBox.config(state='normal')
                                self.restore_backup()
                                return
                        jsonusergames = json.loads(responseinjson.read())
                        self.gameamount = str(jsonusergames['response']['game_count'])

                        # add games between apps which are not present in  the current list
                        for game in jsonusergames['response']['games']:
                            appid = str(game['appid'])
                            # search for appid between Apps tag
                            if (customconfig[customconfig.find('StarCategory1'):customconfig.find('StarCategory2')].
                                    find('"' + appid + '"')) == -1:
                                startaddgames += '\t\t\t\t\t"' + appid + '"\n'
                                startaddgames += '\t\t\t\t\t{\n'
                                startaddgames += '\t\t\t\t\t}\n'
                            gameids += appid + '\n'

                    elif self.profilepublic.get():
                        try:
                            responseinhtml = urllib2.urlopen('https://steamcommunity.com/id/{}/games/?tab=all'
                                                             .format(steamID))
                            text = responseinhtml.read()
                            if text.find('rgGames = [{') == -1 and text.find('private_profile') > -1:

                                self.view.set_label(self.view.leftInfoLabel, 'profile not public')
                                self.view.startButton.config(state='normal')
                                self.view.cancelButton.config(state='disabled')
                                self.view.publicBox.config(state='normal')
                                self.restore_backup()
                                return
                            elif  text.find('rgGames = [{') == -1 and text.find('fatalerror'):
                                self.view.set_label(self.view.leftInfoLabel, 'wrong custom url')
                                self.view.startButton.config(state='normal')
                                self.view.cancelButton.config(state='disabled')
                                self.view.publicBox.config(state='normal')
                                self.restore_backup()
                                return

                            x = text.find('rgGames = [{') + 10
                            y = text[x:].find(';') + x

                            appid = text[x:y]
                            appidstr = '"appid":'
                            count = 0
                            while True:
                                if appidstr not in appid:
                                    self.gameamount = count
                                    break

                                leftside = appid.find(appidstr) + len(appidstr)
                                rightside = appid[leftside:].find(',') + leftside

                                gameids += appid[leftside:rightside] + '\n'
                                appidold, appid = appid[leftside:].split(',', 1)
                                count += 1
                        except urllib2.HTTPError as e:
                            if e.code == 403:
                                self.view.set_label(self.view.leftInfoLabel, 'wrong id')
                                self.view.startButton.config(state='normal')
                                self.view.cancelButton.config(state='disabled')
                                self.view.publicBox.config(state='normal')
                                self.restore_backup()
                                return
                            else:
                                self.view.set_label(self.view.leftInfoLabel, 'http error')
                                self.view.startButton.config(state='normal')
                                self.view.cancelButton.config(state='disabled')
                                self.view.publicBox.config(state='normal')
                                self.restore_backup()
                                return

                        for line in gameids.splitlines():
                            appid = str(line.strip())
                            # search for appid between Apps tag
                            if (customconfig[customconfig.find('StarCategory1'):customconfig.find('StarCategory2')].
                                    find('"' + appid + '"')) == -1:
                                startaddgames += '\t\t\t\t\t"' + appid + '"\n'
                                startaddgames += '\t\t\t\t\t{\n'
                                startaddgames += '\t\t\t\t\t}\n'

                    self.view.set_label(self.view.leftInfoLabel, str(self.gameamount) + ' games found')
                    customconfig = startaddgames + endaddgames
                    gamesbetweenapps = customconfig[customconfig.find('StarCategory1') + 14
                                                    :customconfig.find('StarCategory2')]



                    for game in gameids.splitlines():
                        if not self.alive:
                            self.view.set_label(self.view.leftInfoLabel, 'cancelled')
                            self.restore_backup()
                            return
                        appid = str(game.strip())
                        # change language of api call to german for example
                        # http: // store.steampowered.com / api / appdetails /?l = german & appids = 12140
                        responseinjson = self.resolve_redirects(
                            'https://store.steampowered.com/api/appdetails/?appids=' + appid)
                        jsongameinfo = json.loads(responseinjson.read())

                        if jsongameinfo[appid]['success']:
                            gamecateg = ""
                            idintag = 1
                            if 'categories' in jsongameinfo[appid]['data']:
                                for description in jsongameinfo[appid]['data']['categories']:
                                    categname = description['description'].encode('utf-8')
                                    catid = description['id']
                                    if catid in self.steamcategories.keys():
                                        if self.steamcategories[catid][1].get():
                                            gamecateg += '\t\t\t\t\t\t\t"' + str(idintag) + '"\t\t"' + categname + '"\n'
                                            idintag += 1

                            if 'genres' in jsongameinfo[appid]['data']:

                                # index after gameid and first '{'
                                # tags are added to the begingame
                                curlybegin = gamesbetweenapps.rfind('"' + appid + '"') + len(appid) + 10
                                begingame = gamesbetweenapps[:curlybegin]
                                # if no "tags" is in the current game
                                if gamesbetweenapps.find('{', curlybegin) == -1 or \
                                                        gamesbetweenapps.find('{', curlybegin) - \
                                                        gamesbetweenapps.find('}', curlybegin) > 0:
                                    # what is endgame ( end of tag game ? )
                                    endgame = gamesbetweenapps[curlybegin:]
                                    begingame += '\t\t\t\t\t\t"tags"\n\t\t\t\t\t\t{\n'
                                    for description in jsongameinfo[appid]['data']['genres']:
                                        genrename = description['description'].encode('utf-8')
                                        # id = str(description['id'])
                                        if len(gamecateg) > 0:
                                            begingame += gamecateg
                                            gamecateg = ""  # should be deleted after anyway
                                        begingame += '\t\t\t\t\t\t\t"' + str(idintag) + '"\t\t"' + genrename + '"\n'
                                        idintag += 1
                                    begingame += '\t\t\t\t\t\t}\n'
                                    gamesbetweenapps = begingame + endgame
                                # if "tags" is found, therefore a game is a favorite
                                elif gamesbetweenapps.find('{', curlybegin) - gamesbetweenapps.find('}',
                                                                                                    curlybegin) < 0:
                                    begingame = gamesbetweenapps[:gamesbetweenapps.find('}', curlybegin) - 6]
                                    endgame = gamesbetweenapps[gamesbetweenapps.find('}', curlybegin) + 1:]
                                    for description in jsongameinfo[appid]['data']['genres']:
                                        genrename = description['description'].encode('utf-8')
                                        # id = str(description['id'])
                                        if len(gamecateg) > 0:
                                            begingame += gamecateg
                                            gamecateg = ""
                                        begingame += '\t\t\t\t\t\t\t"' + str(idintag) + '"\t\t"' + genrename + '"\n'
                                        idintag += 1
                                    gamesbetweenapps = begingame + '\t\t\t\t\t\t}' + endgame
                                    # no genres found
                            else:

                                # index after gameid and first '{'
                                curlybegin = gamesbetweenapps.rfind('"' + appid + '"') + len(appid) + 10
                                begingame = gamesbetweenapps[:curlybegin]
                                if gamesbetweenapps.find('{', curlybegin) - gamesbetweenapps.find('}',
                                                                                                  curlybegin) > 0:
                                    endgame = gamesbetweenapps[curlybegin:]
                                    begingame += '\t\t\t\t\t\t"tags"\n\t\t\t\t\t\t{\n'
                                    begingame += gamecateg
                                    begingame += '\t\t\t\t\t\t}\n'
                                    gamesbetweenapps = begingame + endgame
                                elif gamesbetweenapps.find('{', curlybegin) - gamesbetweenapps.find('}',
                                                                                                    curlybegin) < 0:
                                    begingame = gamesbetweenapps[:gamesbetweenapps.find('}', curlybegin) - 6]
                                    endgame = gamesbetweenapps[gamesbetweenapps.find('}', curlybegin) + 1:]
                                    begingame += gamecateg
                                    gamesbetweenapps = begingame + '\t\t\t\t\t\t}' + endgame

                    with open('sharedconfig.vdf', 'w') as F:
                        F.write(customconfig[:customconfig.find('StarCategory1')] + gamesbetweenapps +
                                customconfig[customconfig.find('StarCategory2') + 14:])
                    self.view.set_label(self.view.rightInfoLabel, 'finished')
                    self.alive = False
                    self.gameTimer = 0
                    self.view.startButton.config(state='normal')
                    self.view.cancelButton.config(state='disabled')
                    self.view.publicBox.config(state='normal')
                    return

                else:
                    self.view.set_label(self.view.leftInfoLabel, 'no vdf found')
                    self.restore_backup()
                    return

            else:
                self.view.set_label(self.view.leftInfoLabel, 'wrong key or id')
                self.view.startButton.config(state='normal')
                self.view.cancelButton.config(state='disabled')
                self.view.publicBox.config(state='normal')
                self.alive = False
                return

        t = threading.Thread(target=callback)
        t.daemon = True
        t.start()

    def button_cancel(self):
        self.view.startButton.config(state='normal')
        self.view.cancelButton.config(state='disabled')
        self.view.publicBox.config(state='normal')
        self.gameTimer = 0
        self.alive = False

    def restore_backup(self):
        if os.path.isfile('sharedconfig.vdf.bak'):
            self.view.set_label(self.view.rightInfoLabel, 'Backup restored')
            self.alive = False
            self.view.startButton.config(state='normal')
            self.view.cancelButton.config(state='disabled')
            self.view.publicBox.config(state='normal')
            with open('sharedconfig.vdf.bak', 'r') as F:
                backup = F.read()
                with open('sharedconfig.vdf', 'w') as B:
                    B.write(backup)
        else:
            self.view.set_label(self.view.rightInfoLabel, 'no backup file found')
            self.view.cancelButton.config(state='disabled')
            self.view.startButton.config(state='normal')
            self.view.publicBox.config(state='normal')

    def exit_app(self):
        if self.alive:
            if tkMessageBox.askokcancel("Confirm Exit", "Are you sure you want to exit StarCategorizer and "
                                                        "restore backup?"):
                self.restore_backup()
                self.view.master.destroy()
        else:
            if tkMessageBox.askokcancel("Confirm Exit", "Are you sure you want to exit StarCategorizer?"):
                self.view.master.destroy()

    @staticmethod
    def backup_file():
        if not os.path.isfile('sharedconfig.vdf.bak') and os.path.isfile('sharedconfig.vdf'):
            shutil.copy2('sharedconfig.vdf', 'sharedconfig.vdf.bak')

    def resolve_redirects(self, url):
        try:
            hdr = {'User-Agent': 'super happy category bot'}
            req = urllib2.Request(url, headers=hdr)
            time.sleep(1)
            self.view.set_label(self.view.rightInfoLabel,
                                'categorized: ' + str(self.gameTimer) + ' / ' + str(self.gameamount))
            self.gameTimer += 1
            return urllib2.urlopen(req)
        except urllib2.HTTPError as e:
            if e.code != 0:
                self.view.set_label(self.view.rightInfoLabel, 'HTTP error, wait 20 sec')
                time.sleep(20)
                self.gameTimer -= 1
                return self.resolve_redirects(url)
        raise


class Model(object):
    def __init__(self):
        pass


if __name__ == "__main__":
    control = Controller()




