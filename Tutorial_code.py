    # bot.py
import os

import discord

TOKEN = 'NzMwNjAyNDI1ODA3MDExODQ3.XwZ4ow.kkUqM9YSFyDq7o8vY4AhQDt2E-g'

client = discord.Client()

@client.event
async def on_ready():
    for guild in client.guilds:
        GUILD = guild.name

    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})\n'
    )

    members = '\n - '.join([member.name for member in guild.members])
    print(f'Guild Members:\n - {members}')

client.run(TOKEN)