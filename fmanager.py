import os
import ffmpeg
from pytube import YouTube, Search

nl = "\n" #new line
playlist_extension = ".play"
audio_file_extensions = ["mp3","wav"]

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
    text = "\n".join(list_of_files)
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

def download_audio(yt,path,name):
    if not yt:
        return
    try:
        video = YouTube(yt.watch_url)
        audio_stream = video.streams.filter(only_audio=True).first()
        print("dwonloading..")
        audio_stream.download(path,filename=name)
        convert_audio(f"{path}{os.sep}{name}")
    except Exception as e:
        print(e)


def search_yt(query):
    try:
        search = Search(query)
        return search.results[0]
    except Exception as e:
        print(e)

def get_str_in_quotes(s):
    res = s.split("\"")
    if len(res) != 3:
        return None
    
    return res[1]

