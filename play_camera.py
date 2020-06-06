import cv2
import numpy as np


def get_img(idx):
    img_rgb = cv2.flip(np.transpose(cv2.imread('doc/temp/phone.png', 0)), 0)
    img_rgb, canny_img = getScreen(img_rgb)
    cv2.imwrite('doc/temp/phone_screen.png', img_rgb)

    # cv2.imwrite('doc/temp/last0.png', img_rgb)
    # cv2.imwrite('doc/temp/process_%d_pre0.png' % idx, img_rgb)
    return img_rgb, canny_img


def find4point(points):
    points = points[points[:, 0].argsort()]
    lt, lb = points[0], points[1]
    if points[0][1] > points[1][1]: lt, lb = lb, lt
    rt, rb = points[2], points[3]
    if points[2][1] > points[3][1]: rt, rb = rb, rt
    return ((lt[0], lt[1]), (lb[0], lb[1]), (rt[0], rt[1]), (rb[0], rb[1]))


def getScreen(img_rgb):
    img0 = img_rgb

    img_rgb = cv2.bilateralFilter(img_rgb, 7, 80, 80)
    canny_img = cv2.Canny(img_rgb, 10, 28)
    img_rgb = canny_img
    img_rgb = cv2.GaussianBlur(img_rgb, (9, 13), 0)
    gray = img_rgb
    ret, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY)
    contours0, hierarchy = cv2.findContours(binary, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    size_rectangle_max = 0
    maxi = 0
    for i in range(len(contours0)):
        approximation = cv2.approxPolyDP(contours0[i], 20, True)
        size_rectangle = cv2.contourArea(approximation)
        if size_rectangle> size_rectangle_max:
            size_rectangle_max = size_rectangle
            maxi = i
    cv2.drawContours(canny_img,contours0, maxi, (0, 0, 0), 40)

    pentagram = contours0[maxi]
    cnt = pentagram
    rect = cv2.minAreaRect(cnt)  # 最小外接矩形
    box = np.int0(cv2.boxPoints(rect))  # 矩形的四个角点取整
    # print(box)
    cv2.drawContours(img0, [box], 0, (255, 0, 0), 2)
    lu, ld, ru, rd = find4point(box)
    # print(lu, ru, ld, rd)
    # warp, 原图中卡片的四个角点
    pts1 = np.float32([lu, ru, ld, rd])
    # 变换后分别在左上、右上、左下、右下四个点
    pts2 = np.float32([[0, 0], [1080, 0], [0, 1920], [1080, 1920]])
    # 生成透视变换矩阵
    M = cv2.getPerspectiveTransform(pts1, pts2)
    # 进行透视变换
    dst = cv2.warpPerspective(canny_img, M, (1080, 1920))
    dst0 = cv2.warpPerspective(img0, M, (1080, 1920))
    return dst0, dst
