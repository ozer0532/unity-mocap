import cv2
import numpy as np


# Gamma correction
def gamma_correction(image, gamma=0.7):
    lookUpTable = np.empty((1, 256), np.uint8)
    for i in range(256):
        lookUpTable[0, i] = np.clip(pow(i / 255.0, gamma) * 255.0, 0, 255)

    return cv2.LUT(image, lookUpTable)


# Brightness & Contrast
def brightness_contrast(image, alpha=1.1, beta=30):
    image = image.astype("float32")
    image = (image * alpha) + beta
    image = np.clip(image, 0, 255)
    return image.astype("uint8")


# Saturation
def saturation(image, adjustment=1.3):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV).astype("float32")
    (h, s, v) = cv2.split(hsv)
    s = s * adjustment
    s = np.clip(s, 0, 255)
    hsv = cv2.merge([h, s, v])
    return cv2.cvtColor(hsv.astype("uint8"), cv2.COLOR_HSV2BGR)
