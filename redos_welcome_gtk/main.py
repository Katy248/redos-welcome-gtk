import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Gio", "2.0")
gi.require_version("Adw", "1")

from gi.repository import Adw, Gtk, GLib, Gio, Gdk

APP_ID = "ru.red-soft.redos-welcome-gtk"
APP_NAME = "RED OS welcome"


class PageInfo:
    name: str
    title: str
    widget: Gtk.Widget
    icon: str

    def __init__(self, widget, name, title, icon) -> None:
        self.name = name
        self.title = title
        self.widget = widget
        self.icon = icon


def get_hello_page():
    # page = Adw.ViewStackPage(name="hello_page", title="Hello, World!")
    page = Gtk.Label(label="Hi!")
    return PageInfo(
        widget=page,
        name="hello_page",
        title="Hello, World!",
        icon="media-playback-start-symbolic",
    )


def get_installation_page():
    scroll = Gtk.ScrolledWindow()
    clamp = Adw.Clamp()
    scroll.set_child(clamp)
    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
    clamp.set_child(box)
    list_box = Gtk.ListBox(css_classes=["boxed-list"])
    box.append(list_box)
    for i in range(20):
        list_box.append(
            Adw.ActionRow(title=f"Dummy action row #{i}", subtitle="Subtitle")
        )
    return PageInfo(scroll, "inst", "Installation", icon="gnome-software-symbolic")


COLOR_SCHEME_LIGHT = 0
COLOR_SCHEME_DARK = 1


def switch_ui_style(row, other):
    settings = Gio.Settings(schema_id="org.gnome.desktop.interface")
    settings.set_enum(
        "color-scheme", COLOR_SCHEME_DARK if row.get_active() else COLOR_SCHEME_LIGHT
    )
    # help(Gio.Settings)
    # print(row.get_active())
    # print(other)


COLOR_SCHEME_KEY = "color-scheme"


def on_color_scheme_changed(row):
    print("here")

    def res_fn(settings, key, user_data):
        print(f"Changed key: {key}")
        if key == COLOR_SCHEME_KEY:
            row.set_active(settings.get_enum(COLOR_SCHEME_KEY) == COLOR_SCHEME_DARK)

    return res_fn


def from_key_to_active(key, result) -> int:
    if type(key) is bool:
        print("This was bool")
        result = True
        return True
    result = key == COLOR_SCHEME_DARK
    print(f"Convert to bool from {key} = {result}")
    return result


def from_active_to_key(active: bool, result) -> int:
    result = COLOR_SCHEME_DARK if active else COLOR_SCHEME_LIGHT
    print(f"Convert to int from {active} = {result}")
    return result


def get_color_scheme_switcher() -> Adw.SwitchRow:
    theme_switch = Adw.SwitchRow(
        title="Switch to dark color scheme", subtitle="Change UI style"
    )
    settings = Gio.Settings(schema_id="org.gnome.desktop.interface")
    # settings.connect(f"changed", on_color_scheme_changed(theme_switch))
    theme_switch.set_active(settings.get_enum(COLOR_SCHEME_KEY) == COLOR_SCHEME_DARK)
    # settings.bind_with_mapping(
    #     COLOR_SCHEME_KEY,
    #     theme_switch,
    #     "active",
    #     Gio.SettingsBindFlags.DEFAULT,
    #     from_key_to_active,
    #     from_active_to_key,
    # )
    settings.bind(
        COLOR_SCHEME_KEY, theme_switch, "active", Gio.SettingsBindFlags.DEFAULT
    )
    theme_switch.connect("notify::active", switch_ui_style)
    return theme_switch


def get_setting_page():
    scroll = Gtk.ScrolledWindow()
    clamp = Adw.Clamp()
    scroll.set_child(clamp)
    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
    clamp.set_child(box)
    list_box = Gtk.ListBox(css_classes=["boxed-list"])
    box.append(list_box)
    list_box.append(get_color_scheme_switcher())
    for i in range(20):
        list_box.append(
            Adw.SwitchRow(title=f"Dummy action row #{i}", subtitle="Subtitle")
        )
    return PageInfo(
        scroll, "settings", "Quick settings", icon="org.gnome.Settings-symbolic"
    )


def get_resources_page():
    page = Gtk.Label(label="Resources page")
    return PageInfo(page, "res", "Docs and help", icon="help-about-symbolic")


def get_pages() -> list[PageInfo]:
    return [
        get_hello_page(),
        get_installation_page(),
        get_setting_page(),
        get_resources_page(),
    ]


class WelcomeApplication(Adw.Application):
    def __init__(self) -> None:
        super().__init__()
        self.application_id = APP_ID
        GLib.set_application_name(APP_NAME)
        self.connect("activate", self.on_activate)

        css_provider = Gtk.CssProvider()
        css_provider.load_from_path("./ui/style.css")
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )

    def get_view(self):
        self.view_stack = Adw.ViewStack()
        for page in get_pages():
            self.view_stack.add_titled_with_icon(
                page.widget, page.name, page.title, page.icon
            )

        self.view = Adw.ToolbarView()
        self.view.set_content(self.view_stack)
        self.view_switcher = Adw.ViewSwitcher(
            stack=self.view_stack, policy=Adw.ViewSwitcherPolicy.WIDE
        )
        self.top_bar = Adw.HeaderBar(title_widget=self.view_switcher)
        self.view.add_top_bar(self.top_bar)
        self.bottom_bar = Adw.ViewSwitcherBar(
            stack=self.view_stack,
        )
        self.view.add_bottom_bar(self.bottom_bar)
        return self.view

    def on_activate(self, app: Adw.Application):
        window = Adw.ApplicationWindow(
            application=app, content=self.get_view(), height_request=500
        )
        breakpoint = Adw.Breakpoint(
            condition=Adw.BreakpointCondition.parse("max-width: 500sp"),
        )
        breakpoint.add_setter(
            self.top_bar, "title-widget", Adw.WindowTitle(title=APP_NAME)
        )  # hide top nav
        breakpoint.add_setter(self.bottom_bar, "reveal", True)  # show bottom nav
        window.add_breakpoint(breakpoint)
        window.present()

    # show_about(window)


def show_about(window):
    about = Gtk.AboutDialog()
    about.set_transient_for(
        window
    )  # Makes the dialog always appear in from of the parent window
    about.set_modal(
        True
    )  # Makes the parent window unresponsive while dialog is showing

    about.set_authors(["Your Name"])
    about.set_copyright("Copyright 2022 Your Full Name")
    about.set_license_type(Gtk.License.GPL_3_0)
    about.set_website("http://example.com")
    about.set_website_label("My Website")
    about.set_version("1.0")
    about.set_logo_icon_name(
        APP_ID
    )  # The icon will need to be added to appropriate location
    # E.g. /usr/share/icons/hicolor/scalable/apps/org.example.example.svg

    about.set_visible(True)


if __name__ == "__main__":
    app = WelcomeApplication()
    app.run(None)
