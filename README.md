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

> [Add my bot](https://discord.com/oauth2/authorize?client_id=730602425807011847&permissions=8&scope=bot) to your server

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


# Command List
## Bot controls
- clear
    - clear current queue      
- help
    - Shows this message
- index
    - Aliases: ```-i```
    - Displays Index of the song currently playing. (Useful for troubleshooting some errors)
- join
    - Aliases: ```-j ```
    - Joins the Voice Channel the user is connected to. Does not work if you are not in a Voice Channel already
- leave
    - Aliases: ```-dc, -die```
    - Disconnect from Voice Channel

## Music Player Control Commands
- play
    - Aliases: ```-p (song name or link)```
    - Play followed by the name of your Search Query / Song
- playnext
    - Aliases: ```-pn (song name or link)```
    - Add the given song to Queue right after the currently playing song
- next
    - Aliases: ```-n```
    - Next song
- prev
    - Previous Song
- jump
    - Aliases: ```-jm (enter number here)```
    - Jump to the specified index number given
- loop
    - Aliases: ```-l```
    - Loop queue
- remove
    - Aliases: ```-rm (song index number)```
    - Remove the song with the specified index number (only numbers allowed)

## Music Info Commands
- link
    - Share Youtube link of the currently playing song
- nowplaying
    - Aliases: ```-np```
    - View the song title currently playing
- ping
    - Latency of the bot to the Voice Channel Server
- queue
    - Aliases: ```-q```
    - View the current queue
- save
    - Export and save the current queue to the server database
- test 
    - -test *your_message_here*
    - Responds back with your input message
    
## Commands targeted for Among Us Lobbies 
- vcmute
    - Aliases: ```-vm```
    - Server mute all the people in the current Voice Channel
- vcunmute
    - Aliases: ```-um```
    - Server unmute all the people in the current Voice Channel


# Bot Command Structure
- ask play songname
- find song
- save video_id to q
- change q from txt to just a list in code
- get q[0] for first song
- play song from q
- End of session, export q metadata to a databse: requestorName, songName, etc