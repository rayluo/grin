import PySimpleGUI as sg

from grin import GreenInput, __version__


window_width = 80
window = sg.Window("%s %s" % (GreenInput.__name__, __version__), [
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
    [sg.Text("Debug Info:")],
    [sg.Output(key="DEBUG", size=(window_width, 20))],
    ], return_keyboard_events=True)
grin = GreenInput()

callbacks = {  # event: callback
    "About": lambda event, values: sg.popup(GreenInput.__doc__),
    }

while True:
    event, values = window.read()
    if event == sg.WINDOW_CLOSED:
        break
    print(event, values)

    if event.endswith("::MENU_LOAD"):  # https://github.com/PySimpleGUI/PySimpleGUI/issues/432#issuecomment-766190208
        pass

    # Menu key, falls back to its label
    callbacks.get(event.split("::")[-1], lambda event, values: None)(event, values)

    result = grin.input(values["CODE"])
    window["CODE"].update(result["snippet"])
    window["CANDIDATES"].update("\n".join(
        "{}: {}".format(i+1, c) for i, c in enumerate(result["candidates"])))
    window["OUTPUT"].update(values["OUTPUT"].strip() + result["result"])

window.close()

