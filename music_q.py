import re
import json
import requests
import datetime
from collections import deque
import youtube_dl
import os

# Logic : We have a dict with keys as 'Discord Server(ctx.guild)' name. 
#         Value is the que which is deque from collections library optimized 
#         for queue use

# CURRENT QUEUE ARCHITECTURE
#            -- A dictionary of guilds/Server as keys-- 
#            |                                        |
#       dict 1 (self.guilds)               dict 2 (self.index)
# A Queue of songs using deque()          Keep track of Q index
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
        # self.que = deque()
        self.index = dict()
        self.entry = dict()

    def get_yt_code(self, search_term):
        return

    def add_entry(self, ctx, search_term):

        html_content = requests.get(
            "https://www.youtube.com/results?search_query=" + search_term
        )
        self.yt_code = re.findall(
            r'"videoId":"(.{11})"', html_content.text
        )  # Find song ID on Youtube

        with youtube_dl.YoutubeDL(self.ydl_opts) as ydl:
            self.song_info = ydl.extract_info(
                "https://www.youtube.com/watch?v=" + self.yt_code[0], download=False
            )
            

        self.entry = {
            "guild": str(ctx.guild),
            "channel": str(ctx.author.voice.channel),
            "user": str(ctx.author),
            "time": str(datetime.datetime.now()),
            "name": self.song_info["title"],
            "YT-video": "https://www.youtube.com/watch?v=" + self.yt_code[0],
            "url": self.song_info["url"]
        }

        if ctx.guild not in self.guild:
            self.index[ctx.guild] = INITIAL_INDEX_VALUE
            self.guild[ctx.guild] = list()
            
        self.guild[ctx.guild].append(self.entry)
        
        return self.entry

    def delete_entry(self, ctx, num):
        if num < self.index[ctx.guild]:
            self.index[ctx.guild] -= 1
            
        de = self.guild[ctx.guild]
        del de[num]

    def next_track(self, ctx):
        if self.index[ctx.guild] < len(self.guild[ctx.guild]) - 1:
            self.index[ctx.guild] += 1

        return self.index[ctx.guild]

    def prev_track(self, ctx):
        if self.index[ctx.guild] > 0:
            self.index[ctx.guild] -= 1

        return self.index[ctx.guild]

    def clear_que(self, ctx, save):
        if save.lower == 'y' or save.lower == 'yes':
            print(save)
            self.save_data(ctx)
            # try:
            # except:
            #     pass
        print(save)
        self.guild[ctx.guild].clear()
        self.index[ctx.guild] = INITIAL_INDEX_VALUE

    def url(self):
        return

    def nowplaying(self, ctx, arg="name"):
        index = self.index[ctx.guild]
        return self.guild[ctx.guild][index][arg]

    def my_que(self, ctx):
        formattedQ = []
        count = 1

        for entry in self.guild[ctx.guild]:
            string = f"{count}. {entry['name']} added by {entry['user']}"
            formattedQ.append(string)
            count += 1

        formattedQ = "\n".join(formattedQ)

        return formattedQ

    def save_data(self, ctx):
        # A function to save user playlist statistics and 
        # data to json file with the following formatting 
        print("NEW_DATA")
        FILENAME = "discord_playlist.json"
        KEY = str(ctx.guild)
        NEW_DATA = { KEY : self.guild[ctx.guild]}
        # NEW_DATA = self.guild[ctx.guild]

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
            else:
                old_data[KEY] = NEW_DATA[KEY]
                print(f'File not empty2')
            with open(FILENAME, "w+") as fileW:
                json.dump(old_data, fileW, indent=2)


if __name__ == "__main__":
    import main