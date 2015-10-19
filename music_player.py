import pyglet

class musicPlayer(pyglet.media.Player):

    def __init__(self):
        pyglet.media.Player.__init__(self)
        self.dequeued_sources = []
        self.list_sources = []

    def add_to_queue(self, source, song_file):
        # Add song to playlist queue, and to list of sources
        if(len(self._groups) > 0):
            if(source.audio_format != self._groups[0].audio_format):
                print 'The file %s is not of the same format as the other songs' % song_file
            else:
                self.queue(source)
                self.list_sources.append(source)
        else:
            self.queue(source)
            self.list_sources.append(source)

    def add_to_playlist(self, list_song_names):
        for song_file in list_song_names:
            try:
                song = pyglet.media.load(song_file)
                self.add_to_queue(song, song_file)
            except:
                print 'Could not load song %s' % song_file
            
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

