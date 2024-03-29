import os
import requests
import json
from secret import client_id, client_secret
# from message import data_response



def get_access_token():

    url = "https://accounts.spotify.com/api/token"
    auth_response = requests.post(url, {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
    })
    try:
        # convert the response to JSON
        auth_response_data = auth_response.json()

        # save the access token
        access_token = auth_response_data['access_token']
    except Exception as e:
        print(e)

    if access_token and auth_response.status_code == 200:
        return access_token
    else:
        return None


def get_song_list(user_url):
    FILENAME = "access_token.txt"
    
    try:
        # Opens a file for exclusive creation. 
        # If the file already exists, the operation fails.
        file = open(FILENAME, 'x')
        file.close()
    except:
        pass

    with open(FILENAME, 'r+') as file:
        access_token = file.read()
        
        if access_token:
            print (f'Fetching access token from file : {access_token}')
            playlist = user_url.find('playlist')
            solo_track_id = user_url.strip('https://open.spotify.com/track/')
            playlist_id = user_url.strip('https://open.spotify.com/playlist/')
            print(playlist_id, solo_track_id)
            if playlist != -1:
                url = f'https://api.spotify.com/v1/playlists/{playlist_id}'
            else:
                url =  f'https://api.spotify.com/v1/tracks/{solo_track_id}'
            headers = {'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json'}
            
            page = requests.get(url=url, headers=headers)
            if page.status_code == 200:
                data_response = page.json()
                # print (data_response)
                song_list = []
                if playlist != -1:
                    for item in data_response['tracks']['items']:
                        song_list.append(f"{item['track']['name']} by {item['track']['artists'][0]['name']}")
                    print(song_list)
                    return song_list
                else:
                    print ([data_response['name']])
                    return ([data_response['name']])

            else:
                with open("access_token.txt", 'w'):
                    print(page.status_code, page.text)
                    print('Writing access token')
                get_song_list(user_url)        
        else:
            access_token = get_access_token()
            file.seek(0)
            file.write(access_token)
            file.truncate()
            print('Writing access token')
            get_song_list(user_url)        

if __name__ == '__main__':
    # url = 'https://open.spotify.com/playlist/33a8Tmb4nA4CRDOnYrjTkr?si=880eaa2d8fb943ce'
    # url = 'https://open.spotify.com/playlist/37i9dQZF1DX4mWCZw6qYIw?si=98e44e4c24aa4f3f'
    # url = 'https://open.spotify.com/playlist/37i9dQZEVXbMDoHDwVN2tF?si=107bd93590e146de'
    url = 'https://open.spotify.com/playlist/7Dl3ZKjov0HtLA1K7QkwUY?si=ea8cdd50785b4c9c'
    # url = 'https://open.spotify.com/track/3KkXRkHbMCARz0aVfEt68P?si=69b00587b46247a9'
    # url = 'https://open.spotify.com/track/3KkXRkHbMCARz0aVfEt68P'

    get_song_list(url)