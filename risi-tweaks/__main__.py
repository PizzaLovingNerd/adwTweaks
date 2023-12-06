import gi
import gettext
import RtW
import RtU

_ = gettext.gettext

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw


class Application(Adw.Application):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, application_id="io.risi.Tweaks", **kwargs)
        self.window = TweaksWindow()

    def do_activate(self):
        self.window.set_application(self)
        self.window.present()


class TweaksWindow(Adw.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_title(_("adwTeaks"))
        self.set_default_size(800, 600)
        self.set_icon_name("io.risi.Tweaks")

        self.window_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_content(self.window_box)

        self.header = Adw.HeaderBar()
        self.window_box.append(self.header)

        self.main_stack = Adw.ViewStack()
        self.window_box.append(self.main_stack)

        self.main_stack_switcher = Adw.ViewSwitcherTitle()
        self.main_stack_switcher.set_stack(self.main_stack)
        self.main_stack_switcher.set_title(_("risiTweaks"))
        self.header.set_title_widget(self.main_stack_switcher)

        # Appearance Page
        self.appearance_page = Adw.PreferencesPage()
        self.main_stack.add_titled_with_icon(self.appearance_page, "appearance_page", _("Appearance"),
                                             "preferences-desktop-wallpaper-symbolic")


        # Other Theming Group
        self.other_theming_group = Adw.PreferencesGroup()
        self.other_theming_group.set_title(_("Theming"))
        self.appearance_page.add(self.other_theming_group)
        self.rtheme_group.add(
            RtW.DropdownRow(
                _("Theme Styling"),
                _("This is the same as the light and dark theme options in GNOME Control Center."),
                "org.gnome.desktop.interface", "color-scheme",
                RtW.DropdownItems(
                    ["Default", "Dark"],
                    ["default", "prefer-dark"],
                ),
            )
        )
        self.other_theming_group.add(
            RtW.DropdownRow(
                _("Legacy GTK3/GTK4 Theme"),
                _("This is the theme used by legacy applications that don't use Libadwaita.\n\nWARNING: "
                  "Changing this away from adw-gtk3/adw-gtk3-dark will remove rTheme support for non-Libadwaita apps."),
                "org.gnome.desktop.interface", "gtk-theme",
                RtW.DropdownItems.new_same_items(
                    RtU.get_gtk_themes()
                )
            )
        )
        self.other_theming_group.add(
            RtW.DropdownRow(
                _("Icon Theme"),
                _("This is the icon theme used by your system."),
                "org.gnome.desktop.interface", "icon-theme",
                RtW.DropdownItems.new_same_items(
                    RtU.get_icon_themes(),
                )
            )
        )
        self.other_theming_group.add(
            RtW.DropdownRow(
                _("Cursor Theme"),
                _("This is the theme used for your mouse pointer."),
                "org.gnome.desktop.interface", "cursor-theme",
                RtW.DropdownItems.new_same_items(
                    RtU.get_cursor_themes()
                )
            )
        )

        # Fonts Group
        self.fonts_group = Adw.PreferencesGroup()
        self.fonts_group.set_title(_("Fonts"))
        self.appearance_page.add(self.fonts_group)
        self.fonts_group.add(
            RtW.FontRow(
                _("Interface Font"),
                _("This is the primary font used by your system."),
                "org.gnome.desktop.interface", "font-name",
            )
        )
        self.fonts_group.add(
            RtW.FontRow(
                _("Document Font"),
                _("Font used for viewing documents."),
                "org.gnome.desktop.interface", "document-font-name",
            )
        )
        self.fonts_group.add(
            RtW.FontRow(
                _("Monospace Font"),
                _("Font used when all the letters need to be the same size. For example, terminals and text editors."),
                "org.gnome.desktop.interface", "monospace-font-name",
            )
        )
        self.fonts_group.add(
            RtW.FontRow(
                _("Legacy Titlebar Font"),
                _("Font used in the titlebar for apps that don't use header bars (old Gtk apps, non-Gtk apps)."),
                "org.gnome.desktop.wm.preferences", "titlebar-font",
            )
        )
        self.fonts_group.add(
            RtW.DropdownRow(
                _("Font Hinting"),
                _("Adjusts font so that it lines up with a rasterized grid."),
                "org.gnome.desktop.interface", "font-hinting",
                RtW.DropdownItems.new_lowercase_items(
                    ["None", "Slight", "Medium", "Full"]
                )
            )
        )
        self.fonts_group.add(
            RtW.DropdownRow(
                _("Font Antialiasing"),
                _("The method of antialiasing used."),
                "org.gnome.desktop.interface", "font-antialiasing",
                RtW.DropdownItems(
                    ["None", "Subpixel (for LCD Screens)", "Standard (Grayscale)"],
                    ["none", "rgba", "grayscale"]
                )
            )
        )
        self.fonts_group.add(
            RtW.SpinButtonRow(
                _("Font Scaling Factor"),
                _("The scaling factor for font sizes."),
                "org.gnome.desktop.interface", "text-scaling-factor",
                "double", 0.5, 3, 0.05, True
            )
        )

        # Layout Page
        self.layout_page = Adw.PreferencesPage()
        self.main_stack.add_titled_with_icon(self.layout_page, "layout_page", _("Layout"),
                                             "preferences-desktop-display-symbolic")

        # Layout Group
        self.layout_group = Adw.PreferencesGroup()
        self.layout_group.set_title(_("Top Bar"))
        self.layout_page.add(self.layout_group)
        self.layout_group.add(
            RtW.SwitchRow(
                _("Allow Audio Volume Above 100%"),
                _("This allows you to go above 100% volume in the top bar.\n\nWARNING: this may have an impact on audio "
                  "quality, and potentially could damage your audio hardware."),
                "org.gnome.desktop.sound", "allow-volume-above-100-percent",
            )
        )
        self.layout_group.add(
            RtW.SwitchRow(
                _("Show Battery Percentage"),
                _("This shows the battery percentage in the top bar. This is only useful if you have a laptop."),
                "org.gnome.desktop.interface", "show-battery-percentage",
            )
        )

        # Layout Group
        self.clock_group = Adw.PreferencesGroup()
        self.clock_group.set_title(_("Top Bar Clock"))
        self.layout_page.add(self.clock_group)
        self.clock_group.add(
            RtW.SwitchRow(
                _("Show Weekday on Clock"),
                _("Shows the day of the week on the top bar next to the clock."),
                "org.gnome.desktop.interface", "clock-show-weekday",
            )
        )
        self.clock_group.add(
            RtW.SwitchRow(
                _("Show Date on Clock"),
                _("Show the date on the top bar."),
                "org.gnome.desktop.interface", "clock-show-date",
            )
        )
        self.clock_group.add(
            RtW.SwitchRow(
                _("Show Seconds on Clock"),
                _("Show seconds in the top bar's clock."),
                "org.gnome.desktop.interface", "clock-show-seconds",
            )
        )
        self.clock_group.add(
            RtW.SwitchRow(
                _("Show Week Numbers on Calendar"),
                _("Show week numbers in the calendar when you click on the top bar's clock."),
                "org.gnome.desktop.interface", "show-weekdate",
            )
        )

        # Window Group
        self.window_group = Adw.PreferencesGroup()
        self.window_group.set_title(_("Windows"))
        self.layout_page.add(self.window_group)
        self.window_group.add(
            RtW.SwitchRow(
                _("Attach Modal Dialogs"),
                _("Decides whether dialogs that belong to the window can be moved separately to the parent window."),
                "org.gnome.mutter", "attach-modal-dialogs",
            )
        )
        self.window_group.add(
            RtW.SwitchRow(
                _("Center New Windows"),
                _("Whether or not to start new windows in the center of the screen."),
                "org.gnome.mutter", "center-new-windows",
            )
        )
        self.window_group.add(
            RtW.DropdownRow(
                _("Window Action Key"),
                _("Holding this key basically treats the whole window like the titlebar and allows moving it and "
                  "right clicking it for options."),
                "org.gnome.desktop.wm.preferences", "mouse-button-modifier",
                RtW.DropdownItems(
                    ["None", "Alt", "Super (Default)"],
                    ["none", "<Alt>", "<Super>"],
                )
            )
        )
        self.window_group.add(
            RtW.DropdownRow(
                _("Titlebar Button Layout"),
                _("This is the layout of the titlebar buttons."),
                "org.gnome.desktop.wm.preferences", "button-layout",
                RtW.DropdownItems(
                    [
                        "risiOS Left", "risiOS Right (Default)", "elementary", "elementary inverted",
                        "elementary with minimize", "elementary with minimize inverted", "GNOME Left", "GNOME Right",
                        "macOS Left", "macOS Right", "Windows Left", "Windows Right"
                    ],
                    [
                        "minimize,close:appmenu", "appmenu:minimize,close", "close,appmenu:maximize",
                        "maximize,appmenu:close", "close,appmenu:minimize", "minimize,appmenu:close",
                        "close:appmenu", "appmenu:close", "close,minimize,maximize:appmenu",
                        "appmenu:maximize,minimize,close", "close,maximize,minimize:appmenu",
                        "appmenu:minimize,maximize,close",
                    ],
                )
            )
        )

        # Window Titlebar Action Group
        self.window_titlebar_action_group = Adw.PreferencesGroup()
        self.window_titlebar_action_group.set_title(_("Titlebar Actions"))
        self.window_titlebar_action_group.set_description(_(
            "These are the actions that happen when you click on the titlebar."
        ))
        self.layout_page.add(self.window_titlebar_action_group)
        self.window_titlebar_action_group.add(
            RtW.DropdownRow(
                _("Double Click Action"), None, "org.gnome.desktop.wm.preferences", "action-double-click-titlebar",
                RtW.DropdownItems(
                    ["Lower Window", "Open Menu", "Toggle Maximize", "Minimize", "Nothing"],
                    ["lower", "menu", "toggle-maximize", "minimize", "none"]
                )
            )
        )
        self.window_titlebar_action_group.add(
            RtW.DropdownRow(
                _("Middle Click Action"), None, "org.gnome.desktop.wm.preferences", "action-middle-click-titlebar",
                RtW.DropdownItems(
                    ["Lower Window", "Open Menu", "Toggle Maximize", "Minimize", "Nothing"],
                    ["lower", "menu", "toggle-maximize", "minimize", "none"]
                )
            )
        )
        self.window_titlebar_action_group.add(
            RtW.DropdownRow(
                _("Right Click Action"), None, "org.gnome.desktop.wm.preferences", "action-right-click-titlebar",
                RtW.DropdownItems(
                    ["Lower Window", "Open Menu", "Toggle Maximize", "Minimize", "Nothing"],
                    ["lower", "menu", "toggle-maximize", "minimize", "none"]
                )
            )
        )

        # Keyboard and Mouse Page
        self.keyboard_mouse_page = Adw.PreferencesPage()
        self.main_stack.add_titled_with_icon(self.keyboard_mouse_page, "keyboard_mouse_page", _("Keyboard & Mouse"),
                                             "input-keyboard-symbolic")

        # Keyboard Group
        self.keyboard_group = Adw.PreferencesGroup()
        self.keyboard_group.set_title(_("Keyboard"))
        self.keyboard_mouse_page.add(self.keyboard_group)
        self.keyboard_group.add(
            RtW.SwitchRow(
                _("Show Extended Input Sources in Settings"),
                _("Show extended input sources in GNOME Control Center's Keyboard settings."),
                "org.gnome.desktop.input-sources", "show-all-sources",
            )
        )
        self.keyboard_group.add(
            RtW.DropdownRow(
                _("Keybinding Preset (GTK Apps Only)"),
                _("This modifies some keybindings in GTK apps."),
                "org.gnome.desktop.interface", "gtk-key-theme",
                RtW.DropdownItems.new_same_items(
                    ["Default", "Emacs"],
                )
            )
        )

        # Mouse Group
        self.mouse_group = Adw.PreferencesGroup()
        self.mouse_group.set_title(_("Mouse"))
        self.keyboard_mouse_page.add(self.mouse_group)
        self.mouse_group.add(
            RtW.DetailedDropdownRow.new_from_items(
                _("Acceleration Profile"),
                "org.gnome.desktop.peripherals.mouse", "accel-profile",
                RtW.DropdownItems.new_lowercase_items(
                    [_("Flat"), _("Adaptive"), _("Default")],
                    [
                        _("No mouse acceleration. Less precise for short distances but better for things like FPS "
                          "games."),
                        _("Adaptive mouse acceleration. Adapts the acceleration based on the movement speed."),
                        _("Default mouse acceleration (recommended). Let's the mouse decide it's own acceleration."),
                    ]
                )
            )
        )
        self.mouse_group.add(
            RtW.SwitchRow(
                _("Middle Click Paste"),
                _("Whether or not to paste when you middle click."),
                "org.gnome.desktop.interface", "gtk-enable-primary-paste",
            )
        )

        # Mouse Group
        self.touchpad_group = Adw.PreferencesGroup()
        self.touchpad_group.set_title(_("Touchpad"))
        self.keyboard_mouse_page.add(self.touchpad_group)
        self.touchpad_group.add(
            RtW.DetailedDropdownRow.new_from_items(
                _("Mouse Click Emulation"),
                "org.gnome.desktop.peripherals.touchpad", "click-method",
                RtW.DropdownItems(
                    [_("Fingers"), _("Areas"), _("Disabled")],
                    ["fingers", "areas", "none"],
                    [
                        _("Click the touchpad with two fingers for right-click, and three fingers for middle click."),
                        _("Click the bottom right of the touchpad for right click and the bottom middle for middle click."),
                        _("Don't use mouse click emulation."),
                    ]
                )
            )
        )
        self.touchpad_group.add(
            RtW.SwitchRow(
                _("Disable Touchpad While Typing"),
                _("Prevents you from accidentally moving the touchpad while typing."),
                "org.gnome.desktop.peripherals", "disable-while-typing",
            )
        )


if __name__ == "__main__":
    app = Application()
    app.run(None)
