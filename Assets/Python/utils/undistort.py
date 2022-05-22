import cv2
import numpy as np

criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

checkerboard_corner_size = (11, 7)

objp = np.zeros((checkerboard_corner_size[1] * checkerboard_corner_size[0], 3), np.float32)
objp[:, :2] = np.mgrid[0:checkerboard_corner_size[0], 0:checkerboard_corner_size[1]].T.reshape(-1, 2)


def save_checkerboard_data(corners, objpoints, imgpoints):
    objpoints.append(objp)
    imgpoints.append(corners)

    return objpoints, imgpoints


def draw_checkerboard_corners(frame, corners):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)

    # Draw and display the corners
    cv2.drawChessboardCorners(frame, (checkerboard_corner_size[0], checkerboard_corner_size[1]), corners2, True)

    return frame


def find_chessboard_corners(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    ret, corners = cv2.findChessboardCorners(
        gray, (checkerboard_corner_size[0], checkerboard_corner_size[1]), None, (cv2.CALIB_CB_ADAPTIVE_THRESH)
    )

    return ret, corners


def undistort(frame, K, d, crop=False) -> np.ndarray:
    h, w = frame.shape[:2]
    newcameramtx, roi = cv2.getOptimalNewCameraMatrix(K, d, (w, h), 1, (w, h))

    out = cv2.undistort(frame, K, d, None, newcameramtx)

    if crop:
        x, y, w, h = roi
        out = out[y:(y + h), x:(x + w)]

    return out


def calibrate(frame, objpoints, imgpoints):
    _, K, d, _, _ = cv2.calibrateCamera(objpoints, imgpoints, frame.shape[:2], None, None)
    return K, d
