import re

from scrape_Spotify import Spotify
from scrape_YT import YT_Scrape


class validate(Spotify, YT_Scrape):
    def __init__(self) -> None:
        super().__init__()

    def check_youtube(self, url):
        youtube_check = re.search(r'youtube.com/|youtu.be/', url)
        return True if youtube_check else False

    def check_spotify(self, url):
        spotify_check = re.search('spotify.com/', url)
        return True if spotify_check else False

    def check_playlist(self, url):
        if self.check_youtube(url):
            playlist_check = re.search(r'list=', url)
        elif self.check_spotify():
            playlist_check = re.search(r'playlist/', url)

        return True if playlist_check else False

    def set_url(self):
        if self.check_playlist :
            playlist_id = re.findall(r'list=(.{34})', url)[0]
            url = f"https://www.youtube.com/playlist?list={playlist_id}"
        else:
            video_id = re.findall(r'watch\?v=(.{11})', url)[0]
            url = f"https://www.youtube.com/watch\?v={video_id}"
        return url

    def get_song_list(self):
        spotify = self.check_spotify()
        youtube = self.check_youtube()
        if spotify:
            return self.spotify_song_list()
        elif youtube:
            return self.youtube_song_list()
        else:
            return 404