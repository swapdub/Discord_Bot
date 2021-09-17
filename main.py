# to add bot to your server click here : https://discord.com/oauth2/authorize?client_id=730602425807011847&permissions=8&scope=bot
import os
import re

from music_q import Q
import secret
import json
import discord
from discord.ext import commands
# from keep_alive import keep_alive

my_secret = secret.discord_token


# Discord added this as an extra permission to allow retrieving members related data
intents = discord.Intents().all()


# client = discord.Client()
bot = commands.Bot(command_prefix='`', intents = intents)

que = Q()

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


@bot.command(aliases=['l', 'die'])
async def leave(ctx, arg = 'y'):
    que.clear_que(ctx, arg)
    try:
        await ctx.voice_client.disconnect()
    except:
        return


@bot.command(aliases=['t'])
async def test(ctx, *, arg):
    await ctx.send(arg)


@bot.command(aliases=['p'])
async def play(ctx, *, arg):

    vc = ctx.author.voice.channel
    song = que.add_entry(ctx, arg)
    

    try:
        await vc.connect()
    except AttributeError: # Dont do anything if error
        pass
    except Exception as e:
        print(e)
        pass
    

    def after_song_end():
        vcclient = ctx.voice_client
        vcclient.play(discord.FFmpegPCMAudio(que.guild[ctx.guild][que.next_track(ctx)]["url"]), after = lambda x: after_song_end())

    
    vcclient = ctx.voice_client
    if not vcclient.is_playing():
        vcclient.play(discord.FFmpegPCMAudio(song["url"]), after= lambda x: after_song_end())
        vcclient.source = discord.PCMVolumeTransformer(vcclient.source)
        vcclient.source.volume = 1
        
        #using add entry because we want entry song only, no need for index
        await ctx.send(f"```Now Playing: {song['name']} [{song['user']}] ```")
    else:
        await ctx.send(f"```Added to Q: {song['name']} [{song['user']}] ```")


@bot.command()
async def ping(ctx):
    await ctx.send(f"{ctx.voice_client.average_latency * 1000} ms")

@bot.command(aliases=['np'])
async def nowplaying(ctx, *, arg = "name"):
    if ctx.voice_client.is_playing():
        await ctx.send(f"Now playing: {que.nowplaying(ctx, arg)}")
    else:
        await ctx.send(f"No song playing rn")

@bot.command(aliases=['n'])
async def next(ctx):
    def after_song_end():
        vcclient = ctx.voice_client
        vcclient.play(discord.FFmpegPCMAudio(que.guild[ctx.guild][que.next_track(ctx)]["url"]), after = lambda x: after_song_end())

    vcclient = ctx.voice_client

    if vcclient.is_playing():
      vcclient.stop()
    vcclient.play(discord.FFmpegPCMAudio(que.guild[ctx.guild][que.next_track(ctx)]["url"]), after = lambda x: after_song_end())

    # Using Now playing because next follows index
    await ctx.send(f"```Now Playing: {que.nowplaying(ctx)} [{que.nowplaying(ctx, 'user')}] ```")


@bot.command(aliases=[])
async def prev(ctx):
    index = que.index[ctx.guild]
    # index -= 1
    if index > 0: 
        index -= 1
    que.index[ctx.guild] = index
    my_que = que.guild[ctx.guild]

    vcclient = ctx.voice_client
    if vcclient.is_playing():
      vcclient.stop()
    vcclient.play(discord.FFmpegPCMAudio(my_que[index]["url"]))
    vcclient.source = discord.PCMVolumeTransformer(vcclient.source)
    vcclient.source.volume = 1

    await ctx.send(f"```Now Playing: {que.nowplaying(ctx)} [{que.nowplaying(ctx, 'user')}] ```")

@bot.command(aliases=['q'])
async def queue(ctx):
    await ctx.send(f"```Current queue:\n{que.my_que(ctx)}```")


@bot.command(aliases=['r'])
async def rm(ctx, num: int):
    try:
        que.delete_entry(ctx, num - 1)

        #In case we remove the now playing song
        #Using the next function will should get us to index 0
        if num == 1:
            que.index[ctx.guild] = -1

    except ValueError:
        await ctx.send("Whoops, numbers only please!!")
        return
    except KeyError:
        await ctx.send("Whoops, nothing to clear!!")
    except Exception as e:
        print(e)
        await ctx.send("Whoops, something went wrong!!")
        return

@bot.command(aliases=[])
async def clear(ctx):
    que.clear_que(ctx)

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