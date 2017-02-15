import urllib2
import json
import time
import Tkinter
import threading
import os
import shutil
import sys


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def resolve_redirects(url, gameamount):
    try:
        global gameTimer
        hdr = {'User-Agent': 'super happy category bot'}
        req = urllib2.Request(url, headers=hdr)
        time.sleep(1)
        rightLabel.configure(text='categorized: '+str(gameTimer) + ' / ' + gameamount)
        gameTimer += 1
        return urllib2.urlopen(req)
    except urllib2.HTTPError as e:
        if e.code != 0:
            rightLabel.configure(text='HTTP error, wait 20 sec')
            time.sleep(20)
            gameTimer -= 1
            return resolve_redirects(url, gameamount)
    raise


def quit_categorizer():
    root.quit()


def stop_thread():
    global alive
    global startButton
    alive = False
    startButton.config(state='normal')


def backup_file():
    if not os.path.isfile('sharedconfig.vdf.bak') and os.path.isfile('sharedconfig.vdf'):
        shutil.copy2('sharedconfig.vdf', 'sharedconfig.vdf.bak')


def handle_start():

    def callback():
        global alive
        global gameTimer
        global startButton
        global cancelButton
        startButton.config(state='disabled')
        cancelButton.config(state='normal')
        gameTimer = 1
        alive = True
        while alive:
            if len(e1.get()) == 32 and len(e2.get()) == 17:
                backup_file()

            # delete all set tags, only exception is favorite
                if os.path.isfile('sharedconfig.vdf'):
                    names = ""
                    first = False
                    second = False
                    appfirstindex = 0
                    applastindex = 0
                    with open('sharedconfig.vdf') as F:
                        appscurlyfirst = 0
                        appsopen = False
                        for idx, line in enumerate(F):
                            searchtags = str(line.lstrip())
                            searchtags = searchtags.rstrip()
                            if searchtags == '{' and appsopen:
                                if appscurlyfirst is 0:
                                    appfirstindex = idx
                                appscurlyfirst += 1
                            elif searchtags == '}' and appsopen:
                                appscurlyfirst -= 1
                                if appscurlyfirst is 0:
                                    applastindex = idx
                                    appsopen = False
                                    break

                            elif searchtags.lower() == '"apps"' and not appsopen:
                                appscurlyfirst = 0
                                appsopen = True
                        # jump to the beginning of the fail again, read doesnt reset the cursor
                        if appfirstindex == applastindex:
                            leftLabel.configure(text='')
                            rightLabel.configure(text='No Apps object found in vdf, error')
                            startButton.config(state='normal')
                            cancelButton.config(state='disabled')
                            break
                        #to reset read()
                        F.seek(0)
                        for idx, line in enumerate(F):
                            if idx == appfirstindex:
                                names += line
                                names += 'StarCategory1\n'
                            elif appfirstindex < idx < applastindex:
                                searchtags = str(line.lstrip())
                                searchtags = searchtags.rstrip()
                                if searchtags.lower() == '"tags"':
                                    first = True
                                    continue
                                if first and searchtags == '{':
                                    second = True
                                    continue
                                if first and second and searchtags == '}':
                                    first = False
                                    second = False
                                    continue
                                if searchtags == '':
                                    continue
                                if searchtags == '"0"\t\t"favorite"':
                                    names += '\t\t\t\t\t\t"tags"\n'
                                    names += '\t\t\t\t\t\t{\n'
                                    names += '\t\t\t\t\t\t\t"0"\t\t"favorite"\n'
                                    names += '\t\t\t\t\t\t}\n'
                                    continue
                                if first and second:
                                    continue
                                names += line
                            elif idx == applastindex:
                                names += 'StarCategory2\n'
                                names += line
                            else:
                                names += line

                    steamapikey = str(e1.get())
                    steam64id = str(e2.get())
                    try:
                        response = urllib2.urlopen('http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key=' + steamapikey +
                                                  '&steamid=' + steam64id + '&format=json')
                    except urllib2.HTTPError as e:
                        if e.code == 403:
                            rightLabel.configure(text='wrong key or id')
                            alive = False
                            startButton.config(state='normal')
                            cancelButton.config(state='disabled')
                            break
                        else:
                            rightLabel.configure(text='http error')
                            alive = False
                            startButton.config(state='normal')
                            cancelButton.config(state='disabled')
                            break

                    html = response.read()
                    parsed_json = json.loads(html)
                    # apps + { + linebreakes and tabs
                    if(names.rfind('StarCategory1') > -1):
                        firstappsindex = names.rfind('StarCategory1') + 14

                    beginvdf = names[:firstappsindex]
                    endvdf = names[firstappsindex:]

                    gameamount = str(parsed_json['response']['game_count'])
                    leftLabel.configure(text=gameamount + " games found")

                    # add apps not present in current list
                    for idx, each in enumerate(parsed_json['response']['games']):
                        appid = str(each['appid'])

                        if (names[names.find('StarCategory1'):names.find('StarCategory2')].find('"' + appid + '"')) == -1:
                            beginvdf += '\t\t\t\t\t"' + appid + '"\n'
                            beginvdf += '\t\t\t\t\t{\n'
                            beginvdf += '\t\t\t\t\t}\n'

                    with open('sharedconfig.vdf', 'w') as F:
                        F.write(beginvdf + endvdf)

                    with open('sharedconfig.vdf', 'r') as F:
                        names = F.read()
                        namebetweenapps = names[names.rfind('StarCategory1') + 14:names.rfind('StarCategory2')]

                    for idx, each in enumerate(parsed_json['response']['games']):
                        if not alive:
                            break
                        appid = str(each['appid'])
                        #response = resolve_redirects('http://store.steampowered.com/api/appdetails/?appids=' + appid + '&filters=genres', gameamount)
                        # change language of api call to german for example
                        #http: // store.steampowered.com / api / appdetails /?l = german & appids = 12140
                        response = resolve_redirects('http://store.steampowered.com/api/appdetails/?appids=' + appid, gameamount)
                        html = response.read()
                        parsed_json2 = json.loads(html)

                        if parsed_json2[appid]['success']:
                            categ = ""
                            idnumber = 1
                            if 'categories' in parsed_json2[appid]['data']:
                                for description in parsed_json2[appid]['data']['categories']:
                                    descript = description['description'].encode('utf-8')
                                    id = str(description['id'])
                                    if id == '18' or id == '39':
                                        categ += '\t\t\t\t\t\t\t"' + str(idnumber) + '"\t\t"' + descript + '"\n'
                                        idnumber += 1

                            if 'genres' in parsed_json2[appid]['data']:

                                # index after gameid and first '{'

                                firstidindex = namebetweenapps.rfind('"' + appid + '"') + len(appid) + 10
                                beginvdf = namebetweenapps[:firstidindex]
                                if namebetweenapps.find('{', firstidindex) == -1 or namebetweenapps.find('{', firstidindex) - namebetweenapps.find('}', firstidindex) > 0:
                                    lastinvdf = namebetweenapps[firstidindex:]
                                    beginvdf += '\t\t\t\t\t\t"tags"\n\t\t\t\t\t\t{\n'
                                    for description in parsed_json2[appid]['data']['genres']:
                                        descript = description['description'].encode('utf-8')
                                        #id = str(description['id'])
                                        if len(categ) > 0:
                                            beginvdf += categ
                                            categ = ""
                                        beginvdf += '\t\t\t\t\t\t\t"' + str(idnumber) + '"\t\t"' + descript + '"\n'
                                        idnumber += 1
                                    beginvdf += '\t\t\t\t\t\t}\n'
                                    namebetweenapps = beginvdf + lastinvdf
                                elif namebetweenapps.find('{', firstidindex) - namebetweenapps.find('}', firstidindex) < 0:
                                    beginvdf = namebetweenapps[:namebetweenapps.find('}', firstidindex) - 6]
                                    lastinvdf = namebetweenapps[namebetweenapps.find('}', firstidindex) + 1:]
                                    for description in parsed_json2[appid]['data']['genres']:
                                        descript = description['description'].encode('utf-8')
                                        #id = str(description['id'])
                                        if len(categ) > 0:
                                            beginvdf += categ
                                            categ = ""
                                        beginvdf += '\t\t\t\t\t\t\t"' + str(idnumber) + '"\t\t"' + descript + '"\n'
                                        idnumber += 1
                                    namebetweenapps = beginvdf + '\t\t\t\t\t\t}' + lastinvdf

                        #no genres found
                            else:

                                # index after gameid and first '{'
                                firstidindex = namebetweenapps.rfind('"' + appid + '"') + len(appid) + 10
                                beginvdf = namebetweenapps[:firstidindex]
                                if namebetweenapps.find('{', firstidindex) - namebetweenapps.find('}', firstidindex) > 0:
                                    lastinvdf = namebetweenapps[firstidindex:]
                                    beginvdf += '\t\t\t\t\t\t"tags"\n\t\t\t\t\t\t{\n'
                                    beginvdf += categ
                                    beginvdf += '\t\t\t\t\t\t}\n'
                                    namebetweenapps = beginvdf + lastinvdf
                                elif namebetweenapps.find('{', firstidindex) - namebetweenapps.find('}', firstidindex) < 0:
                                    beginvdf = namebetweenapps[:namebetweenapps.find('}', firstidindex) - 6]
                                    lastinvdf = namebetweenapps[namebetweenapps.find('}', firstidindex) + 1:]
                                    beginvdf += categ
                                    namebetweenapps = beginvdf + '\t\t\t\t\t\t}' + lastinvdf

                    if alive:
                        with open('sharedconfig.vdf', 'w') as F:
                            F.write(names[:names.rfind('StarCategory1')] + namebetweenapps + names[names.rfind(
                                'StarCategory2') + 14:])

                        rightLabel.configure(text='finished')
                        alive = False
                    else:
                        rightLabel.configure(text='Backup restored')
                        with open('sharedconfig.vdf.bak', 'r') as F:
                            backup = F.read()
                            with open('sharedconfig.vdf', 'w') as B:
                                B.write(backup)

                        alive = False
                else:
                    rightLabel.configure(text='no sharedconfig.vdf found')
                    alive = False
            else:
                rightLabel.configure(text='wrong key or id')
                alive = False
            if not alive:
                startButton.config(state='normal')
                cancelButton.config(state='disabled')
                break
    leftLabel.configure(text='')
    rightLabel.configure(text='')
    t = threading.Thread(target=callback)
    t.daemon = True
    t.start()

root = Tkinter.Tk()
root.iconbitmap(resource_path('logo.ico'))
root.title('StarCategorizer')

apiLabel = Tkinter.Label(root, text="Steam API Key")
apiLabel.grid(row=0)

idLabel = Tkinter.Label(root, text="steamID64")
idLabel.grid(row=1)
leftLabel = Tkinter.Label(root, text="Version 1.1.1")
leftLabel.grid(row=2, column=0)
rightLabel = Tkinter.Label(root, text="")
rightLabel.grid(row=2, column=1)
e1 = Tkinter.Entry(root, width=34)
e2 = Tkinter.Entry(root, width=18)
e1.grid(row=0, column=1)
e2.grid(row=1, column=1)
Tkinter.Button(root, text='Quit', command=quit_categorizer).grid(row=3, column=0)
startButton = Tkinter.Button(root, text='Start', command=handle_start, state='normal')
startButton.grid(row=3, column=2)
cancelButton = Tkinter.Button(root, text='Cancel', command=stop_thread, state='disabled')
cancelButton.grid(row=3, column=1)
gameTimer = 1
alive = True
root.mainloop()









