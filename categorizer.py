import urllib2
import json
import time


def resolve_redirects(url):
    try:
        hdr = {'User-Agent': 'super happy category bot'}
        req = urllib2.Request(url, headers=hdr)
        time.sleep(1)
        return urllib2.urlopen(req)
    except urllib2.HTTPError as e:
        if e.code != 0:
            print 'error 429'
            time.sleep(20)
    raise

# delete all set tags, only exception is favorite
names = ""
first = False
second = False
with open('sharedconfig.vdf') as F:
    for idx, line in enumerate(F):
        searchtags = str(line.lstrip())
        searchtags = searchtags.rstrip()
        if searchtags == '"tags"':
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

steamapikey = 'YOURSTEAMAPIKEYHERE'
steam64id = 'YOURSTEAM64IDHERE'

#http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key=YOURSTEAMKEYHERE&steamid=YOURSTEAMIDHERE&format=json
response = urllib2.urlopen('http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key=' + steamapikey +
                           '&steamid=' + steam64id + '&format=json')
html = response.read()
parsed_json = json.loads(html)
# apps + { + linebreakes and tabs
firstappsindex = names.rfind('"apps"') + 13

beginvdf =names[:firstappsindex]
endvdf = names[firstappsindex:]

#add apps not present in current list
for idx, each in enumerate(parsed_json['response']['games']):
    appid = str(each['appid'])
    if (names.find('"'+appid+'"')) == -1:
        beginvdf += '\t\t\t\t\t"'+appid+'"\n'
        beginvdf += '\t\t\t\t\t{\n'
        beginvdf += '\t\t\t\t\t}\n'

with open('sharedconfig.vdf', 'w') as F:
    F.write(beginvdf + endvdf)

for idx, each in enumerate(parsed_json['response']['games']):
    appid = str(each['appid'])
    response = resolve_redirects('http://store.steampowered.com/api/appdetails/?appids='+appid+'&filters=genres')
    html = response.read()
    parsed_json2 = json.loads(html)
    if str(parsed_json2[appid]['success']) == 'True':
        if str(parsed_json2[appid]['data']) != '[]':
            with open('sharedconfig.vdf', 'r') as F:
                print appid
                names = F.read()
                # index after gameid and first '{'
                firstidindex = names.rfind('"'+appid+'"') + len(appid) + 10
                beginvdf = names[:firstidindex]
                if names.find('{', firstidindex) - names.find('}', firstidindex) > 0:
                    lastinvdf = names[firstidindex:]
                    beginvdf += '\t\t\t\t\t\t"tags"\n\t\t\t\t\t\t{\n'
                    for description in parsed_json2[appid]['data']['genres']:
                        descript = str(description['description'])
                        id = str(description['id'])
                        beginvdf += '\t\t\t\t\t\t\t"' + id + '"\t\t"' + descript + '"\n'
                    beginvdf += '\t\t\t\t\t\t}\n'
                    names = beginvdf + lastinvdf
                elif names.find('{', firstidindex) - names.find('}', firstidindex) < 0:
                    beginvdf = names[:names.find('}', firstidindex)-6]
                    lastinvdf = names[names.find('}', firstidindex):]
                    for description in parsed_json2[appid]['data']['genres']:
                        descript = str(description['description'])
                        id = str(description['id'])
                        beginvdf += '\t\t\t\t\t\t\t"' + id + '"\t\t"' + descript + '"\n'
                        names = beginvdf + lastinvdf
            with open('sharedconfig.vdf', 'w') as F:
                F.write(names)
print 'all gamefiles updated'





