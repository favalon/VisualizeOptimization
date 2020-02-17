import os
import json
from common.data_preparation import data_preparation_main

def init_animation_score_dict(project_data):
    animation_score_dict = {}
    for key in project_data.animation_dict:
        if "talk" in key:
            animation_score_dict[project_data.animation_dict[key]] = 10
        else:
            animation_score_dict[project_data.animation_dict[key]] = 1

    with open("static_datas/animation_score_dict", "w") as f:
        json.dump(animation_score_dict, f)


def main():
    project_data = data_preparation_main(32)
    init_animation_score_dict(project_data)


if __name__ == "__main__":
    main()