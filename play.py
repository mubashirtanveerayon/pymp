import os
from pygame import mixer
import threading
from fmanager import *
import random


#files = os.listdir("data")

mixer.init()

playlists = []

current_track = ""

pos = 0

run = True

root_dir = ""

queue = []

playing = False

paused = False

loop = False

text = ""

converted_files = []

help_text = """1. use "dir" command followed by the audio directory to scan the folder for audio files(mp3 and wav)
2. play any audio from the printed list using "play" followed by the audio index number
3. use "play" again to add another audio in queue
4. use "loop" to play the current queue on loop
5. use "queue" to print the list of audio tracks in the queue
6. use "p", "r" and "s" to pause, resume and stop playing the queue respectively
7. use "e" to exit the program
8. save the current playlist to file using "save" followed by the name of the playlist
   note that the playlist file is saved at the directory that was chosen by using the dir command with a ".play" extension
9. load playlist and audio files using "refresh"
10. select playlist by name using "select" command 
11. list playlists using "print"
12. list audio tracks in a playlist by using "print" followed by the playlist name
13. use "h" to get the help text
14. use "get" followed by the audio name surrounded by double quotes you want to download
15. use "remove" followed by the serial number of track in the queue to remove it from the queue/playlist
16. use "next", "prev" commands for playing the next and previous track repectively
17. use "v/" to increase and "v\\" to decrease the volume
18. use "shuffle" to shuffle the current queue
"""

print(help_text)



def take_input():
    global text
    while run:
        text = input().lower()


input_thread = threading.Thread(target=take_input)
input_thread.start()

def set_pos():
    global pos
    new_pos = mixer.music.get_pos()
    if new_pos > pos:
        pos = new_pos

def check_if_playing():
    global playing
    playing = True
    while mixer.music.get_busy() and run:
        continue
    playing = False
    

def set_root(root):
    global root_dir,converted_files,playlists
    root_dir = os.path.abspath(root)
    for file in os.listdir(root_dir):
        if file.endswith("m4a"):
            if file.split(".")[0] in get_names(list_audio_files(root_dir)):
                converted_files.append(file)
    print(read_names(list_audio_files(root_dir)))
    playlists = get_playlists(root_dir)
    print("playlists:")
    print(read_names(playlists))

while run:
    if not playing and not paused:
        if len(queue) > 0:
            if loop:
                if not current_track in queue or current_track == queue[len(queue) - 1]:
                    current_track = queue[0]
                else:
                    current_track = queue[queue.index(current_track)+1]
            

            elif current_track:
                if not current_track in queue:
                    current_track = queue[0]
                elif current_track != queue[len(queue) - 1]:
                    
                    current_track = queue[queue.index(current_track)+1]
                    
                else:
                     
                    current_track = ""
            
            if current_track:
                mixer.music.load(current_track)
                mixer.music.play()
                thread = threading.Thread(target=check_if_playing)
                thread.start()
            else:
                print("queue ended")
                queue.clear()

            pos = 0

    if playing:
        set_pos()

    if text == "":
        continue

    
    cmd = text.split(" ")
    length = len(cmd)
    


    if text == "e":
        run = False
        os._exit(0)
    elif text == "p" and mixer.music.get_busy():
        mixer.music.pause()
        paused = True
    elif text == "r" and not mixer.music.get_busy():
        mixer.music.unpause()
        thread = threading.Thread(target=check_if_playing)
        thread.start()
        paused = False
    elif length > 1:
        if cmd[0] == "dir":
            if os.path.exists(os.path.abspath(cmd[1])):
                set_root(cmd[1])
            else:
                os.mkdir(os.path.abspath(cmd[1]))
                set_root(cmd[1])


        elif cmd[0] == "play" and cmd[1].isdigit():
            if root_dir:
                audio_files = list_audio_files(root_dir)
                audio = audio_files[int(cmd[1])-1]
                if playing:
                    print(f"added {get_name(audio)} to queue")
                else:
                    current_track = audio
                    mixer.music.load(audio)
                    thread = threading.Thread(target=check_if_playing)
                    mixer.music.play()
                    thread.start()
                    pos = 0
                    print(f"playing {get_name(audio)}")
                queue.append(audio)
                paused = False
        elif cmd[0] == "save":
            if len(queue) != 0:
                save_playlist(queue,root_dir,cmd[1])
                playlists = get_playlists(root_dir)
            
        elif cmd[0] == "select":
            playlist = ""
            if cmd[1].isdigit():
                playlist = playlists[int(cmd[1]) -1]
            else:
                
                for path in playlists:
                    if cmd[1] == get_name(path):
                        playlist = path

                
            if playlist:
                queue.clear()
                thread = threading.Thread(target=check_if_playing)
                queue = read_content(playlist)
                for i in range(len(queue)):
                    if(not os.path.exists(root_dir + os.sep + queue[i])):
                        audio = queue[i].split(".")[0]
                        search = search_yt(audio)
                        download_audio(search,root_dir,audio)
                        if(os.path.exists(root_dir+os.sep+audio)):
                            os.remove(root_dir+os.sep+audio)
                    queue[i] = root_dir + os.sep + queue[i]
                # read_names(queue)
                if playing:
                    mixer.music.stop()
                mixer.music.load(queue[0])
                mixer.music.play()
                thread.start()

        elif cmd[0] == "remove" and cmd[1].isdigit():
            queue.remove(queue[int(cmd[1]) - 1])
            print(read_names(queue))
            
            
        elif cmd[0] == "print":
            playlist_names = get_names(playlists)
            playlist = ""
            for i in range(len(playlist_names)):
                if cmd[1] == playlist_names[i]:
                    playlist = playlists[i]
                    break
            if playlist:
                print(read_names(read_content(playlist)))
            
        elif cmd[0] == "get":
            query = get_str_in_quotes(text)
            if query:
                
                download_audio(query,root_dir)
                if(os.path.exists(root_dir+os.sep+query)):
                    os.remove(root_dir+os.sep+query)
                print(read_names(list_audio_files(root_dir)))

    elif text == "v/":
        mixer.music.set_volume(mixer.music.get_volume() + 0.1)
        print(f"Volume set to {mixer.music.get_volume()}")

    elif text == "v\\":
        mixer.music.set_volume(mixer.music.get_volume() - 0.1)
        print(f"Volume set to {mixer.music.get_volume()}")

    
    elif text == "refresh" :
        for file in os.listdir(root_dir):
            if file.endswith("m4a") and file not in converted_files:
                print(f"converting {file} to mp3 format")
                convert_audio( os.path.abspath(root_dir+os.sep+ file))
                print("conversion finished")
                converted_files.append(file)
        print(read_names(list_audio_files(root_dir)))
        playlists = get_playlists(root_dir)
        print("playlists:")
        print(read_names(playlists))


    elif text == "s":
        mixer.music.stop()
        loop = False
        queue.clear()
        current_track = ""
        pos = 0
        paused = False
    
    elif text == "print":
        print(read_names(playlists))
    
    elif text == "loop":
        loop = not loop
    
    elif text == "queue":
        if current_track:
            print(f"currently playing {get_name(current_track)}")
        print(read_names(queue))
        print(f"loop: {loop}")
    
    elif text == "next" and len(queue)>0:
        if playing:
            mixer.music.stop()
        if current_track in queue:
            if current_track == queue[len(queue) - 1] :
                if loop:
                    current_track = queue[0]
                else:
                    current_track = ""
            else:
                current_track = queue[queue.index(current_track) + 1]
        else:
            current_track = queue[0]
        if current_track:
            mixer.music.load(current_track)
            mixer.music.play()
            thread = threading.Thread(target=check_if_playing)
            thread.start()
        pos = 0
        
    elif text == "prev" and len(queue)>0:
        if playing:
            mixer.music.stop()
        if current_track in queue:
            if current_track == queue[0] :
                if loop:
                    current_track = queue[len(queue)-1]
                else:
                    current_track = ""
            else:
                current_track = queue[queue.index(current_track) - 1]
        else:
            current_track = queue[len(queue) - 1]

        if current_track:
            mixer.music.load(current_track)
            mixer.music.play()
            thread = threading.Thread(target=check_if_playing)
            thread.start()
        pos = 0

    elif text == "shuffle":
        if(len(queue)>1):
            size = len(queue)
            for i in range(size-1):
                random_index = random.randint(0,size-1)
                queue.append(queue.pop(random_index))
            if current_track:
                print(f"currently playing {get_name(current_track)}")
            print(read_names(queue))

    

    elif text == "seek" and playing:
        new_pos = pos/1000.0 + 10
        mixer.music.play(start=new_pos)

    elif text == "h":
        print(help_text)
    text = ""

mixer.quit()
