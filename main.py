# to add bot to your server click here : https://discord.com/oauth2/authorize?client_id=730602425807011847&permissions=8&scope=bot
import os
import re
import json
import discord
from discord.ext import commands

# user Libraries
from music_q import Q
from secret import discord_token
import scraping
import spotify


my_secret = discord_token


# Discord added this as an extra permission to allow retrieving members related data
intents = discord.Intents().all()


# client = discord.Client()
bot = commands.Bot(command_prefix='-', intents = intents)

que = Q()

# Template function kept from a tutorial
def get_quote():
    response = requests.get("https://zenquotes.io/api/random")
    json_data = json.loads(response.text)
    quote = json_data[0]["q"] + " - " + json_data[0]["a"]
    
    return quote


def play_song_function(ctx, discord):
    # Architecture:
    #   call song -> check if playing -> not playing: play now
    #                                   |
    #                                   -> playing: wait
 
    # Fixes randomly skipping music due to errors
    ffmpeg_options = {
    'options': '-vn',
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
    }

    print(f'First it is : {que.index[ctx.guild]}')
    vcclient = ctx.voice_client
    
    if not vcclient.is_playing():
        song = que.guild[ctx.guild][que.next_track(ctx)]
        vcclient.play(discord.FFmpegPCMAudio(song["url"], **ffmpeg_options), after = lambda func: play_song_function(ctx, discord))
        vcclient.source = discord.PCMVolumeTransformer(vcclient.source)
        vcclient.source.volume = 1
        print(f'middle it is : {que.index[ctx.guild]}')
    print(f'last it is : {que.index[ctx.guild]}')

@bot.event
async def on_ready():
    print(" We have logged in as {0.user}".format(bot))


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


@bot.command(aliases=['dc', 'die', 'disconnect'])
async def leave(ctx, arg = "y"):
    que.clear_que(ctx,arg)
    try:
        await ctx.voice_client.disconnect()
    except:
        return

@bot.command(aliases=['s'])
async def save(ctx):
    que.save_data(ctx)

@bot.command()
async def link(ctx):
    await ctx.send(f'Youtube link : {que.nowplaying(ctx, "YT-video")}')

@bot.command(aliases=['l'])
async def loop(ctx):
    if que.loop_switch(ctx):
        await ctx.send(f"```Now looping Queue```")
    else:
        await ctx.send(f"```Queue Looping disabled```")


@bot.command(aliases=['t'])
async def test(ctx, *, arg):
    await ctx.send(arg)

@bot.command(aliases=['jm'])
async def jump(ctx, arg:int):
    que.jump(ctx, (arg - 1))

    vcclient = ctx.voice_client
    if vcclient.is_playing():
        vcclient.stop()
    play_song_function(ctx, discord)
    await ctx.send(f"```Now Playing: {que.nowplaying(ctx)} [{que.nowplaying(ctx, 'user')}] ```")


@bot.command(aliases=['p'])
async def play(ctx, *, arg):
    vc = ctx.author.voice.channel
    try:
        await vc.connect()
    except AttributeError: # Dont do anything if error
        print("AttributeError")
    except Exception as e:
        print(e)

    STARTPOINT = 0
    ENDPOINT = 1
    try:
        SONG_ADD_POSTION = len(que.guild[ctx.guild])
    except:
        SONG_ADD_POSTION = 0

    song, num_of_songs = que.add_entry(ctx, arg, STARTPOINT, ENDPOINT, SONG_ADD_POSTION)
        
    play_song_function(ctx, discord)
    vcclient = ctx.voice_client
    if not vcclient.is_playing():        
        #using add entry because we want entry song only, no need for index
        await ctx.send(f"```Now Playing: {song['name']} [{song['user'][0:-5]}] ```")
    else:
        await ctx.send(f"```Added to Q: {song['name']} [{song['user'][0:-5]}] ```")


@bot.command(aliases=['pn'])
async def playnext(ctx, *, arg, startpoint = 0, endpoint = -1):
    try:
        SONG_ADD_POSTION = que.index[ctx.guild]  + 1
        song, num_of_songs = que.add_entry(ctx, arg, startpoint, endpoint, SONG_ADD_POSTION)
        await ctx.send(f"```Added to Q: {song['name']} [{song['user'][0:-5]}] ```")
    except:
        await ctx.send(f"```There is no Queue to add to yet```")    
    
@bot.command(aliases=['i'])
async def index(ctx):
    await ctx.send(f"Current Song Index : {que.index[ctx.guild] + 1} | Queue Looping: {que.loop[ctx.guild]}")

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
    vcclient = ctx.voice_client
    if vcclient.is_playing():
        vcclient.stop()
    play_song_function(ctx, discord)
    
    # Using Now playing because next follows index
    await ctx.send(f"```Now Playing: {que.nowplaying(ctx)} [{que.nowplaying(ctx, 'user')}] ```")


@bot.command(aliases=[])
async def prev(ctx):
    my_que = que.guild[ctx.guild][que.prev_track(ctx)]["url"]

    vcclient = ctx.voice_client
    if vcclient.is_playing():
      vcclient.stop()
    vcclient.play(discord.FFmpegPCMAudio(my_que))
    vcclient.source = discord.PCMVolumeTransformer(vcclient.source)
    vcclient.source.volume = 1

    await ctx.send(f"```Now Playing: {que.nowplaying(ctx)} [{que.nowplaying(ctx, 'user')}] ```")

@bot.command(aliases=['q'])
async def queue(ctx, page = 1):
    await ctx.send(f"```Current queue:\n{que.my_que(ctx, page)}```")


@bot.command(aliases=['r', 'rm', 'del'])
async def remove(ctx, num: int):
    try:
        zero_adjusted_num = num - 1
        await ctx.send(f"```Removed:\n{que.guild[ctx.guild][zero_adjusted_num]['name']}```")
        que.delete_entry(ctx, zero_adjusted_num)

        # In case we remove the now playing song
        # Using the next function will should get us to index 0
        if num == que.index[ctx.guild]:
            que.index[ctx.guild] = que.index[ctx.guild] - 1

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
async def clear(ctx, arg = 'y'):
    que.clear_que(ctx, arg)

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

@bot.command(aliases=['pa', 'pall'])
async def playall(ctx, arg, startpoint = 0, endpoint = -1):
    vc = ctx.author.voice.channel
    try:
        await vc.connect()
    except AttributeError: # Dont do anything if error
        print("AttributeError")
    except Exception as e:
        print(e)

    try:
        SONG_ADD_POSTION = len(que.guild[ctx.guild])
    except:
        SONG_ADD_POSTION = 0

    song, num_of_songs = que.add_entry(ctx, arg, startpoint, endpoint, SONG_ADD_POSTION)
        
    play_song_function(ctx, discord)
    vcclient = ctx.voice_client
    if not vcclient.is_playing():        
        # using add entry because we want entry song only, no need for index
        await ctx.send(f"```Now Playing: {num_of_songs} songs added by [{song['user'][0:-5]}] ```")
    else:
        await ctx.send(f"```Added to Q: {num_of_songs} songs added by [{song['user'][0:-5]}] ```")

@bot.command(aliases=['pna', 'pnal', 'pnall'])
async def playnextall(ctx, arg, startpoint = 0, endpoint = -1):
    vc = ctx.author.voice.channel
    try:
        await vc.connect()
    except AttributeError: # Dont do anything if error
        print("AttributeError")
    except Exception as e:
        print(e)
    try:
        SONG_ADD_POSTION = que.index[ctx.guild] + 1
        song, num_of_songs = que.add_entry(ctx, arg, startpoint, endpoint, SONG_ADD_POSTION)
        await ctx.send(f"```Added to Q: {num_of_songs} songs added by [{song['user'][0:-5]}] ```")
    except:
        await ctx.send(f"```There is no Queue to add to yet```")    




bot.run(my_secret)