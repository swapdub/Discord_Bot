import re
import json
import requests
import datetime
from collections import deque
import youtube_dl
import os
import scraping
import discord

import spotify
from utils import *

# Logic : We have a dict with keys as 'Discord Server(ctx.guild)' name. 
#         Value is the que which is deque from collections library optimized 
#         for queue use

# CURRENT QUEUE ARCHITECTURE
#            -- A dictionary of guilds/Server as keys-- 
#            |                                        |
#       dict 1 (self.guilds)               dict 2 (self.index)
# A Queue of songs using lists()          Keep track of Q index
#           |
#    Each Song entry 


class Q:

    INITIAL_INDEX_VALUE = -1
    ydl_opts = {
        "format": "bestaudio/best",
        "postprocessor_args": ["-ar", "192000"], # Audio Freq:192 KHz
        "keepvideo": False,
        "default_search": "auto",
    }
    def __init__(self):
        self.guild = dict()
        self.index = dict()
        self.entry = dict()
        self.loop = dict()
        self.q_range = dict()


    async def check_input(self, ctx, playlist_url, startpoint, endpoint, add_position):
        print(playlist_url)
        youtube_check = re.search(r'youtube.com/|youtu.be/', playlist_url)
        spotify_check = re.search('spotify.com/', playlist_url)
        http_check = re.search('https:', playlist_url)

        if youtube_check != None:
            playlist_check = re.search('list=', playlist_url)
            if not playlist_check:
                endpoint = 1
            else:
                await ctx.send(">>> Please wait ...")

            try:
                song_list = scraping.youtube(playlist_url)[int(startpoint):int(endpoint) if endpoint else None]
            except:
                await ctx.send(">>> ------------------Link not supported------------------\
                     \n (Youtube Mixes and private links not available from YT API) \n------------------Try again------------------ 😅\n.")
                return
            await self.play_each_song(song_list, ctx, add_position)

            if playlist_check:
                await ctx.send(f">>> \nAdded to Q: \n{len(song_list)} songs added by [{self.entry['user'][0:-5]}] at index {add_position}\n.")

            return len(song_list)
        
        elif spotify_check != None:
            playlist_check = re.search('playlist', playlist_url)
            if not playlist_check:
                endpoint = 1
            else:
                await ctx.send(">>> Please wait ...")

            song_list = spotify.get_song_list(playlist_url)[int(startpoint):int(endpoint) if endpoint else None]
            await self.play_each_song(song_list, ctx, add_position)

            if playlist_check:
                await ctx.send(f">>> \nAdded to Q: \n{len(song_list)} songs added by [{self.entry['user'][0:-5]}] at index {add_position}\n.")

            return len(song_list)

        elif http_check != None:
            await ctx.send(">>> ------------------Link not supported------------------\
                    \n (Only Youtube and Spotify Link work) \n------------------Try again------------------ 😅\n.")
            return

        else:
            song_info, yt_code = self.get_yt_code(playlist_url)
            self.build_entry(ctx, song_info, yt_code)
            self.guild[ctx.guild].insert(add_position, self.entry) 
            await playall_song_function(ctx, discord, self)
            return 1
    
    async def play_each_song(self, song_list, ctx, add_position):
        print(song_list)
        for song in song_list:
            try:
                print("Its a playlist 👍")
                song_info, yt_code = self.get_yt_code(song)
                song_entry = self.build_entry(ctx, song_info, yt_code)
                self.guild[ctx.guild].insert(add_position, song_entry)  
                await playall_song_function(ctx, discord, self)
            except Exception as e:
                print(e)

    def yt_dl_info(self, yt_code):
        with youtube_dl.YoutubeDL(self.ydl_opts) as ydl:
            song_info = ydl.extract_info(
                "https://www.youtube.com/watch?v=" + yt_code, download=False
            )
        return song_info

    def get_yt_code(self, search_term):
        html_content = requests.get(
            "https://www.youtube.com/results?search_query=" + search_term
        )

        # Find song ID on Youtube
        yt_code = (re.findall(r'"videoId":"(.{11})"', html_content.text))[0]

        song_info = self.yt_dl_info(yt_code)

        return song_info, yt_code

    def build_entry(self, ctx, song_info, yt_code):
        # song_info, yt_code = self.get_yt_code(search_term)
        self.entry = {
            "guild": str(ctx.guild),
            "channel": str(ctx.author.voice.channel),
            "user": str(ctx.author),
            "time": str(datetime.datetime.now()),
            "name": song_info["title"],
            "YT-video": "https://www.youtube.com/watch?v=" + yt_code,
            "url": song_info["url"]
        }
        return self.entry


    async def add_entry(self, ctx, playlist_url, startpoint, endpoint, position):
        if ctx.guild not in self.guild:
            self.index[ctx.guild] = self.INITIAL_INDEX_VALUE
            self.guild[ctx.guild] = list()
            self.loop[ctx.guild] = False
        self.q_range = {
            ctx.guild : {
                "startpoint" : startpoint,
                "endpoint" : endpoint,
                "position" : position,
            }
        }
        print(ctx.guild)
        num_of_songs = await self.check_input(ctx, playlist_url, startpoint, endpoint, position)
        return self.entry, num_of_songs

        
    def delete_entry(self, ctx, num):
        if num <= self.index[ctx.guild]:
            self.index[ctx.guild] -= 1
            
        current_queue = self.guild[ctx.guild]
        del current_queue[num]
        return


    def next_track(self, ctx):
        self.index[ctx.guild] += 1
        if self.index[ctx.guild] > len(self.guild[ctx.guild]) - 1:
            if self.loop[ctx.guild]:
                self.index[ctx.guild] = 0
            else:
                self.index[ctx.guild] -= 1
                return None # Need this none so that Q doesnt keep looping
        return self.index[ctx.guild]


    def loop_switch(self, ctx):
        if self.loop[ctx.guild] == False:
            self.loop[ctx.guild] = True
        elif self.loop[ctx.guild] == True:
            self.loop[ctx.guild] = False
        print(f'Currently Looping: {self.loop[ctx.guild]}')
        return self.loop[ctx.guild]


    def prev_track(self, ctx):
        self.index[ctx.guild] -= 1
        if self.index[ctx.guild] < 0:
            if self.loop[ctx.guild]:
                self.index[ctx.guild] = len(self.guild[ctx.guild]) - 1
            else:
                self.index[ctx.guild] = 0
        return self.index[ctx.guild]


    def clear_que(self, ctx, save):
        if save.lower() == 'y' or save.lower() == 'yes':
            print(save)
            self.save_data(ctx)

        self.guild[ctx.guild].clear()
        self.index[ctx.guild] = self.INITIAL_INDEX_VALUE


    def nowplaying(self, ctx, arg="name"):
        index = self.index[ctx.guild]
        return self.guild[ctx.guild][index][arg]


    def jump(self, ctx, arg):
        arg -= 1
        if arg <= 0:
            arg = -1
        elif arg > len(self.guild[ctx.guild]) - 1:
            arg = len(self.guild[ctx.guild]) - 1
        
        self.index[ctx.guild] = arg
        return self.index[ctx.guild]


    def my_que(self, ctx, page_num, page_size):
        formattedQ = []
        index_count = 1

        if_false    = page_size * page_num
        if_true     = len(self.guild[ctx.guild])
        condition   = page_size * page_num >= len(self.guild[ctx.guild])
        endpoint    = (if_false, if_true)[condition]
        startpoint  = page_size * (page_num - 1)

        for entry in self.guild[ctx.guild][startpoint : endpoint]:
            index   = index_count + (page_size * (page_num - 1))
            string  = f"{index}. {entry['name']} | [{entry['user'][:-5]}]"
            
            if index - 1 == self.index[ctx.guild]:
                string = ">> " + string
                
            formattedQ.append(string)
            index_count += 1

        formattedQ = "\n".join(formattedQ)
        return formattedQ


    def save_data(self, ctx):
        # A function to save user playlist statistics and 
        # data to json file with the following formatting 
        print("NEW_DATA")
        FILENAME = "discord_playlist.json"
        KEY = str(ctx.guild)
        NEW_DATA = { KEY : self.guild[ctx.guild]}

        try:
            file = open(FILENAME, 'x')
            file.close()
        except:
            pass

        with open(FILENAME, "r+") as fileR:
            try:
                old_data = json.load(fileR)
            except:
                old_data = dict()

            if KEY in old_data:
                old_data[KEY] += NEW_DATA[KEY]
                print(f'File not empty1')
                if 'Session ID' not in old_data[KEY][-1]:
                    NEW_DATA[KEY][-1]['Session ID'] = 1
                else:
                    for elements in NEW_DATA[KEY]: 
                        elements['Session ID'] = old_data[KEY][-1]['Session ID'] + 1
            else:
                old_data[KEY] = NEW_DATA[KEY]
                print(f'File not empty2')
            with open(FILENAME, "w+") as fileW:
                json.dump(old_data, fileW, indent=2)
        return


if __name__ == "__main__":
    import main