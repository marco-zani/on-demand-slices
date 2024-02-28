import sys
import gi
from slicer import Slicer, Profile
from common import set_margin
from gi.repository import GObject as gobject

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

class NewProfileWindow(Gtk.ApplicationWindow):
    def __init__(self, devices, id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.out = []
        self.profileId = id
        self.set_title("New profile")

        self.buildUI(devices)

    def buildUI(self, devices):
        self.set_default_size(300, 100)

        body = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        body.set_hexpand(True)

        nameBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        set_margin(nameBox, 15)

        entryLbl = Gtk.Label(label="Insert profile name:", halign=Gtk.Align.START)
        entryLbl.set_margin_bottom(5)
        self.nameEntry = Gtk.Entry(hexpand=True, text="profile"+str(self.profileId))

               

        checksBox = Gtk.Box()
        leftChecksBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, halign=Gtk.Align.CENTER,hexpand=True)
        rightChecksBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, halign=Gtk.Align.CENTER,hexpand=True)
        self.checks = self.getChecks(devices)
        set_margin(checksBox, 15)

        confirmBtn = Gtk.Button(label="Confirm")
        confirmBtn.set_hexpand(True)
        confirmBtn.connect("clicked", self.saveProfile)
        set_margin(confirmBtn, 15)

        nameBox.append(entryLbl)
        nameBox.append(self.nameEntry)
        body.append(nameBox)
        for el in self.checks[:len(self.checks)//2]:
            leftChecksBox.append(el)
        for el in self.checks[len(self.checks)//2:]:
            rightChecksBox.append(el)
        checksBox.append(leftChecksBox)
        checksBox.append(rightChecksBox)
        body.append(checksBox)
        body.append(confirmBtn)
        self.set_child(body)

    def saveProfile(self, button):
        selectedDevices = []

        for el in self.checks:
            if el.get_active():
                selectedDevices.append(el.get_label())

        self.out = Profile(self.profileId, self.nameEntry.get_text(),selectedDevices)
        self.close()
        self.emit("newProfileWindowClosed")





    def getChecks(self, devices):
        out = []

        for dev in devices:
            check = Gtk.CheckButton(label=" "+dev)
            out.append(check)
        return out

gobject.type_register(NewProfileWindow)
gobject.signal_new("newProfileWindowClosed", NewProfileWindow, gobject.SIGNAL_RUN_FIRST,
                   gobject.TYPE_NONE, ())