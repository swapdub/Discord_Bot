from email import header
import os
import re
import requests
import youtube_dl

from dotenv import load_dotenv
load_dotenv()

from scraping import spotify

class YT_Scrape():
    def __init__(self) -> None:
        self.headers = {
            'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36'
        }
        pass

    def check_playlist(self, url):
        playlist_check = re.search(r'list=', url)
        return True if playlist_check else False

    def check_for_link(self, url):
        playlist_check = re.search('https:', query)
        return True if playlist_check else False

    def search_YT(self, search_term):
        search_uri = "https://www.youtube.com/results?search_query="
        page = requests.get(search_uri + search_term, headers=self.headers)        
        yt_code = re.findall(r'"videoId":"(.{11})"', page.text)
        return yt_code[0]

    def get_yt_codes(self, url):
        page = requests.get(url)
        yt_codes = re.findall(r'"videoId":"(.{11})"', page.text)
        return yt_codes

    def get_code_playlist_yt(self, url):
        return self.get_yt_codes(url)[::4]
        
    def get_code_song_yt(self, search_term):
        return self.get_yt_codes(search_term)[0]
    
    def youtube_song_list(self, query):
        playlist = self.check_playlist(query)
        http_check = self.check_for_link(query)
        if not http_check:
            return self.search_YT(query)
        elif playlist :
            playlist_id = re.findall(r'list=(.{34})', query)[0]
            url = f"https://www.youtube.com/playlist?list={playlist_id}"
            return self.get_code_playlist_yt(url)
        else:
            video_id = re.findall(r'watch\?v=(.{11})', query)[0]
            url = f"https://www.youtube.com/watch\?v={video_id}"
            return self.get_code_song_yt(url)

    def get_song_info_yt(self, yt_code):
        with youtube_dl.YoutubeDL(self.ydl_opts) as ydl:
            song_info = ydl.extract_info(
                "https://www.youtube.com/watch?v=" + yt_code, download=False
            )
        return song_info


if __name__ == "__main__":
    s = YT_Scrape()
    url = os.getenv('YT_39')
    l = s.get_code_playlist_yt(url)
    print(len(l))
    print(l)
    