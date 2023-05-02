import gi
import gettext
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw, Gio, Pango, Gdk

_ = gettext.gettext

ACCENT_BUTTON_CSS = b"""
.accent-button {
  border-radius: 9999px;
  padding: 3px;
  background: transparent;
  min-width: 24px;
  min-height: 24px;
}

.accent-button:checked {
  box-shadow: 0 0 0 3px @accent_bg_color;
}

.accent-button > widget {
  border-radius: 9999px;
}
"""


class SettingObject:
    def __init__(self, schema: str, key: str):
        self.schema = schema
        self.key = key
        self.settings = Gio.Settings.new(schema)
        self.settings.connect("changed::" + key, self.on_setting_changed)

    def on_setting_changed(self, *args):
        raise NotImplementedError("on_setting_changed not implemented by subclass")


class ActionRow(SettingObject, Adw.ActionRow):
    def __init__(self, title: str, subtitle: str, schema: str, key: str):
        SettingObject.__init__(self, schema, key)
        Adw.ActionRow.__init__(self, title=_(title), subtitle=_(subtitle))
        self.set_activatable(True)
        self.set_selectable(False)

    def set_main_widget(self, widget: Gtk.Widget):
        self.add_suffix(widget)
        self.set_activatable_widget(widget)

    def on_setting_changed(self, *args):
        raise NotImplementedError("on_setting_changed not implemented by subclass")


class SwitchRow(ActionRow):
    def __init__(self, title: str, subtitle: str | None, schema: str, key: str):
        super().__init__(title, subtitle, schema, key)
        self.switch = Gtk.Switch()
        self.switch.set_valign(Gtk.Align.CENTER)
        self.switch.connect("state-set", self.on_switch_set)
        self.set_main_widget(self.switch)

    def on_setting_changed(self, *args):
        self.switch.set_state(self.settings.get_boolean(self.key))

    def on_switch_set(self, switch, state):
        if state != self.settings.get_boolean(self.key):
            self.settings.set_boolean(self.key, state)


class DropdownItems:
    def __init__(self, user_items: list, backend_items: list, item_descriptions=None):
        if item_descriptions is None:
            item_descriptions = []
        self.user_items = user_items
        self.translated_items = [_(item) for item in user_items]
        self.backend_items = backend_items
        self.item_descriptions = item_descriptions
        self.amount = len(user_items)

        if self.amount != len(backend_items):
            raise ValueError("The amount of user items and backend items must be the same!")
        if self.amount != len(item_descriptions) and item_descriptions is not None and len(item_descriptions) != 0:
            raise ValueError("The amount of user items and item descriptions must be the same!")
        if self.amount == 0:
            raise ValueError("The amount of user items must be at least 1!")

    @classmethod
    def new_same_items(cls, items: list, item_descriptions=None):
        if item_descriptions is None:
            return cls(items, items)
        else:
            return cls(items, items, item_descriptions)

    @classmethod
    def new_lowercase_items(cls, items: list, item_descriptions=None):
        if item_descriptions is None:
            print(items, [item.lower() for item in items])
            return cls(items, [item.lower() for item in items])
        else:
            return cls(items, [item.lower() for item in items], item_descriptions)


class DropdownRow(ActionRow):
    def __init__(self, title: str, subtitle: str | None, schema: str, key: str, items: DropdownItems):
        super().__init__(title, subtitle, schema, key)
        self.items = items
        self.error = False

        self.dropdown = Gtk.DropDown.new_from_strings(self.items.translated_items)
        self.errorless_model = self.dropdown.get_model()
        self.dropdown.set_vexpand(False)
        self.dropdown.set_valign(Gtk.Align.CENTER)
        self.set_main_widget(self.dropdown)
        self.select_item()
        self.dropdown.connect("notify::selected", self.on_dropdown_changed)

    def on_setting_changed(self, *args):
        self.select_item()

    def set_error(self, error: bool):
        self.error = error
        if error:
            self.add_css_class("error")
        else:
            self.remove_css_class("error")
            self.dropdown.set_model(self.errorless_model)

    def select_item(self):
        try:
            if self.error:
                self.set_error(False)

            new_id = self.items.backend_items.index(self.settings.get_string(self.key))
        except ValueError:
            self.set_error(True)
            new_list = self.errorless_model
            new_list.append((self.settings.get_string(self.key)))
            self.dropdown.set_model(new_list)

            new_id = new_list.get_n_items() - 1
        if new_id != self.dropdown.get_selected():
            self.dropdown.set_selected(new_id)

    def on_dropdown_changed(self, dropdown, selected_item):
        try:
            value = self.items.backend_items[self.dropdown.get_selected()]
        except IndexError:
            value = self.dropdown.get_model().get_string(self.dropdown.get_selected())
        if value != self.settings.get_string(self.key):
            self.settings.set_string(self.key, value)


class DetailedDropdownRow(SettingObject, Adw.ExpanderRow):
    def __init__(self, title: str, schema: str, key: str, items: DropdownItems):
        SettingObject.__init__(self, schema, key)
        Adw.ExpanderRow.__init__(self)
        self.set_title(title)
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
        return None

    def item_clicked(self, item):
        self.settings.set_string(self.key, item.backend_item)
        self.set_subtitle(item.get_title())

    def on_setting_changed(self, *args):
        setting_value = self.settings.get_string(self.key)
        for item in self.item_widgets:
            if item.backend_item == setting_value:
                item.radio.set_active(True)
                self.set_subtitle(item.get_title())
                self.remove_css_class("error")
                return
        self.add_css_class("error")

    def check_error(self):
        if self.get_selected() is None:
            self.add_css_class("error")
        else:
            self.remove_css_class("error")

    @classmethod
    def new_from_items(cls, title: str, schema: str, key: str, items: DropdownItems):
        dropdown_row = cls(title, schema, key, items)
        for i in range(items.amount):
            last_item = None
            if i != 0:
                last_item = dropdown_row.item_widgets[i - 1]
            if items.item_descriptions is None:
                raise ValueError("DetailedDropdownRow Items must have descriptions!")
            item = DetailedDropdownItem(items.user_items[i], items.item_descriptions[i], items.backend_items[i],
                                        dropdown_row, last_item)
            dropdown_row.add_item(item)
        dropdown_row.check_error()
        return dropdown_row


class DetailedDropdownItem(Adw.ActionRow):
    def __init__(self, title, subtitle, backend_item, dropdown_row, last_widget):
        Adw.ActionRow.__init__(self, title=title, subtitle=subtitle)
        self.backend_item = backend_item
        self.dropdown_row = dropdown_row

        self.radio = Gtk.CheckButton()
        self.radio.set_halign(Gtk.Align.END)
        if last_widget is not None:
            self.radio.set_group(last_widget.radio)
        if dropdown_row.settings.get_string(dropdown_row.key) == self.backend_item:
            self.radio.set_active(True)
            dropdown_row.set_subtitle(title)
        self.add_suffix(self.radio)
        self.set_activatable(True)
        self.set_activatable_widget(self.radio)

        self.connect("activated", self.on_clicked)

    def on_clicked(self, widget):
        self.dropdown_row.item_clicked(self)


class SpinButtonRow(ActionRow):
    def __init__(self, title: str, subtitle: str | None, schema: str, key: str, value_type: str, minimum: int,
                 maximum: int, step: int, percent: bool):
        super().__init__(title, subtitle, schema, key)
        self.percent = percent
        if percent:
            self.spin_button = Gtk.SpinButton.new_with_range(minimum * 100, maximum * 100, step * 100)
        else:
            self.spin_button = Gtk.SpinButton.new_with_range(minimum, maximum, step)
        self.add_suffix(self.spin_button)

        self.value_type = value_type
        # Gets the value type because it could be any of these 3 values
        if self.value_type == "int":
            self.value = self.setting.get_int(key)
        elif self.value_type == "uint":
            self.value = self.setting.get_uint(key)
        elif self.value_type == "double":
            self.value = self.setting.get_double(key)
        if self.percent is True:
            self.value *= 100
        self.spin_button.set_value(self.value)

        self.spin_button.connect("value-changed", self.value_changed)
        self.set_main_widget(self.spin_button)

    def value_changed(self, spin_button):
        self.value = self.spin_button.get_value()
        if self.percent is True:
            self.value /= 100

        if self.value_type == "int":
            self.setting.set_int(self.key, self.value)
        elif self.value_type == "uint":
            self.setting.set_uint(self.key, self.value)
        elif self.value_type == "double":
            self.setting.set_double(self.key, self.value)

    def on_setting_changed(self, *args):
        if self.setting.get_double(self.key) != self.spin_button.get_value():
            new_value = self.setting.get_double(self.key)
            if self.percent:
                new_value *= 100
            self.spin_button.set_value(new_value)


# TODO: Implement this on Fedora 38
# class FontRow(ActionRow):
#     def __init__(self, title: str, subtitle: str, schema: str, key: str):
#         super().__init__(title, subtitle, schema, key)
#         self.font_dialog = Gtk.FontChooserDialog()
#         self.font_dialog.set_title(title)
#
#
#         self.font_button = Gtk.FontDialogButton()
#         self.font_button.set_use_font(True)
#         self.font_button.set_use_size(True)
#
#     def set_font(self, font):
#         map = Pango.FontMap.
#         self.font_dialog.set_font_map(
#             Pango.FontMap.get_family(font)
#         )
#         Pango.FontMap.load_font(font)
