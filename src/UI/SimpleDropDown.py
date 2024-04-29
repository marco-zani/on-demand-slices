import gi

gi.require_version('Adw', '1')
gi.require_version('Gtk', '4.0')

from gi.repository import Gio, GObject, Gtk

class Entry(GObject.Object):
    __gtype_name__ = 'Widget'

    def __init__(self, name):
        super().__init__()
        self._name = name

    @GObject.Property
    def name(self):
        return self._name

class SimpleDropDown(Gtk.DropDown):
    def __init__(self, list, selected):

        ## Create model
        self.model = Gio.ListStore(item_type=Entry)

        ## Populate it
        for item in list:
            self.model.append(Entry(name=item))

        ## Create factory
        factory = Gtk.SignalListItemFactory()
        factory.connect("setup", self._on_factory_widget_setup)
        factory.connect("bind", self._on_factory_widget_bind)

        super().__init__(model=self.model, factory=factory)
    
        self.connect("notify::selected-item", self._on_selected_widget)
        self.set_selected(selected)
    
    def _on_factory_widget_setup(self, factory, list_item):
        box = Gtk.Box(spacing=6, orientation=Gtk.Orientation.HORIZONTAL)
        label = Gtk.Label()
        box.append(label)
        list_item.set_child(box)

    def _on_factory_widget_bind(self, factory, list_item):
        box = list_item.get_child()
        label = box.get_first_child()
        widget = list_item.get_item()
        label.set_text(widget.name)

    def _on_selected_widget(self, dropdown, data):
        self.emit("dropDownElementSelected")


GObject.type_register(SimpleDropDown)
GObject.signal_new("dropDownElementSelected", SimpleDropDown, GObject.SignalFlags.RUN_FIRST,
                   GObject.TYPE_NONE, ())
        