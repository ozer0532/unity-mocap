import cv2
from mahotas.features import surf
import numpy as np


def draw_epilines_one_image(img_l, img_r, lines, pts_l, pts_r):
    """img1 - image on which we draw the epilines for the points in img2
    lines - corresponding epilines"""
    r, c = img_l.shape[:2]

    np.random.seed(42)
    for r, pt_l, pt_r in zip(lines, pts_l, pts_r):
        color = tuple(np.random.randint(0, 255, 3).tolist())
        x0, y0 = map(int, [0, -r[2] / r[1]])
        x1, y1 = map(int, [c, -(r[2] + r[0] * c) / r[1]])
        img_l = cv2.line(img_l, (x0, y0), (x1, y1), color, 1)
        img_l = cv2.circle(img_l, tuple(pt_l), 5, color, -1)
        img_r = cv2.circle(img_r, tuple(pt_r), 5, color, -1)
    return img_l, img_r


def draw_epilines_two_image(frame_l, frame_r, pts_l, pts_r, F):
    # Find epilines corresponding to points in right image (second image) and
    # drawing its lines on left image
    lines_l = cv2.computeCorrespondEpilines(pts_r.reshape(-1, 1, 2), 2, F)
    lines_l = lines_l.reshape(-1, 3)
    out_l, _ = draw_epilines_one_image(frame_l, frame_r, lines_l, pts_l, pts_r)
    # Find epilines corresponding to points in left image (first image) and
    # drawing its lines on right image
    lines_r = cv2.computeCorrespondEpilines(pts_l.reshape(-1, 1, 2), 1, F)
    lines_r = lines_r.reshape(-1, 3)
    out_r, _ = draw_epilines_one_image(frame_r, frame_l, lines_r, pts_r, pts_l)

    return out_l, out_r


def find_keypoints_sift(frame_l, frame_r):
    sift = cv2.SIFT_create()

    frame_l = cv2.cvtColor(frame_l, cv2.COLOR_BGR2GRAY)
    frame_r = cv2.cvtColor(frame_r, cv2.COLOR_BGR2GRAY)

    # find the keypoints and descriptors with SIFT
    kp1, des1 = sift.detectAndCompute(frame_l, None)
    kp2, des2 = sift.detectAndCompute(frame_r, None)

    # FLANN parameters
    FLANN_INDEX_KDTREE = 1
    index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
    search_params = dict(checks=50)

    flann = cv2.FlannBasedMatcher(index_params, search_params)
    matches = flann.knnMatch(des1, des2, k=2)

    pts_l = []
    pts_r = []
    # ratio test as per Lowe's paper
    for i, (m, n) in enumerate(matches):
        if m.distance < 0.8 * n.distance:
            pts_r.append(kp2[m.trainIdx].pt)
            pts_l.append(kp1[m.queryIdx].pt)

    pts_l = np.int32(pts_l)
    pts_r = np.int32(pts_r)

    return pts_l, pts_r


def find_keypoints_surf(frame_l, frame_r):
    frame_l = cv2.cvtColor(frame_l, cv2.COLOR_BGR2GRAY)
    frame_r = cv2.cvtColor(frame_r, cv2.COLOR_BGR2GRAY)

    # find the keypoints and descriptors with SIFT
    points1 = surf.surf(frame_l)
    points2 = surf.surf(frame_r)

    kp1, des1 = points1[0:2], points1[6:]
    kp2, des2 = points2[0:2], points2[6:]

    # FLANN parameters
    FLANN_INDEX_KDTREE = 1
    index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
    search_params = dict(checks=50)

    flann = cv2.FlannBasedMatcher(index_params, search_params)
    matches = flann.knnMatch(des1, des2, k=2)

    pts_l = []
    pts_r = []
    # ratio test as per Lowe's paper
    for i, (m, n) in enumerate(matches):
        if m.distance < 0.8 * n.distance:
            pts_r.append(kp2[m.trainIdx].pt)
            pts_l.append(kp1[m.queryIdx].pt)

    pts_l = np.int32(pts_l)
    pts_r = np.int32(pts_r)

    return pts_l, pts_r


def calibrate(pts_l, pts_r, K_l, K_r):
    F, mask = cv2.findFundamentalMat(pts_l, pts_r, cv2.FM_RANSAC)
    E, _ = cv2.findEssentialMat(pts_l, pts_r, K_l, cv2.FM_RANSAC)
    points, R, t, _ = cv2.recoverPose(E, pts_l, pts_r)

    M_r = np.hstack((R, t))
    M_l = np.hstack((np.eye(3, 3), np.zeros((3, 1))))

    P_l = np.dot(K_l, M_l)  # TODO: Assume different matrix
    P_r = np.dot(K_r, M_r)

    # We select only inlier points
    # pts_l = pts_l[mask.ravel() == 1]
    # pts_r = pts_r[mask.ravel() == 1]

    return P_l, P_r, M_l, M_r, F


def transform_points(A: np.ndarray, M: np.ndarray):
    # Convert to homogenous
    B = np.hstack((A, np.ones((A.shape[0], 1))))

    # Transform
    M = np.vstack((M, [0, 0, 0, 1]))
    B = B @ M

    # Convert to cartesian
    B = B.T[:-1] / B.T[-1]

    return B.T
