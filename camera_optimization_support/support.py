import os
import sys
import numpy as np
from cost_functions import cost_functions


def initial_sequence_matrix(project_data, cost_matrix):

    # ===== data ======
    num_sequence = len(project_data.script)
    len_sequence = np.zeros((num_sequence,), dtype=int)
    sequence_cover = np.full((project_data.totalTime,), -1)

    # ===== initialization =======
    for i in range(num_sequence):
        len_sequence[i] = max(project_data.script[i]["duration"])

    p = 0
    for i in range(len_sequence.shape[0]):
        for j in range(len_sequence[i]):
            sequence_cover[p] = i
            p += 1

    cost_matrix.init_sequence_cover(sequence_cover)


def get_character_animation(project_data, sequence_index, character_id, timestamp):

    c_t_animation = np.full((8,), -1)
    action_data = project_data.action_data
    c_t_animation_dict = action_data[sequence_index][character_id]['animations']
    if len(c_t_animation_dict) > 0:
        i = 0
        for key in c_t_animation_dict.keys():
            c_t_animation[i] = int(key)

    return c_t_animation


def initial_action_map(project_data, cost_matrix):

    num_action_parts = 8  # model animation parts, current number is 8

    # ===== data =========
    # character has action on time t or not
    action_map = np.full((project_data.numCharacters, project_data.totalTime, num_action_parts), -1)

    action_weight_map = 0

    # ===== initialization =======
    character_dict = project_data.characters

    for i in range(action_map.shape[1]):
        sequence_index = cost_matrix.sequence_cover[i]

        for j, c in enumerate(project_data.script[sequence_index]["subjects"]):
            character_id = character_dict[c[0]]  # character_id
            char_action_start = project_data.script[sequence_index]["startTime"][j]
            char_action_end = char_action_start + project_data.script[sequence_index]["duration"][j]-1

            if i <= char_action_end:
                action_map[character_id][i] = get_character_animation(project_data, sequence_index, character_id, i)

    cost_matrix.init_action_map(action_map)


def initial_visual_cost_map(project_data, cost_matrix):
    DefaultQualityHash = \
        [[sys.maxsize for i in range(project_data.numDefaultCameras)] for j in range(project_data.totalTime)]

    cost_functions.prepareQualityHashWoUserCam(DefaultQualityHash, project_data.totalTime, project_data.startTime,
                                               project_data.endTime,
                                               project_data.defaultCameras,
                                               project_data.characters, project_data.protagonist, project_data.script,
                                               project_data.charVisibility,
                                               project_data.headRoom,
                                               project_data.eyePos, project_data.distMap, project_data.objects,
                                               project_data.objVisibility)

    cost_matrix.init_visual_cost_map(DefaultQualityHash)


def initial_action_cost_map(project_data, cost_matrix):

    action_cost_map = np.full((project_data.numCharacters, project_data.totalTime), 1, dtype=float)

    action_dict = project_data.animation_dict
    action_score_dict = [x for x in range(len(action_dict))]
    for i, c_t_a in enumerate(cost_matrix.action_map):
        for j, t_a in enumerate(c_t_a):
            score = 0
            for a in t_a:
                if a == -1:
                    score += 0
                else:
                    score += action_score_dict[a]
            if score == 0:
                action_cost_map[i][j] = 1
            else:
                action_cost_map[i][j] = float(1/score)

    cost_matrix.init_action_cost_map(action_cost_map)
    pass


def init_quality_cost(project_data, cost_matrix):
    quality_cost = cost_matrix.visual_cost_map

    for t, t_cam_cost in enumerate(quality_cost):
        for cam, v_cost in enumerate(t_cam_cost):
            char_index = project_data.defaultCameras[cam]['charIndex']
            action_cost = cost_matrix.action_cost_map[char_index][t]
            quality_cost[t][cam] = cost_matrix.visual_cost_weight * v_cost \
                                   + cost_matrix.action_cost_weight * action_cost

    # ======== talking cost  map =================

    talking_char_t = np.full((project_data.totalTime), -1)
    talking_cost_map = np.full((project_data.totalTime, project_data.numDefaultCameras), 1, dtype=float)
    char2camera_id = project_data.char2camera_id

    for t, seq in enumerate(cost_matrix.sequence_cover):
        for char, char_sentence in enumerate(project_data.action_data[seq]):
            for s_id in char_sentence['sentences'].keys():
                if char_sentence['sentences'][s_id]['animation_duration'] != 0:
                    talking_cost = 0
                    talking_char_t[t] = int(char)
                else:
                    talking_cost = 1

            for cam in char2camera_id[char]:
                cam_angle = project_data.defaultCameras[cam]['angle']
                cam_distance = project_data.defaultCameras[cam]['distance']
                if cam_angle == 0:
                    cam_angle_weight = 0
                elif cam_angle == 45 or cam_angle == -45:
                    cam_angle_weight = 0.25
                elif cam_angle == 90 or cam_angle == -90:
                    cam_angle_weight = 0.5
                else:
                    print("angle_wrong")

                if cam_distance == 'MS':
                    cam_distance_cost = 0
                else:
                    cam_distance_cost = 0.2

                talking_cost_map[t][cam] = talking_cost + cam_angle_weight + cam_distance_cost

    cost_matrix.init_talking_cost(talking_cost_map)

    quality_cost = np.array(quality_cost) + cost_matrix.talking_cost_weight * talking_cost_map
    cost_matrix.init_quality_cost(quality_cost.tolist())
    project_data.initial_talking_char_t(talking_char_t)

def initial_cost_map(project_data, cost_matrix):

    # ========== initialization =======================
    initial_visual_cost_map(project_data, cost_matrix)
    initial_action_cost_map(project_data, cost_matrix)



    pass






