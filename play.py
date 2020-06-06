from PyQt5 import QtCore
import play_dobot as dobot
import play_camera
import play_cv


def get_press_time(distance, rate=1.25):
    # rate may change by different size of screen
    return int(distance * rate)


class WechatJump(QtCore.QObject):
    """wechatJump Logic and Motion Part"""

    runSig = QtCore.pyqtSignal()
    runFlag = True
    Eye = play_cv.Eye()

    def runSigCall(self):
        """receive signal from AllForOne to stop jump"""
        self.runFlag = False

    def main(self, w_length, h_length, sig):
        self.runFlag = True
        self.runSig.connect(self.runSigCall)
        # dobot_state = dobot.dType.ConnectDobot(dobot.api, "", 115200)[0]
        # dobot.dType.SetPTPJointParams(api, 200, 200, 200, 200, 200, 200, 200, 200, isQueued=1)
        # dobot.dType.SetHOMEParams(api, 251, -29, 150, 0, isQueued=1)

        # main loop
        for i in range(10000):
            if not self.runFlag:
                break
            img_rgb, canny_img = play_camera.get_img(i)
            if self.Eye.game_over(img_rgb):
                break
            img_rgb = self.Eye.find_player(img_rgb)
            if img_rgb is None:
                continue
            img_rgb, dot_x, dot_y = self.Eye.find_dot(img_rgb, canny_img)
            img_rgb,  player_pos = self.Eye.tag_2_dots(img_rgb, dot_x, dot_y, i)

            distance = ((player_pos[0] - dot_x) ** 2 + (player_pos[1] - dot_y) ** 2) ** 0.5
            press_time = get_press_time(distance=distance)
            print('distance = %.4f, press_time = %d' % (distance, press_time))

            sig.emit(press_time)
            dobot.play_1_loop(press_time)

        # dobot.dType.DisconnectDobot(dobot.api)
