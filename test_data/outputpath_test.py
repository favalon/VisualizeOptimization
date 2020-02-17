import os
import sys
import json
import shutil






def test_output_path():
    path =  [[0, 9, 3], [3, 8, 4], [7, 28, 4], [11, 49, 3], [14, 48, 3], [17, 9, 2], [19, 8, 3], [22, 28, 3], [25, 8, 3], [28, 48, 3], [31, 49, 2], [33, 48, 3], [36, 28, 2], [38, 48, 2], [40, 68, 4], [44, 69, 3], [47, 8, 3], [50, 69, 2], [52, 8, 2], [54, 29, 3], [57, 69, 3], [60, 68, 2], [62, 29, 4], [66, 68, 3], [69, 28, 3], [72, 29, 3], [75, 28, 3], [78, 29, 3], [81, 28, 3], [84, 29, 3], [87, 28, 3], [90, 29, 3], [93, 8, 3], [96, 9, 3], [99, 69, 2], [101, 68, 3], [104, 7, 2], [106, 48, 3], [109, 49, 3], [112, 48, 3], [115, 49, 3], [118, 48, 3], [121, 49, 3], [124, 48, 3], [127, 27, 2], [129, 9, 2], [131, 49, 5], [136, 9, 1], [137, 28, 3], [140, 29, 3], [143, 27, 4], [147, 8, 2], [149, 9, 3], [152, 69, 3], [155, 8, 2], [157, 49, 2], [159, 28, 2], [161, 69, 3], [164, 49, 4], [168, 8, 4], [172, 49, 4], [176, 49, 3]]



    cur_t = 0
    for t_cam_dura in path:
        start = t_cam_dura[0]
        end = t_cam_dura[-1] + start
        camera_id = t_cam_dura[1]
        for t in range(start,end):
            img_path = "C:/Users/TCLA/Desktop\MineStory1206/TCL_MineTool/UnityProject\MineStudioPrototype/CameraSnapShot/CameraSnapShot/replaced_58/{}/{}_{}.jpg".format(camera_id, camera_id, t)
            if os.path.isfile(img_path):
                dest = shutil.copyfile(img_path, "output_test/{}.jpg".format(t))


if __name__ == "__main__":
    test_output_path()