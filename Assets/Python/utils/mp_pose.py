import traceback
import cv2
import mediapipe as mp
import numpy as np

from utils.dataclass import Point, Point3D

DRAW_LANDMARKS = True

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose
Pose = mp_pose.Pose

COLORS = [
    "#DDDDDD",  # 0
    "#7289DA",  # 1
    "#7289DA",  # 2
    "#7289DA",  # 3
    "#FF4500",  # 4
    "#FF4500",  # 5
    "#FF4500",  # 6
    "#7289DA",  # 7
    "#FF4500",  # 8
    "#7289DA",  # 9
    "#FF4500",  # 10
    "#7289DA",  # 11
    "#FF4500",  # 12
    "#7289DA",  # 13
    "#FF4500",  # 14
    "#7289DA",  # 15
    "#FF4500",  # 16
    "#7289DA",  # 17
    "#FF4500",  # 18
    "#7289DA",  # 19
    "#FF4500",  # 20
    "#7289DA",  # 21
    "#FF4500",  # 22
    "#7289DA",  # 23
    "#FF4500",  # 24
    "#7289DA",  # 25
    "#FF4500",  # 26
    "#7289DA",  # 27
    "#FF4500",  # 28
    "#7289DA",  # 29
    "#FF4500",  # 30
    "#7289DA",  # 31
    "#FF4500",  # 32
]


def preprocess(image: np.ndarray) -> np.ndarray:
    # Flip horizontally, BGR -> RGB
    image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)

    # Mark read only (for performance)
    image.flags.writeable = False

    return image


def process_data(image: np.ndarray, pose_detector: Pose) -> None:
    results = {}

    results['est_results'] = pose_detector.process(image)

    try:
        landmarks = results['est_results'].pose_landmarks.landmark
        results['landmarks'] = [Point(landmark.x, landmark.y) for landmark in landmarks]
        landmarks3D = results['est_results'].pose_world_landmarks.landmark
        results['landmarks3D'] = [Point3D(landmark.x, landmark.y, landmark.z) for landmark in landmarks3D]
    except Exception:
        # traceback.print_exc()
        pass

    return results


def postprocess(image: np.ndarray, processing_results: dict) -> np.ndarray:
    image.flags.writeable = True

    # RGB -> BGR
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    # Draw the pose annotation on the image (optional)
    if DRAW_LANDMARKS:
        mp_drawing.draw_landmarks(
            image,
            processing_results['est_results'].pose_landmarks,
            mp_pose.POSE_CONNECTIONS,
            landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style(),
        )

    return image


def triangulate(P_l, P_r, results_l, results_r):
    if results_l.get('landmarks') is None or results_r.get('landmarks') is None:
        return

    pts_l = results_to_landmark_array(results_l)
    pts_r = results_to_landmark_array(results_r)

    point_4d_hom = cv2.triangulatePoints(P_l, P_r, np.expand_dims(pts_l, axis=1), np.expand_dims(pts_r, axis=1))
    point_4d = point_4d_hom / np.tile(point_4d_hom[-1, :], (4, 1))
    point_3d = point_4d[:3, :].T

    return point_3d


# TODO: Try changing P_l to M_l


def results_to_landmark_array(results, key="landmarks"):
    return np.array([list(landmark) for landmark in results[key]])
