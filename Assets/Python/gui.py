import PySimpleGUI as sg
from utils.gui import list_ports

from views import intrinsic, extrinsic, pose

MENU_INTRINSIC = "Calibrate Intrinsic Params [I]"
MENU_EXTRINSIC = "Calibrate Extrinsic Params [E]"
MENU_ESTIMATE = "Estimate Pose [P]"

global_data = {}


def layout():
    return [
        [sg.Text("Kepala Kepeletek Simulator: The Calibration Tool")],
        [sg.Button(MENU_INTRINSIC)],
        [sg.Button(MENU_EXTRINSIC)],
        # [sg.Button(MENU_ESTIMATE)],
        [sg.Button("Exit")],
    ]


# print(sg.theme_list())
sg.theme("Material1")

# INIT
init_popup = sg.Window("Initializing", [[sg.Text(key="-TEXT-", size=(20, 2))]], no_titlebar=True)

event, value = init_popup.read(timeout=0)
init_popup["-TEXT-"].update("Detecting available ports")
event, value = init_popup.read(timeout=0)
global_data["cameras"] = list_ports()[1]

init_popup.close()


# Create the window
window = sg.Window("Super Mocap Tool", layout(), return_keyboard_events=True)

# Create an event loop
while True:
    event, values = window.read()

    if event in ("Exit", sg.WIN_CLOSED, "Escape:27"):
        break

    if event in (MENU_INTRINSIC, "i", "I"):
        window.close()
        intrinsic.main(global_data)
        window = sg.Window("Super Mocap Tool", layout(), return_keyboard_events=True)

    if event in (MENU_EXTRINSIC, "e", "E"):
        window.close()
        extrinsic.main(global_data)
        window = sg.Window("Super Mocap Tool", layout(), return_keyboard_events=True)

    if event in (MENU_ESTIMATE, "p", "P"):
        window.close()
        pose.main(global_data)
        window = sg.Window("Super Mocap Tool", layout(), return_keyboard_events=True)

window.close()
