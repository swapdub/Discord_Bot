import re
import json
import requests
import datetime
from collections import deque
import youtube_dl
import os
import scraping

import spotify

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

INITIAL_INDEX_VALUE = -1

class Q:

    ydl_opts = {
        "format": "bestaudio/best",
        "postprocessor_args": ["-ar", "48000"], # Audio Freq:48 KHz
        "keepvideo": True,
        "default_search": "auto",
    }
    def __init__(self):
        self.guild = dict()
        self.index = dict()
        self.entry = dict()
        self.loop = dict()


    def check_input(self, ctx, playlist_url, startpoint, endpoint, add_position):
        print(playlist_url)
        youtube_check = re.search(r'youtube.com/|youtu.be/', playlist_url)
        spotify_check = re.search('spotify.com/', playlist_url)

        if youtube_check != None:
            song_list = scraping.youtube(playlist_url)
            for yt_code in song_list[startpoint:endpoint]:
                try:
                    song_info = self.yt_dl_info(yt_code)
                    self.entry = {
                        "guild": str(ctx.guild),
                        "channel": str(ctx.author.voice.channel),
                        "user": str(ctx.author),
                        "time": str(datetime.datetime.now()),
                        "name": song_info["title"],
                        "YT-video": "https://www.youtube.com/watch?v=" + yt_code,
                        "url": song_info["url"]
                    }
                    print(song_info['title'])
                    self.guild[ctx.guild].insert(add_position, self.entry)
                except Exception as e:
                    print(e)

            return len(song_list)
        
        elif spotify_check != None:
            song_list = scraping.spotify(playlist_url)
            print(song_list)
            for song in song_list[startpoint:endpoint]:
                try:
                    self.build_entry(ctx, song)
                    # self.guild[ctx.guild].insert(len(self.guild[ctx.guild]), self.entry)
                    self.guild[ctx.guild].insert(add_position, self.entry)  
                except Exception as e:
                    print(e)
            return  len(song_list)

        else:
            self.build_entry(ctx, playlist_url)
            self.guild[ctx.guild].insert(add_position, self.entry) 
            return 1
        
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

    def build_entry(self, ctx, search_term):
        song_info, yt_code = self.get_yt_code(search_term)
        self.entry = {
            "guild": str(ctx.guild),
            "channel": str(ctx.author.voice.channel),
            "user": str(ctx.author),
            "time": str(datetime.datetime.now()),
            "name": song_info["title"],
            "YT-video": "https://www.youtube.com/watch?v=" + yt_code[0],
            "url": song_info["url"]
        }
        return self.entry


    def add_entry(self, ctx, playlist_url, startpoint, endpoint, position):
        if ctx.guild not in self.guild:
            self.index[ctx.guild] = INITIAL_INDEX_VALUE
            self.guild[ctx.guild] = list()
            self.loop[ctx.guild] = False
        print(ctx.guild)
        num_of_songs = self.check_input(ctx, playlist_url, startpoint, endpoint, position)
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
        self.index[ctx.guild] = INITIAL_INDEX_VALUE


    def nowplaying(self, ctx, arg="name"):
        index = self.index[ctx.guild]
        return self.guild[ctx.guild][index][arg]


    def jump(self, ctx, arg):
        arg -= 1
        if arg <= 0:
            arg = 0
        elif arg > len(self.guild[ctx.guild]) - 1:
            arg = len(self.guild[ctx.guild]) - 1
        
        self.index[ctx.guild] = arg
        return self.index[ctx.guild]


    def my_que(self, ctx, page_num):
        formattedQ = []
        index_count = 1
        q_view_size = 8
                    #   False             True                    Condition
        endpoint    = (q_view_size * page_num, len(self.guild[ctx.guild]))[q_view_size * page_num >= len(self.guild[ctx.guild])]
        startpoint  = q_view_size * (page_num - 1)
        for entry in self.guild[ctx.guild][startpoint : endpoint]:
            string = f"{index_count + (q_view_size * (page_num - 1))}. {entry['name']} added by {entry['user'][:-5]}"
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