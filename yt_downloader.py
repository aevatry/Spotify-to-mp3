from yt_dlp import YoutubeDL
from spotify_client import Playlist 
from search_yt import searchyt


class yt_mp3_downloader(Playlist):


    def __init__(self, client_id, client_secret, playlist_url, local_path, *args, **kwargs):
        super().__init__(client_id, client_secret, playlist_url)
        self.local_path = local_path


    def query_link(self):

        playlist_data_df = self.get_playlist_data()
        

        for i in range(0,len(playlist_data_df['artists'])):

            url_for_search = ""
            title = playlist_data_df['track name'][i].split()

            for k in range(0, len(title)):
                url_for_search = url_for_search + f" {title[k]}" #in youtube search, the + is a space

            for j in range(0,len(playlist_data_df['artists'][i])):
                artist_name = playlist_data_df['artists'][i][j].split()
                for indiv_names in artist_name:
                    url_for_search = url_for_search + f" {indiv_names}"
    
            playlist_data_df.at[i, 'query data'] = url_for_search
        
        return playlist_data_df

    def find_yt_link(self):

        playlist_data_df = self.query_link()
        watch_link = 'https://www.youtube.com/watch?v='

        for i in range (0, len(playlist_data_df['query data'])):
             
            syt = searchyt() 
            id = syt.search(query= playlist_data_df['query data'][i])['id']
            playlist_data_df.at[i, 'id'] = id
            playlist_data_df.at[i,'yt_link'] = watch_link + id

        return playlist_data_df


    
    def download_global (self):

        playlist_data_df = self.find_yt_link() 
        for i, link in enumerate (playlist_data_df['yt_link']):
            
            self.download_indiv(link) #should be return link but have to scrape the links first

    
    def download_indiv (self, link):
        if not ('https://www.youtube.com/' in link):
            raise Exception('Not a youtube link')
        with YoutubeDL(self.get_ydl_options()) as ydl:
            ydl.download([link])


    def get_ydl_options(self):

        ydl_opts = {
            'format': 'bestaudio/best',
	        'postprocessors': [{
		    'key': 'FFmpegExtractAudio',
		    'preferredcodec': 'mp3',
		    'preferredquality': '192',
	    }],
            'paths':{'home':self.local_path},
            'outtmpl':'%(title)s.%(ext)s',
            'ignoreerrors': 'only_download',
        }

        return ydl_opts