import logging  # Use logger rather than print(...).
    # Not only print(...) would require an unconvenient sg.Output() to work,
    # uncaught exception message would have no chance to be shown during crash.
from contextlib import closing

import PySimpleGUI as sg

from grin import GreenInput, __version__


logger = logging.getLogger(__name__)
grin = GreenInput()
callbacks = {  # event: callback
    "About": lambda event, values: sg.popup(GreenInput.__doc__),
    "MENU_LOAD": lambda e, v: grin.load_table(
        sg.popup_get_file("Open a code definition file", file_types=(
            ("Windows 2000 files", ".w2k"),
            )),  # This is higher level than sg.Window(...).read(close=True)[1][0]
        ),
    }
window_width = 80
with closing(sg.Window("%s %s" % (GreenInput.__name__, __version__), [
            [sg.MenuBar([
                ["&File", ["&Load::MENU_LOAD"]],
                ["&Help", ["&About"]],
                ])],
            [sg.Text("Input your code here")],
            [sg.Input(key="CODE", size=(20, 1))],
            [sg.Multiline(key="CANDIDATES", size=(40, 10))],
            [sg.Text("_" * window_width)],
            [sg.Text("Result (Select all, and press CTRL+C to copy, then CTRL+V to elsewhere):")],
            [sg.Multiline(key="OUTPUT", size=(window_width, 20))],
        ],
        #icon="grin.ico",  # Neither ico or xbm format seems to work on Linux
        return_keyboard_events=True,
        location=(0, 0),  # Otherwise it locates between multiple monitor on Linux
        )) as window:  # If not close() properly, other app would need re-focus.
    while True:
        event, values = window.read()
        logger.debug("event=%s, values=%s", event, values)
        if event == sg.WINDOW_CLOSED:
            break

        callbacks.get(
            event.split("::")[-1],  # Menu key, falls back to its label
            lambda event, values: None,
            )(event, values)
        # TODO: After choosing new code table BY KEYBOARD, main window loses focus
        #window["CODE"].SetFocus()  # This does not help either

        result = grin.input(values["CODE"])
        window["CODE"].update(result["snippet"])
        window["CANDIDATES"].update("\n".join(
            "{}: {}".format(i+1, c) for i, c in enumerate(result["candidates"])))
        window["OUTPUT"].update(values["OUTPUT"].strip() + result["result"])

