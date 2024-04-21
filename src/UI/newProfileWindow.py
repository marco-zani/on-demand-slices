import gi
from src.slicer.slicer import Profile
from src.common import set_margin, get_children
from gi.repository import GObject as gobject
from src.UI.newSliceBox import NewSliceBox

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk


class NewProfileWindow(Gtk.Dialog):
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
        self.nameEntry = Gtk.Entry(hexpand=True, text="profile" + str(self.profileId))

        checksBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        set_margin(checksBox, 15)

        addSliceBtn = Gtk.Button(label="Add Slice")
        addSliceBtn.set_hexpand(True)
        addSliceBtn.connect("clicked", self.addSlice, checksBox, devices)
        set_margin(addSliceBtn, 15)

        confirmBtn = Gtk.Button(label="Confirm")
        confirmBtn.set_hexpand(True)
        confirmBtn.connect("clicked", self.saveProfile, checksBox)
        set_margin(confirmBtn, 15)

        nameBox.append(entryLbl)
        nameBox.append(self.nameEntry)
        body.append(nameBox)

        body.append(checksBox)
        body.append(addSliceBtn)
        body.append(confirmBtn)
        self.set_child(body)

    def saveProfile(self, button, box):
        slices = []
        for child in get_children(box):
            h,s = child.getSelected()
            p = child.getPercentage()
            slices.append({'devices':h+s, 'minBandwidth':p})


        self.out = Profile(self.profileId, self.nameEntry.get_text(), slices)
        self.close()
        self.emit("newProfileWindowClosed")

    def addSlice(self, button, box, devices):
        remainingHosts = []
        switches = []
        for dev in devices:
            if dev[0] == "h":
                remainingHosts.append(dev)
            else:
                switches.append(dev)

        sliceCount = 1
        netSupply = 100
        for child in get_children(box):
            h, s = child.getSelected()
            p = child.getPercentage()

            if len(h) > 0:
                netSupply = netSupply-  p
                sliceBox = NewSliceBox(sliceCount, h + s, False, p, netSupply+p)
                sliceCount += 1
                box.append(sliceBox)

                for host in h:
                    if host in remainingHosts:
                        remainingHosts.remove(host)

            box.remove(child)

        if len(remainingHosts) > 0 and netSupply > 0:
            newSliceBox = NewSliceBox(sliceCount, remainingHosts + switches, True, 0, netSupply)
            box.append(newSliceBox)
        else :
            button.set_sensitive(False)
        


gobject.type_register(NewProfileWindow)
gobject.signal_new(
    "newProfileWindowClosed",
    NewProfileWindow,
    gobject.SIGNAL_RUN_FIRST,
    gobject.TYPE_NONE,
    (),
)
