import gi
from pathlib import Path 

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk 
from gi.repository import GLib 

from rify import get_songs, download_song
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

        self.listbox = Gtk.ListBox()

        self.scroll = Gtk.ScrolledWindow()
        self.scroll.set_child(self.listbox)
        self.scroll.set_vexpand(True)
        self.scroll.set_hexpand(True)

        self.main_box.append(self.url_entry)
        self.main_box.append(self.download_button)
        self.main_box.append(self.scroll)

        self.refresh_listbox()

        self.listbox.connect(
            "row-activated",
            self.play_selected
        )

        self.set_child(self.main_box) 
    def drag_begin(self, *args):
        self.dragging = True
    def drag_end(self, *args):
        self.dragging = False

    def on_seek(self,scale):
        self.player.player.time_pos = scale.get_value() 
    
    def update_seek(self):
        if not self.dragging:
          duration = self.player.player.duration
          position = self.player.player.time_pos
          if duration is not None :
            self.seek.set_range(0, duration)
          if position is not None:
            self.seek.set_value(position)
        return True 
    
    def refresh_listbox(self):
        self.listbox.remove_all()

        print("refreshing:", len(self.songs))

        for song in self.songs:
            row = Gtk.ListBoxRow()

            label = Gtk.Label(
                label=f"{Path(song['path']).parent.parent.name} - {song['title']}",
                xalign=0
            )

            row.set_child(label)
            self.listbox.append(row)


    def download_clicked(self, button):
        url = self.url_entry.get_text()

        if url:
            download_song(url)
            self.songs = get_songs()
            self.refresh_listbox()


    def play_selected(self, listbox, row):
        song = self.songs[row.get_index()]
        self.player.play(song["path"]) 


    def toggle_pause(self, button):
        self.player.pause()


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