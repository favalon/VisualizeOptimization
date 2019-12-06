# files relate utils
import os
import re

DEBUG = True


class ImageLoader:
    def __init__(self, path, num_camera, num_time):
        if os.path.isdir(path):
            self.path = path
        else:
            print("wrong root path")
            return

        if isinstance(num_camera, int) and isinstance(num_time, int):
            self.num_camera = num_camera
            self.num_time = num_time
        else:
            self.num_camera = 0
            self.num_time = 0
            print("initial with wrong args, cameras, times set to 0")

    def get_image_path(self):
        path_list = []
        for camera in range(self.num_camera):
            for time in range(self.num_time):
                image_path = "{root}/{camera}/{time}.{ext}".\
                    format(root=self.path, camera=camera, time=time, ext="jpg")
                if os.path.isfile(image_path):
                    path_list.append(image_path)
                else:
                    print("{path} is empty or not a file".format(path = image_path))

        if DEBUG:
            print("ImageLoader->get_image_path:")
            print(path_list)
        return path_list


if __name__ == "__main__":
    loader = ImageLoader("../test_data/image_root", 2, 1)
    p = loader.get_image_path()
    pass

