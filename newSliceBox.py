import sys
import gi
from slicer import Slicer, Profile
from common import set_margin
from gi.repository import GObject as gobject

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

class NewSliceBox(Gtk.Box):
    def __init__(self, id, devices, selectable, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id = id
        self.selectable = selectable
        self.buildUI(devices)

    def getChecks(self, devices):
        out = []
        for dev in devices:
            check = Gtk.CheckButton(label=" "+dev)
            if not self.selectable:
                check.set_active(True)
                check.set_sensitive(False)
            out.append(check)
        return out

    def buildUI(self, devices):
        self.set_orientation(Gtk.Orientation.VERTICAL)
        sliceName = Gtk.Label(hexpand=True)
        sliceName.set_markup("<b>Slice #" + str(self.id)+"</b>")

        checksBox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,hexpand=True)
        leftChecksBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, halign=Gtk.Align.CENTER,hexpand=True)
        rightChecksBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, halign=Gtk.Align.CENTER,hexpand=True)
        self.checks = self.getChecks(devices)

        for el in self.checks[:len(self.checks)//2]:
            leftChecksBox.append(el)
        for el in self.checks[len(self.checks)//2:]:
            rightChecksBox.append(el)
        
        self.append(sliceName)
        checksBox.append(leftChecksBox)
        checksBox.append(rightChecksBox)
        self.append(checksBox)

    def getSelected(self):
        hosts = []
        switches = []
        for el in self.checks:
            if el.get_active():
                name = (el.get_label())[1:]
                if name[0] == "h":
                   hosts.append(name)
                else:
                    switches.append(name)
        return hosts,switches