import re
import json
import requests
import datetime
from collections import deque
import youtube_dl

# Logic : We have a dict with keys as 'Discord Server(ctx.guild)' name. 
#         Value is the que which is deque from collections library optimized 
#         for queue use

# CURRENT QUEUE ARCHITECTURE
# A dictionary of guilds/Server as keys
# |
# -- A Queue of songs using deque()
#    |
#    -- Each Song entry 

class Q:

    ydl_opts = {
        "format": "bestaudio/best",
        "postprocessor_args": ["-ar", "24000"],
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
        # entry = dict()
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
        # get_yt_code(search_term)

        self.entry = {
            "url": self.song_info["url"],
            "name": self.song_info["title"],
            "user": str(ctx.author),
            "channel": str(ctx.author.voice.channel),
            "guild": str(ctx.guild),
            "time": str(datetime.datetime.now())
        }

        if ctx.guild not in self.guild:
            self.index[ctx.guild] = 0
            self.guild[ctx.guild] = deque()
            
        self.guild[ctx.guild].append(self.entry)

        # self.que.append(self.entry)
        
        return self.entry

    def delete_entry(self, ctx, num):
        de = self.guild[ctx.guild]
        del de[num]

    def next_track(self, ctx):
        if self.index[ctx.guild] <= len(self.guild[ctx.guild]):
            self.index[ctx.guild] += 1

        return self.index[ctx.guild]

    def prev_track(self, ctx):
        if self.index[ctx.guild] > 0:
            self.index[ctx.guild] -= 1

        return self.index[ctx.guild]

    def clear_que(self, ctx, save = 'n'):
        if save == 'y' or save == 'yes':
            print(save)
            self.save_data(ctx)
        self.guild[ctx.guild].clear()
        self.index[ctx.guild] = 0

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
        # A function to save user playlist statistics and data to 
        # json file with the following formatting 

        with open("discord_playlist.json", "a") as file:
            # Delete last ']' character
            file.seek(-2, os.SEEK_CUR)
            
            # Append our json converted data
            for i in self.guild[ctx.guild]:
                json.dump(i, file, indent=2)
                file.write(",\n")

            # format as data end with last character being ']'
            file.seek(-2, os.SEEK_CUR)
            file.write("] ")



if __name__ == "__main__":
    import main