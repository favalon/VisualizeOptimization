# main script
import os


# util imports
from utils.files import ImageLoader
from common.process_image import process


def main(image_root, num_camera, num_time):
    loader = ImageLoader(image_root, num_camera, num_time)
    images_path = loader.get_image_path()



if __name__ == "__main__":
    image_root = "../test_data/image_root"
    num_camera = 2
    num_time = 1
    main(image_root, num_camera, num_time)
    pass
