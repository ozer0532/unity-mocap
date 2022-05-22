import cv2
import signal
import zmq

import numpy as np
# from pprint import pprint

from config import load_config
from utils import epipolar, mp_pose, serialization, undistort

signal.signal(signal.SIGINT, signal.SIG_DFL)


def main():
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:5555")

    # cam_ids = [0, 1]
    # count = len(cam_ids)
    cam_id_l = 0
    cam_id_r = 1

    # K, d, P, cap = [], [], [], []
    # for i in range(count):
    #     K[i], d[i] = load_config(*[f"K_{cam_ids[i]}", f"d_{cam_ids[i]}"])
    #     P[i] =
    K_l, d_l = load_config(*[f"K_{cam_id_l}", f"d_{cam_id_l}"])
    K_r, d_r = load_config(*[f"K_{cam_id_r}", f"d_{cam_id_r}"])

    M_l, M_r = load_config("M_l", "M_r")

    cap_l = cv2.VideoCapture(cam_id_l)
    cap_r = cv2.VideoCapture(cam_id_r)

    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose_detector_l:
        with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose_detector_r:
            while True:
                _ = cv2.waitKey(1)

                # Wait for poll
                socket.recv()

                while True:
                    ret, frame_l = cap_l.read()
                    if not ret:
                        print("Can't receive frame (stream end?). TODO: Do something ...")
                        continue

                    ret, frame_r = cap_r.read()
                    if not ret:
                        print("Can't receive frame (stream end?). TODO: Do something ...")
                        continue

                    break

                frame_l = undistort.undistort(frame_l, K_l, d_l, True)
                frame_r = undistort.undistort(frame_r, K_r, d_r, True)
                # frame_r = image_filter.gamma_correction(frame_r, 0.7)
                # frame_r = image_filter.brightness_contrast(frame_r, 1.1, 10)
                # frame_r = image_filter.saturation(frame_r, 1.3)

                # Pose estimation
                frame_l = mp_pose.preprocess(frame_l)
                result_l = mp_pose.process_data(frame_l, pose_detector_l)
                frame_l = mp_pose.postprocess(frame_l, result_l)

                frame_r = mp_pose.preprocess(frame_r)
                result_r = mp_pose.process_data(frame_r, pose_detector_r)
                frame_r = mp_pose.postprocess(frame_r, result_r)
                # print(result_r)

                # keypoints = mp_pose.triangulate(P_l, P_r, result_l, result_r)
                keypoints_l = keypoints_r = None
                if result_l.get('landmarks') is not None:
                    keypoints_l = mp_pose.results_to_landmark_array(result_l, "landmarks3D")
                if result_r.get('landmarks') is not None:
                    keypoints_r = mp_pose.results_to_landmark_array(result_r, "landmarks3D")

                if keypoints_l is None:
                    if keypoints_r is None:
                        keypoints = None
                    else:
                        keypoints = keypoints_r
                else:
                    if keypoints_r is None:
                        keypoints = keypoints_l
                    else:
                        # TODO: Handle rotations
                        keypoints_l = epipolar.transform_points(keypoints_l, M_l)
                        keypoints_r = epipolar.transform_points(keypoints_r, M_r)
                        keypoints = (keypoints_l + keypoints_r) / 2

                if keypoints is not None:
                    trig_x, trig_y, trig_z = tuple(np.hsplit(keypoints, 3))
                    trig_xyz = [None, None, None]
                    trig_xyz[0] = -trig_x.flatten()
                    trig_xyz[1] = -trig_y.flatten()
                    trig_xyz[2] = trig_z.flatten()
                    trig_xyz = np.array(trig_xyz).T
                else:
                    trig_xyz = keypoints

                # if trig_xyz is not None:
                #     pprint(trig_xyz.tolist())


                cv2.imshow('Window L', frame_l)
                cv2.imshow('Window R', frame_r)
                socket.send(serialization.pack(trig_xyz))

    cap_l.release()
    cap_r.release()


if __name__ == "__main__":
    main()
