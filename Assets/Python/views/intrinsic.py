import PySimpleGUI as sg
import cv2
from utils import undistort
from config import save_config

STRING_SAMPLES_CAPTURED = "%d samples captured"


def main(global_data: dict):
    sg.theme("Material1")

    cam_id = global_data["cameras"][0]

    controls_column = [
        [sg.Text("Camera Select:")],
        [
            sg.Listbox(
                global_data["cameras"],
                [cam_id],
                key="-CAMERAS-",
                select_mode=sg.SELECT_MODE_SINGLE,
                size=(20, 3),
                enable_events=True,
            )
        ],
        [sg.Text(STRING_SAMPLES_CAPTURED % 0, size=(30, 1), key="-COUNT-")],
        [sg.Button("Save Sample [S]", key="-SAMPLE-"), sg.Button("Calibrate Distortion [C]", key="-CALIBRATE-")],
        [sg.Button("Exit", size=(10, 1))],
    ]

    data_column = [
        [sg.Text("Camera Intrinsic Matrix (K)", size=(30, 1))],
        [
            sg.Column([[sg.Text("-", key="K00")], [sg.Text("-", key="K10")], [sg.Text("-", key="K20")]]),
            sg.Column([[sg.Text("-", key="K01")], [sg.Text("-", key="K11")], [sg.Text("-", key="K21")]]),
            sg.Column([[sg.Text("-", key="K02")], [sg.Text("-", key="K12")], [sg.Text("-", key="K22")]]),
        ],
        [sg.Text("Distortion Coefficients", size=(60, 1))],
        [sg.Text("k1:"), sg.Text("-", key="d0")],
        [sg.Text("k2:"), sg.Text("-", key="d1")],
        [sg.Text("p1:"), sg.Text("-", key="d2")],
        [sg.Text("p2:"), sg.Text("-", key="d3")],
        [sg.Text("k3:"), sg.Text("-", key="d4")],
        [sg.Button("Save", key="-SAVE-")],
    ]

    # Define the window layout
    layout = [
        [sg.Text("OpenCV Demo", size=(60, 1), justification="center")],
        [sg.Image(filename="", key="-IMAGE-")],
        [sg.Column(controls_column), sg.VSeparator(), sg.Column(data_column)],
    ]

    # Create the window and show it without the plot
    window = sg.Window("OpenCV Integration", layout, return_keyboard_events=True)

    # Arrays to store object points and image points from all the images.
    objpoints = []  # 3d point in real world space
    imgpoints = []  # 2d points in image plane.

    K = d = None

    cap = cv2.VideoCapture(cam_id)

    while True:
        event, values = window.read(timeout=20)
        if event in ("Exit", sg.WIN_CLOSED, "Escape:27"):
            break

        ret, frame = cap.read()

        # if frame is read correctly ret is True
        if not ret:
            print("Can't receive frame (stream end?). TODO: Do something ...")
            break

        # frame = image_filter.brightness_contrast(frame, 3, -200)

        # Try draw checkerboard
        ret, corners = undistort.find_chessboard_corners(frame)

        # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if ret:
            frame = undistort.draw_checkerboard_corners(frame, corners)

            # Get save sample event
            if event in ("-SAMPLE-", "s", "S"):
                objpoints, imgpoints = undistort.save_checkerboard_data(corners, objpoints, imgpoints)
                window["-COUNT-"].update(STRING_SAMPLES_CAPTURED % len(objpoints))

        # Try undistort
        if K is not None and d is not None:
            frame = undistort.undistort(frame, K, d)

        # Get calibrate event
        if event in ("-CALIBRATE-", "c", "C"):
            try:
                K, d = undistort.calibrate(frame, objpoints, imgpoints)

                # Update GUI
                for i in range(3):
                    for j in range(3):
                        window[f"K{i}{j}"].update("%.3f" % K[i][j])
                for i in range(5):
                    window[f"d{i}"].update("%.3f" % d[0][i])

                # Save config for Camera
                save_config(
                    **{
                        f"K_{cam_id}": K.tolist(),
                        f"d_{cam_id}": d.tolist(),
                    }
                )
            except Exception as e:
                sg.Popup("Calibration failed. Reason:\n%s" % e)

        # Render
        imgbytes = cv2.imencode(".png", frame)[1].tobytes()
        window["-IMAGE-"].update(data=imgbytes)

        # Save
        if event == "-SAVE-":
            # TODO: Force .json ext
            file_name = sg.PopupGetFile("Save config", save_as=True)
            if file_name is not None:
                try:
                    save_config(file_name, K=K.tolist(), d=d.tolist())
                except Exception:
                    pass

        # Update camera used
        if event == "-CAMERAS-":
            cap.release()

            cam_id = values["-CAMERAS-"][0]
            cap = cv2.VideoCapture(cam_id)

    cap.release()
    window.close()


if __name__ == "__main__":
    main()
