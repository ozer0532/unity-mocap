import traceback
import PySimpleGUI as sg
import cv2
from utils import epipolar, undistort
from config import save_config, load_config

STRING_SAMPLES_CAPTURED = "%d samples captured"


def main(global_data: dict):
    sg.theme("Material1")

    cam_id_l = global_data["cameras"][0]
    cam_id_r = global_data["cameras"][1]

    controls_column = [
        # TODO: Add camera selector
        [sg.Button("Calibrate Distortion [C]", key="-CALIBRATE-")],
        [sg.Button("Exit", size=(10, 1))],
    ]

    data_column = [
        [sg.Text("Fundemental Matrix (F)", size=(30, 1))],
        [
            sg.Column([[sg.Text("-", key="F00")], [sg.Text("-", key="F10")], [sg.Text("-", key="F20")]]),
            sg.Column([[sg.Text("-", key="F01")], [sg.Text("-", key="F11")], [sg.Text("-", key="F21")]]),
            sg.Column([[sg.Text("-", key="F02")], [sg.Text("-", key="F12")], [sg.Text("-", key="F22")]]),
        ],
        [sg.Text("Left Cam Position:"), sg.Text("-", key="P_l")],
        [sg.Text("Right Cam Position:"), sg.Text("-", key="P_r")],
    ]

    # Define the window layout
    layout = [
        [sg.Text("OpenCV Demo", size=(60, 1), justification="center")],
        [sg.Image(filename="", key="-L_IMAGE-"), sg.Image(filename="", key="-R_IMAGE-")],
        [sg.Column(controls_column), sg.VSeparator(), sg.Column(data_column)],
    ]

    # Create the window and show it without the plot
    window = sg.Window("OpenCV Integration", layout, return_keyboard_events=True)

    # Arrays to store object points and image points from all the images.

    K_l, d_l = load_config(*[f"K_{cam_id_l}", f"d_{cam_id_l}"])
    K_r, d_r = load_config(*[f"K_{cam_id_r}", f"d_{cam_id_r}"])

    F = pts_l = pts_r = P_l = P_r = None

    cap_l = cv2.VideoCapture(cam_id_l)
    cap_r = cv2.VideoCapture(cam_id_r)

    while True:
        event, values = window.read(timeout=20)
        if event in ("Exit", sg.WIN_CLOSED, "Escape:27"):
            break

        ret, frame_l = cap_l.read()
        if not ret:
            print("Can't receive frame (stream end?). TODO: Do something ...")
            continue

        ret, frame_r = cap_r.read()
        if not ret:
            print("Can't receive frame (stream end?). TODO: Do something ...")
            continue

        # Undistort
        frame_l = undistort.undistort(frame_l, K_l, d_l, True)
        frame_r = undistort.undistort(frame_r, K_r, d_r, True)
        # frame_r = image_filter.gamma_correction(frame_r, 0.7)
        # frame_r = image_filter.brightness_contrast(frame_r, 1.1, 10)
        # frame_r = image_filter.saturation(frame_r, 1.3)

        # Get calibrate event
        if event in ("-CALIBRATE-", "c", "C"):
            try:
                pts_l, pts_r = epipolar.find_keypoints_sift(frame_l, frame_r)
                P_l, P_r, M_l, M_r, F = epipolar.calibrate(pts_l, pts_r, K_l, K_r)

                # Update GUI
                for i in range(3):
                    for j in range(3):
                        window[f"F{i}{j}"].update("%.3f" % F[i][j])
                window["P_l"].update(str(P_l))
                window["P_r"].update(str(P_r))

                # Save config for Camera
                save_config(**{
                    "P_l": P_l.tolist(),
                    "P_r": P_r.tolist(),
                    "M_l": M_l.tolist(),
                    "M_r": M_r.tolist(),
                    "F": F.tolist(),
                })
            except Exception as e:
                print(traceback.format_exc())
                sg.Popup("Calibration failed. Reason:\n%s" % e)

        # Try draw epilines
        if pts_l is not None and pts_r is not None:
            epipolar.draw_epilines_two_image(frame_l, frame_r, pts_l, pts_r, F)

        # Render
        imgbytes = cv2.imencode(".png", frame_l)[1].tobytes()
        window["-L_IMAGE-"].update(data=imgbytes)
        imgbytes = cv2.imencode(".png", frame_r)[1].tobytes()
        window["-R_IMAGE-"].update(data=imgbytes)

    cap_l.release()
    cap_r.release()
    window.close()

    cap_l.release()
    cap_r.release()
    window.close()


if __name__ == "__main__":
    main()
