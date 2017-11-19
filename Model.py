import urllib2
import time
import json
import os
import shutil


class Model(object):

    def resolve_redirects(self, url):
        try:
            return urllib2.urlopen(url), urllib2.urlopen(url).getcode()
        except urllib2.HTTPError as e:
            if e.code == 429:
                time.sleep(20)

                return self.resolve_redirects(url)

            else:
                return False, e.code

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
        response, statuscode = Model.resolve_redirects('https://steamcommunity.com/id/{}/games/?tab=all'.format(steamid))
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
        response, statuscode = Model.resolve_redirects(
            'https://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={}'
            '&steamid={}&include_played_free_games=1&include_appinfo=1&format=json'.format(apikey, steamid))
        if not response:
            return gameids, statuscode
        gamelist = json.loads(response.read())
        for appid in gamelist['response']['games']:
            gameids.append(str(appid['appid']))
        return gameids, statuscode



    @staticmethod
    def add_games_not_in_string_to_file(gameids, file_content, level):
        newgameids = ""
        '''level of the outmost tag, therefore add 1 when a tag is added inside'''
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
        response, success = Model.resolve_redirects('https://store.steampowered.com/api/appdetails/?appids={}&l=en'.format(gameid))
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


