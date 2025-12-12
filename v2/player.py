import os
import json
import random
import threading
import time
from pygame import mixer as mixer
from thefuzz import fuzz,process

# mixer.init()

# mixer.music.load('1.mp3')

# mixer.music.play()

# while mixer.music.get_busy():
#     continue

dataFile = "data.json"

userInput=""

tracks=[]


info={'libraryPath':'.','playlist':{}}

# playlist: {'<name>':[],'<name>':[],'<name>':[]}

helpText='''
add <track>: add track to current playlist
t: toggle play/pause
clear: clear current playlist
s: shuffle current playlist
n: next track
p: previous track
q: print current playlist
load <playlist>: add all tracks from playlist
save <playlist>: save current playlist with name <playlist>
library <library path>: set music library path to <library path>
r: reload tracks from library
'''

def loadData():
    global info

    lines=[]
    with open(dataFile,'r') as file:
        for line in file:
            lines.append(line)
    jsonStr='\n'.join(lines)
    info=json.loads(jsonStr)
    tracks.clear()
    for file in os.listdir(info['libraryPath']):
        if file.endswith('.mp3') or file.endswith('.m4a'):
            tracks.append(file)
    print(f'mp>Found {len(tracks)} tracks in {os.path.abspath(info['libraryPath'])}')

def saveData():
    with open(dataFile,'w') as file:
        file.write(json.dumps(info))

def search(key:str, space:list[str],threshold=60):
    bestMatches=process.extract(key,space)
    accepted=[]
    for item in bestMatches:
        if item[1]>=threshold:
            accepted.append(item[0])
    
    return accepted if len(accepted)>0 else [item[0] for item in bestMatches]

def chooseByIndex(things:list[str])->str:
    prompt='mp>Choose by index:'
    i = 1
    for item in things:
        prompt += f'\n{i}. {item}'
        i += 1
    prompt += '\nmp>'
    userInput = input(prompt)
    while userInput != 'abort' or userInput !='exit' or userInput != '!':
        try:
            index= int(userInput)
            if index>=1 and index <i:
                
                return things[index-1]
        except:
            print('Not a valid index')
        userInput = input(prompt)
    return None

class Player:
    playlist = []
    currentIndex=-1
    _loaded=False
    
    paused = True
    def __init__(self):
        mixer.init()

    def add(self,track:str):
        self.playlist.append(track)

    def remove(self,index:int):
        self.playlist.pop(index)

    def next(self):
        self.currentIndex = (self.currentIndex + 1) % self.length()

    def prev(self):
        self.currentIndex = (self.currentIndex - 1) % self.length()
        

    def shuffle(self):
        currentlyPlaying = []
        nextPossibleTracks = []
        for track in self.playlist:
            if track == self.playlist[self.currentIndex]:
                currentlyPlaying.append(track)
            else:
                nextPossibleTracks.append(track)
        if len(nextPossibleTracks)==0:
            return
        
        nextPossibleTracks=random.sample(nextPossibleTracks,len(nextPossibleTracks))
        i = min(self.currentIndex,len(nextPossibleTracks))
        for track in currentlyPlaying:
            nextPossibleTracks.insert(i,track)
            i += 1
        self.playlist = nextPossibleTracks
        self.currentIndex += len(currentlyPlaying)-1

        

    
    def length(self):
        return len(self.playlist)
    
    def isEmpty(self):
        return self.length() == 0
    
    def play(self):
        thread=threading.Thread(target=self._begin,daemon=True)
        thread.start()
    
    def wait(self):
        while mixer.music.get_busy():
            time.sleep(1)
        if not self.paused:
            self.stop()
            self.next()
            self.play()

    def _begin(self):
        global info
        abspath = info['libraryPath']
        if abspath[len(abspath)-1] not in ['/','\\']:
            if '/' in abspath:
                abspath += '/'
            elif '\\' in abspath:
                abspath += '\\'
            else:
                abspath += os.path.sep
        mixer.music.load(abspath+self.getTrack())
        mixer.music.play()
        self._loaded=True
        self.wait()

    def getTrack(self):
        return self.playlist[self.currentIndex]

    def toggle(self):
        if mixer.music.get_busy():
            mixer.music.pause()
            self.paused = True
        else:
            if self._loaded:
                mixer.music.unpause()
                thread = threading.Thread(target=self.wait,daemon=True)
                thread.start()
            else:
                self.next()
                self.play()
                print(f'Now playing {self.getTrack()}')
            self.paused = False
    def stop(self):
        mixer.music.stop()
        self._loaded=False
        mixer.music.unload()
    
    def clear(self):
        self.stop()
        self.playlist.clear()
        self.currentIndex=-1

if dataFile not in os.listdir():
    userInput=input("mp>Enter library path:")
    while not os.path.isdir(userInput):
        userInput=input("mp>Please enter a valid path:")
    info['libraryPath']=userInput
    saveData()



loadData()

player=Player()
print('mp>h for help')


while True:

    userInput = input("mp>")
    if userInput == "exit" or userInput == "!":
        break
    parts = userInput.split()
    if parts[0] == 'add':
        track=userInput.split('add')[1].strip()
        bestMatches = search(track,tracks)
        if len(bestMatches)>1:
            choice = chooseByIndex(bestMatches)
            if choice != None:
                player.add(choice)
                print(f'mp>{choice} added to queue')
        else:
            player.add(bestMatches[0])
            print(f'mp>{bestMatches[0]} added to queue')
    elif parts[0] == 'load':
        playlist = userInput.split('load')[1].strip()
        playlistNames=[key for key in info['playlist']]
        bestMatches = search(playlist,playlistNames)
        # print(f'here {bestMatches}')
        if len(bestMatches)>1:
            choice = chooseByIndex(bestMatches)
            if choice != None:
                playlistTracks = info['playlist'][choice]
                for item in playlistTracks:
                    player.add(item)
                print(f'mp>{choice} loaded')
        else:
            playlistTracks = info['playlist'][bestMatches[0]]
            for item in playlistTracks:
                player.add(item)
            print(f'mp>{bestMatches[0]} loaded')
    elif parts[0] == 'remove' and player.length() > 0:
        toRemove=-1
        try:
            toRemove = int(parts[1].strip())
        except:
            print(f'mp>Not a valid index')
        if toRemove < 1 and toRemove > player.length() + 1:
            print(f'mp>Index not in range')
        else:
            player.remove(toRemove-1)

    elif parts[0] == 'n':
        player.stop()
        player.next()
        player.play()
    elif parts[0] == 'p':
        player.stop()
        player.prev()
        player.play()
    elif parts[0] == 'save':
        playlistName = userInput.split('save')[1].strip()
        info['playlist'][playlistName]=player.playlist
        saveData()
    elif parts[0] == 'q':
        i = 1
        for item in player.playlist:
            if i != player.currentIndex + 1:
                print(f' {i}.{item}')
            else:
                print(f'>{i}.{item}')
            i += 1
    elif parts[0] == 't':
        player.toggle()
    elif parts[0] == 'c':
        player.clear()
    elif parts[0] == 's':
        player.shuffle()
    elif parts[0] == 'r':
        loadData()
    elif parts[0] == 'library':
        path = userInput.split('library')[1].strip()
        while not os.path.isdir(path):
            userInput=input("mp>Please enter a valid path:")
            path = userInput
        info['libraryPath']=path
        saveData() 
        loadData()
    elif parts[0] == 'h':
        print(helpText)
    elif parts[0] == 'tracks':
        i = 1
        for track in tracks:
            print(f'{i}. {track}')
            i += 1
       
    

player.stop()
saveData()

