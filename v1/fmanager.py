import os
import ffmpeg
from pytube import YouTube
from bs4 import BeautifulSoup
import yt_dlp
from googleapiclient.discovery import build
from pytube.exceptions import VideoUnavailable, PytubeError

nl = "\n" #new line
playlist_extension = ".play"
audio_file_extensions = ["mp3","wav"]
api_key = ""
with open("api.key","r") as file:
    api_key= file.readlines()[0].strip()

def get_name(path):
    return path.split(os.sep).pop().split(".")[0]

def list_audio_files(folder)->list:
    dir = os.path.abspath(folder)
    res = []
    for file in os.listdir(dir):
        for extension in audio_file_extensions:
            if file.endswith(extension):
                res.append(dir+os.sep+file)
                break
   
    return res

def save_playlist(list_of_files,root_dir,name):
    text = ""
    for file in list_of_files:
        text+=(file.split(os.sep).pop())+"\n"
    with open(root_dir+os.sep+name+playlist_extension,"w") as list:
        list.write(text.strip())

def read_content(file)->list:
    files = open(file).readlines()
    for i in range(len(files)):
        files[i] = files[i].split(nl)[0]
    return nl.join(files).strip().split(nl)


def get_playlists(folder)->list:
    dir = os.path.abspath(folder)
    res = []
    for file in os.listdir(dir):
        if file.endswith(playlist_extension):
            res.append(dir+os.sep+file)
   
    return res

def get_names(paths:list)->list:
    text = []
    for i in range(len(paths)):
        name = get_name(paths[i])
        text.append(name)
    return text

def read_names(any_path_list:list)->str:
    text = ""
    for i in range(len(any_path_list)):
        name = get_name(any_path_list[i])
        text += f"{i+1}.{name}{nl}"
    return (text.strip())

def play_audio(mixer,file):
    if mixer.music.get_busy():
        mixer.music.stop()
    try:
        mixer.music.load(file)
        mixer.music.play()
    except Exception as e:
        print(e)

def convert_audio(file):
    input_stream = ffmpeg.input(file)
    output = ffmpeg.output(input_stream,file.split(".")[0]+".mp3",format="mp3")
    ffmpeg.run(output,overwrite_output=True)

def get_first_video(query):
    if api_key == "":
        print("Could not read API KEY")
        return
    youtube = build('youtube', 'v3', developerKey=api_key)
    
    # Execute the search request
    request = youtube.search().list(
        q=query,
        part="snippet",
        type="video",
        maxResults=1  # Fetch only the first result
    )
    
    response = request.execute()
    if 'items' in response and len(response['items']) > 0:
        first_video = response['items'][0]
        video_id = first_video['id']['videoId']
        return video_id
    else:
        return None




def download_audio(query,path):

    try:
        video_id = get_first_video(query)
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        
        if video_id == None:
            print("Error occurred!")
            return
        print(f"Downloading: {video_url}")

        ydl_opts = {
            'format': 'bestaudio/best',  # Download the best audio
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',  # Convert to mp3
                'preferredquality': '192',  # Audio quality
            }],
            # Specify the download path and file name template
            'outtmpl': f'{path}/%(title)s.%(ext)s',  # Download path
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
    except Exception as e:
        print(e)
    #     video = YouTube(video_url)
    #     audio_stream = video.streams.filter(only_audio=True).first()
    #     audio_stream.download(path,filename=name)
    #     convert_audio(f"{path}{os.sep}{name}")
    # except VideoUnavailable:
    #     print(f"Video {video_id} is unavailable, please check the video ID.")
    
    # except PytubeError as e:
    #     print(f"An error occurred: {e}")




def get_str_in_quotes(s):
    res = s.split("\"")
    if len(res) != 3:
        return None
    
    return res[1]


def get_path(audio_file:str,root:str)->str:
    return root+os.sep+audio_file
