import gi
from src.common import set_margin

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

class NewSliceBox(Gtk.Box):
    def __init__(self, id, devices, selectable, defaultPercentage, usedPercentage, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id = id
        self.selectable = selectable
        self.buildUI(devices, defaultPercentage, usedPercentage)

    def getChecks(self, devices):
        out = []
        for dev in devices:
            check = Gtk.CheckButton(label=" "+dev)
            if not self.selectable:
                check.set_active(True)
                check.set_sensitive(False)
            out.append(check)
        return out
    
    def getPercentageBtn(self, default, available):
        adjustment = Gtk.Adjustment(value=default,
                                    lower=0,
                                    upper=available,
                                    step_increment=10,
                                    page_increment=5,
                                    page_size=0)
        out = Gtk.SpinButton(adjustment=adjustment)
        if not self.selectable:
            out.set_sensitive(False)
        set_margin(out, 5)
        return out

    def buildUI(self, devices, defaultPercentage, availablePercentage):
        self.set_orientation(Gtk.Orientation.VERTICAL)
        sliceName = Gtk.Label(hexpand=True)
        sliceName.set_markup("<b>Slice #" + str(self.id)+"</b>")

        percentageBox = Gtk.Box(hexpand=True)
        set_margin(percentageBox, 5)
        percentageLbl = Gtk.Label(label="Min bandwidth (%): ")

        percentageBtnBox = Gtk.Box(hexpand=True, halign=Gtk.Align.CENTER)
        self.percentageBtn = self.getPercentageBtn(defaultPercentage, availablePercentage)
        percentageBtnBox.append(self.percentageBtn)

        checksBox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,hexpand=True)
        leftChecksBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, halign=Gtk.Align.CENTER,hexpand=True)
        rightChecksBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, halign=Gtk.Align.CENTER,hexpand=True)
        self.checks = self.getChecks(devices)

        for el in self.checks[:len(self.checks)//2]:
            leftChecksBox.append(el)
        for el in self.checks[len(self.checks)//2:]:
            rightChecksBox.append(el)
        
        self.append(sliceName)
        percentageBox.append(percentageLbl)
        percentageBox.append(percentageBtnBox)
        self.append(percentageBox)
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
    
    def getPercentage(self):
        return self.percentageBtn.get_value()