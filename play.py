import cv2
import numpy as np
import time
from play_dobot import *
from PyQt5 import QtCore


def jump(distance):
    # 这个参数还需要针对屏幕分辨率进行优化
    coffine = 1.2
    press_time = int(distance * coffine)
    print('distance = %.4f, press_time = %d' % (distance, press_time))
    return press_time


def get_center(img_canny):
    # 利用边缘检测的结果寻找物块的上沿和下沿
    # 进而计算物块的中心点
    startY = 520
    linewith1 = np.nonzero([max(row) for row in img_canny[startY:]])
    y_center = x_center = 0
    maxl = cnt = cnt0 = 0
    flag = False
    for i in range(len(linewith1[0])):
        y0_temp = linewith1[0][i] + startY
        x0_list = np.nonzero(img_canny[y0_temp])[0]
        if x0_list[-1] - x0_list[0] < 20: continue
        if flag and x0_list[-1] - x0_list[0] - maxl > 150:
            cnt0 += 1
            if cnt0 > 20 :
                cnt = 0
                maxl = x0_list[-1] - x0_list[0]
                x_center = int((x0_list[-1] + x0_list[0]) / 2)
                y_center = y0_temp
            continue
        if x0_list[-1] - x0_list[0] > maxl:
            cnt = cnt0 = 0
            flag = True
            maxl = x0_list[-1] - x0_list[0]
            x_center = int((x0_list[-1]+x0_list[0])/2)
            y_center = y0_temp
        if x0_list[-1]-x0_list[0] <= maxl and maxl > 50:
            cnt0 = 0
            cnt += 1
            if cnt > 3: break
    return img_canny, x_center, y_center


def find4point(points):
    points = points[points[:, 0].argsort()]
    lt, lb = points[0], points[1]
    if points[0][1] > points[1][1]: lt, lb = lb, lt
    rt, rb = points[2], points[3]
    if points[2][1] > points[3][1]: rt, rb = rb, rt
    return ((lt[0], lt[1]), (lb[0], lb[1]), (rt[0], rt[1]), (rb[0], rb[1]))


def getScreen(img_rgb):
    img0 = img_rgb

    img_rgb = cv2.bilateralFilter(img_rgb,7, 80, 80)
    canny_img = cv2.Canny(img_rgb, 10, 28)
    img_rgb = canny_img
    img_rgb = cv2.GaussianBlur(img_rgb, (9,13), 0)
    gray = img_rgb
    ret, binary = cv2.threshold(gray,0,255,cv2.THRESH_BINARY)
    _, contours0, hierarchy = cv2.findContours(binary, cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
    size_rectangle_max = 0
    maxi = 0
    for i in range(len(contours0)):
        approximation = cv2.approxPolyDP(contours0[i], 20, True)
        size_rectangle = cv2.contourArea(approximation)
        if size_rectangle> size_rectangle_max:
            size_rectangle_max = size_rectangle
            maxi = i
    cv2.drawContours(canny_img,contours0,maxi,(0,0,0),40)

    pentagram = contours0[maxi]
    cnt=pentagram
    rect = cv2.minAreaRect(cnt)  # 最小外接矩形
    box = np.int0(cv2.boxPoints(rect))  # 矩形的四个角点取整
    print(box)
    cv2.drawContours(img0, [box], 0, (255, 0, 0), 2)
    lu, ld, ru, rd = find4point(box)
    print(lu, ru, ld, rd)
    # warp, 原图中卡片的四个角点
    pts1 = np.float32([lu, ru, ld, rd])
    # 变换后分别在左上、右上、左下、右下四个点
    pts2 = np.float32([[0, 0], [1080, 0], [0, 1920], [1080, 1920]])
    # 生成透视变换矩阵
    M = cv2.getPerspectiveTransform(pts1, pts2)
    # 进行透视变换
    dst = cv2.warpPerspective(canny_img, M, (1080, 1920))
    dst0 = cv2.warpPerspective(img0, M, (1080,1920))
    return dst0, dst


class wechatJump(QtCore.QObject):
    """wechatJump Logic and Motion Part"""

    runSig = QtCore.pyqtSignal()
    runFlag = True

    def runSigCall(self):
        """receive signal from AllForOne to stop jump"""
        self.runFlag = False

    def main(self, w_length, h_length,sig):
        self.runFlag = True
        self.runSig.connect(self.runSigCall)
        state = dType.ConnectDobot(api, "", 115200)[0]

        # 匹配小跳棋的模板
        temp1 = cv2.imread('temp_player.jpg', 0)
        w1, h1 = temp1.shape[::-1]
        # 匹配游戏结束画面的模板
        temp_end = cv2.imread('temp_end.jpg', 0)
        # 匹配中心小圆点的模板
        temp_white_circle = cv2.imread('temp_white_circle.jpg', 0)
        w2, h2 = temp_white_circle.shape[::-1]

        # 循环直到游戏失败结束
        for i in range(10000):
            if not self.runFlag: break
            img_rgb = cv2.imread('phone.png', 0)
            img_rgb = np.transpose(img_rgb)
            img_rgb = cv2.flip(img_rgb, 0)
            # 如果在游戏截图中匹配到带"再玩一局"字样的模板，则循环中止
            res_end = cv2.matchTemplate(img_rgb, temp_end, cv2.TM_CCOEFF_NORMED)
            if cv2.minMaxLoc(res_end)[1] > 0.8:
                print('Game over!')
                break

            img_rgb, canny_img = getScreen(img_rgb)
            cv2.imwrite("imgs/"+str(i)+"_pre.png",img_rgb)
            # 模板匹配截图中小跳棋的位置
            res1 = cv2.matchTemplate(img_rgb, temp1, cv2.TM_CCOEFF_NORMED)
            min_val1, max_val1, min_loc1, max_loc1 = cv2.minMaxLoc(res1)
            print(max_val1)
            if (max_val1 < 0.3): continue
            if state == dType.DobotConnect.DobotConnect_NoError: moveForward()

            left_top = max_loc1  # 左上角
            right_bottom = (left_top[0] + w1, left_top[1] + h1)  # 右下角

            center1_loc = (int((left_top[0]+right_bottom[0]) / 2), int((left_top[1]+right_bottom[1]) / 2) + int(h1/2))
            print(center1_loc)
            cv2.rectangle(img_rgb, left_top, right_bottom, 255, 2)

            # 先尝试匹配截图中的中心原点，
            # 如果匹配值没有达到0.95，则使用边缘检测匹配物块上沿

            res2 = cv2.matchTemplate(img_rgb, temp_white_circle, cv2.TM_CCOEFF_NORMED)
            min_val2, max_val2, min_loc2, max_loc2 = cv2.minMaxLoc(res2)
            if max_val2 > 0.91:
                print('found white circle!')
                x_center, y_center = max_loc2[0] + w2 // 2, max_loc2[1] + h2 // 2
            else:
                # 边缘检测, 消去小跳棋轮廓对边缘检测结果的干扰
                for k in range(left_top[1], right_bottom[1]):
                    for b in range(left_top[0], right_bottom[0]):
                        canny_img[k][b] = 0
                img_rgb, x_center, y_center = get_center(canny_img)

            # 将图片输出以供调试
            img_rgb = cv2.circle(img_rgb, (x_center, y_center), 10, 255, -1)
            img_rgb = cv2.circle(img_rgb, center1_loc, 10, 255, -1)
            cv2.imwrite('last.png', img_rgb)
            cv2.imwrite("imgs/"+str(i)+'_last.png',img_rgb)
            print("last write down")

            distance = (center1_loc[0] - x_center) ** 2 + (center1_loc[1] - y_center) ** 2
            distance = distance ** 0.5
            print("distance:", distance)
            press_time = jump(distance)
            sig.emit(press_time)
            if state == dType.DobotConnect.DobotConnect_NoError:
                work(press_time)
                time.sleep(1.7)
                moveForward(offset=-70)
                time1 = 0.2
                time.sleep(time1)
                divide = 500.0
                if press_time / divide < time1: time.sleep(time1)
                else: time.sleep(press_time / divide)

        dType.DisconnectDobot(api)
