import sys
import gi

from gi.repository import GObject
from slicer import Slicer, Profile
from common import set_margin
from newProfileWindow import NewProfileWindow

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw
from gi.repository import GObject as gobject


def formatProfiles(profiles):
    out = ""
    for profile in profiles:
        out = out + "<b>@" + str(profile.id) + " - " + profile.name + "</b>\n"
        for dev in profile.devices:
            out = out + " " + dev
        out = out + "\n\n"
    return out


def formatDevices(devices):
    out = ""
    for dev in devices:
        conn = devices[dev]
        out = out + "<b>@" + dev + "</b>\n"

        lastItem = conn[-1]
        for port, connDev in conn:
            if (port, connDev) == lastItem:
                out = out + "  └─ Eth" + port + " ── " + connDev + "\n\n"
            else:
                out = out + "  ├─ Eth" + port + " ── " + connDev + "\n"

    splitIndex = len(out) // 2
    while out[splitIndex] != "\n" or out[splitIndex + 1] != "\n":
        splitIndex += 1

    outLeft = out[:splitIndex]
    outRight = out[splitIndex:]

    return outLeft, outRight


class SlicerWindow(Gtk.ApplicationWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.slicer = Slicer()
        self.slicer.importTopology()

        self.buildUI()

    def buildUI(self):
        self.set_default_size(600, 700)
        body = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        viewSwitcher = Gtk.StackSwitcher()

        set_margin(viewSwitcher, 15)

        viewStack = Gtk.Stack()

        viewStack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        viewStack.set_transition_duration(500)

        viewStack.add_titled(self.getNetworkView(), "netView", "network view")
        viewStack.add_titled(
            self.getActiveSlicesView(), "slicesView", "active slices view"
        )
        viewStack.add_titled(self.getProfilesView(), "profView", "profiles view")

        viewSwitcher.set_stack(viewStack)

        self.set_child(body)
        body.append(viewSwitcher)
        body.append(viewStack)

    def getNetworkView(self):
        out = Gtk.ScrolledWindow()
        container = Gtk.Box()
        set_margin(container, 25)
        container.set_hexpand(True)
        container.set_vexpand(True)

        lSep = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)
        rSep = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)

        leftText, rightText = formatDevices(self.slicer.topology.devices)

        networkTextLeft = Gtk.Label()
        networkTextLeft.set_markup(leftText)
        networkTextLeft.set_hexpand(True)

        networkTextRight = Gtk.Label()
        networkTextRight.set_markup(rightText)
        networkTextRight.set_hexpand(True)

        container.append(lSep)
        container.append(networkTextLeft)
        container.append(networkTextRight)
        container.append(rSep)

        out.set_child(container)

        return container

    def getActiveSlicesView(self):
        out = Gtk.Box()
        set_margin(out, 25)
        out.set_hexpand(True)
        out.set_vexpand(True)

        lSep = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)
        rSep = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)

        activeSlicesText = Gtk.Label(label="active slices view")
        activeSlicesText.set_hexpand(True)

        out.append(lSep)
        out.append(activeSlicesText)
        out.append(rSep)

        return out

    def getProfilesView(self):
        out = Gtk.Box()
        set_margin(out, 25)

        body = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        body.set_hexpand(True)
        body.set_vexpand(True)

        lSep = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)
        rSep = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)

        profilesText = Gtk.Label()
        profilesText.set_markup(formatProfiles(self.slicer.profiles))
        profilesText.set_hexpand(True)
        profilesText.set_vexpand(True)
        self.connect("updateProfiles", self.updateProfiles, profilesText)

        addProfileBtn = Gtk.Button(label="Create new profile")
        set_margin(addProfileBtn, 35)
        addProfileBtn.set_hexpand(True)
        addProfileBtn.connect(
            "clicked", self.spawnNewProfileWidget, self.slicer.topology.devices
        )

        body.append(profilesText)
        body.append(addProfileBtn)

        out.append(lSep)
        out.append(body)
        out.append(rSep)

        return out

    def updateProfiles(self, window, label):
        label.set_markup(formatProfiles(self.slicer.profiles))

    def spawnNewProfileWidget(self, button, devices):
        npw = NewProfileWindow(devices, self.slicer.profiles[-1].id + 1)
        npw.set_modal(self)
        npw.present()

        npw.connect("newProfileWindowClosed", self.newProfileWindowsClosed)

    def newProfileWindowsClosed(self, npw):
        if npw.out.devices != []:
            self.slicer.profiles.append(npw.out)
        npw.destroy()
        self.emit("updateProfiles")


class visualizer(Adw.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connect("activate", self.on_activate)

    def on_activate(self, app):
        self.win = SlicerWindow(application=app)
        self.win.present()


gobject.type_register(SlicerWindow)
gobject.signal_new(
    "updateProfiles", SlicerWindow, gobject.SignalFlags.RUN_FIRST, gobject.TYPE_NONE, ()
)

app = visualizer(application_id="com.OnDemandSlices.GTKSlicer")

app.run(sys.argv)
