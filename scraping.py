import requests
import re
from bs4 import BeautifulSoup
import json

def spotify(user_url):
    # playlist_id = user_url.strip('https://open.spotify.com/playlist/')
    # url = f'https://api.spotify.com/v1/playlists/{playlist_id}'
    page = requests.get(user_url)
    print(page.status_code)
    try:
        print(json.loads(page.text))
        print(page.raise_for_status())
    except Exception as e:
        print('Problem with Json : ', str(e))

    soup = BeautifulSoup(page.text, 'html.parser')
    track_list = soup.find_all('span', {'class':'track-name'})
    track_list = [tracks.text for tracks in track_list]

    return page.status_code

def youtube(url):
    page = requests.get(url)
    yt_code = re.findall(r'"videoId":"(.{11})"', page.text)  # Find song ID on Youtube
    yt_code = list(set(yt_code))
    # print(yt_code, len(yt_code))

    return yt_code

if __name__ == "__main__":

    url = 'https://www.youtube.com/playlist?list=PL1-ZtxkZHhu25SQgOFe18WTophBrB153b'
    # url = 'https://www.youtube.com/watch?v=ab3f_SMAidk&list=PL1-ZtxkZHhu25SQgOFe18WTophBrB153b&index=1'
    # url = 'https://www.youtube.com/watch?v=ab3f_SMAidk&list=PL1-ZtxkZHhu25SQgOFe18WTophBrB153b&index=2'
    # url = 'https://youtu.be/LL5RJ3Is4So'
    # url = 'https://open.spotify.com/track/5PjdY0CKGZdEuoNab3yDmX?si=bd233e25b6224eb9'
    # url = 'https://open.spotify.com/playlist/7Dl3ZKjov0HtLA1K7QkwUY?si=ea8cdd50785b4c9c'
    # spotify(url)

    youtube(url)
    # print(requests.get('https://open.spotify.com/playlist/7Dl3ZKjov0HtLA1K7QkwUY?si=ea8cdd50785b4c9c').status_code)