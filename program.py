import pyglet

import os
from os import listdir, walk
from os.path import isfile, join

from multiprocessing import Process, Value


playlist = {}
current_song = None
current_playlist = None


class _Getch:
    def __init__(self):
        import tty, sys

    def __call__(self):
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


class musicPlayer(pyglet.media.Player):

    def __init__(self):
        pyglet.media.Player.__init__(self)
        self.dequeued_sources = []
        self.list_sources = []

    def add_to_queue(self, source):
        # Add song to playlist queue, and to list of sources
        self.queue(source)
        self.list_sources.append(source)

    def next_song(self):
        # Play the next song, set timestamp to 0 to play from beginning
        self.next_source()
        self._groups[-1].seek(0)

    def previous_song(self):
        # Find and play the previous song, set timestamp to 0 to play from beginning
        current_source = self._groups[-1]._sources[0]
        prev_source = self.list_sources[ self.list_sources.index(current_source)-1 ]
        self._groups[-1]._timestamp_offset -= prev_source.duration
        self._groups[-1]._dequeued_durations = self._groups[-1]._dequeued_durations[1:]
        self._groups[-1]._sources.insert(0, prev_source)
        self._groups[-1].duration += prev_source.duration
        self._groups[-1].seek(0)


def printCommands():
    print 'n: New Playlist\t\ta: Add Song to Playlist'
    print 'p: Play Playlist\tSpace: Play/Pause Toggle'
    print 'x: Next Song\t\tz: Previous Song'
    print 'r: Repeat Playlist\ts: Repeat Song'
    print 'w: Save Playlists\tq: Quit'


def play_playlist(player):
    pyglet.app.run()


MUSIC_DIR = "/home/tejas/Music/"

printCommands()

playlist_file = open("list_playlists.txt", "r")
file_lines = playlist_file.readlines()
playlist_file.close()

#Build up existing playlists
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
dash_line = '------------------------------------------------------------------'
print dash_line

getch = _Getch()

while(quit is not True):
    os.system("stty -echo")
    command = getch()
    os.system("stty echo")

    if(command == 'n'):
        # Create new playlist
        playlist_name = raw_input("Enter name of playlist: ")
        if(playlist_name in playlist.keys()):
            print "This playlist already exists!"
        else:
            create_from_folder = raw_input("Import from folder? (Y/n) ")
            if(create_from_folder == 'Y' or create_from_folder == 'y'):
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
        print dash_line
        
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
        print dash_line
        
    elif(command == 'p'):
        # Play a given playlist, run in a second background process
        name = raw_input("Enter playlist name: ")
        # If already currently playing, terminate existing process before creating new one
        if(play_process is not None):
            player.delete()
            play_process.terminate()
            play_process.join()

        try:
            # current_playlist = playlist[name]
            player = musicPlayer()
            for song_file in playlist[name]:
                song = pyglet.media.load(song_file)
                player.add_to_queue(song)
            player.play()
            play_process = Process(target = play_playlist, args=(player, ))
            play_process.start()
        except:
            print "The playlist %s does not exist!" % name
            print "The existing playlists are: "
            for key in playlist.keys():
                print key
        print dash_line

    elif(command == ' '):
        # Play/pause current playlist
        try:
            if(player.playing is True):
                player.pause()
            else:
                player.play()
        except:
            print "No playlist currently being played"
            print dash_line

    elif(command == 'x'):
        # Next song in playlist
        try:
            player.next_song()
        except:
            print "No playlist currently being played"
            print dash_line

    elif(command == 'z'):
        try:
            player.previous_song()
        except:
            print "No playlist currently being played"
            print dash_line

    elif(command == 'r'):
        # Repeat playlist
        try:
            if(player._groups[-1]._loop is False):
                player._groups[-1]._loop = True
                print 'Repeat Song: ON'
            else:
                player._groups[-1]._loop = False
                print 'Repeat Song: OFF'
        except:
            print "No playlist currently being played"
        print dash_line

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
        print dash_line

    elif(command == 'q'):
        if(play_process is not None):
            player.delete()
            play_process.terminate()
            play_process.join()
        quit = True