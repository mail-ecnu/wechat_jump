import cv2
from directory import *
import numpy as np


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
            if cnt0 > 20:
                cnt = 0
                maxl = x0_list[-1] - x0_list[0]
                x_center = int((x0_list[-1] + x0_list[0]) / 2)
                y_center = y0_temp
            continue
        if x0_list[-1] - x0_list[0] > maxl:
            cnt = cnt0 = 0
            flag = True
            maxl = x0_list[-1] - x0_list[0]
            x_center = int((x0_list[-1] + x0_list[0]) / 2)
            y_center = y0_temp
        if x0_list[-1] - x0_list[0] <= maxl and maxl > 50:
            cnt0 = 0
            cnt += 1
            if cnt > 3: break
    return img_canny, x_center, y_center


class Eye:
    # pattern of Game Over
    pattern_game_over = cv2.imread(pattern_dir + 'pattern_game_over.jpg', 0)
    # pattern of chess piece(player)
    pattern_player = cv2.imread(pattern_dir + 'pattern_player.jpg', 0)
    width_player, height_player = pattern_player.shape[::-1]
    # pattern of centre dot
    pattern_white_dot = cv2.imread(pattern_dir + 'pattern_white_dot.jpg', 0)
    width_dot, height_dot = pattern_white_dot.shape[::-1]

    def __init__(self):
        self.left_top = None
        self.right_bottom = None

    def game_over(self, img_rgb):
        # when we get 'game over', break it
        res_game_over = cv2.matchTemplate(img_rgb, self.pattern_game_over, cv2.TM_CCOEFF_NORMED)
        return cv2.minMaxLoc(res_game_over)[1] > 0.8

    def find_player(self, img_rgb):
        # find where the player(chess) is
        pos_player = cv2.matchTemplate(img_rgb, self.pattern_player, cv2.TM_CCOEFF_NORMED)
        min_val_player, max_val_player, min_loc_player, max_loc_player = cv2.minMaxLoc(pos_player)
        # did not find the player(chess piece)
        if max_val_player < 0.3: return None
        self.left_top = max_loc_player  # left_top_point of chess piece
        self.right_bottom = (self.left_top[0] + self.width_player, self.left_top[1] + self.height_player)
        cv2.rectangle(img_rgb, self.left_top, self.right_bottom, 255, 2)  # mark the chess piece
        return img_rgb

    def find_dot(self, img_rgb, canny_img):  # destination
        # find the destination
        res_dot = cv2.matchTemplate(img_rgb, self.pattern_white_dot, cv2.TM_CCOEFF_NORMED)
        min_val_dot, max_val_dot, min_loc_dot, max_loc_dot = cv2.minMaxLoc(res_dot)
        if max_val_dot > 0.9:  # find the dot
            x_center, y_center = max_loc_dot[0] + self.width_dot // 2, max_loc_dot[1] + self.height_dot // 2
            return img_rgb, x_center, y_center
        else:  # did not find the dot
            # clear the chess piece
            canny_img[self.left_top[1]:self.right_bottom[1]][self.left_top[0]:self.right_bottom[0]] = 0
            return get_center(canny_img)

    def tag_2_dots(self, img_rgb, x_center, y_center, idx):
        left_top, right_bottom = self.left_top, self.right_bottom
        # tag 2 points
        player_pos = (int((left_top[0] + right_bottom[0]) / 2),
                      int((left_top[1] + right_bottom[1]) / 2) + int(self.height_player / 2))
        img_rgb = cv2.circle(img_rgb, (x_center, y_center), 10, 255, -1)
        img_rgb = cv2.circle(img_rgb, player_pos, 10, 255, -1)

        # write on disk
        cv2.imwrite('doc/temp/last1.png', img_rgb)
        cv2.imwrite('doc/temp/process_%d_pre1.png' % idx, img_rgb)
        return img_rgb, player_pos
