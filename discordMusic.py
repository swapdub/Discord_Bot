import re               #To lookup Youtube links
import urllib.parse
import urllib.request
import os

import discord
import youtube_dl                   #Download Youtube link
from discord.ext import commands
import collections                  #For deque method in lists to make a Q

bot = commands.Bot(command_prefix = '`')

client = discord.Client()

TOKEN = 'NzMwNjAyNDI1ODA3MDExODQ3.XwZ4ow.kkUqM9YSFyDq7o8vY4AhQDt2E-g'

class Youtube:
    def __init__(self, arg):
        self.arg = arg

    def get_yt_video_code(self):
        query_string = urllib.parse.urlencode({"search_query" : self.arg})
        html_content = urllib.request.urlopen("https://www.youtube.com/results?" + query_string)
        search_results = re.findall(r'"videoId":"(.{11})', html_content.read().decode())        #Find song ID on Youtube
        return search_results

    def add_to_q(self):
        with open("myfiles/songQ.txt", "a+") as file_object:
                video_id = file_object.read().splitlines()

                # Check if value exists, if not, then append to file
                if self.get_yt_video_code not in video_id:
                    file_object.seek(0)             # Move read cursor to the start of file.
                    data = file_object.read(10)     # If file is not empty then append '\n'
                    if len(data) > 0:
                        file_object.write("\n")     # Append text at the end of file
                    file_object.write(self.get_yt_video_code)
    
    def get_music_url(self):
        with open("myfiles/songQ.txt", "r") as f:
            video_id = f.read().splitlines()

        full_link = ('https://www.youtube.com/watch?v=' + video_id[self.index])

        return full_link

    def download_from_yt(self):
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([self.get_music_url])

#youtube Video download settings
ydl_opts = {
       'format': 'bestaudio/best',
       'postprocessor_args': 
           [
           '-ar', '16000'
           ],
       'keepvideo': True,
       'default_search': 'auto',
   }

Q = collections.deque()
username = collections.deque()

@bot.command()
async def ping(ctx):
    await ctx.send(f'Pong! {round(bot.latency * 1000)}ms')

@bot.command(aliases = ['j'])
async def join(ctx):
    vc = ctx.author.voice.channel
    await vc.connect()  

@bot.command(aliases = ['die','dc','bye'])
async def leave(ctx):
    await ctx.voice_client.disconnect() 



@bot.command(aliases = ['p'])
async def play(ctx, *, input):

    query_string = urllib.parse.urlencode({"search_query" : input})
    html_content = urllib.request.urlopen("https://www.youtube.com/results?" + query_string)
    search_results = re.findall(r'"videoId":"(.{11})', html_content.read().decode())        #Find song ID on Youtube
    

    exists = 1                  #checking if song exists in Q
    for song in Q:
        if song == search_results[0]:
            exists = 0          #0 so if there is a song, song is not appended into the queue
    
    if exists == 1 :
        Q.append(search_results[0])
        #print(Q)
        username.append(ctx.message.author)

    index = 1
    
    for song in Q:  #downloading all songs from Q -> try better way, by making it download on new track
        download = ('https://www.youtube.com/watch?v=' + song)*(input[0:5] != 'https') + input*(input[0:5] == 'https')

        await ctx.send('now playing: ' + str(index) + ' link=> https://www.youtube.com/watch?v=' + song)

        index = index + 1

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([download])
    
        await ctx.send(f'Download Complete')

        # Repeat for each file in the directory  
        for fname in os.listdir():
            # Apply file type filter   
            if fname.endswith(song + '.webm'):
                file = fname
        print(file)


        source = await discord.FFmpegOpusAudio.from_probe(file, method='fallback')
        ctx.voice_client.play(source)
    

@bot.event
async def on_ready():
    print('Bot is ready.')
bot.run(TOKEN)


x =2
y= 3
z= 4

print("yo wassup")