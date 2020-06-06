import DobotDll.DobotDllType as dType

CON_STR = {
    dType.DobotConnect.DobotConnect_NoError:  "DobotConnect_NoError",
    dType.DobotConnect.DobotConnect_NotFound: "DobotConnect_NotFound",
    dType.DobotConnect.DobotConnect_Occupied: "DobotConnect_Occupied"}

#Load Dll
api = dType.load()
waittime2=0.486
postion=[236.7609, 35.4838, -26.2502, 8.5236]

def init():
    speed1=150
    speed = 500
    coordinate=500
    dType.SetPTPJointParams(api, speed1,speed1,speed1,speed1,speed1,speed1,speed1,speed1, isQueued=1)
    dType.SetPTPCommonParams(api, speed, speed, isQueued=1)
    dType.SetPTPCoordinateParams(api,coordinate,coordinate,coordinate,coordinate,isQueued=1)
    # Async Home
    # dType.SetHOMECmd(api, temp=0, isQueued=1)


def work():
    dType.SetQueuedCmdClear(api)
    init()
    offset=0;offset1=0
    print(waittime2)
    for i in range(0, 10):
        print(i)
        if i % 4 == 0:
            offset = 0;offset1=-50
        elif i % 4 == 1:
            offset = 0;offset1=0
        elif i % 4 == 2:
            offset = 20;offset1=0
        elif i % 4 == 3:
            offset = 0;offset1=0

        lastIndex = dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode,postion[0]+offset1,postion[1],postion[2]-offset,postion[3])[0]  # 移动

        dType.SetWAITCmd(api, waittime2)
        dType.SetQueuedCmdStartExec(api)

    # Wait for Executing Last Command
    while lastIndex > dType.GetQueuedCmdCurrentIndex(api)[0]:
        dType.dSleep(200)

    #Stop to Execute Command Queued
    dType.SetQueuedCmdStopExec(api)
    dType.SetQueuedCmdClear(api)


def main():
    state = dType.ConnectDobot(api, "", 115200)[0]
    print("Connect status:", CON_STR[state])
    if state == dType.DobotConnect.DobotConnect_NoError:
        work()
    dType.DisconnectDobot(api)


if __name__ == '__main__':
    main()