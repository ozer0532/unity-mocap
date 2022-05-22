import PySimpleGUI as sg
import cv2
import numpy as np
from utils import canvas, image_filter, mp_pose, undistort
from config import load_config

STRING_SAMPLES_CAPTURED = "%d samples captured"


def main(global_data: dict):
    sg.theme("Material1")

    cam_id_l = global_data["cameras"][0]
    cam_id_r = global_data["cameras"][1]

    controls_column = [
        # TODO: Add camera selector
        # [sg.Text(STRING_SAMPLES_CAPTURED % 0, size=(30, 1), key="-COUNT-")],
        # [sg.Button("Save Sample [S]", key="-SAMPLE-"), sg.Button("Calibrate Distortion [C]", key="-CALIBRATE-")],
        [sg.Button("Exit", size=(10, 1))],
    ]

    data_column = [
        # [sg.Text("Fundemental Matrix (F)", size=(30, 1))],
        # [
        #     sg.Column([[sg.Text("-", key="F00")], [sg.Text("-", key="F10")], [sg.Text("-", key="F20")]]),
        #     sg.Column([[sg.Text("-", key="F01")], [sg.Text("-", key="F11")], [sg.Text("-", key="F21")]]),
        #     sg.Column([[sg.Text("-", key="F02")], [sg.Text("-", key="F12")], [sg.Text("-", key="F22")]]),
        # ],
        # [sg.Text("Distortion Coefficients", size=(60, 1))],
        # [sg.Text("Left Cam Position:"), sg.Text("-", key="P_l")],
        # [sg.Text("Right Cam Position:"), sg.Text("-", key="P_r")],
        # [sg.Text("p1:"), sg.Text("-", key="d2")],
        # [sg.Text("p2:"), sg.Text("-", key="d3")],
        # [sg.Text("k3:"), sg.Text("-", key="d4")],
        # [sg.Button("Save", key="-SAVE-")]
        [sg.Canvas(size=(320, 240), key="-CANVAS-")]
    ]

    # Define the window layout
    layout = [
        [sg.Text("OpenCV Demo", size=(60, 1), justification="center")],
        [sg.Image(filename="", key="-L_IMAGE-"), sg.Image(filename="", key="-R_IMAGE-")],
        [sg.Column(controls_column), sg.VSeparator(), sg.Column(data_column)],
    ]

    # Create the window and show it without the plot
    window = sg.Window("OpenCV Integration", layout, return_keyboard_events=True, finalize=True)

    # Arrays to store object points and image points from all the images.

    K_l, d_l = load_config(*[f"K_{cam_id_l}", f"d_{cam_id_l}"])
    K_r, d_r = load_config(*[f"K_{cam_id_r}", f"d_{cam_id_r}"])

    P_l, P_r = load_config("P_l", "P_r")

    cap_l = cv2.VideoCapture(cam_id_l)
    cap_r = cv2.VideoCapture(cam_id_r)

    # canvas.init_matplolib_figure()
    # canvas.draw_3d_points([])
    # canvas.draw_figure(window['-CANVAS-'].TKCanvas)
    plot = canvas.AnimatablePlot(window["-CANVAS-"].TKCanvas)
    plot.init_fig(projection='3d')

    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose_detector_l:
        with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose_detector_r:
            while True:
                event, values = window.read(timeout=20)
                if event in ("Exit", sg.WIN_CLOSED, "Escape:27"):
                    break

                ret, frame_l = cap_l.read()
                if not ret:
                    print("Can't receive frame (stream end?). TODO: Do something ...")
                    break

                ret, frame_r = cap_r.read()
                if not ret:
                    print("Can't receive frame (stream end?). TODO: Do something ...")
                    break

                # Undistort
                frame_l = undistort.undistort(frame_l, K_l, d_l, True)
                frame_r = undistort.undistort(frame_r, K_r, d_r, True)
                frame_r = image_filter.gamma_correction(frame_r, 0.7)
                frame_r = image_filter.brightness_contrast(frame_r, 1.1, 10)
                frame_r = image_filter.saturation(frame_r, 1.3)

                # Pose estimation
                frame_l = mp_pose.preprocess(frame_l)
                result_l = mp_pose.process_data(frame_l, pose_detector_l)
                frame_l = mp_pose.postprocess(frame_l, result_l)

                frame_r = mp_pose.preprocess(frame_r)
                result_r = mp_pose.process_data(frame_r, pose_detector_r)
                frame_r = mp_pose.postprocess(frame_r, result_r)

                trig = mp_pose.triangulate(P_l, P_r, result_l, result_r)

                # Get calibrate event
                # if event in ("-CALIBRATE-", "c", "C"):
                #     try:
                #         pts_l, pts_r, P_l, P_r, F = epipolar.calibrate(frame_l, frame_r, K_l, K_r)

                #         # Update GUI
                #         for i in range(3):
                #             for j in range(3):
                #                 window[f"F{i}{j}"].update("%.3f" % F[i][j])
                #         window["P_l"].update(str(P_l))
                #         window["P_r"].update(str(P_r))

                #         # Save config for Camera
                #         save_config(**{
                #             "P_l": P_l.tolist(),
                #             "P_r": P_r.tolist(),
                #             "F": F.tolist(),
                #         })
                #     except Exception as e:
                #         print(traceback.format_exc())
                #         sg.Popup("Calibration failed. Reason:\n%s" % e)

                # Try draw epilines
                # if pts_l is not None and pts_r is not None:
                #     epipolar.draw_epilines_two_image(frame_l, frame_r, pts_l, pts_r, F)

                # Render Image
                imgbytes = cv2.imencode(".png", frame_l)[1].tobytes()
                window["-L_IMAGE-"].update(data=imgbytes)
                imgbytes = cv2.imencode(".png", frame_r)[1].tobytes()
                window["-R_IMAGE-"].update(data=imgbytes)

                # Render Canvas
                # figure = canvas.init_matplolib_figure()
                # if trig is not None:
                #     canvas.draw_3d_points(trig)
                # canvas.draw_figure(window['-CANVAS-'].TKCanvas, figure)
                # canvas.draw_figure(window['-CANVAS-'].TKCanvas)
                plot.clear()
                if trig is not None:
                    trig_x, trig_y, trig_z = tuple(np.hsplit(trig, 3))
                    trig_xyz = [None, None, None]
                    trig_xyz[0] = trig_x.flatten()
                    trig_xyz[1] = trig_z.flatten()
                    trig_xyz[2] = -trig_y.flatten()
                    plot.scatter(trig_xyz[0], trig_xyz[1], trig_xyz[2], c=mp_pose.COLORS)

                    # for i in range(33):
                    #     plot.text(trig_xyz[0], trig_xyz[1], trig_xyz[2], str(i))
                    plot.plot([trig_xyz[0][0], trig_xyz[0][1]], [trig_xyz[1][0], trig_xyz[1][1]], [trig_xyz[2][0], trig_xyz[2][1]])
                    plot.plot([trig_xyz[0][1], trig_xyz[0][2]], [trig_xyz[1][1], trig_xyz[1][2]], [trig_xyz[2][1], trig_xyz[2][2]])
                    plot.plot([trig_xyz[0][2], trig_xyz[0][3]], [trig_xyz[1][2], trig_xyz[1][3]], [trig_xyz[2][2], trig_xyz[2][3]])
                    plot.plot([trig_xyz[0][3], trig_xyz[0][7]], [trig_xyz[1][3], trig_xyz[1][7]], [trig_xyz[2][3], trig_xyz[2][7]])
                    plot.plot([trig_xyz[0][0], trig_xyz[0][4]], [trig_xyz[1][0], trig_xyz[1][4]], [trig_xyz[2][0], trig_xyz[2][4]])
                    plot.plot([trig_xyz[0][4], trig_xyz[0][5]], [trig_xyz[1][4], trig_xyz[1][5]], [trig_xyz[2][4], trig_xyz[2][5]])
                    plot.plot([trig_xyz[0][5], trig_xyz[0][6]], [trig_xyz[1][5], trig_xyz[1][6]], [trig_xyz[2][5], trig_xyz[2][6]])
                    plot.plot([trig_xyz[0][6], trig_xyz[0][8]], [trig_xyz[1][6], trig_xyz[1][8]], [trig_xyz[2][6], trig_xyz[2][8]])
                    plot.plot([trig_xyz[0][9], trig_xyz[0][10]], [trig_xyz[1][9], trig_xyz[1][10]], [trig_xyz[2][9], trig_xyz[2][10]])
                    plot.plot([trig_xyz[0][11], trig_xyz[0][12]], [trig_xyz[1][11], trig_xyz[1][12]], [trig_xyz[2][11], trig_xyz[2][12]])
                    plot.plot([trig_xyz[0][11], trig_xyz[0][13]], [trig_xyz[1][11], trig_xyz[1][13]], [trig_xyz[2][11], trig_xyz[2][13]])
                    plot.plot([trig_xyz[0][13], trig_xyz[0][15]], [trig_xyz[1][13], trig_xyz[1][15]], [trig_xyz[2][13], trig_xyz[2][15]])
                    plot.plot([trig_xyz[0][15], trig_xyz[0][17]], [trig_xyz[1][15], trig_xyz[1][17]], [trig_xyz[2][15], trig_xyz[2][17]])
                    plot.plot([trig_xyz[0][15], trig_xyz[0][19]], [trig_xyz[1][15], trig_xyz[1][19]], [trig_xyz[2][15], trig_xyz[2][19]])
                    plot.plot([trig_xyz[0][15], trig_xyz[0][21]], [trig_xyz[1][15], trig_xyz[1][21]], [trig_xyz[2][15], trig_xyz[2][21]])
                    plot.plot([trig_xyz[0][17], trig_xyz[0][17]], [trig_xyz[1][17], trig_xyz[1][17]], [trig_xyz[2][17], trig_xyz[2][17]])
                    plot.plot([trig_xyz[0][12], trig_xyz[0][14]], [trig_xyz[1][12], trig_xyz[1][14]], [trig_xyz[2][12], trig_xyz[2][14]])
                    plot.plot([trig_xyz[0][14], trig_xyz[0][16]], [trig_xyz[1][14], trig_xyz[1][16]], [trig_xyz[2][14], trig_xyz[2][16]])
                    plot.plot([trig_xyz[0][16], trig_xyz[0][18]], [trig_xyz[1][16], trig_xyz[1][18]], [trig_xyz[2][16], trig_xyz[2][18]])
                    plot.plot([trig_xyz[0][16], trig_xyz[0][20]], [trig_xyz[1][16], trig_xyz[1][20]], [trig_xyz[2][16], trig_xyz[2][20]])
                    plot.plot([trig_xyz[0][16], trig_xyz[0][22]], [trig_xyz[1][16], trig_xyz[1][22]], [trig_xyz[2][16], trig_xyz[2][22]])
                    plot.plot([trig_xyz[0][18], trig_xyz[0][18]], [trig_xyz[1][18], trig_xyz[1][18]], [trig_xyz[2][18], trig_xyz[2][18]])
                    # 23/24 kebawah belom
                plot.draw()

                # Save
                # if event == "-SAVE-":
                #     # TODO: Force .json ext
                #     file_name = sg.PopupGetFile("Save config", save_as=True)
                #     if file_name is not None:
                #         # TODO: Add functionality
                #         try:
                #             save_config(
                #                 file_name,
                #                 K=K.tolist(),
                #                 d=d.tolist()
                #             )
                #         except Exception:
                #             pass
                #     pass

    cap_l.release()
    cap_r.release()
    window.close()


if __name__ == "__main__":
    main()
