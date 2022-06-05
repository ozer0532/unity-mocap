import argparse
import cv2
import signal
import zmq

import numpy as np
# from pprint import pprint

from config import load_config
from utils import mp_pose, serialization, undistort

# Initialize parser
parser = argparse.ArgumentParser()
parser.add_argument("-a", "--cam1", help="First Camera", default=0, type=int)
parser.add_argument("-b", "--cam2", help="Second Camera", default=1, type=int)
args = parser.parse_args()

signal.signal(signal.SIGINT, signal.SIG_DFL)


def main():
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:5555")

    cam_id = args.cam1

    K, d = load_config(*[f"K_{cam_id}", f"d_{cam_id}"])

    cap = cv2.VideoCapture(cam_id)

    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose_detector:
        while True:
            _ = cv2.waitKey(1)

            # Wait for poll
            socket.recv()

            while True:
                ret, frame = cap.read()
                if not ret:
                    print("Can't receive frame (stream end?). TODO: Do something ...")
                    continue

                break

            frame = undistort.undistort(frame, K, d, True)

            # Pose estimation
            frame = mp_pose.preprocess(frame)
            result = mp_pose.process_data(frame, pose_detector)
            frame = mp_pose.postprocess(frame, result)

            keypoints = None
            if result.get('landmarks3D') is not None:
                keypoints = mp_pose.results_to_landmark_array(result, "landmarks3D")

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

            cv2.imshow('Window', frame)
            socket.send(serialization.pack(trig_xyz))

    cap.release()


if __name__ == "__main__":
    main()
