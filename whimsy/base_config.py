# Written by Nick Welch in the years 2005-2008.  Author disclaims copyright.

from Xlib import X

from whimsy import event, main
from whimsy.actions import ewmh
from whimsy.actions.builtins import *
from whimsy.actions.transformers import *
from whimsy.actions.event_handling import *
from whimsy.filters.bindings import *
from whimsy.filters import *
from whimsy.modifiers import modifier_mask, modifier_core

app = main.main()
dpy = app.dpy
hub = app.hub
wm = app.wm
xec = app.xec
ticker = app.ticker

modcore = modifier_core(dpy)

makemod = lambda raw_modifier: modifier_mask(modcore, raw_modifier)

Any = makemod(X.AnyModifier)

M1 = Mod1 = makemod(X.Mod1Mask)
M2 = Mod2 = makemod(X.Mod2Mask)
M3 = Mod3 = makemod(X.Mod3Mask)
M4 = Mod4 = makemod(X.Mod4Mask)
M5 = Mod5 = makemod(X.Mod5Mask)

S  = Shift   = makemod(X.ShiftMask)
C  = Control = makemod(X.ControlMask)

A = Alt = Mod1

Button1Mask = makemod(X.Button1Mask)
Button2Mask = makemod(X.Button2Mask)
Button3Mask = makemod(X.Button3Mask)
Button4Mask = makemod(X.Button4Mask)
Button5Mask = makemod(X.Button5Mask)
ButtonMask = Button1Mask+Button2Mask+Button3Mask+Button4Mask+Button5Mask

root_geometry = app.wm.root.get_geometry()
W = root_geometry.width
H = root_geometry.height

startup_shutdown_signal_methods = {
    'wm_manage_after': 'startup',
    'wm_shutdown_before': 'shutdown',
}

client_list_tracking_signal_methods = {
    'after_manage_window': 'refresh',
    'after_unmanage_window': 'refresh',
    'wm_shutdown_before': 'shutdown',
}

viewport_tracking_signal_methods = {
    'wm_manage_after': 'startup',
    'after_viewport_move': 'refresh',
}

clicks = click_counter()

def if_doubleclick(signal):
    return clicks.if_multi(2)(signal)

actions = [
    (startup_shutdown_signal_methods,     ewmh.net_supported()),
    (startup_shutdown_signal_methods,     ewmh.net_supporting_wm_check()),
    (startup_shutdown_signal_methods,     ewmh.net_number_of_desktops()),
    (startup_shutdown_signal_methods,     ewmh.net_current_desktop()),
    (startup_shutdown_signal_methods,     ewmh.net_desktop_geometry(W*3, H*3)),
    (viewport_tracking_signal_methods,    ewmh.net_desktop_viewport()),
    (client_list_tracking_signal_methods, ewmh.net_client_list()),

    ('wm_manage_after', discover_existing_windows()),

    ('existing_window_discovered', manage_window(),
     if_should_manage_existing_window),

    ('event', manage_window(),
     if_(X.MapRequest, wintype="unmanaged"), if_should_manage_new_window),

    ('event', client_method('focus'), if_(X.MapRequest, wintype='client')),

    ('event', client_method('focus'),
     if_(X.EnterNotify, wintype='client'), if_state(~ButtonMask)),

    ('event', unmanage_window(), if_(X.DestroyNotify, wintype='client')),

    ('event', unmanage_window(), if_(X.UnmapNotify, wintype='client')),

    ('event', update_client_list_focus(), if_(X.FocusIn, wintype='client')),

    ('event', update_client_property(),
     if_(X.PropertyNotify, wintype='client')),

    ('event', focus_last_focused(), if_(X.DestroyNotify)),

    ('event', install_colormap(), if_(X.ColormapNotify)),

    ('event', configure_request_handler(), if_(X.ConfigureRequest)),

    ('event', clicks, if_(X.ButtonPress)),

    ('client_init_after', client_method('configure', border_width=0)),

    ('client_init_after', client_method('map_normal')),

    ('event_done', event.smart_replay(),
     if_event_type(X.KeyPress, X.KeyRelease, X.ButtonPress, X.ButtonRelease)),
]

for action in actions:
    app.hub.register(action[0], action[1], *action[2:])
