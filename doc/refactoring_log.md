# Refactoring Log

by cww97

## Files

- `1-AsyncImageRecordingSample`: `C#` project for JAI camera, open with `vs`.
- `DobotDll` is dll we need.
- `doc`: documents
- `imgs`: folder for temp pictures, maybe rename to 'temp' later


## 2018.10.17

Today for python codes we have `AllForOne.py` which is the GUI(pyQT) and `play.py` which is the backend codes(including pictures process and operation on dobot robotic arm).

Separation `play_dobot.py`, for most dobot operations.

Tomorrow maybe codes for pictures, Tired today.

## 2018.10.18

Separate 
- `play_camera.py`: get images from camera and preprocessing
- `play_cv.py`: image processing.

Jarvis, you are dead.

Future work: `main.py`, GUI need update.









