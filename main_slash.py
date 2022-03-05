# to add bot to your server click here : https://discord.com/oauth2/authorize?client_id=730602425807011847&permissions=8&scope=bot
from ast import arg
import os
from pydoc import cli
import re
import json
import diskord
from diskord.ext import commands

# user Libraries
from music_q import Q
from secret import discord_token, test_server
import scraping
import spotify
from utils import play_song_function


my_secret = discord_token


# Discord added this as an extra permission to allow retrieving members related data
# client = diskord.Client(application_command_guild_ids=[test_server]) # For testing
client = diskord.Client()

que = Q()

@client.event
async def on_ready():
    print(" We have logged in as {0.user}".format(client))


@client.slash_command(description="Join voice channel")
# @diskord.application.option('arg')
async def join(ctx):
    # Connect directly
    try:
        vc = ctx.author.voice.channel
        await vc.connect()
        await ctx.respond("Joining")

    # Dont do anything if error
    except AttributeError:
        await ctx.respond("Attribute Error")
        return

    # Disconnect then connect to new channel
    except Exception as e:
        print(e)
        await ctx.voice_client.disconnect()
        vc = ctx.author.voice.channel
        await vc.connect()
        await ctx.respond("Reconnected")


@client.slash_command(description="Leave voice channel")
@diskord.application.option('save')
async def disconnect(ctx, save: str = 'y'):
    que.clear_que(ctx, save)
    try:
        await ctx.voice_client.disconnect()
        await ctx.respond("Have a nice day")
    except:
        await ctx.respond("Oops Error")
        return

@client.slash_command(description="Save current playlist")
# @diskord.application.option('arg')
async def save(ctx):
    que.save_data(ctx)
    await ctx.respond("Saved Playlist")


@client.slash_command(description="View youtube link of Now Playing song")
# @diskord.application.option('arg')
async def link(ctx):
    await ctx.respond(f'>>> Youtube link : {que.nowplaying(ctx, "YT-video")}')

@client.slash_command(description="Loop queue")
# @diskord.application.option('arg')
async def loop(ctx):
    if que.loop_switch(ctx):
        await ctx.respond(f">>> Now looping Queue")
    else:
        await ctx.respond(f">>> Queue Looping disabled")


@client.slash_command(description="Echo what you enter")
@diskord.application.option('arg')
async def test(ctx, *, arg):
    await ctx.respond(arg)

@client.slash_command(description="Echo what you enter")
@diskord.application.option('arg')
async def test2(ctx, arg):
    await ctx.respond(arg)

@client.slash_command(description="Echo what you enter")
@diskord.application.option('arg')
async def test3(ctx, arg):
    await ctx.respond(arg)

@client.slash_command(description="Jump to the song number in Queue")
@diskord.application.option('index')
async def jump(ctx, index:int):
    que.jump(ctx, (index - 1))

    vcclient = ctx.voice_client
    if vcclient.is_playing():
        vcclient.stop()
    play_song_function(ctx, diskord, que)
    await ctx.respond(f">>> \nNow Playing: \n{que.index[ctx.guild] + 1}.{que.nowplaying(ctx)} [{que.nowplaying(ctx, 'user')}] \n.")

@client.slash_command(description="Add a single song")
@diskord.application.option('arg', description='Type song name or link here. For playlist use playall')
async def play(ctx, arg: str):
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

    song, num_of_songs = await que.add_entry(ctx, arg, STARTPOINT, ENDPOINT, SONG_ADD_POSITION)
        
    play_song_function(ctx, diskord, que)
    vcclient = ctx.voice_client
    if not vcclient.is_playing():        
        #using add entry because we want entry song only, no need for index
        await ctx.respond(f">>> \nNow Playing: \n{que.index[ctx.guild] + 1}.{song['name']} [{song['user'][0:-5]}] \n.```")
    else:
        await ctx.respond(f">>> \nAdded to Q: \n{len(que.guild[ctx.guild])}.{song['name']} [{song['user'][0:-5]}] \n.")


@client.slash_command(description="Add song right after currently playing song")
@diskord.application.option('arg')
async def playnext(ctx, *, arg, startpoint = 0, endpoint = None):
    try:
        SONG_ADD_POSITION = que.index[ctx.guild]  + 1
        song, num_of_songs = await que.add_entry(ctx, arg, startpoint, endpoint, SONG_ADD_POSITION)
        await ctx.respond(f">>> \nAdded to Q: \n{que.index[ctx.guild] + 1}.{song['name']} [{song['user'][0:-5]}] \n.")
    except:
        await ctx.respond(f">>> \nThere is no Queue to add to yet \n.")    
    
@client.slash_command(description="View queue position of Now Playing song")
# @diskord.application.option('arg')
async def index(ctx):
    await ctx.respond(f">>> Current Song Index : {que.index[ctx.guild] + 1} | Queue Looping: {que.loop[ctx.guild]}")

@client.slash_command()
# @diskord.application.option('arg')
async def ping(ctx):
    await ctx.respond(f">>> {ctx.voice_client.average_latency * 1000} ms")

@client.slash_command(description="Show now playing song")
@diskord.application.option('arg', description='', choices=[
  diskord.OptionChoice(name='Server Name', value='guild'),
  diskord.OptionChoice(name='Channel', value='channel'),
  diskord.OptionChoice(name='DJ', value='user'),
  diskord.OptionChoice(name='Time Added', value='time'),
  diskord.OptionChoice(name='Name of Song', value='name'),
  diskord.OptionChoice(name='YT Link', value='YT-video'),
  diskord.OptionChoice(name='Audio Link', value='url')
])
async def nowplaying(ctx, *, arg: str = "name"):
    if ctx.voice_client.is_playing():
        await ctx.respond(f">>> Now playing: \n{que.index[ctx.guild] + 1}. {que.nowplaying(ctx, arg)}")
    else:
        await ctx.respond(f">>> No song playing rn")

@client.slash_command(description="Skip to next track")
# @diskord.application.option('arg')
async def next(ctx):
    vcclient = ctx.voice_client
    if vcclient.is_playing():
        vcclient.stop()
    play_song_function(ctx, diskord, que)
    
    # Using Now playing because next follows index
    await ctx.respond(f">>> \nNow Playing: \n{que.index[ctx.guild] + 1}.{que.nowplaying(ctx)} [{que.nowplaying(ctx, 'user')}] \n.")


@client.slash_command(description="Go back to prev song")
# @diskord.application.option('arg')
async def prev(ctx):
    my_que = que.guild[ctx.guild][que.prev_track(ctx)]["url"]

    vcclient = ctx.voice_client
    if vcclient.is_playing():
      vcclient.stop()
    vcclient.play(diskord.FFmpegPCMAudio(my_que))
    vcclient.source = diskord.PCMVolumeTransformer(vcclient.source)
    vcclient.source.volume = 1

    await ctx.respond(f">>> Now Playing: \n{que.index[ctx.guild] + 1}.{que.nowplaying(ctx)} [{que.nowplaying(ctx, 'user')}] \n.")

@client.slash_command(description="Show queue")
@diskord.application.option('page', description = "Page number")
@diskord.application.option('page_size', description = "Number of songs per page")
async def queue(ctx, page:int = 1, page_size:int = 8):
    songs = len(que.guild[ctx.guild])
    num_of_pages = [round(songs/page_size), round(songs/page_size) + 1][round(songs/page_size) < (songs/page_size)]
    await ctx.respond(f"```css\n.Page_{page}_of_{num_of_pages} | .Total_number_of_Songs: {songs}\
        \n\n{que.my_que(ctx, page, page_size)}```")


@client.slash_command(description="Remove song from Queue")
@diskord.application.option('num', description="Index to remove")
async def remove(ctx, num: int):
    try:
        zero_adjusted_num = num - 1
        await ctx.respond(f"```Removed:\n{num}.{que.guild[ctx.guild][zero_adjusted_num]['name']}```")
        que.delete_entry(ctx, zero_adjusted_num)

        # In case we remove the now playing song
        # Using the next function will should get us to index 0
        if num == que.index[ctx.guild]:
            que.index[ctx.guild] = que.index[ctx.guild] - 1

    except ValueError:
        await ctx.respond(">>> Whoops, numbers only please!!")
        return
    except KeyError:
        await ctx.respond(">>> Whoops, nothing to clear!!")
    except Exception as e:
        print(e)
        await ctx.respond(">>> Whoops, something went wrong!!")
    return

@client.slash_command(description="Clear queue. Remove all Songs.  Defaut saves")
@diskord.application.option('arg', description="Save queue then empty.", choice = [ 
    diskord.OptionChoice(name="No", value="No")
])
async def clear(ctx, arg:str = 'y'):
    que.clear_que(ctx, arg)

@client.slash_command(description="Server mute all people in Voice channel")
# @diskord.application.option('arg')
async def vc_mute(ctx):
    vc = ctx.author.voice.channel
    for member in vc.members:
        print(member)
        await member.edit(mute=True)
    await ctx.respond(f">>> Muting all people in voice channel {vc}")

@client.slash_command(description="Server unmute all people in Voice channel")
# @diskord.application.option('arg')
async def vc_unmute(ctx):
    vc = ctx.author.voice.channel
    for member in vc.members:
        await member.edit(mute=False)
    await ctx.respond(f">>> Un-Muting all people in voice channel {vc}")

@client.slash_command(description="Add Playlist to queue")
@diskord.application.option('arg')
async def playall(ctx, arg, startpoint = 0, endpoint = None):
    vc = ctx.author.voice.channel
    await ctx.respond(">>> Please wait ...")
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

    song, num_of_songs = await que.add_entry(ctx, arg, startpoint, endpoint, SONG_ADD_POSITION)
    
    # play_song_function(ctx, diskord, que)
    vcclient = ctx.voice_client
    if not vcclient.is_playing():        
        # using add entry because we want entry song only, no need for index
        await ctx.respond(f">>> \nNow Playing: \n{num_of_songs} songs added by [{song['user'][0:-5]}] \n.")
    else:
        await ctx.respond(f">>> \nAdded to Q: \n{num_of_songs} songs added by [{song['user'][0:-5]}] at index {len(que.guild[ctx.guild])}\n.")

@client.slash_command(description="Add Playlist right after now playing")
@diskord.application.option('arg')
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
        song, num_of_songs = await que.add_entry(ctx, arg, startpoint, endpoint, SONG_ADD_POSITION)
        await ctx.respond(f">>> \nAdded to Q: \n{num_of_songs} songs added by [{song['user'][0:-5]}] at index {SONG_ADD_POSITION}\n.")
    except:
        await ctx.respond(f">>> \nThere is no Queue to add to yet\n.")    

@client.slash_command(description="DJs for this session")
# @diskord.application.option('arg')
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
    await ctx.respond("\n".join(output))

# async def history(ctx, arg = ctx.author):

client.run(my_secret)