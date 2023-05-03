import gettext

import gi

import rthemelib

import RtW

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, Gio, Gdk, Graphene

ACCENT_SUPPORTED_THEMES = ["adwaita", "risi", "classic"]

ACCENT_BUTTON_CSS = """
.accent-button {
    margin: 3px;
    padding: 0;
    background: transparent;
    min-width: 24px;
    min-height: 24px;
}

.accent-button:checked {
    box-shadow: 0 0 0 3px @card_fg_color;
}

.accent-button > widget {
    border-radius: 9999px;
}
"""

colors = {
    "main": "#3584e4",
    "teal": "#277779",
    "green": "#26a269",
    "yellow": "#cd9309",
    "orange": "#e66100",
    "red": "#e01b24",
    "pink": "#D34166",
    "purple": "#9141ac",
    "brown": "#865e3c",
    "grey": "#485a6c",
}

rtheme_settings = Gio.Settings.new("io.risi.rtheme")
_ = gettext.gettext


def load_accent_css():
    css_provider = Gtk.CssProvider()
    css_provider.load_from_data(ACCENT_BUTTON_CSS, -1)
    Gtk.StyleContext.add_provider_for_display(
        Gdk.Display.get_default(),
        css_provider,
        Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
    )


class ColorButton(Gtk.ToggleButton):
    def __init__(self, color, last_button):
        super().__init__()
        self.color = color
        self.set_vexpand(False)
        self.set_hexpand(False)
        self.set_overflow(True)
        self.add_css_class("accent-button")
        self.add_css_class("circular")
        self.set_child(CcAccentColour(colors[self.color]))
        rtheme_settings.connect("changed::variant-name", self.settings_changed)
        self.connect("toggled", self.toggled)
        self.set_active(self.color == rtheme_settings.get_string("variant-name"))

        tooltip_text = self.color.capitalize()
        if self.color == "main":
            tooltip_text = "Blue"
        self.set_tooltip_text(_(tooltip_text))

        if last_button is not None:
            self.set_group(last_button)

    def toggled(self, state):
        if self.get_active():
            rtheme_settings.set_string("variant-name", self.color)

    def settings_changed(self, settings, key):
        if key == "variant-name":
            self.set_active(self.color == settings.get_string("variant-name"))


class CcAccentColour(Gtk.Widget):
    _colour = ""

    def __init__(self, colour, **kwargs):
        super().__init__(**kwargs)
        self.set_layout_manager(Gtk.BinLayout())
        self._colour = colour

    def do_snapshot(self, snapshot):
        width = self.get_width() * 2
        height = self.get_height() * 2
        rect = Graphene.Rect()
        rgba = Gdk.RGBA()
        rect.init(-10, -10, width, height)
        rgba.parse(self._colour)

        snapshot.save()
        snapshot.append_color(rgba, rect)
        snapshot.restore()


class AccentRow(Adw.ActionRow):
    def __init__(self):
        super().__init__(title=_("Accent Color"))

        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        box.set_vexpand(False)
        box.set_valign(Gtk.Align.CENTER)
        last_button = None
        for color in colors:
            button = ColorButton(color, last_button)
            box.append(button)
            last_button = button

        self.add_suffix(box)


class AccentStack(Gtk.Stack):
    def __init__(self):
        super().__init__()
        self.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        self.set_transition_duration(200)

        self.accents = AccentRow()
        self.variants = RtW.DropdownRow(
            _("rTheme Variant"),
            _("Variant of the color scheme."),
            "io.risi.rtheme", "variant-name",
            RtW.DropdownItems.new_same_items([v.name for v in rthemelib.get_current_theme().variants]),
        )
        self.variants.set_activatable(False)
        self.add_child(self.accents)
        self.add_child(self.variants)
        self.set_page()

        rtheme_settings.connect("changed::theme-name", self.theme_changed)

    def theme_changed(self, settings, key):
        if key == "theme-name":
            self.variants.repopulate(
                RtW.DropdownItems.new_same_items([v.name for v in rthemelib.get_current_theme().variants])
            )
            self.set_page()

    def set_page(self):
        theme = rtheme_settings.get_string("theme-name")
        if theme in ACCENT_SUPPORTED_THEMES:
            self.set_visible_child(self.accents)
        else:
            self.set_visible_child(self.variants)
        self.variants.set_sensitive(not len(rthemelib.get_current_theme().variants) == 1)
