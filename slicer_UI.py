import sys
import gi
import json
from multiprocessing import Process
import time
from slicer import Slicer, Profile

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw

def set_margin(obj, size):
    obj.set_margin_top(size)
    obj.set_margin_bottom(size)
    obj.set_margin_start(size)
    obj.set_margin_end(size)

def formatProfiles(profiles):
    out = ""
    for profile in profiles:
        out = out + "<b>@" + str(profile.id)+" - "+profile.name+"</b>\n"
        for dev in profile.devices:
            out = out + " " + dev
        out = out + "\n\n"
    return out


class Window(Gtk.ApplicationWindow):
    
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.slicer = Slicer()

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
        viewStack.add_titled(self.getActiveSlicesView(), "slicesView", "active slices view" )
        viewStack.add_titled(self.getProfilesView(),  "profView","profiles view")
        

        viewSwitcher.set_stack(viewStack)

        self.set_child(body)
        body.append(viewSwitcher)
        body.append(viewStack)

    def getNetworkView(self):
        out = Gtk.Box()
        set_margin(out, 25)
        out.set_hexpand(True)
        out.set_vexpand(True)

        lSep = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)
        rSep = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)

        networkText = Gtk.Label(label="network view")
        networkText.set_hexpand(True)

        out.append(lSep)
        out.append(networkText)
        out.append(rSep)

        return out
    
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

        addProfileBtn = Gtk.Button(label="Create new profile")
        set_margin(addProfileBtn, 35)
        addProfileBtn.set_hexpand(True)
        #TODO add click function

        body.append(profilesText)
        body.append(addProfileBtn)

        out.append(lSep)
        out.append(body)
        out.append(rSep)

        return out



class visualizer(Adw.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connect("activate", self.on_activate)

    def on_activate(self, app):
        self.win = Window(application=app)
        self.win.present()

app = visualizer(application_id="com.OnDemandSlices.GTKSlicer")

app.run(sys.argv)