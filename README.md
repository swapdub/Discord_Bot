# Discord Music bot
This is my version of a Discord Bot built to play Music. 

## Option 1
To use this code for your own bot follow the steps below if you have Python installed:

- Download this repository. 
- Extract the contents.
- Install dependencies from <strong> requirements.txt </strong>
<br>
    Windows

        pip install -r requirements.txt
    Linux

        pip3 install -r requirements.txt
- Paste the token for your bot in the variable "my_secrets" at the top of main.py file.
<br> 
(You can find your token in the dev pages on discord.com)
<br>
- Run the file main.
<br>
    Windows command:                        

        python main.py
   
   Linux command:

        python3 main.py


## Option 2
I have my code with my bot's Token on repl.it <br>
> Feel free to run my bot using [this link from repl.it](https://replit.com/@swapdub/DiscordBot#main.py) and click play

OR                        

> [Add my bot](https://discord.com/oauth2/authorize?client_id=730602425807011847&permissions=8&scope=) to your server

This allows you to run the bot on their server without having to download anything on your device. It runs in the browser and can be used and viewed by anyone.


In-Progress Features and Known Bugs:

- Queue out of index when cleared or next enough times
- No seek for now playing music yet
- Bot sends too many reply messages, need to change that to editable embeds for better visuals

---
## Known Issues and Fixes


**_NOTE:_ You may encounter an error while installing multidict package. To fix this try updating setuptools on your distro**
<br>
Linux

        sudo apt install libpython3.7-dev && sudo apt install python3-dev

Windows
        
        https://visualstudio.microsoft.com/visual-cpp-build-tools/

To install ffmpeg use the following command

Linux

        sudo apt install ffmpeg
Windows
        
        https://visualstudio.microsoft.com/visual-cpp-build-tools/

---


## Upcoming Features

- Re-add a session playlist
