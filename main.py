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
from utils import play_song_function


my_secret = discord_token


# Discord added this as an extra permission to allow retrieving members related data
intents = discord.Intents().all()

bot = commands.Bot(command_prefix='-', intents = intents)

que = Q()

# Template function kept from a tutorial
def get_quote():
    response = requests.get("https://zenquotes.io/api/random")
    json_data = json.loads(response.text)
    quote = json_data[0]["q"] + " - " + json_data[0]["a"]
    
    return quote


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
    await ctx.send(f'>>> Youtube link : {que.nowplaying(ctx, "YT-video")}')

@bot.command(aliases=['l'])
async def loop(ctx):
    if que.loop_switch(ctx):
        await ctx.send(f">>> Now looping Queue")
    else:
        await ctx.send(f">>> Queue Looping disabled")


@bot.command(aliases=['t'])
async def test(ctx, *, arg):
    await ctx.send(arg)

@bot.command(aliases=['jm'])
async def jump(ctx, arg:int):
    que.jump(ctx, (arg - 1))

    vcclient = ctx.voice_client
    if vcclient.is_playing():
        vcclient.stop()
    play_song_function(ctx, discord, que)
    await ctx.send(f">>> \nNow Playing: \n{que.index[ctx.guild] + 1}.{que.nowplaying(ctx)} [{que.nowplaying(ctx, 'user')}] \n.")


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
        SONG_ADD_POSITION = len(que.guild[ctx.guild])
    except:
        SONG_ADD_POSITION = 0

    song, num_of_songs = que.add_entry(ctx, arg, STARTPOINT, ENDPOINT, SONG_ADD_POSITION)
        
    play_song_function(ctx, discord, que)
    vcclient = ctx.voice_client
    if not vcclient.is_playing():        
        #using add entry because we want entry song only, no need for index
        await ctx.send(f">>> \nNow Playing: \n{que.index[ctx.guild] + 1}.{song['name']} [{song['user'][0:-5]}] \n.```")
    else:
        await ctx.send(f">>> \nAdded to Q: \n{len(que.guild[ctx.guild])}.{song['name']} [{song['user'][0:-5]}] \n.")


@bot.command(aliases=['pn'])
async def playnext(ctx, *, arg, startpoint = 0, endpoint = None):
    try:
        SONG_ADD_POSITION = que.index[ctx.guild]  + 1
        song, num_of_songs = que.add_entry(ctx, arg, startpoint, endpoint, SONG_ADD_POSITION)
        await ctx.send(f">>> \nAdded to Q: \n{que.index[ctx.guild] + 1}.{song['name']} [{song['user'][0:-5]}] \n.")
    except:
        await ctx.send(f">>> \nThere is no Queue to add to yet \n.")    
    
@bot.command(aliases=['i'])
async def index(ctx):
    await ctx.send(f">>> Current Song Index : {que.index[ctx.guild] + 1} | Queue Looping: {que.loop[ctx.guild]}")

@bot.command()
async def ping(ctx):
    await ctx.send(f">>> {ctx.voice_client.average_latency * 1000} ms")

@bot.command(aliases=['np'])
async def nowplaying(ctx, *, arg = "name"):
    if ctx.voice_client.is_playing():
        await ctx.send(f">>> Now playing: \n{que.index[ctx.guild] + 1}. {que.nowplaying(ctx, arg)}")
    else:
        await ctx.send(f">>> No song playing rn")

@bot.command(aliases=['n', 'skip'])
async def next(ctx):
    vcclient = ctx.voice_client
    if vcclient.is_playing():
        vcclient.stop()
    play_song_function(ctx, discord, que)
    
    # Using Now playing because next follows index
    await ctx.send(f">>> \nNow Playing: \n{que.index[ctx.guild] + 1}.{que.nowplaying(ctx)} [{que.nowplaying(ctx, 'user')}] \n.")


@bot.command(aliases=[])
async def prev(ctx):
    my_que = que.guild[ctx.guild][que.prev_track(ctx)]["url"]

    vcclient = ctx.voice_client
    if vcclient.is_playing():
      vcclient.stop()
    vcclient.play(discord.FFmpegPCMAudio(my_que))
    vcclient.source = discord.PCMVolumeTransformer(vcclient.source)
    vcclient.source.volume = 1

    await ctx.send(f">>> Now Playing: \n{que.index[ctx.guild] + 1}.{que.nowplaying(ctx)} [{que.nowplaying(ctx, 'user')}] \n.")

@bot.command(aliases=['q'])
async def queue(ctx, page = 1):
    page_size = 8
    songs = len(que.guild[ctx.guild])
    num_of_pages = [round(songs/page_size), round(songs/page_size) + 1][round(songs/page_size) < (songs/page_size)]
    await ctx.send(f"```css\n.Page_{page}_of_{num_of_pages} | .Total_number_of_Songs: {songs}\
        \n\n{que.my_que(ctx, page, page_size)}```")


@bot.command(aliases=['r', 'rm', 'del'])
async def remove(ctx, num: int):
    try:
        zero_adjusted_num = num - 1
        await ctx.send(f"```Removed:\n{num}.{que.guild[ctx.guild][zero_adjusted_num]['name']}```")
        que.delete_entry(ctx, zero_adjusted_num)

        # In case we remove the now playing song
        # Using the next function will should get us to index 0
        if num == que.index[ctx.guild]:
            que.index[ctx.guild] = que.index[ctx.guild] - 1

    except ValueError:
        await ctx.send(">>> Whoops, numbers only please!!")
        return
    except KeyError:
        await ctx.send(">>> Whoops, nothing to clear!!")
    except Exception as e:
        print(e)
        await ctx.send(">>> Whoops, something went wrong!!")
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
async def playall(ctx, arg, startpoint = 0, endpoint = None):
    vc = ctx.author.voice.channel
    await ctx.send(">>> Please wait ...")
    try:
        await vc.connect()
    except AttributeError: # Dont do anything if error
        print("AttributeError")

    except Exception as e:
        print(e)

    try:
        SONG_ADD_POSITION = len(que.guild[ctx.guild])
    except:
        SONG_ADD_POSITION = -1

    song, num_of_songs = que.add_entry(ctx, arg, startpoint, endpoint, SONG_ADD_POSITION)
    
    # play_song_function(ctx, discord, que)
    vcclient = ctx.voice_client
    if not vcclient.is_playing():        
        # using add entry because we want entry song only, no need for index
        await ctx.send(f">>> \nNow Playing: \n{num_of_songs} songs added by [{song['user'][0:-5]}] \n.")
    else:
        await ctx.send(f">>> \nAdded to Q: \n{num_of_songs} songs added by [{song['user'][0:-5]}] at index {len(que.guild[ctx.guild])}\n.")

@bot.command(aliases=['pna', 'pnal', 'pnall'])
async def playnextall(ctx, arg, startpoint = 0, endpoint = None):
    vc = ctx.author.voice.channel
    try:
        await vc.connect()
    except AttributeError: # Dont do anything if error
        print("AttributeError")
    except Exception as e:
        print(e)
    try:
        SONG_ADD_POSITION = que.index[ctx.guild] + 1
        song, num_of_songs = que.add_entry(ctx, arg, startpoint, endpoint, SONG_ADD_POSITION)
        await ctx.send(f">>> \nAdded to Q: \n{num_of_songs} songs added by [{song['user'][0:-5]}] at index {SONG_ADD_POSITION}\n.")
    except:
        await ctx.send(f">>> \nThere is no Queue to add to yet\n.")    

@bot.command(aliases=[])
async def dj(ctx):
    output = ["```CSS\nDJs for the current queue are:\n"]
    dj = []
    for entry in que.guild[ctx.guild]:
        dj.append(entry['user'][0:-5])
    user = set(dj)
    bullets = 1
    for name in user:
        string = f"{bullets}. {name} added: {dj.count(name)} songs"
        output.append(string)
        bullets += 1

    output.append('```')
    await ctx.send("\n".join(output))

# async def history(ctx, arg = ctx.author):

bot.run(my_secret)