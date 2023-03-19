import requests
from bs4 import BeautifulSoup
import base64
import datetime
from urllib.parse import urlencode
import pandas as pd


class SpotifyAPI(object): #object is a class in itself and accepts only one argument for super

    client_id = None
    client_secret = None
    token_url = "https://accounts.spotify.com/api/token"

    access_token = None
    access_token_expires = datetime.datetime.now()
    access_token_did_expire = True


    def __init__(self, client_id, client_secret, *args, **kwargs):
        # super().__init__(*args, **kwargs)
        # just to know that it exists if need comes to be

        self.client_id = client_id
        self.client_secret = client_secret

        # all those keys will be initialized as class attributes
        allowed_keys = set([])
        # initialize all allowed keys to false
        self.__dict__.update((key, False) for key in allowed_keys)
        # and update the given keys by their given values
        self.__dict__.update((key, value) for key, value in kwargs.items() if key in allowed_keys)


    def get_client_credetials_b64(self):

        if self.client_id == None or self.client_secret == None:
            raise Exception("Need both client id and secret key")

        client_creds = base64.b64encode (f"{self.client_id}:{self.client_secret}".encode()).decode()

        return client_creds


    def get_token_headers(self):

        token_headers ={
            "Authorization": f"Basic {self.get_client_credetials_b64()}",
            "Content-type": "application/x-www-form-urlencoded",
            }
        return token_headers 

    
    def get_request_data(self):

        request_body = {
            "grant_type": "client_credentials",
            }

        return request_body


    def perform_auth (self):

        api_r = requests.post(self.token_url, data=self.get_request_data(), headers = self.get_token_headers())

        if api_r.status_code not in range(200,299):
            raise Exception('could not perform authentication')
        
        data = api_r.json()
        
        self.access_token = data["access_token"]

        now = datetime.datetime.now()
        expires_in = data["expires_in"]
        expire_time = now + datetime.timedelta(seconds = expires_in)

        self.access_token_expires = expire_time
        self.access_token_did_expire = now > expire_time

        return True, data["access_token"]
    
    def get_access_token(self):

        token = self.access_token
        access_token_did_expire = self.access_token_did_expire #this will return True if token is expired

        if access_token_did_expire:
            self.perform_auth()
            return self.get_access_token()
        
        elif token == None:
            self.perform_auth()
            return self.get_access_token()

        return token

    def get_resource(self, _id, resource_type, resource_parameters, version = 'v1'):

        bearer_token = self.get_access_token()

        call_headers ={
            'Authorization':f"Bearer {bearer_token}",
            }
        lookup_url = f"https://api.spotify.com/{version}/{resource_type}/{_id}/{resource_parameters}"

        r = requests.get(lookup_url, headers = call_headers)
        if r.status_code not in range(200, 299):
            return {}

        return r.json()


class Playlist(SpotifyAPI):
    
    def __init__(self, client_id, client_secret,playlist_url, *args, **kwargs):
        super().__init__(client_id, client_secret,*args, **kwargs)
        self.playlist_url = playlist_url
    

    def find_playlist_id(self):
        if not ("https://open.spotify.com/playlist/" in self.playlist_url):
            raise Exception('Not a apotify playlist')
    
        elif self.playlist_url == False:
            raise Exception('You need to provide a Spotify playlist url') 
        else:
            mod_url = self.playlist_url.replace("https://open.spotify.com/playlist/", "")
            complete_id = False
            position = 0
            playlist_id = "" #initiate the playlist id
            while not complete_id: 
                char = mod_url[position] #current character
                playlist_id = "".join((playlist_id,char))
                position += 1
                next_char = mod_url[position] #next character
                if next_char == "?": #check if complete id is finished
                    complete_id = True  
                
        return playlist_id

    def get_playlist_items(self, query): #query is a dictionary of parameters

        playlist_id = self.find_playlist_id()
        global_resource_type = 'playlists'
        version = 'v1'

        resource_type = "tracks"
        data = urlencode(query)
        resource_parameters = f"{resource_type}?{data}"

        return self.get_resource(playlist_id, global_resource_type, resource_parameters, version)


    def get_playlist_length(self):

        query = {
            "fields":"total",
            "limit":1,
            "offset":0,
        }

        return self.get_playlist_items(query)['total']

    
    def get_playlist_tracks_name(self, offset):

        query = {
            "fields":"items(track(name,artists(name)))",
            "limit":50,
            "offset":offset,
        }

        items = self.get_playlist_items(query)
        return items


    def get_playlist_data (self):

        length = self.get_playlist_length()
        iterations = (length // 50) +1 #need to repeat the get/playlist this number of times

        dict_for_dataframe = {
            "track name": [],
            "artists": [],
        }

        for i in range(0,iterations):

            data = self.get_playlist_tracks_name(offset=i*50)

            for k in range(len(data['items'])):

                artists = []
                for j in range(0,len(data['items'][k]['track']['artists'])):
                    artists += [data['items'][k]['track']['artists'][j]['name']]

                dict_for_dataframe['artists'].append(artists)
                dict_for_dataframe['track name'].append(data['items'][k]['track']['name'])
        
        df_songs_names = pd.DataFrame.from_dict(dict_for_dataframe)
        return df_songs_names
        
        
    

