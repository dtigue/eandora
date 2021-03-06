import elementary
import evas
import urllib
import time
import os
import shutil

class playerWindow(elementary.Table):
    def __init__( self, parent ):
        #Builds an elementary tabel that displays our information
        elementary.Table.__init__(self, parent.mainWindow)

        #Store our parent window
        self.rent = parent

        #Access the player function we need to talk to
        self.ourPlayer = parent.ourPlayer
        self.ourPlayer.setGUI(self)

        #These are widgets that appear at the player page of our window
        self.songList = elementary.List(parent.mainWindow)
        self.stationButton = elementary.Button(parent.mainWindow)
        self.thumb = elementary.Button(parent.mainWindow)
        self.song = elementary.Button(parent.mainWindow)
        self.artist = elementary.Label(parent.mainWindow)
        self.album = elementary.Button(parent.mainWindow)
        self.rating = elementary.Button(parent.mainWindow)
        self.menubutton = elementary.Toolbar(parent.mainWindow)
        self.mainmenu = elementary.Menu(parent.mainWindow)
        self.counter = [elementary.Clock(parent.mainWindow), elementary.Label(parent.mainWindow), elementary.Label(parent.mainWindow)]
        self.pauseTime = None

        #Build the page layout
        home = os.path.expanduser("~")
        if os.path.exists("%s/.config/eAndora/stationinfo"%home):
            f = open('%s/.config/eAndora/stationinfo'%home, 'r')
            lines = f.readlines()
            self.ourPlayer.setStation(self.ourPlayer.getStationFromName(lines[0].rstrip("\n")))
        else:
            self.ourPlayer.setStation(self.ourPlayer.getStations()[0])

        self.stationButton.tooltip_text_set("Change Stations")
        self.stationButton.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
        self.stationButton.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
        self.stationButton.callback_unpressed_add(self.station_selection)
        self.pack(self.stationButton, 4, 0, 2, 3)

        self.songList.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
        self.songList.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
        self.pack(self.songList, 0, 4, 4, 3)

        #Our main menu
        self.menubutton.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
        self.menubutton.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
        item = self.menubutton.item_append("images/eAndora.png", "Menu", None, None)
        item.menu_set(True)
        self.menubutton.menu_parent_set(parent.mainWindow)
        menu = item.menu_get()
        menu.item_add(None, "About", "images/about.png", self.logout)
        menu.item_add(None, "Create Station", "images/search.png", self.logout)
        menu.item_add(None, "Settings", "images/settings.png", self.logout)
        menu.item_add(None, "Logout", "refresh", self.logout)
        self.pack(self.menubutton, 5, 3, 1, 1)
        self.menubutton.show()

        ic = elementary.Icon(parent.mainWindow)
        ic.file_set("images/skip.png")
        bt = elementary.Button(parent.mainWindow)
        bt.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
        bt.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
        bt.content_set(ic)
        bt.callback_unpressed_add(self.skip_track)
        self.pack(bt, 4, 4, 1, 1)
        bt.show()

        ic = elementary.Icon(parent.mainWindow)
        ic.file_set("images/pause.png")
        bt = elementary.Button(parent.mainWindow)
        bt.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
        bt.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
        bt.content_set(ic)
        bt.callback_unpressed_add(self.play_pause)
        self.pack(bt, 4, 5, 1, 1)
        bt.show()

        ic = elementary.Icon(parent.mainWindow)
        ic.file_set("images/ban.png")
        bt = elementary.Button(parent.mainWindow)
        bt.tooltip_text_set("Ban Song")
        bt.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
        bt.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
        bt.content_set(ic)
        bt.callback_unpressed_add(self.ban_track)
        self.pack(bt, 5, 5, 1, 1)
        bt.show()

        #Define callbacks for all our buttons that will be updated
        #Button content is generated on song change

        self.thumb.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
        self.thumb.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
        self.pack(self.thumb, 2, 0, 2, 3)

        self.song.callback_pressed_add(self.show_song)
        self.song.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
        self.song.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
        self.pack(self.song, 0, 0, 2, 1)

        self.album.callback_pressed_add(self.show_album)
        self.album.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
        self.album.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
        self.pack(self.album, 0, 1, 2, 1)

        self.rating.callback_unpressed_add(self.love_track)
        self.artist.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
        self.artist.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
        self.pack(self.artist, 0, 2, 2, 1)

        self.counter[0].size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
        self.counter[0].size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
        self.counter[0].show_seconds_set(True)
        self.pack(self.counter[0], 0, 3, 1, 1)

        self.counter[1].size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
        self.counter[1].size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
        self.pack(self.counter[1], 2, 3, 1, 1)

        self.rating.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
        self.rating.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
        self.pack(self.rating, 5, 4, 1, 1)

        self.ourPlayer.addSongs()

    def ban_track( self, bt ):
        #Tell pandora we don't want this song played anymore, then skip to the next track
        self.ourPlayer.banSong()
        self.ourPlayer.skipSong()

    def love_track( self, bt ):
        #Tell pandora we love this song, then update the GUI so it reflects this change
        self.ourPlayer.loveSong()
        ic = elementary.Icon(self.rent.mainWindow)
        ic.file_set('images/love.png')
        self.rating.hide()
        self.rating.tooltip_text_set("Song already liked")
        self.rating.content_set(ic)
        self.rating.show()

    def show_song( self, bt ):
        #Opens song information in the user's default web browser
        self.ourPlayer.showSong()

    def show_album( self, bt ):
        #Opens album information in the user's default web browser
        self.ourPlayer.showAlbum()

    def song_change( self ):
        #Updates the GUI so it reflects a new song's infromation
        info = self.ourPlayer.getCurSongInfo()
        print("DEBUG: Changing Album Art")
        try:
            os.remove('/tmp/albumart.jpg')
        except:
            pass
        urllib.urlretrieve(str(info['thumbnail']), '/tmp/albumart.jpg')
        ic = elementary.Icon(self.rent.mainWindow)
        ic.file_set('/tmp/albumart.jpg')
        self.thumb.show()
        self.thumb.content_set(ic)
        self.thumb.show()

        print("DEBUG: Changing song title")
        self.song.hide()
        self.song.text_set("Song: %s"%info['title'])
        self.song.show()

        print("DEBUG: Changing album title")
        self.album.hide()
        self.album.text_set("Album: %s"%info['album'])
        self.album.show()

        print("DEBUG: Changing artist")
        self.artist.hide()
        self.artist.text_set("<b><div align='center'>Artist: %s</div></b>"%info['artist'])
        self.artist.show()

        print("DEBUG: Changing clock to zero")
        self.counter[0].hide()
        self.counter[0].time_set(0, 0, 0)
        self.counter[0].show()

        print("DEBUG: Changing total time")
        self.counter[1].hide()
        mins, seconds = 0, 0
        while not mins and (seconds == 1 or seconds == 0):
            time.sleep(0.25)
            mins, seconds = self.ourPlayer.getSongDuration()
        if int(seconds) > 9:
            self.counter[1].text_set("<b>/      %s : %s</b>"%(mins, int(seconds)))
        else:
            self.counter[1].text_set("<b>/      %s : 0%s</b>"%(mins, int(seconds)))
        self.counter[1].show()

        print("DEBUG: Changing ratings")
        self.rating.hide()
        ic = elementary.Icon(self.rent.mainWindow)
        rating = self.ourPlayer.getSongRating()
        if not rating:
            ic.file_set('images/favorite.png')
            self.rating.tooltip_text_set("Like Song")
        elif rating == 'love':
            ic.file_set('images/love.png')
            self.rating.tooltip_text_set("Song already liked")
        else:
            ic.file_set('images/ban.png')
        self.rating.content_set(ic)
        self.rating.show()

        print("DEBUG: Adding song to list")
        self.refreshInterface()

        print("Hey look the song changed!")

    def play_pause(self, bt):
        ic = elementary.Icon(self.rent.mainWindow)
        if self.ourPlayer.player.play:
            ic.file_set("images/play.png")
            self.pauseTime = self.counter[0].time_get()
            self.counter[0].hide()
            self.counter[2].size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
            self.counter[2].size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
            if self.pauseTime[2] > 9:
                self.counter[2].text_set("<b>%s : %s</b>"%(self.pauseTime[1], self.pauseTime[2]))
            else:
                self.counter[2].text_set("<b>%s : 0%s</b>"%(self.pauseTime[1], self.pauseTime[2]))
            self.pack(self.counter[2], 0, 3, 1, 1)
            self.counter[2].show()
            self.ourPlayer.pauseSong()
        else:
            ic.file_set("images/pause.png")
            self.counter[2].hide()
            self.counter[0].size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
            self.counter[0].size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
            self.counter[0].show_seconds_set(True)
            self.counter[0].time_set(0, self.pauseTime[1], self.pauseTime[2])
            self.pack(self.counter[0], 0, 3, 1, 1)
            self.counter[0].show()
            self.ourPlayer.playSong()
        bt.content_set(ic)
        bt.show()

    def skip_track(self, bt):
        self.ourPlayer.skipSong()

    def cb_items(self, li, item):
        print(("ctxpopup item selected: %s" % (item.text)))
        self.refreshInterface(True)
        self.ourPlayer.setStation(self.ourPlayer.getStationFromName(item.text))
        home = os.path.expanduser("~")
        if not os.path.exists("%s/.config/eAndora"%home):
            os.makedirs("%s/.config/eAndora"%home)
        if os.path.exists("%s/.config/eAndora/stationinfo"%home):
            os.remove('%s/.config/eAndora/stationinfo'%home)
        f = open('%s/.config/eAndora/stationinfo'%home, 'w')
        f.write('%s\n'%item.text)
        f.close()
        self.ourPlayer.pauseSong()
        self.ourPlayer.clearSongs()
        self.ourPlayer.addSongs()

    def refreshInterface( self, clear=False ):
        if clear:
            self.songList.clear()
        info = self.ourPlayer.getCurSongInfo()
        self.songList.item_prepend("%s - %s"%(info['title'], info['artist']))
        self.songList.show()
        self.songList.go()
        self.stationButton.text_set(str(self.ourPlayer.getStation().name))
        self.stationButton.hide()
        self.stationButton.show()

    def item_new(self, cp, label, icon = None):
        if icon:
            ic = elementary.Icon(cp)
            ic.standard_set(icon)
            ic.resizable_set(False, False)
            return cp.item_append(label, ic, self.cb_items)
        else:
            return cp.item_append(label, None, self.cb_items)

    def station_selection(self, bt):
        cp = elementary.Ctxpopup(bt)
        stations = self.ourPlayer.getStations()
        for station in stations:
            bt = self.item_new(cp, str(station['stationName']))
        cp.show()

    def logout(self, menu, item):
        print "Log out"
        self.ourPlayer.pauseSong()
        self.ourPlayer.clearSongs()
        home = os.path.expanduser("~")
        shutil.rmtree('%s/.config/eAndora'%home)
        self.rent.spawn_login()
