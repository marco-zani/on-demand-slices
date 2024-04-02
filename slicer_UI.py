import sys
import gi

from gi.repository import GObject
from slicer import Slicer, Profile
from common import set_margin, get_children, splitArray, formatDevices
from newProfileWindow import NewProfileWindow
from SimpleDropDown import SimpleDropDown
from activeSliceBox import ActiveSliceBox

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
gi.require_version("Gio", "2.0")
from gi.repository import Gtk, Adw, Gio
from gi.repository import GObject as gobject


def formatProfiles(profiles):
    out = ""
    for profile in profiles:
        out = out + "<b>@" + str(profile.id) + " - " + profile.name + "</b>"
        sliceCount = 0
        for slice in profile.slices:
            sliceCount += 1
            out = out + "\n " + "Slice #" + str(sliceCount) + ":" + "\n   Reserved percentage: " + str(slice['minBandwidth'])+ "%\n   "
            for dev in slice['devices']:
                out = out + " " + dev
        out = out + "\n\n"
    return out


class SlicerWindow(Gtk.ApplicationWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.slicer = Slicer()
        self.slicer.importTopology()
        self.slicer.sendDevices()

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

        descriptorLbl = Gtk.Label(
            hexpand=True, halign=Gtk.Align.START, valign=Gtk.Align.START
        )
        descriptorLbl.set_markup("<b>Descriptor:</b>")

        descriptorBox = Gtk.Box(hexpand=True, orientation=Gtk.Orientation.VERTICAL)
        set_margin(descriptorBox, 5)

        self.buildActiveConfUI(descriptorBox)

        dropDownBox = Gtk.Box(hexpand=True)
        self.connect("updateProfiles", self.updateDropDown, dropDownBox, descriptorBox)
        self.loadDropDown(dropDownBox, descriptorBox)

        body.append(activeSliceLabel)
        body.append(dropDownBox)
        body.append(descriptorLbl)
        body.append(descriptorBox)

        return body

    def updateActiveSlice(self, dropdown, box):
        self.slicer.toggleProfile(dropdown.get_selected())

        for child in get_children(box):
            box.remove(child)

        self.buildActiveConfUI(box)

    def buildActiveConfUI(self, box):
        sliceCount = 1
        if self.slicer.topology.activeConfiguration == None:
            label = Gtk.Label(hexpand=True)
            label.set_markup("No slice has been selected")
            box.append(label)
        else:
            for conf in self.slicer.topology.activeConfiguration:
                t = ActiveSliceBox(sliceCount, conf, self.slicer.topology.devices)
                box.append(t)
                sliceCount += 1

    def loadDropDown(self, container, outputBox):
        profilesList = []
        for profile in self.slicer.profiles:
            profilesList.append(profile.name)

        sliceSelector = SimpleDropDown(profilesList, self.slicer.sliceActive)
        sliceSelector.set_hexpand(True)
        sliceSelector.set_margin_top(15)
        sliceSelector.set_margin_bottom(15)

        sliceSelector.connect(
            "dropDownElementSelected",
            self.updateActiveSlice,
            outputBox
        )

        container.append(sliceSelector)

    def updateDropDown(self,window, container, outputBox):
        for child in get_children(container):
            container.remove(child)
        self.loadDropDown(container, outputBox)

       

    def getProfilesView(self):
        body = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        body.set_hexpand(True)
        body.set_vexpand(True)

        textBox = Gtk.Box(hexpand=True,vexpand=True, orientation=Gtk.Orientation.HORIZONTAL)
        set_margin(textBox, 35)

        profilesTextLeft = Gtk.Label(
            hexpand=True, halign=Gtk.Align.START, valign=Gtk.Align.START
        )
        profilesTextRight = Gtk.Label(
            hexpand=True, halign=Gtk.Align.START, valign=Gtk.Align.START
        )
        leftText, rightText = splitArray(formatProfiles(self.slicer.profiles))
        profilesTextLeft.set_markup(leftText)
        profilesTextRight.set_markup(rightText)

        self.connect(
            "updateProfiles", self.updateProfiles, profilesTextLeft, profilesTextRight
        )

        addProfileBtn = Gtk.Button(label="Create new profile")
        set_margin(addProfileBtn, 35)
        addProfileBtn.set_hexpand(True)
        addProfileBtn.connect(
            "clicked", self.spawnNewProfileWidget, self.slicer.topology.devices
        )

        textBox.append(profilesTextLeft)
        textBox.append(profilesTextRight)
        body.append(textBox)
        body.append(addProfileBtn)

        return body

    def updateProfiles(self, window, leftLabel, rightLabel):
        leftText, rightText = splitArray(formatProfiles(self.slicer.profiles))
        leftLabel.set_markup(leftText)
        rightLabel.set_markup(rightText)

    def spawnNewProfileWidget(self, button, devices):
        npw = NewProfileWindow(devices, self.slicer.profiles[-1].id + 1)
        npw.set_modal(self)
        npw.present()

        npw.connect("newProfileWindowClosed", self.newProfileWindowsClosed)

    def newProfileWindowsClosed(self, npw):
        if npw.out.slices != []:
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
