import re               #To lookup Youtube links
import urllib.parse
import urllib.request
import os
from myfiles.secrets import bot_token_id

import discord
import youtube_dl                   #Download Youtube link
from discord.ext import commands
import collections                  #For deque method in lists to make a Q

bot = commands.Bot(command_prefix = '`')
client = discord.Client()

TOKEN = bot_token_id

class Yutoob:
    def get_yt_video_code(self, arg):
        query_string = urllib.parse.urlencode({"search_query" : arg})
        html_content = urllib.request.urlopen("https://www.youtube.com/results?" + query_string)
        search_results = re.findall(r'"videoId":"(.{11})', html_content.read().decode())        #Find song ID on Youtube
        return search_results[0]

    def add_to_q(self, words):
        with open("myfiles/songQ.txt", "a+") as file_object:
                video_id = file_object.read().splitlines()

                # Check if value exists, if not, then append to file
                if self.get_yt_video_code(words) not in video_id:
                    file_object.seek(0)             # Move read cursor to the start of file.
                    data = file_object.read(10)     # If file is not empty then append '\n'
                    if len(data) > 0:
                        file_object.write("\n")     # Append text at the end of file
                    file_object.write(self.get_yt_video_code(words))
    
    def read_q(self):
        with open("myfiles/songQ.txt", "r") as file_object:
                video_id = file_object.read().splitlines()
        return video_id


    def get_music_url(self,index):
        with open("myfiles/songQ.txt", "r") as f:
            video_id = f.read().splitlines()

        full_link = ('https://www.youtube.com/watch?v=' + video_id[index])

        return full_link

    def play_q(self):
        for fname in os.listdir("myfiles/"):
            # Apply file type filter   
            if fname.endswith(song + '.webm'):
                file = fname
        print(file)

    def download_from_yt(self, index = 0):
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([self.get_music_url(index)])

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



@bot.command()
async def jump(ctx, index):
    run = Yutoob.get_music_url(index)


@bot.command(aliases = ['classp'])
async def q(ctx):
    hmm = Yutoob()
    q = hmm.read_q()
    
    await ctx.send(f"``` {q} ```")


@bot.command(aliases = ['p'])
async def play(ctx, *, input):

    hmm = Yutoob()

    hmm.add_to_q(input)

        # username.append(ctx.message.author)

    np = hmm.read_q()

    await ctx.send('now playing: ' + "str(index)" + ' link=> https://www.youtube.com/watch?v=' + np[0])

    hmm.download_from_yt()
    
    await ctx.send(f'Download Complete')

    # Repeat for each file in the directory  
    for fname in os.listdir("myfiles/"):
        # Apply file type filter   
        if fname.endswith(np[0] + '.webm'):
            file = fname
    print(file)


    source = await discord.FFmpegOpusAudio.from_probe(file, method='fallback')
    ctx.voice_client.play(source)

@bot.command(aliases = ['m'])
async def vcmute(ctx):
    vc = ctx.author.voice.channel
    for member in vc.members:
        await member.edit(mute=True)

@bot.command(aliases = ['um'])
async def vcunmute(ctx):
    vc = ctx.author.voice.channel
    for member in vc.members:
        await member.edit(mute=False)

@bot.event
async def on_ready():
    print('Bot is ready.')

bot.run(TOKEN)