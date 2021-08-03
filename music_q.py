import re
import requests
import datetime
from collections import deque
import youtube_dl

class Q():
  guild = dict()
  que = deque()
  index = dict()
  entry = dict()

  ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessor_args': ['-ar', '16000'],
        'keepvideo': True,
        'default_search': 'auto',
    }
  def __init__(self):
    return

  def get_yt_code(self, search_term):
    return


  def add_entry(self, ctx, search_term):
    # entry = dict()
    html_content = requests.get("https://www.youtube.com/results?search_query=" + search_term)
    self.yt_code = re.findall(r'"videoId":"(.{11})"', html_content.text)  #Find song ID on Youtube

    with youtube_dl.YoutubeDL(self.ydl_opts) as ydl:
      self.song_info = ydl.extract_info("https://www.youtube.com/watch?v=" + self.yt_code[0], download=False)
    # get_yt_code(search_term)

    self.entry = {
      "url" : self.song_info["url"],
      "name" : self.song_info["title"],
      "user" : ctx.author,
      "channel" : ctx.author.voice.channel,
      "guild" : ctx.guild,
      "time" : datetime.datetime.now()
    }
    self.que.append(self.entry)

    if ctx.guild not in self.guild:
      self.guild[ctx.guild] = []
      self.index[ctx.guild] = 0
      self.guild[ctx.guild] = self.que
    else: 
      self.guild[ctx.guild] = self.que
    return self.entry


  def delete_entry(self, ctx, num):
    de = self.guild[ctx.guild]
    del de[num]
  
  def next_track(self, ctx):
    self.index[ctx.guild] += 1
    return self.index[ctx.guild]
    
  def prev_track(self, ctx):
    self.index[ctx.guild] -= 1


    return self.index[ctx.guild]

  def clear_que(self, ctx, save = "n"):
    self.guild[ctx.guild].clear()
    self.index[ctx.guild] = 0

  def url(self):
    return

  def nowplaying(self, ctx, arg = "name"):
    index = self.index[ctx.guild]
    return self.que[index][arg]

  def my_que(self, ctx):
    formattedQ = []
    count = 1

    for entry in self.guild[ctx.guild]:
      string = f"{count}. {entry['name']} added by {entry['user']}"
      formattedQ.append(string)
      count += 1
      
    formattedQ = "\n".join(formattedQ)

    return formattedQ



# l = "this is a sentence".split()
# d = dict()
# dl = dict()
# nameasvar = "name"
# d[nameasvar] = l 
# print(d)
# dl[nameasvar] = ("another sentence".split())
# l.append(dl)
# d[nameasvar] = l
# print(d["name"])

# que = Q()
# print(que.que_entry())