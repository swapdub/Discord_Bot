import os
import re
import requests
from dotenv import load_dotenv
load_dotenv()

from scraping import spotify

class YT_Scrape():
    def __init__(self) -> None:
        pass

    def search_YT(self, search_term):
        search_uri = "https://www.youtube.com/results?search_query="
        ret = requests.get(search_uri + search_term)        
        return ret 

    def get_yt_codes(self, url):
        page = requests.get(url)
        yt_codes = re.findall(r'"videoId":"(.{11})"', page.text)
        return yt_codes

    def get_code_playlist_yt(self, url):
        return self.get_yt_codes(url)[::4]
        
    def get_code_song_yt(self, search_term):
        return self.get_yt_codes(search_term)[0]

    def get_song_info_yt(self, yt_code):
        song_info = self.yt_dl_info(yt_code)
        return song_info

    def get_playlist(self):
        pass

    def youtube_song_list(self, url):
        pass

if __name__ == "__main__":
    s = YT_Scrape()
    url = os.getenv('YT_39')
    l = s.get_code_playlist_yt(url)
    print(len(l))
    print(l)
    