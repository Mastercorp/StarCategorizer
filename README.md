# StarCategorizer
Add all genres tags from the steamstore to your gamelibrary
(all custom tags are deleted, only favorites are saved)

First you need your own Steam API Key.
You can get it here: https://steamcommunity.com/dev/apikey
(it still works if you put in your e-mail as domain or fake domain)
Than you need to find out your steamID64 
You can use https://steamid.io/ 

You have to change the url on line 48 for the programm to work!
http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key=YOURSTEAMKEYHERE&steamid=YOURSTEAMIDHERE&format=json

Install python 2.7.13 https://www.python.org/ftp/python/2.7.13/python-2.7.13.msi 
or look here https://www.python.org/downloads/release/python-2713/
 
download my file and save it in a directory.
Copy the sharedconfig.vdf in the same folder.
(you can find sharedconfig.vdf in \Steam\userdata\youruserid\7\remote\sharedconfig.vdf

start the programm in your cmd with python categorizer.py
wait till programm is finished.
(To avoid HTTP error for flooding the server, every apicall waits for 1 second.
Therefore, updating 600 games takes at least 600 seconds (10 minutes ))

Now rename sharedconfig.vdf in your steam folder ( as backup if something goes wrong ).
Copy the new sharedconfig.vdf from the directory folder to the steam folder and your done.
Make sure to close steam before you coppy the file over.
CARE: All custom categories are deleted. Only your favorites are saved!



