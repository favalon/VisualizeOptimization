# main script
import os
import pickle
from common.data_preparation import data_preparation_main
from common.camera_optimization import camera_optimization_main, camera_pre_optimization
from prepare.structure import CostMatrix

# util imports
from utils.files import ImageLoader
# from common.process_image import process


def save_data(path, fn, data):
    if os.path.isdir(path):
        with open(os.path.join(path, fn), "wb") as f:
            pickle.dump(data, f)
    else:
        print("data save error")


def load_data(path, fn):
    if os.path.isfile(os.path.join(path, fn)):
        with open(os.path.join(path, fn), "rb") as f:
            data = pickle.load(f)
    return data


def main(image_root, num_camera, num_time):
    result_path = "../results"
    # ================ Data Preparation ==============
    # project_data = data_preparation_main(58)

    # save_data(result_path, "project_data", project_data)

    # =============== Camera Optimization ============

    project_data = load_data(result_path, "project_data")
    project_data.initial_minimum_cost_map()
    project_data.initial_animation_score_dict("../prepare/static_datas/animation_score_dict")
    project_data.init_char2camera_id()

    cost_matrix = CostMatrix(project_data.project_id,
                             action_cost_weight=5, visual_cost_weight=1)
    camera_pre_optimization(project_data, cost_matrix)
    camera_optimization_main(project_data, cost_matrix)



    # =================Image Visualization==============

    # loader = ImageLoader(image_root, num_camera, num_time)
    # images_path = loader.get_image_path()

    pass


if __name__ == "__main__":
    image_root = "../test_data/image_root"
    num_camera = 2
    num_time = 1
    main(image_root, num_camera, num_time)
    pass
