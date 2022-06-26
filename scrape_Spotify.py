from email import header
import os
import re
from urllib import response
import requests
from dotenv import load_dotenv
load_dotenv()


class Spotify():
    
    def __init__(self) -> None:
        self.access_token_file_spotify = "access_token.txt"

    def check_file_exists(self):
        try:
            # Opens a file for exclusive creation. 
            # If the file already exists, the operation fails.
            with open (self.access_token_file_spotify, 'x') as file:
                print("File created to save access token")
            return False
        except Exception as e:
            print(f"Exception: {e}")
            return True

    def req_token_from_spotify(self):
        url = "https://accounts.spotify.com/api/token"
        data = { 'grant_type': 'client_credentials',
                    'client_id': os.getenv('CLIENT_ID'),
                    'client_secret': os.getenv('CLIENT_SECRET'),}
        auth_response = requests.post(url, data)
        print(auth_response)
        try:
            auth_response_data = auth_response.json()
            access_token = auth_response_data['access_token']

        except Exception as e: print(e)

        if access_token and auth_response.status_code == 200:
            self.check_file_exists() # otherwise create it
            with open(self.access_token_file_spotify, 'w+') as file:
                file.write(access_token)
            return access_token
        else:
            return None

    def read_my_token(self):
        try:
            with open(self.access_token_file_spotify, 'r+') as file:
                access_token = file.read()
                if access_token:
                    return access_token
                else:
                    self.req_token_from_spotify()
        except:
            self.check_file_exists()

    def url_type(self, url):
        span = re.search(r'/[\w]{4,9}/', url).span()
        type = url[ span[0]+1 : span[1]-1 ]
        return type

    def create_url(self, url):
        type = self.url_type(url)
        type_id = url.strip(f'https://open.spotify.com/{type}/')[:22]
        req_url = f'https://api.spotify.com/v1/{type}s/{type_id}'
        return req_url
    
    def get_track_name(self, data_response):
        return ([data_response['name']])

    def get_full_playlist(self, data_response):
        song_list = []
        for item in data_response['tracks']['items']:
            song_list.append(f"{item['track']['name']} by {item['track']['artists'][0]['name']}")
        print(song_list)
        return song_list

    def req_spotify_api(self, user_url):
        access_token = self.read_my_token()
        print (f'Fetching access token from file : {access_token}')
        url = self.create_url(user_url)
        headers = {'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json'}
            
        page = requests.get(url=url, headers=headers)
        print(page.status_code)
        if page.status_code == 401:
            self.req_token_from_spotify()
            response = False
            return page, response
        if page.status_code == 200:
            response = True
            return page, response
        else:
            response = False
            return page, response

    def spotify_song_list(self, user_url):
        page, response = self.req_spotify_api(user_url)
        if not response:
            page, response = self.req_spotify_api(user_url)
        data_response = page.json()
        type = self.url_type(user_url)
        if type == 'playlist':
            return self.get_full_playlist(data_response)
        elif type == 'track':
            return self.get_track_name(data_response)    

spotify_class = Spotify()

if __name__ == '__main__':
    sp = Spotify()
    url = os.getenv('SP_URL')
    print(sp.spotify_song_list(url))