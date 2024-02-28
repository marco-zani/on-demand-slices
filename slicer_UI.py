import sys
import gi

from gi.repository import GObject
from slicer import Slicer, Profile
from common import set_margin
from newProfileWindow import NewProfileWindow
from SimpleDropDown import SimpleDropDown

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
gi.require_version("Gio", "2.0")
from gi.repository import Gtk, Adw, Gio
from gi.repository import GObject as gobject


def formatProfiles(profiles):
    out = ""
    for profile in profiles:
        out = out + "<b>@" + str(profile.id) + " - " + profile.name + "</b>\n"
        for dev in profile.devices:
            out = out + " " + dev
        out = out + "\n\n"
    return out


def splitArray(arr):
    splitIndex = len(arr) // 2
    while splitIndex < len(arr) and (
        arr[splitIndex] != "\n" or arr[splitIndex + 1] != "\n"
    ):
        splitIndex += 1

    outLeft = arr[:splitIndex]
    outRight = arr[splitIndex + 2 :]

    return outLeft, outRight


def formatDevices(devices):
    out = ""
    for dev in devices:
        conn = devices[dev]
        out = out + "<b>@" + dev + "</b>\n"

        if type(conn) != list:
            conn = [conn]

        lastItem = conn[-1]

        for port, connDev in conn:
            if (port, connDev) == lastItem:
                out = out + "  └─ Eth" + port + " ── " + connDev + "\n\n"
            else:
                out = out + "  ├─ Eth" + port + " ── " + connDev + "\n"

    return out


def formatActiveSlice(profile, devices, switchConf):
    out = ""
    if profile == None or switchConf == None:
        out = out + "No slice has been selected"
    else:
        for el in profile.devices:
            tempDev = {el: []}
            if el in switchConf:
                usedPorts = []
                for port, _ in switchConf[el]:
                    usedPorts.append(port)

                for port, conn in devices[el]:
                    if port in usedPorts:
                        tempDev[el].append((port, conn))
                out = out + formatDevices(tempDev)

            else:
                tempDev[el] = devices[el]
                out = out + formatDevices(tempDev)
    return out


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

        viewStack.add_titled(
            self.buildWrapper(self.getNetworkView()), "netView", "network view"
        )
        viewStack.add_titled(
            self.buildWrapper(self.getActiveSlicesView()),
            "slicesView",
            "active slices view",
        )
        viewStack.add_titled(
            self.buildWrapper(self.getProfilesView()), "profView", "profiles view"
        )

        viewSwitcher.set_stack(viewStack)

        self.set_child(body)
        body.append(viewSwitcher)
        body.append(viewStack)

    def buildWrapper(self, body):
        out = Gtk.Box()
        set_margin(out, 25)
        out.set_hexpand(True)
        out.set_vexpand(True)

        lSep = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)
        rSep = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)

        out.append(lSep)
        out.append(body)
        out.append(rSep)

        return out

    def getNetworkView(self):
        body = Gtk.Box()

        leftText, rightText = splitArray(formatDevices(self.slicer.topology.devices))

        networkTextLeft = Gtk.Label(valign=Gtk.Align.START, hexpand=True)
        networkTextLeft.set_markup(leftText)

        networkTextRight = Gtk.Label(valign=Gtk.Align.START, hexpand=True)
        networkTextRight.set_markup(rightText)

        body.append(networkTextLeft)
        body.append(networkTextRight)

        return body

    def getActiveSlicesView(self):
        body = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, hexpand=True)
        set_margin(body, 20)

        activeSliceLabel = Gtk.Label(
            hexpand=True, halign=Gtk.Align.START, margin_start=5
        )
        activeSliceLabel.set_markup("<b>Active slice:</b>")

        profilesList = []
        for profile in self.slicer.profiles:
            profilesList.append(profile.name)

        sliceSelector = SimpleDropDown(profilesList)
        sliceSelector.set_hexpand(True)
        sliceSelector.set_margin_top(15)
        sliceSelector.set_margin_bottom(15)

        descriptorLbl = Gtk.Label(
            hexpand=True, halign=Gtk.Align.START, valign=Gtk.Align.START
        )
        descriptorLbl.set_markup("<b>Descriptor:</b>")

        descriptorBox = Gtk.Box(hexpand=True, orientation=Gtk.Orientation.HORIZONTAL)
        set_margin(descriptorBox, 5)

        activeSliceDescriptorLeft = Gtk.Label(
            hexpand=True, halign=Gtk.Align.START, valign=Gtk.Align.START
        )
        activeSliceDescriptorRight = Gtk.Label(
            hexpand=True, halign=Gtk.Align.START, valign=Gtk.Align.START
        )

        leftText, rightText = splitArray(
            formatActiveSlice(
                self.slicer.profiles[self.slicer.sliceActive],
                self.slicer.topology.devices,
                self.slicer.topology.activeConfiguration,
            )
        )
        activeSliceDescriptorLeft.set_markup(leftText)
        activeSliceDescriptorRight.set_markup(rightText)

        sliceSelector.connect(
            "dropDownElementSelected",
            self.updateActiveSlice,
            activeSliceDescriptorLeft,
            activeSliceDescriptorRight,
        )

        body.append(activeSliceLabel)
        body.append(sliceSelector)
        body.append(descriptorLbl)
        descriptorBox.append(activeSliceDescriptorLeft)
        descriptorBox.append(activeSliceDescriptorRight)
        body.append(descriptorBox)

        return body

    def updateActiveSlice(self, dropdown, leftLabel, rightLabel):
        self.slicer.toggleProfile(dropdown.get_selected())

        leftText, rightText = splitArray(
            formatActiveSlice(
                self.slicer.profiles[self.slicer.sliceActive],
                self.slicer.topology.devices,
                self.slicer.topology.activeConfiguration,
            )
        )
        leftLabel.set_markup(leftText)
        rightLabel.set_markup(rightText)

    def getProfilesView(self):
        body = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        body.set_hexpand(True)
        body.set_vexpand(True)

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

        return body

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
