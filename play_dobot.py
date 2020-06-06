import time
from DobotDll import DobotDllType as dType

CON_STR = {
    dType.DobotConnect.DobotConnect_NoError:  "DobotConnect_NoError",
    dType.DobotConnect.DobotConnect_NotFound: "DobotConnect_NotFound",
    dType.DobotConnect.DobotConnect_Occupied: "DobotConnect_Occupied"}
api = dType.load()  # Load Dll
postion = [237.7514, 49.2358, -25.7501, 7.1569]


def init(speed=100, coordinate=4000):
    dType.SetQueuedCmdClear(api)
    dType.SetPTPJointParams(api, 200, 200, 200, 200, 200, 200, 200, 200, isQueued=1)
    # dType.SetPTPJointParams(api, speed, speed, speed, speed, speed, speed, speed, speed, isQueued=1)
    dType.SetPTPCoordinateParams(api, coordinate, coordinate, coordinate, coordinate, isQueued=1)


def press_screen(press_time):
    dType.SetQueuedCmdClear(api)
    init() if press_time > 450 else init(coordinate=9000)
    waiting_time = press_time * 0.001

    for i in range(0, 2):
        offset = 20 if i % 2 == 0 else 0
        last_index = dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, postion[0], postion[1], postion[2]-offset, postion[3])[0]
        dType.SetWAITCmd(api, waiting_time)
        dType.SetQueuedCmdStartExec(api)

    while last_index > dType.GetQueuedCmdCurrentIndex(api)[0]:
        dType.dSleep(0)
    dType.SetQueuedCmdStopExec(api)
    dType.SetQueuedCmdClear(api)


def moveForward(offset=0):
    """
    default offset = 0 means above the phone screen
    when offset = -70, it means moveBackward, (to let the camera get the image)
    """
    dType.SetQueuedCmdClear(api)
    init()
    last_index = dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode,postion[0]+offset,postion[1],postion[2],postion[3])[0]  # 移动
    dType.SetQueuedCmdStartExec(api)

    while last_index > dType.GetQueuedCmdCurrentIndex(api)[0]:
        dType.dSleep(0)
    dType.SetQueuedCmdStopExec(api)
    dType.SetQueuedCmdClear(api)


def play_1_loop(press_time):
    dobot_state = dType.ConnectDobot(api, "", 115200)[0]
    if dobot_state == dType.DobotConnect.DobotConnect_NoError:
        moveForward()
        press_screen(press_time)
        time.sleep(1.7)
        moveForward(offset=-70)
    dType.DisconnectDobot(api)

    time.sleep(4)


if __name__ == '__main__':
    play_1_loop(555)