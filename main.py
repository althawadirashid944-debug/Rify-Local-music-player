import os
import sys

if sys.platform == "win32":
    os.add_dll_directory(
        os.path.join(
            os.path.dirname(__file__),
            "runtime",
            "gtk",
            "bin"
        )
    ) 









import gi
from pathlib import Path 

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk 
from gi.repository import GLib 

from rify import get_songs, download_song, build_library
from player import Player


class RifyWindow(Gtk.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app)

        self.set_title("Rify")
        self.set_default_size(700, 500)

        self.main_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=8
        )
        self.seek = Gtk.Scale.new_with_range(
            Gtk.Orientation.HORIZONTAL,
            0,
            100,
            1,
        )  
        self.seek.set_draw_value(False)
        self.main_box.append(self.seek) 
        self.seek.connect("value-changed",self.on_seek) 
       
        self.player = Player() 
        self.updating_seek = False 
        self.dragging = False 
        GLib.timeout_add(500, self.update_seek) 


        self.songs = get_songs()
        print("Songs found:", len(self.songs))

        self.play_button = Gtk.Button(label="▶ Play/Pause")
        self.stop_button = Gtk.Button(label="⏹ Stop")

        self.play_button.connect(
            "clicked",
            self.toggle_pause
        )

        self.stop_button.connect(
            "clicked",
            self.stop_song
        )

        self.main_box.append(self.play_button)
        self.main_box.append(self.stop_button)

        self.url_entry = Gtk.Entry()
        self.url_entry.set_placeholder_text("Paste music URL...")

        self.download_button = Gtk.Button(label="Download")
        self.download_button.connect(
            "clicked",
            self.download_clicked
        )

        self.library = build_library(self.songs) 
        self.artist_list = Gtk.ListBox()
        self.album_list = Gtk.ListBox()
        self.song_list = Gtk.ListBox() 
        library_box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=8
        ) 
        artist_scroll = Gtk.ScrolledWindow() 
        album_scroll = Gtk.ScrolledWindow()
        song_scroll = Gtk.ScrolledWindow()
        artist_scroll.set_child(self.artist_list)
        album_scroll.set_child(self.album_list)
        song_scroll.set_child(self.song_list) 
        artist_scroll.set_vexpand(True) 
        artist_scroll.set_hexpand(True)
        album_scroll.set_vexpand(True) 
        album_scroll.set_hexpand(True) 
        
        
        song_scroll.set_vexpand(True) 
        song_scroll.set_hexpand(True) 
        library_box.append(artist_scroll)
        library_box.append(album_scroll)
        library_box.append(song_scroll) 
        self.main_box.append(self.url_entry)
        self.main_box.append(self.download_button)
        self.main_box.append(library_box) 
        self.populate_artists() 
        self.artist_list.connect(
        "row-activated",
        self.artist_selected
        )

        self.album_list.connect(
        "row-activated",
        self.album_selected
        )

        self.song_list.connect(
        "row-activated",
        self.play_selected
        )



        

        self.set_child(self.main_box) 
    def drag_begin(self, *args):
        self.dragging = True
    def drag_end(self, *args):
        self.dragging = False

    def on_seek(self,scale):
        if not self.updating_seek: 
         self.player.player.time_pos = scale.get_value() 
    
    def update_seek(self):
        if not self.dragging:
          duration = self.player.player.duration
          position = self.player.player.time_pos
          if duration is not None :
            self.seek.set_range(0, duration)
          if position is not None:
            self.updating_seek = True
            self.seek.set_value(position)
            self.updating_seek = False 
        return True 
    
    def populate_artists(self) : 
        self.artist_list.remove_all()
        for artist in self.library:
            row= Gtk.ListBoxRow()
            row.set_child(Gtk.Label(
                label=artist,
                xalign=0
            )) 
            self.artist_list.append(row) 

    def download_clicked(self, button):
        url = self.url_entry.get_text()

        if url:
            download_song(url)
            self.songs = get_songs()
            self.refresh_listbox()


    def play_selected(self, listbox, row):
        song = self.current_songs[row.get_index()] 
        self.player.play(song["path"]) 


    def toggle_pause(self, button):
        self.player.pause()

    def artist_selected(self,listbox,row):
        self.selected_artist=row.get_child().get_text()
        self.album_list.remove_all()
        self.song_list.remove_all()
        for album in self.library[self.selected_artist] :
            album_row = Gtk.ListBoxRow()
            label=Gtk.Label(
                label=album,
                xalign=0
            ) 
            album_row.set_child(label)
            self.album_list.append(album_row) 
    
    def album_selected(self,listbox,row):
        self.selected_album=row.get_child().get_text()
        self.song_list.remove_all()
        self.current_songs = self.library[
            self.selected_artist
        ] [
            self.selected_album
        ] 
        for song in self.current_songs:
            song_row=Gtk.ListBoxRow()
            label=Gtk.Label(
                label=song["title"],
                xalign=0
            )
            song_row.set_child(label)
            self.song_list.append(song_row) 

            
    def stop_song(self, button):
        self.player.stop()


class RifyApp(Gtk.Application):
    def __init__(self):
        super().__init__(
            application_id="com.rashid.rify"
        )

    def do_activate(self):
        window = RifyWindow(self)
        window.present()


app = RifyApp()
app.run() 