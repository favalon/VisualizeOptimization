# image process
import os
import cv2


DEBUG = False

class Image:

    scale_percent = 10 # percent of original size

    def __init__(self, path, camera_i, time_i, ori_img=True):
        self.ori_path = path
        self.resize_path = None
        self.camera_i = -1
        self.time_i = -1
        self.image_name = "Camera:{camera} Time:{time}".format(camera=camera_i, time=time_i)
        self._img = None
        self.ORIGINAL_FLAG = ori_img

    def _read_image(self):
        if self.ORIGINAL_FLAG and os.path.isfile(self.ori_path):
            self._img = cv2.imread(self.ori_path, cv2.IMREAD_UNCHANGED)
        elif not self.ORIGINAL_FLAG and os.path.isfile(self.resize_path):
            self._img = cv2.imread(self.resize_path, cv2.IMREAD_UNCHANGED)
        else:
            print("image {image_name} path is wrong".format(image_name=self.image_name ))

    def _resize(self):
        width = int(self._img.shape[1] * self.scale_percent / 100)
        height = int(self._img.shape[0] * self.scale_percent / 100)
        dim = (width, height)
        # resize image
        resized = cv2.resize(self._img, dim, interpolation = cv2.INTER_AREA)
        return resized

    def _show_image(self):
        if self._img is not None:
            show_image = self._img
            if self._img.shape[1] > 1000 or self._img[0] > 800:
                show_image = self._resize()
            cv2.imshow(self.image_name, show_image)
            cv2.waitKey(0) % 256
        elif self.ori_path is not None or self.resize_path is not None:
            self._read_image()
            show_image = self._img
            if self._img.shape[1] > 1000 or self._img[0] > 800:
                show_image = self._resize()
            cv2.imshow(self.image_name, show_image)
            cv2.waitKey(0) % 256
        else:
            print("image is not loaded")


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
                image_path = "{root}/{camera}/{time}.{ext}". \
                    format(root=self.path, camera=camera, time=time, ext="jpg")
                if os.path.isfile(image_path):
                    path_list.append(image_path)
                else:
                    print("{path} is empty or not a file".format(path = image_path))

        if DEBUG:
            print("ImageLoader->get_image_path:")
            print(path_list)
        return path_list


class ImageProcessor:

    project_images = []

    def __init__(self, path, camera_i, time_i):
        assert len(path) == camera_i * time_i,"Error: wrong image numbers"

        count = 0
        for camera in range(camera_i):
            camera_images = []
            for time in range(time_i):
                camera_images.append(Image(path[0], camera, time))
                count += 1
            self.project_images.append(camera_images)


if __name__ == "__main__":
    image_root = "../test_data/image_root"
    num_camera = 2
    num_time = 1
    ld = ImageLoader(image_root, num_camera, num_time)
    images_path = ld.get_image_path()
    ip = ImageProcessor(images_path, num_camera, num_time)
    image = ip.project_images[0][0]
    image._show_image()
    pass





while program is running
    if cur_time == pre_time + d_t:
        if buffer is empty:
            pre_time = cur_time
            output the p_last
        else:
            pre_time = cur_time
            pop the first p in the buffer
    else:
        wait until cur_time == pre_time + d_t





























