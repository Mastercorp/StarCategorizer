# StarCategorizer
Add all genres tags from the steamstore to your gamelibrary  
(all custom tags are first deleted, only favorites are saved)

##What you need
Python 2.7.13  
Install for windows https://www.python.org/ftp/python/2.7.13/python-2.7.13.msi      
else https://www.python.org/downloads/release/python-2713/        
Steam API key  
You can get it here: https://steamcommunity.com/dev/apikey  
(if you do not have a domain, enter your e-mail)  
Steam 64 ID    
search with your custom url name https://steamid.io/  
or read here : https://steamcommunity.com/discussions/forum/1/364039785160857002/  
your sharedconfig.vdf  
(you can find sharedconfig.vdf in \Steam\userdata\YOURID\7\remote\sharedconfig.vdf)  

#HowTo

You have to change steamapikey and steam64id on line 48 and 49 to your own values!  
Make sure they are inside the single quotes : 'yourkey'   
 
download categorizer.py and save it in a directory.  
Copy the sharedconfig.vdf in the same folder as categorizer.py  
(you can find sharedconfig.vdf in \Steam\userdata\youruserid\7\remote\sharedconfig.vdf)  

start the programm in your cmd with: python categorizer.py  
All processed appids are printed in the cmd.  
If you see "all gamefiles updated", you can close the cmd.  
(To avoid HTTP errors for flooding the server, every apicall waits for 1 second.  
Therefore, updating 600 games takes at least 600 seconds (10 minutes ))  

After the program is finished, make sure steam is closed.  
Now rename sharedconfig.vdf in your steam folder to sharedconfig_back.vdf (as backup if something goes wrong).  
Copy the new sharedconfig.vdf from the directory folder to the steam folder and your done.  
Start steam and enjoy the new categories ;)  
CARE: All custom categories are deleted. Only your favorites are saved!  



