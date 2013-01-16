import emotion
import pandora
import webbrowser

def openBrowser(url):
    print "Opening %s"%url
    webbrowser.open(url)
    try:
        os.wait() # workaround for http://bugs.python.org/issue5993
    except:
        pass

class eAndora(object):
    def __init__( self, parent ):
        self.gui = ""
        self.rent = parent
        self.pandora = pandora.Pandora()
        self.curStation = ""
        self.curSong = None
        self.skip = False
        self.die = False
        self.settings = {"username":"", "password":""}
        self.player = None
        self.skinName = "Default"
        self.song = None
        self.songinfo = []
        self.displaysongs = []
        self.songCount = 0

    def setGUI( self, GUI):
        self.gui = GUI
        self.player = emotion.Emotion(self.gui.rent.mainWindow.evas_get(), module_filename="gstreamer")
        self.player.callback_add("playback_finished", self.nextSong)

    def auth( self, user, passwd):
        print "User %s - Password %s"%(user, passwd)
        self.settings['username'] = user
        self.settings['password'] = passwd
        try:
            self.pandora.connect(self.settings['username'], self.settings['password'])
        except:
            self.rent.login_error()

    def playSong( self ):
        self.player.play_set(True)

    def pauseSong( self ):
        self.player.play_set(False)

    def skipSong( self ):
        self.nextSong("skip")

    def setStation( self, station ):
        self.curStation = pandora.Station(self.pandora, station)

    def getStations( self ):
        return self.pandora.get_stations()

    def getStation( self ):
        return self.curStation

    def getCurSongInfo( self ):
        return self.songinfo[self.curSong]

    def getSongInfo( self ):
        return self.songinfo

    def getStationFromName( self, name):
        stations = self.getStations()
        for station in stations:
            if station['stationName'] == name:
                return station

    def getSongDuration( self ):
        print "Getting Song duration"
        seconds = self.player.play_length
        print "Starting Seconds %s"%seconds
        mins = 0
        while seconds >= 60:
            seconds -= 60
            mins += 1
        print "Minutes %s Seconds %s"%(mins, seconds) 
        return mins, seconds

    def getSongRating( self ):
        return self.songinfo[self.curSong]['rating']

    def showSong( self ):
        openBrowser(self.songinfo[self.curSong]['object'].songDetailURL)

    def showAlbum( self ):
        openBrowser(self.songinfo[self.curSong]['object'].albumDetailURL)

    def banSong( self ):
        info = self.songinfo[self.curSong]
        info['object'].rate('ban')

    def loveSong( self ):
        info = self.songinfo[self.curSong]
        info['object'].rate('love')

    def clearSongs( self ):
        self.song = None
        self.songCount = 0
        self.songinfo = []
        self.displaysongs = []

    def addSongs( self ):
        playlist = self.curStation.get_playlist()
        for song in playlist:
            info = { "title"	:	song.title, \
        	 "artist"	:	song.artist, \
        	 "album"	:	song.album, \
        	 "thumbnail"	:	song.artRadio, \
             "url"      : str(song.audioUrl), \
             "rating"   : song.rating, \
             "object"   : song
        	}
            self.songinfo.append(info)
        if not self.song:
            self.startPlaying()

    def startPlaying( self ):
        self.curSong = -1
        self.nextSong()

    def nextSong( self , event=False ):
        print("Debug 1")
        if self.player:
            if self.player.play_get():
                self.player.play_set(False)
        print("Debug 3")
        self.curSong += 1
        info = self.songinfo[self.curSong]
        self.displaysongs.append(info)
        self.song = info['title']
        print(info)
        print("Debug 4")
        self.player.file = info['url']
        print("Debug 5")
        self.player.play_set(True)
        print("Debug 6")
        self.gui.song_change()
        print("Debug 7")
        if self.curSong >= len(self.songinfo)-1:
            print("Debug 8")
            self.addSongs()
        print("Debug 9")
        self.songCount += 1
        if self.songCount >= 15:
            print("Debug 10")
            self.songCount = 0
            self.auth(self.settings['username'], self.settings['password'])

