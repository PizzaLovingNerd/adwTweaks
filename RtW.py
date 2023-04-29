import gi
import gettext
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw, Gio

# For code optimization by avoiding duplicate settings classes
# Adds org.gnome.shell because the extension classes need it and
# org.gnome.desktop.interface for accent colors.
known_schemas = {}
_ = gettext.gettext


class SettingObject:
    def __init__(self, schema: str, key: str):
        self.schema = schema
        self.key = key
        self.settings = Gio.Settings.new(schema)
        self.settings.connect("changed::" + key, self.on_setting_changed)

    def on_setting_changed(self, *args):
        raise NotImplementedError("on_setting_changed not implemented by subclass")


class ActionRow(Adw.ActionRow, SettingObject):
    def __init__(self, title: str, subtitle: str, schema: str, key: str):
        Adw.ActionRow.__init__(self, title=_(title), subtitle=_(subtitle))
        SettingObject.__init__(self, schema, key)
        self.set_activatable(True)
        self.set_selectable(False)

    def set_main_widget(self, widget: Gtk.Widget):
        self.add_suffix(widget)
        self.set_activatable_widget(widget)

    def on_setting_changed(self, *args):
        raise NotImplementedError("on_setting_changed not implemented by subclass")


class SwitchRow(ActionRow):
    def __init__(self, title: str, subtitle: str, schema: str, key: str):
        super().__init__(title, subtitle, schema, key)
        self.switch = Gtk.Switch()
        self.switch.connect("state-set", self.on_switch_set)
        self.set_main_widget(self.switch)

    def on_setting_changed(self, *args):
        self.set_active(self.settings.get_boolean(self.key))

    def on_switch_set(self, switch, state):
        self.settings.set_boolean(self.key, state)


class DropdownItems:
    def __init__(self, user_items: list, backend_items: list, item_descriptions=None):
        if item_descriptions is None:
            item_descriptions = []
        self.user_items = user_items
        self.translated_items = [_(item) for item in user_items]
        self.backend_items = backend_items
        self.item_descriptions = item_descriptions

    @classmethod
    def new_same_items(cls, items: list, item_descriptions=None):
        if item_descriptions is None:
            return cls(items, items)
        else:
            return cls(items, items, item_descriptions)

    @classmethod
    def new_lowercase_items(cls, items: list, item_descriptions=None):
        if item_descriptions is None:
            return cls(items, [item.lower() for item in items])
        else:
            return cls(items, [item.lower() for item in items], item_descriptions)


class DropdownRow(ActionRow):
    def __init__(self, title: str, subtitle: str, schema: str, key: str, items: DropdownItems):
        super().__init__(title, subtitle, schema, key)
        self.add_suffix(self.dropdown)
        self.items = items

        self.dropdown = Gtk.DropDown.new_from_strings(self.items.translated_items)
        self.dropdown.connect("changed", self.on_dropdown_changed)
        self.set_main_widget(self.dropdown)

    def on_setting_changed(self, *args):
        try:
            new_id = self.items.backend_items.index(self.settings.get_string(self.key))
            if new_id != self.dropdown.get_selected():
                self.dropdown.set_selected(new_id)
            self.remove_css_class("error")
        except ValueError:
            self.dropdown.set_selected(-1)
            self.add_css_class("error")

    def on_dropdown_changed(self, dropdown):
        self.settings.set_string(self.key, self.items.backend_items[dropdown.get_selected()])


class DetailedDropdownRow(Adw.ExpanderRow, SettingObject):
    def __init__(self, title: str, schema: str, key: str, items: DropdownItems):
        Adw.ExpanderRow.__init__(self, title)
        SettingObject.__init__(self, schema, key)
        self.items = items
        self.item_widgets = []
        self.radio_group = None

    def add_item(self, item):
        self.add_row(item)
        self.item_widgets.append(item)

    def get_selected(self):
        for item in self.item_widgets:
            if item.radio.get_active():
                return item

    def on_setting_changed(self, *args):
        pass


class DetailedDropdownItem(Adw.ActionRow):
    def __init__(self, title, subtitle, backend_item, dropdown_row, last_widget):
        super().__init__(self, title=title, subtitle=subtitle)
        self.backend_item = backend_item
        self.dropdown_row = dropdown_row

        self.radio = Gtk.CheckButton()
        if last_widget is not None:
            self.set_group(last_widget.radio)
        self.add_suffix(self.radio)
