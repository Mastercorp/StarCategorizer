import threading
import time

import Model
import View


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
               ((len(self.steamID) > 0) and self.view.profilePublic.get())):


                '''Sometimes when profilePublic.get() is marked and the button start is spammed, None is returned to
                         steamID. This is catched in the else'''
                self.org_file = Model.Model.load_file(self.filename)
                if self.org_file:
                    self.tag_begin_curl, self.tag_end_curl, self.tag_level, self.tag_found =\
                        Model.Model.find_begin_and_end_of_tag_and_level(self.org_file, 'apps')
                    if self.tag_found:
                        self.file_content = self.org_file.splitlines()[self.tag_begin_curl: self.tag_end_curl + 1]
                        self.file_content = '\n'.join(self.file_content)
                        self.file_content = Model.Model.delete_text_between_tags(self.file_content, 'tags')
                        if self.view.profilePublic.get():
                            self.gameids, statuscode = Model.Model.load_games_public_profile(self.steamID)
                        else:
                            self.gameids, statuscode = Model.Model.load_games_private_profile(self.apiKey, self.steamID)
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
                                Model.Model.add_games_not_in_string_to_file(self.gameids, self.file_content, self.tag_level)
                            self.view.rightInfoLabel.configure(text='categorizing')
                            for idx, gameid in enumerate(self.gameids):

                                if not self.startPressed:
                                    self.finish_button('cancelled!')
                                    return False

                                start_time = time.time()
                                self.cat_gen = \
                                    Model.Model.load_game_categories_and_genres(gameid, self.view.steamCategories)
                                end_time = time.time()
                                if end_time - start_time < 1:
                                    time.sleep(1.2 - (end_time - start_time))
                                if not self.cat_gen:
                                    continue
                                self.file_content = Model.Model.add_categories_and_genres_to_game(
                                    self.cat_gen, gameid, self.file_content, self.tag_level)
                                self.view.leftInfoLabel.configure(text=str(idx) + ' / ' +
                                                                  str(len(self.gameids)) + ' games')
                        else:
                            self.finish_button('wrong input')
                            return False

                    else:
                        self.finish_button('"app" tag not found in vdf')
                        return False
                else:
                    self.finish_button('file not found')
                    return False

                start_to_first = self.org_file.splitlines()[0:self.tag_begin_curl + 1]
                last_to_end = self.org_file.splitlines()[self.tag_end_curl:]
                self.file_content = '\n'.join(start_to_first + self.file_content.splitlines()[1:-1] + last_to_end)

                if not Model.Model.backup_file(self.filename):
                    self.finish_button('no file found')
                    return False

                Model.Model.save_file(self.filename, self.file_content)
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
    viewer = View.View()
    controllers = Controller(viewer)
    viewer.mainloop()
