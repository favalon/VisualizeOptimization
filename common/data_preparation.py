import os
import json
from database.database import DataBase, DBLoader
from prepare.structure import Project


def load_local_json(path, fn):
    fp = os.path.join(path, fn + ".data")
    if os.path.isfile(fp):
        with open(fp, "r") as f:
            data = json.load(f)
    else:
        print("file path {} is wrong".format(fn))
    return data


def load_local_data(path, project):
    print("load local data")

    file_list = ["color_abs_coverage", "color_code", "color_diff_coverage", "time_data", "animation_dict"]

    color_abs_coverage = load_local_json(path, file_list[0])
    color_code = load_local_json(path, file_list[1])
    color_diff_coverage = load_local_json(path, file_list[2])
    action_data = load_local_json(path, file_list[3])
    animation_dict = load_local_json(path, file_list[4])

    project.load_color_code(color_code)
    project.load_action_data(action_data)
    project.load_animation_dict(animation_dict)
    project.load_color_diff_coverage(color_diff_coverage)
    project.load_color_abs_coverage(color_abs_coverage)


def data_preparation_main(project_id):

    db_address = "mysql.minestoryboard.com"
    database = DataBase(db_address, "minestory", "2870", "minestory")
    database.db_connect()
    dl = DBLoader(database, project_id)
    project_data = Project(dl, project_id)

    # TODO: change local data load to mysql
    path = "../../TCL_MineTool/UnityProject/MineStudioPrototype/Assets/StreamingAssets/camera_data_58"
    if not os.path.isdir(path):
        print("local path is wrong")
    else:
        load_local_data(path, project_data)
    print(project_data.project_id)

    return project_data


if __name__ == "__main__":
    data_preparation_main(32)
