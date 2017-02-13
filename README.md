


## StarCategorizer

StarCategorizer autocategorizes your games in your Steam library. The games' Steam store genre is used as category ( + Partial Controller Support and Local Co-OP categorie). Your old categories are deleted, only your Favorites are saved. A backup is made from your old config file (called sharedconfig.vdf.bak)
You don't need to set your profile status to public for this programm to work ;)


## What you need

Steam API key: you can get it here: https://steamcommunity.com/dev/apikey  
(if you do not have a domain, enter your e-mail)  
steam64ID: search with your custom url name at https://steamid.io/  
or read here : https://steamcommunity.com/discussions/forum/1/364039785160857002/  

## Motivation

I could not manage to make Depressurizer work on my system, therefore i wrote my own programm.  https://github.com/rallion/depressurizer

## Installation

Download the StarCategorizer.exe file and put it in your \Steam\userdata\<Steam User ID>\7\remote\ folder. Start the exe, put in your Steam API key and steamID64 and press the 'Start' button. Wait until the programm is finished and start Steam. Enjoy your categories. You need an internet connection for the programm to work! (No python needed! I used pyinstall to pack everything you need into the exe file.) 

If you don´t trust my exe, you can download the categorizer.py and start the programm from there. Don´t forget to download the logo.ico as well, else it wont work ;) (You need to install python to use the categorizer.py)

## Buttons

Quit closes the app.  
Start starts the process of categorizing your games and makes a backup of your sharedconfig.vdf file. (If a sharedconfig.vdf.bak exists, sharedconfig.vdf.bak does't get overwritten.If you want to make a new backup you have to delete sharedconfig.vdf.bak first)
Cancel stops categorizing your games and restores sharedconfig.vdf(everything in sharedconfig.vdf.bak is coppied back to sharedconfig.vdf)  


## License

MIT License

Copyright (c) 2017 Mastercorp

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.


