
import os
import urllib2
import json
import Tkinter as tk
import tkMessageBox
#from tkFileDialog import askopenfilename
import webbrowser
import shutil
import threading
import time


def resource_path(relative_path):
    """ Get absolute path to resource, works for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def resolve_redirects(url):
    try:
        return urllib2.urlopen(url), urllib2.urlopen(url).getcode()
    except urllib2.HTTPError as e:
        if e.code == 429:
            time.sleep(20)
            return resolve_redirects(url)
        else:
            return False, e.code


class Model(object):

    @staticmethod
    def load_file(file_name):
        '''file_name  of type String'''
        try:
            with open(file_name, 'r') as f:
                file_content = f.read()
            return file_content
        except EnvironmentError:
            return False


    @staticmethod
    def save_file(file_name, file_content):
        '''file_name and file_content of type String'''
        try:
            with open(file_name, 'w') as f:
                f.write(file_content)
            return True
        except EnvironmentError:
            return False

    @staticmethod
    def backup_file(file_name):
        if not os.path.isfile(file_name + '.bak') and os.path.isfile(file_name):
            shutil.copy2(file_name, file_name + '.bak')
            return True
        elif os.path.isfile(file_name + '.bak'):
            return True
        else:
            return False

    @staticmethod
    def find_begin_and_end_of_tag_and_level(file_content, tag):
        '''file_content and tag of type String'''
        '''tag is converted to lower, searched file is converted to lower too'''
        ''' find the first occurrence of the tag'''
        tag_begin_curl = 0
        tag_end_curl = 0
        tag_level = 0
        tag_found = False
        for idx, line in enumerate(file_content.splitlines()):
            line = line.lower()
            if line.strip() == '"{}"'.format(tag.lower()) and not tag_found:
                tag_found = True
                tag_begin_curl = idx + 1
                tag_end_curl = 0
                tag_level = len(line) - len(line.lstrip())
            elif tag_found and line.strip() == '{}'.format('{'):
                tag_end_curl += 1
            elif tag_found and line.strip() == '{}'.format('}'):
                tag_end_curl -= 1
                if tag_end_curl == 0:
                    tag_end_curl = idx
                    break

        return tag_begin_curl, tag_end_curl, tag_level, tag_found

    @staticmethod
    def delete_text_between_tags(file_content, tag):
        '''delete all text betwenn tag'''
        tag_found = False
        new_file_content = ""
        tag_end_curl = 0
        listsize = len(file_content.splitlines()) - 1
        for idx, line in enumerate(file_content.splitlines()):
            line = line.lower()

            if line.strip() == '"{}"'.format(tag.lower()) and not tag_found:
                tag_found = True
                new_file_content += line + '\n'
            elif tag_found and line.strip() == '{}'.format('{'):
                new_file_content += line + '\n'
                tag_end_curl += 1
            elif tag_found and line.strip() == '{}'.format('"0"\t\t"favorite"'):
                new_file_content += line + '\n'
            elif tag_found and line.strip() == '{}'.format('}'):
                tag_end_curl -= 1
                if tag_end_curl == 0:
                    new_file_content += line + '\n'
                    tag_found = False
            elif tag_end_curl == 0:
                new_file_content += line + '\n'

        return new_file_content

    @staticmethod
    def load_games_public_profile(steamid):
        gameids = []
        response, statuscode = resolve_redirects('https://steamcommunity.com/id/{}/games/?tab=all'.format(steamid))
        if not response:
            return gameids, statuscode
        text = response.read()
        if text.find('rgGames = [{') == -1 and text.find('fatalerror'):
            return gameids, 500
        elif text.find('rgGames = [{') == -1 and text.find('private_profile') > -1:
            return gameids, 20
        #startposition is the position of [ after rgGames
        startposition = text.find('rgGames = [{') + 10
        endposition = text[startposition:].find('];') + startposition

        gamelist = text[startposition:endposition + 1]
        while True:
            if '"appid":' not in gamelist:
                break
            gamelist.find('"appid":')
            startid = gamelist.find('"appid":') + len('"appid":')
            endid = gamelist[startid:].find(',') - 1 + startid
            gameids.append(gamelist[startid:endid + 1])
            _, gamelist = gamelist[startid:].split(',', 1)

        return gameids, statuscode

    @staticmethod
    def load_games_private_profile(apikey, steamid):
        gameids = []
        response, statuscode = resolve_redirects(
            'https://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={}'
            '&steamid={}&include_played_free_games=1&include_appinfo=1&format=json'.format(apikey, steamid))
        if not response:
            return gameids, statuscode
        gamelist = json.loads(response.read())
        for appid in gamelist['response']['games']:
            gameids.append(str(appid['appid']))
        return gameids, statuscode

    '''level of the outmost tag, therefore add 1 when a tag is added inside'''

    @staticmethod
    def add_games_not_in_string_to_file(gameids, file_content, level):
        newgameids = ""
        tag_level = level + 1
        for gameid in gameids:
            if '"'+gameid+'"' not in file_content:
                newgameids += tag_level*'\t'+'"' + gameid + '"\n'
                newgameids += tag_level*'\t'+'{\n'
                newgameids += tag_level*'\t'+'}\n'
        insert_position = file_content.rfind('}') - level
        return file_content[:insert_position] + newgameids + file_content[insert_position:]

    @staticmethod
    def load_game_categories_and_genres(gameid, selectedcateg):
        #selectedcateg holds integer variables with the categories selected to detect
        response, success = resolve_redirects('https://store.steampowered.com/api/appdetails/?appids={}&l=en'.format(gameid))
        gameinfo = json.loads(response.read())
        gamecategories = []
        gamegenres = []
        if gameinfo[gameid]['success']:
            if 'categories' in gameinfo[gameid]['data']:
                for categ in gameinfo[gameid]['data']['categories']:
                    if categ['id'] in selectedcateg.keys():
                        if selectedcateg[categ['id']][1].get():
                            gamecategories.append(categ['description'].encode('utf-8'))
            if 'genres' in gameinfo[gameid]['data']:
                for genre in gameinfo[gameid]['data']['genres']:
                    gamegenres.append(genre['description'].encode('utf-8'))

        return gamecategories + gamegenres

    @staticmethod
    def add_categories_and_genres_to_game(cat_gen, gameid, file_content, level):
        newgametags = ""
        tag_level = level + 3
        startposition = file_content.find('"'+gameid+'"')
        endposition = file_content[startposition:].find('}') + startposition
        x = file_content[endposition]
        if '"tags"' in file_content[startposition:endposition]:
            for idx, categ in enumerate(cat_gen):
                newgametags += tag_level*'\t' + '"' + str(idx + 1) + '"' + 2 * '\t' + '"' + categ + '"\n'
                '''Want to add something before the end curly, therefore i need to substract the level of the tag'''
            return file_content[:endposition - tag_level + 1] + newgametags + file_content[endposition - tag_level + 1:]
        else:
            newgametags += (tag_level - 1)*'\t' + '"tags"\n'
            newgametags += (tag_level - 1) * '\t' + '{\n'
            for idx, categ in enumerate(cat_gen):
                newgametags += tag_level*'\t' + '"' + str(idx + 1) + '"' + 2 * '\t' + '"' + categ + '"\n'
            newgametags += (tag_level - 1) * '\t' + '}\n'
            return file_content[:endposition - tag_level + 2] + newgametags + file_content[endposition - tag_level + 2:]


class View(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master=master)
        self.controller = None
        self.grid()
        self.master.protocol('WM_DELETE_WINDOW', self.exit_app)
        self.master.title('StarCategorizer')
        self.master.iconbitmap(resource_path('logo.ico'))
        self.master.geometry('350x120')
        self.apiKeyLabel = tk.Label(self, text=" Steam API Key               ")
        self.steamIDLabel = tk.Label(self, text=" SteamID64     ")
        self.leftInfoLabel = tk.Label(self, text="")
        self.rightInfoLabel = tk.Label(self, text="")

        self.steamCategories = {}
        self.profilePublic = tk.BooleanVar()
        with open(resource_path('categories.txt'), 'r') as F:
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
        window.iconbitmap(resource_path('logo.ico'))
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
        window.iconbitmap(resource_path('logo.ico'))
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


class Controller(object):
    def __init__(self, view):
        self.view = view
        self.view.register(self)
        self.startPressed = False
        self.apiKey = None
        self.steamID = None
        self.gameids = None
        self.file_content = ""
        self.org_file = None
        self.tag_begin_curl = None
        self.tag_end_curl = None
        self.tag_level = None
        self.tag_found = None
        self.cat_gen = None
        self.filename = 'sharedconfig.vdf'

    def finish_button(self, message):
        self.view.startButton.config(state='normal')
        self.view.cancelButton.config(state='disabled')
        self.view.publicBox.config(state='normal')
        self.view.steamIDEntry.configure(state='normal')
        self.view.settingMenu.entryconfig('Categories', state='normal')
        self.view.leftInfoLabel.configure(text='')
        self.view.rightInfoLabel.configure(text=message)

        if not self.view.profilePublic.get():
            self.view.apiKeyEntry.configure(state='normal')
        self.startPressed = False

    def button_start(self):
        self.view.cancelButton.config(state='normal')
        self.view.startButton.config(state='disabled')
        self.view.publicBox.config(state='disabled')
        self.view.apiKeyEntry.configure(state='disabled')
        self.view.steamIDEntry.configure(state='disabled')
        self.view.settingMenu.entryconfig('Categories', state='disabled')
        self.view.leftInfoLabel.configure(text='')
        self.view.rightInfoLabel.configure(text='')

        def callback():
            self.startPressed = True
            start_time1 = time.time()
            self.apiKey = self.view.apiKeyEntry.get()
            self.steamID = self.view.steamIDEntry.get()
            if (len(self.apiKey) == 32 and len(self.steamID) == 17 or
               (self.view.profilePublic.get() and len(self.steamID) > 0)):
                self.org_file = Model.load_file(self.filename)
                if self.org_file:
                    self.tag_begin_curl, self.tag_end_curl, self.tag_level, self.tag_found =\
                        Model.find_begin_and_end_of_tag_and_level(self.org_file, 'apps')
                    if self.tag_found:
                        self.file_content = self.org_file.splitlines()[self.tag_begin_curl: self.tag_end_curl + 1]
                        self.file_content = '\n'.join(self.file_content)
                        self.file_content = Model.delete_text_between_tags(self.file_content, 'tags')
                        if self.view.profilePublic.get():
                            self.gameids, statuscode = Model.load_games_public_profile(self.steamID)
                        elif not self.view.profilePublic.get():
                            self.gameids, statuscode = Model.load_games_private_profile(self.apiKey, self.steamID)
                        if statuscode != 200:
                            if statuscode == 403:
                                self.finish_button('wrong Steam API Key ')
                            elif statuscode == 500:
                                self.finish_button('wrong SteamID')
                            elif statuscode == 20:
                                self.finish_button('profile status not public')
                            else:
                                self.finish_button('HTTP error: ' + str(statuscode))
                            return False

                        if self.gameids:
                            self.file_content = \
                                Model.add_games_not_in_string_to_file(self.gameids, self.file_content, self.tag_level)
                            self.view.rightInfoLabel.configure(text='categorizing')
                            for idx, gameid in enumerate(self.gameids):

                                if not self.startPressed:
                                    self.finish_button('cancelled!')
                                    return False

                                start_time = time.time()
                                self.cat_gen = \
                                    Model.load_game_categories_and_genres(gameid, self.view.steamCategories)
                                end_time = time.time()
                                if end_time - start_time < 1:
                                    time.sleep(1.2 - (end_time - start_time))
                                if not self.cat_gen:
                                    continue
                                self.file_content = Model.add_categories_and_genres_to_game(
                                    self.cat_gen, gameid, self.file_content, self.tag_level)
                                self.view.leftInfoLabel.configure(text=str(idx) + ' / ' +
                                                                  str(len(self.gameids)) + ' games')
                        else:
                            self.finish_button('wrong input')
                            return False

                    else:
                        self.finish_button('"app" tag not found in vdf')
                        return False

                start_to_first = self.org_file.splitlines()[0:self.tag_begin_curl + 1]
                last_to_end = self.org_file.splitlines()[self.tag_end_curl:]
                self.file_content = '\n'.join(start_to_first + self.file_content.splitlines()[1:-1] + last_to_end)

                if not Model.backup_file(self.filename):
                    self.finish_button('no file found')
                    return False

                Model.save_file(self.filename, self.file_content)
                end_time = time.time()
                self.view.leftInfoLabel.configure(text=(end_time - start_time1)/60)

            else:
                self.finish_button('wrong key/id')
                return False

            self.finish_button('finished!')

        t = threading.Thread(target=callback)
        t.daemon = True
        t.start()

    def button_cancel(self):
        self.view.startButton.config(state='normal')
        self.view.cancelButton.config(state='disabled')
        self.view.publicBox.config(state='normal')
        self.view.steamIDEntry.configure(state='normal')
        self.view.settingMenu.entryconfig('Categories', state='normal')
        if not self.view.profilePublic.get():
            self.view.apiKeyEntry.configure(state='normal')
        self.startPressed = False

    def button_loadvdf(self):
        pass


if __name__ == "__main__":
    viewer = View()
    controllers = Controller(viewer)
    viewer.mainloop()
