from random import randint
import re
import json
import requests
import asyncio
import datetime
from collections import deque
import youtube_dl
import os
import scraping
import discord

from scrape_Spotify import spotify_class
# from utils import *

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
        self.shuffle = dict()


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
                print(f"endpoint is: {endpoint}")
                song_list = scraping.youtube(playlist_url)[int(startpoint):endpoint]
                await self.play_each_song(song_list, ctx, add_position)
                await self.song_add_disp_msg(playlist_check, ctx, song_list, add_position)
                return len(song_list)
            except:
                await ctx.send(">>> ------------------Link not supported------------------\
                     \n (Youtube Mixes and private links not available from YT API) \n------------------Try again------------------ 😅\n.")
                return
        
        elif spotify_check != None:
            playlist_check = re.search('playlist', playlist_url)
            if not playlist_check:
                endpoint = 1
            else:
                await ctx.send(">>> Please wait ...")

            song_list = spotify_class.spotify_song_list(playlist_url)[int(startpoint):endpoint]
            await self.play_each_song(song_list, ctx, add_position)
            await self.song_add_disp_msg(playlist_check, ctx, song_list, add_position)
            return len(song_list)

        elif http_check != None:
            await ctx.send(">>> ------------------Link not supported------------------\
                    \n (Only Youtube and Spotify Link work) \n------------------Try again------------------ 😅\n.")
            return

        else:
            playlist_check = False
            song_info, yt_code = self.get_yt_code(playlist_url)
            self.build_entry(ctx, song_info, yt_code)
            self.guild[ctx.guild].insert(add_position, self.entry) 
            await self.playall_song_function(ctx, discord)
            await self.song_add_disp_msg(playlist_check, ctx, song_info, add_position)
            return 1
    
    async def song_add_disp_msg(self, playlist_check, ctx, song_list, add_position):
        if playlist_check:
            await ctx.send(f">>> \nAdded to Q: \n{len(song_list)} songs added by [{self.entry['user'][0:-5]}] at index {add_position+1}\n.")
        else:
            if self.index[ctx.guild] != add_position:
               await ctx.send(f">>> \nAdded to Q: \n{add_position+1}. {self.entry['name']} 🎶 [{self.entry['user'][0:-5]}] \n.")
            else:
               await ctx.send(f">>> \nNow Playing: \n{add_position+1}. {self.entry['name']} 🎶 [{self.entry['user'][0:-5]}] \n.")

    
    async def play_each_song(self, song_list, ctx, add_position):
        try:
            song_info, yt_code = self.get_yt_code(song_list[0])
            song_entry = self.build_entry(ctx, song_info, yt_code)
            self.guild[ctx.guild].insert(add_position, song_entry)  
            await self.playall_song_function(ctx, discord)
        except Exception as e:
            print(e)

        if len(song_list) >= 1:
            print("Its a playlist 👍")
            # add_position + 1 needed for reverse playlist glitch fix
            song_list = song_list[::-1]
            for song in song_list[0:-1]:
                try:
                    song_info, yt_code = self.get_yt_code(song)
                    song_entry = self.build_entry(ctx, song_info, yt_code)
                    self.guild[ctx.guild].insert(add_position + 1, song_entry)  
                    await self.playall_song_function(ctx, discord)
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
            self.shuffle[ctx.guild] = False

        num_of_songs = await self.check_input(ctx, playlist_url, startpoint, endpoint, position)
        return self.entry, num_of_songs

        
    def delete_entry(self, ctx, num):
        if num <= self.index[ctx.guild]:
            self.index[ctx.guild] -= 1
            
        current_queue = self.guild[ctx.guild]
        del current_queue[num]
        return


    def next_track(self, ctx):
        if self.shuffle[ctx.guild]:
            random = randint(0, len(self.guild[ctx.guild]) - 1)
            print(f"Index is : {random}")
            self.index[ctx.guild] = random
            return self.index[ctx.guild]
            
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


    def shuffle_switch(self, ctx):
        if self.shuffle[ctx.guild] == False:
            self.shuffle[ctx.guild] = True
        elif self.shuffle[ctx.guild] == True:
            self.shuffle[ctx.guild] = False
        print(f'Currently shuffleing: {self.shuffle[ctx.guild]}')
        return self.shuffle[ctx.guild]


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

    async def empty_channel_check(self, ctx):
        members = ctx.me.voice.channel.members
        print("NOT dc-ing")
        if len(members) <= 1:
            print("dc-ing")
            self.clear_que(ctx, 'y')
            await ctx.voice_client.disconnect()

    # async def playall_song_function(self, ctx, discord):
    #     self.play_song_function(ctx, discord)

    async def playall_song_function(self, ctx, discord):
        await self.empty_channel_check(ctx)

        # Fixes randomly skipping music due to errors
        ffmpeg_options = {
        'options': '-vn',
        "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
        }
        vcclient = ctx.voice_client
        if not vcclient.is_playing():
            guild_queue = self.guild[ctx.guild]
            song = guild_queue[self.next_track(ctx)]
            vcclient.play(discord.FFmpegPCMAudio(song["url"], **ffmpeg_options), after = lambda func: self.play_song_function(ctx, discord))
            vcclient.source = discord.PCMVolumeTransformer(vcclient.source)
            vcclient.source.volume = 1

    def play_song_function(self, ctx, discord):
        # Architecture:
        #   call song -> check if playing -> not playing: play now
        #                                   |
        #                                   -> playing: wait
    
        # Fixes randomly skipping music due to errors
        ffmpeg_options = {
        'options': '-vn',
        "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
        }

        print(f'First it is : {self.index[ctx.guild]}')
        vcclient = ctx.voice_client
        
        if not vcclient.is_playing():

            guild_queue = self.guild[ctx.guild]
            song = guild_queue[self.next_track(ctx)]
            vcclient.play(discord.FFmpegPCMAudio(song["url"], **ffmpeg_options), after = lambda func: self.play_song_function(ctx, discord))
            vcclient.source = discord.PCMVolumeTransformer(vcclient.source)
            vcclient.source.volume = 1
            print(f'middle it is : {self.index[ctx.guild]}')
        print(f'last it is : {self.index[ctx.guild]}')




if __name__ == "__main__":
    import main