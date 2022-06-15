import requests
import re
from bs4 import BeautifulSoup
import json
import aiohttp

async def spotify(user_url):
    # async with aiohttp.ClientSession() as session: #i'm seriously retarded for doing this
    #         async with session.get(user_url) as response:
    #             print("Status:", response.status)
    #             results = await response.text()
            
    page = requests.get(user_url)
    print(page.status_code)

    soup = BeautifulSoup(page, 'html.parser')
    track_list = soup.find_all('span', {'class':'track-name'})
    track_list = [tracks.text for tracks in track_list]
    print(track_list)
    return track_list

def youtube(url):
    single = re.search(r'watch', url)
    playlist = re.search(r'list', url)
    if playlist:
        playlist_id = re.findall(r'list=(.{34})', url)[0]
        url = f"https://www.youtube.com/playlist?list={playlist_id}"
    elif single:
        video_id = re.findall(r'watch\?v=(.{11})', url)[0]
        url = f"https://www.youtube.com/watch?v={video_id}"


    page = requests.get(url)
    yt_code = re.findall(r'"videoId":"(.{11})"', page.text)[::4]  # Find song ID on Youtube
    print(url)
    
    return yt_code

if __name__ == "__main__":

    # url = 'https://www.youtube.com/playlist?list=PL1-ZtxkZHhu25SQgOFe18WTophBrB153b'
    # url = 'https://youtu.be/playlist?list=PL1-ZtxkZHhu25SQgOFe18WTophBrB153b'
    # url = 'https://www.youtube.com/watch?v=ab3f_SMAidk&list=PL1-ZtxkZHhu25SQgOFe18WTophBrB153b&index=1'
    # url = 'https://www.youtube.com/watch?v=3SDBTVcBUV'
    url = 'https://youtu.be/LL5RJ3Is4So'
    # url = 'https://youtu.be/EgFTc6Xwjos'
    # url = 'https://open.spotify.com/track/5PjdY0CKGZdEuoNab3yDmX?si=bd233e25b6224eb9'
    # url = 'https://open.spotify.com/playlist/7Dl3ZKjov0HtLA1K7QkwUY?si=ea8cdd50785b4c9c'
    # url = 'https://www.youtube.com/watch?v=abEqJxDWPuc&list=RDabEqJxDWPuc&start_radio=1'
    # url = 'https://www.youtube.com/watch?v=nPA2czkOsFE&start_radio=1&list=RDnPA2czkOsFE'
    # spotify(url)

    youtube(url)
    # print(requests.get('https://open.spotify.com/playlist/7Dl3ZKjov0HtLA1K7QkwUY?si=ea8cdd50785b4c9c').status_code)