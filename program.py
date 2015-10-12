from pydub import AudioSegment
from pydub.playback import play

import os
from os import listdir, walk
from os.path import isfile, join

import threading
from multiprocessing import Process, Value


playlist = {}
current_song = None
current_playlist = None

'''
class myThread (threading.Thread):
    def __init__(self, name, func):
        threading.Thread.__init__(self)
        self.name = name
        self.func = func
    def run(self):
        print "Starting " + self.name
        self.func()
        print "Exiting " + self.name
'''

def printCommands():
    print 'Alt+N: New Playlist\tAlt+A: Add Song to Playlist'
    print 'Alt+P: Play Playlist\tAlt+Space: Play/Pause Toggle'
    print 'Alt+X: Next Song\tAlt+Z: Previous Song'
    print 'Alt+R: Repeat Playlist\tAlt+S: Repeat Song'
    print 'Alt+W: Save Playlists\tAlt+Q: Quit'


def play_playlist(name):
    for song_file in playlist[name]:
        song = AudioSegment.from_mp3(song_file)
        current_song = song
        play(song)
        print "Here!"


MUSIC_DIR = "/home/hp/Music/"

printCommands()

playlist_file = open("list_playlists.txt", "r")
file_lines = playlist_file.readlines()
playlist_file.close()

#Build up playlists
for line in file_lines:
    if(line[:6] == 'Name: '):
        playlist_name = line[6:].rstrip()
        new_list = []
        next_line_index = file_lines.index(line) + 1
        while(file_lines[next_line_index][:3] != '---'):
            new_list.append(file_lines[next_line_index].rstrip())
            next_line_index += 1
        line = file_lines[next_line_index+1]
        playlist[playlist_name] = new_list

quit = False
play_process = None

while(quit is not True):
    print "Enter command: ",
    command = raw_input()

    if(command == 'n'):
        # Create new playlist
        playlist_name = raw_input("Enter name of playlist: ")
        if(playlist_name in playlist.keys()):
            print "This playlist already exists!"
        else:
            create_from_folder = raw_input("Import from folder? (Y/n) ")
            if(create_from_folder == 'Y'):
                songs_list = []
                folder_name = raw_input("Enter folder name (relative to Music/ directory): ")
                # Get all files in given folder, including those in subfolders
                for root, directories, files in walk(join(MUSIC_DIR, folder_name)):
                    for filename in files:
                        if(filename[-4:] == '.mp3'):
                            songs_list.append(join(root, filename))  
                playlist[playlist_name] = songs_list
            else:
                songs_list = []
                playlist[playlist_name] = songs_list
        
    elif(command == 'a'):
        # Add a song to existing playlist
        playlist_name = raw_input("Enter name of playlist: ")
        if(playlist_name in playlist.keys()):
            song_name = raw_input("Enter file name (relative to Music/ directory): ")
            if(isfile(join(MUSIC_DIR, song_name))):
                playlist[playlist_name].append(join(MUSIC_DIR, song_name))
            else:
                print "The file %s does not exist!" % (MUSIC_DIR+song_name)
        else:
            print "The playlist %s does not exist!" % (playlist_name)
        
    elif(command == 'p'):
        # Play a given playlist, run in a second background process
        name = raw_input("Enter playlist name: ")
        # If already currently playing, terminate existing process before creating new one
        if(play_process is not None):
            play_process.terminate()
            play_process.join()

        current_playlist = playlist[name]
        play_process = Process(target = play_playlist, args=(name, ))
        play_process.start()

    elif(command == 'k'):
        print 'Keys:', playlist.keys()

    elif(command == 'w'):
        # Write all the playlists to list_playlists.txt
        print 'Saving playlist...'
        playlist_file = open('list_playlists.txt', 'w')
        for name in playlist.keys():
            playlist_file.write('Name: ' + name + '\n')
            for song in playlist[name]:
                playlist_file.write(song + '\n')
            playlist_file.write('--------------\n')
        playlist_file.write('\n')
        playlist_file.close()
        print 'Playlist saved!'

    elif(command == 'q'):
        if(play_process is not None):
            play_process.terminate()
            play_process.join()
        quit = True