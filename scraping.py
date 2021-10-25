import requests
from bs4 import BeautifulSoup

def spotify(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')
    track_list = soup.find_all('span', {'class':'track-name'})

    for tracks in track_list:
        print(tracks.text)
    
    return track_list