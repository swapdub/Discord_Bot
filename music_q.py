# building a queue class

class music_q:
  tst = [1, 2, 3, 4, 5]
  
  def __init__(self, queue, songinfo):
    self.queue = queue
    self.songinfo = songinfo
    self.que = []
    self.dataset = []
    self.q_index = 0

  def add_to_q(self):
    if self.songinfo:
      url = self.songinfo["url"]
      name = self.songinfo["name"]
      return name, url

  def q_reset(self):
    self.que = []
    self.q_index = 0
    return self.que

  def test(self):
    print(self.tst[2])

see = music_q(1, 4)
see.test()