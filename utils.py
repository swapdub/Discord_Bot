def play_song_function(ctx, discord, que):
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
        guild_queue = que.guild[ctx.guild]
        song = guild_queue[que.next_track(ctx)]
        vcclient.play(discord.FFmpegPCMAudio(song["url"], **ffmpeg_options), after = lambda func: play_song_function(ctx, discord, que))
        vcclient.source = discord.PCMVolumeTransformer(vcclient.source)
        vcclient.source.volume = 1

        print(f'middle it is : {que.index[ctx.guild]}')
    print(f'last it is : {que.index[ctx.guild]}')

async def playall_song_function(ctx, discord, que):
    vcclient = ctx.voice_client
    ffmpeg_options = {
    'options': '-vn',
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
    }

    if vcclient is None:
        await ctx.author.voice.channel.connect()
        vcclient = ctx.voice_client

    if not vcclient.is_playing() and que.guild[ctx.guild][1]:
        guild_queue = que.guild[ctx.guild]
        payload = guild_queue[que.next_track(ctx)]
        vcclient.play(discord.FFmpegPCMAudio(payload["url"], **ffmpeg_options), after = lambda func: play_song_function(ctx, discord, que))
        vcclient.source = discord.PCMVolumeTransformer(vcclient.source)
        vcclient.source.volume = 1