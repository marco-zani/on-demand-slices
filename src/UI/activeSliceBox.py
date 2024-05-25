import gi

from src.common import set_margin, splitArray, formatDevices

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk


class ActiveSliceBox(Gtk.Box):
    def __init__(self, id, conf, devices, perc,*args, **kwargs):
        super().__init__(*args, **kwargs)

        self.set_orientation(Gtk.Orientation.VERTICAL)
        set_margin(self, 10)

        sliceLabel = Gtk.Label(hexpand=True, halign=Gtk.Align.START, margin_bottom=5)
        sliceLabel.set_markup("<b>Slice #" + str(id) + ":</b>\nMax bandwidth: " + str(perc)
                               + "%")

        textBox = Gtk.Box(hexpand=True)

        leftLabel = Gtk.Label(
            hexpand=True, halign=Gtk.Align.START, valign=Gtk.Align.START
        )
        rightLabel = Gtk.Label(
            hexpand=True, halign=Gtk.Align.START, valign=Gtk.Align.START
        )

        leftText, rightText = splitArray(self.formatActiveSlice(devices, conf))
        leftLabel.set_markup(leftText)
        rightLabel.set_markup(rightText)

        textBox.append(leftLabel)
        textBox.append(rightLabel)
        self.append(sliceLabel)
        self.append(textBox)

    def formatActiveSlice(self, devices, conf):
        out = ""
        usedHosts, switchConf = conf
        allDev = usedHosts
        for switch in switchConf:
            allDev.append(switch)
        for dev in allDev:
            tempDev = {dev: []}
            if dev in switchConf:
                usedPorts = []
                for port, _ in switchConf[dev]:
                    usedPorts.append(port)

                for port, conn in devices[dev]:
                    for usedPort, _ in usedPorts:
                        if port == usedPort:
                            tempDev[dev].append((port, conn))
                out = out + formatDevices(tempDev)
            else:
                tempDev[dev] = devices[dev]
                out = out + formatDevices(tempDev)
        return out

