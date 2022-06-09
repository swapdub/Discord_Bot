import re

from scrape_Spotify import Spotify
from scrape_YT import YT_Scrape


class validate(Spotify, YT_Scrape):
    def __init__(self) -> None:
        super().__init__()

    def check_youtube(self, query):
        youtube_check = re.search(r'youtube.com/|youtu.be/', query)
        return True if youtube_check else False

    def check_spotify(self, query):
        spotify_check = re.search('spotify.com/', query)
        return True if spotify_check else False

    def check_link(self, query):
        http_check = re.search('https:', query)
        return True if http_check else False
        
    # def check_playlist(self, query):
    #     if self.check_youtube(query):
    #         playlist_check = re.search(r'list=', query)
    #     elif self.check_spotify():
    #         playlist_check = re.search(r'playlist/', query)

    #     return True if playlist_check else False

    def get_song_list(self, query):
        spotify = self.check_spotify(query)
        youtube = self.check_youtube(query)
        http_check = self.check_link(query)

        if spotify:
            return self.spotify_song_list(query)
        elif youtube:
            return self.youtube_song_list(query)
        elif http_check:
            return 404
        else:
            # search term
            return self.youtube_song_list(query)
