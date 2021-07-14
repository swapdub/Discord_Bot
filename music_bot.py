# to add bot to your server click here : https://discord.com/oauth2/authorize?client_id=730602425807011847&permissions=8&scope=bot
import re
import os
import json
import requests
import youtube_dl
import pandas as pd

import discord
from discord.ext import commands
# from keep_alive import keep_alive

my_secret = os.environ['TOKEN']


# Discord added this as an extra permission to allow retrieving members related data
intents = discord.Intents().all()


# client = discord.Client()
bot = commands.Bot(command_prefix='`', intents = intents)

df = pd.DataFrame()
count = 0

def get_quote():
    response = requests.get("https://zenquotes.io/api/random")
    json_data = json.loads(response.text)
    quote = json_data[0]["q"] + " - " + json_data[0]["a"]
    
    return quote


def get_yt_video_code(arg):
    html_content = requests.get("https://www.youtube.com/results?search_query=" + arg)
    search_results = re.findall(r'"videoId":"(.{11})"', html_content.text)  #Find song ID on Youtube

    return search_results[1]


@bot.event
async def on_ready():
    print(" We have logged in as {0.user}".format(bot))


@bot.event
async def on_message(arg):
    arg.content = arg.content.lower()
    if arg.author == bot.user:
      return
    
    """KHAN related messages"""

    global count
    if arg.content.startswith("-a") and arg.author:
      count += 1
      await arg.delete()
      await arg.channel.send("Khan has used 'Anyways' " + str(count) + " times in this conversation.")
    
    if arg.content.startswith("-c") and arg.author:
      count -= 1
      await arg.delete()
      await arg.channel.send("Khan has used 'Anyways' " + str(count) + " times in this conversation.")

    if arg.content == ("reset") and arg.author:
      count = 0
      await arg.delete()
      await arg.channel.send("'Anyways' counter has reset!")
    
    if arg.content.startswith("khan says"):
        await arg.channel.send("Anyways")

    if arg.content.find("line") != -1 and arg.content.find("tamatar") != -1:
        await arg.channel.send("https://tenor.com/view/paisa-hi-hoga-gif-20395381")


    """OTHER messages"""

    if arg.content.startswith("akku bole toh"):
        await arg.channel.send("Samurai Jack ka enemy")

    if arg.content.startswith("good one"):
        await arg.channel.send("Thanks lol! ;)")
    

    """ 
    THIS LINE IS IMPORTANT WHEN USING BOT FOR MESSAGES !!!
    (its a quirk of using the extension's bot library)
    """
    await bot.process_commands(arg) 

# @client.event
# async def on_message(message):
#     if message.content.startswith("Khan says"):
#         # quote = get_quote()
#         await message.channel.send("Anyways")


# @bot.event
# async def on_message(arg):




@bot.command(aliases=['j'])
async def join(ctx):
    # Connect directly
    print(ctx.guild)
    try:
        vc = ctx.author.voice.channel
        await vc.connect()

    # Dont do anything if error
    except AttributeError:
        return

    # Disconnect then connect to new channel
    except Exception as e:
        print(e)
        await ctx.voice_client.disconnect()
        vc = ctx.author.voice.channel
        await vc.connect()


@bot.command(aliases=['l'])
async def leave(ctx):
    print(ctx.author)
    try:
        await ctx.voice_client.disconnect()
    except:
        return


@bot.command(aliases=['t'])
async def test(ctx, *, arg):
    await ctx.send(arg)


que = {}
q_index = 0
@bot.command(aliases=['p'])
async def play(ctx, *, arg):
    global df, que, q_index

    vc = ctx.author.voice.channel

    try:
        await vc.connect()

    # # Dont do anything if error
    except AttributeError:
        pass
    except Exception as e:
        print(e)
        pass

    # # Disconnect then connect to new channel
    # except Exception as e:
    #   print(e)
    # await ctx.voice_client.disconnect()
    # vc = ctx.author.voice.channel
    # await vc.connect()
    # songID = get_yt_video_code(arg)

    df = df.append(
        {
            'Server': ctx.guild,
            'Song': arg,
            "Author": ctx.author,
            # "YT name": song_info["title"]
        },
        ignore_index=True)

    
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessor_args': ['-ar', '16000'],
        'keepvideo': True,
        'default_search': 'auto',
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        song_info = ydl.extract_info("https://www.youtube.com/watch?v=" + get_yt_video_code(arg), download=False)
    
    # vcclient.stop()
    que.append(song_info)
    vcclient = ctx.voice_client
    if not vcclient.is_playing():
      vcclient.play(discord.FFmpegPCMAudio(que[q_index]["url"]))
      vcclient.source = discord.PCMVolumeTransformer(vcclient.source)
      vcclient.source.volume = 0.5
      await ctx.send(f"```Now Playing: {song_info['title']} [{str(ctx.author)}] ```")
    print(vcclient.is_playing())


@bot.command()
async def ping(ctx):
    await ctx.send(f"{ctx.voice_client.average_latency * 1000} ms")

@bot.command(aliases=['n'])
async def next(ctx):
    global q_index
    
    q_index += 1
    vcclient = ctx.voice_client

    if vcclient.is_playing():
      vcclient.stop()
    vcclient.play(discord.FFmpegPCMAudio(que[q_index]["url"]))
    vcclient.source = discord.PCMVolumeTransformer(vcclient.source)
    vcclient.source.volume = 0.5

    await ctx.send(f"```Now Playing: {que[q_index]['title']} [{str(ctx.author)}] ```")


@bot.command()
async def prev(ctx):
    global q_index

    q_index -= 1

    vcclient = ctx.voice_client
    if vcclient.is_playing():
      vcclient.stop()
    vcclient.play(discord.FFmpegPCMAudio(que[q_index]["url"]))
    vcclient.source = discord.PCMVolumeTransformer(vcclient.source)
    vcclient.source.volume = 0.5

    await ctx.send(f"```Now Playing: {que[q_index]['title']} [{str(ctx.author)}] ```")

@bot.command(aliases=['q'])
async def queue(ctx):
    await ctx.send(f"```Current queue:\n{df}```")
    # await ctx.send(f"```Current queue:\n{que}```")


@bot.command(aliases=['r'])
async def rm(ctx, num: int):
    global df, que
    try:
        print(num)
        df.pop(num)
        que.pop(num)
    except ValueError:
        await ctx.send("Whoops, numbers only please!!")
        return
    except KeyError:
        await ctx.send("Whoops, nothing to clear!!")
    except:
        await ctx.send("Whoops, something went wrong!!")
        return


@bot.command(aliases=['m'])
async def vcmute(ctx):
    vc = ctx.author.voice.channel
    for member in vc.members:
        print(member)
        await member.edit(mute=True)


@bot.command(aliases=['um'])
async def vcunmute(ctx):
    vc = ctx.author.voice.channel
    for member in vc.members:
        await member.edit(mute=False)


# keep_alive()
bot.run(my_secret)
# client.run(my_secret)