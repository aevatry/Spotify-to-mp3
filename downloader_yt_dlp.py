
from yt_dlp import YoutubeDL


playlist_path=r'C:\Users\Antonin\Documents\personal projects\music\yt_to_mp3\playlist'
#r is to convert to raw string

ydl_opts = {
	'format': 'bestaudio/best',
	'postprocessors': [{
		'key': 'FFmpegExtractAudio',
		'preferredcodec': 'mp3',
		'preferredquality': '192',
	}],
    'paths':{'home':playlist_path},
    'outtmpl':'%(title)s.%(ext)s',
    'ignoreerrors': 'only_download',
}


def download (link):

    if not ('https://www.youtube.com/' in link):
        raise Exception('Not a youtube link')
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([link])


if __name__ == '__main__':  

    music=input('youtube link:')
    if download(music):
        print('\n[+] Audio Downloaded \n')

    