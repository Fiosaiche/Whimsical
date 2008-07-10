# Written by Nick Welch in the years 2005-2008.  Author disclaims copyright.

from Xlib import X

def replay_or_swallow(dpy, ev, replay):
    if ev.type not in (X.ButtonPress, X.ButtonRelease, X.KeyPress, X.KeyRelease):
        return

    what = ev.__class__.__name__.startswith("Key") and "Keyboard" or "Pointer"
    how = replay and "Replay" or "Async"

    # beware, voodoo!  this is pretty much the only correct way to do this
    # without letting events leak through or other bad stuff
    dpy.allow_events(getattr(X, how+what), ev.time)
    if replay:
        dpy.flush()

class smart_replay(object):
    def __init__(self):
        self.replayed = []
    def __call__(self, signal):
        key = (signal.ev.time, signal.ev.sequence_number)
        if key not in self.replayed:
            replay_or_swallow(signal.wm.dpy, signal.ev, not hasattr(signal.ev, 'swallow'))

            self.replayed.append(key)
            if len(self.replayed) > 100:
                self.replayed.pop(0)

