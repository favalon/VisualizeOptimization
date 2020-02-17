import os
import sys
import numpy as np
from utils import utils
from cost_functions import cost_functions
from camera_optimization_support.support import *


MAX_DURATION = 6


def camera_pre_optimization(project_data, cost_matrix):
    script = project_data.script
    characters = project_data.characters
    action_data = project_data.action_data
    animation_dict = project_data.animation_dict

    # ========= initial sequence matrix ==========
    initial_sequence_matrix(project_data, cost_matrix)

    # ========= initial action matrix ============
    initial_action_map(project_data, cost_matrix)
    initial_cost_map(project_data, cost_matrix)

    init_quality_cost(project_data, cost_matrix)


def helper(project_data, t, camIndex, DefaultCamCostHash, DefaultCamNextCamHash, DefaultQualithHash):
    # recursion
    print("calculate time {} cam {}".format(t, camIndex))
    if t == project_data.endTime + 1:
        # dummy end node has 0 node cost
        return 0

    if t == -1:
        print("start Node!")
    else:
        if DefaultCamCostHash[t - project_data.startTime][camIndex]:
            # if this cost has already been calculated
            # return this cost directly
            return DefaultCamCostHash[t - project_data.startTime][camIndex]

    validNextNodes = utils.getValidNextNodesWoUserCam(t, MAX_DURATION, project_data.numDefaultCameras, project_data.startTime,
                                                      project_data.endTime)
    minCost = sys.maxsize

    for nextNode in validNextNodes:
        duration = nextNode[-1]
        nextNodeCost = helper(project_data, nextNode[0], nextNode[1], DefaultCamCostHash, DefaultCamNextCamHash,
                                   DefaultQualithHash)
        qualityCost = cost_functions.getDurationQualityCost([t, camIndex], duration, DefaultQualithHash, project_data.startTime,
                                                            project_data.endTime)
        # hops cost
        durationCost = cost_functions.getDurationCost([t, camIndex], [nextNode[0], nextNode[1]], duration)
        transferCost = cost_functions.getWeightedTransferCostWoUserCam([t, camIndex], [nextNode[0], nextNode[1]],
                                                                       project_data.endTime, project_data.characters, project_data.script,
                                                                       project_data.eyePos, project_data.leftRightOrder, project_data.objects)
        totalCost = nextNodeCost + .5 * transferCost + .5 * durationCost + qualityCost
        if totalCost < minCost:
            minCost = totalCost
            minNextNode = [nextNode[0], nextNode[1]]

    if t != -1:
        DefaultCamCostHash[t - project_data.startTime][camIndex] = minCost
        DefaultCamNextCamHash[t - project_data.startTime][camIndex] = minNextNode
        print("time {} camera {} min cost: {}".format(t, camIndex, minCost))
    return minCost


def camera_optimization_main(project_data, cost_matrix):
    optimizeDuration = project_data.endTime -project_data.startTime + 1
    # 从任意点开始到end的cost
    DefaultCamCostHash = [[None for i in range(project_data.numDefaultCameras)] for j in range(optimizeDuration)]
    DefaultCamNextCamHash = [[[None, None] for i in range(project_data.numDefaultCameras)] for j in range(optimizeDuration)]
    # node cost
    DefaultQualityHash = cost_matrix.quality_cost
    minCost = helper(project_data, -1, -1, DefaultCamCostHash, DefaultCamNextCamHash, DefaultQualityHash)

    path = []
    startIndex = DefaultCamCostHash[0].index(min(DefaultCamCostHash[0]))
    startNode = [project_data.startTime, startIndex]
    while startNode[0] < project_data.endTime + 1:
        duration = DefaultCamNextCamHash[startNode[0] - project_data.startTime][startNode[1]][0] - startNode[0]
        path.append([startNode[0], startNode[1], duration])
        startNode = DefaultCamNextCamHash[startNode[0] - project_data.startTime][startNode[1]]

    # path = [[0, 7, 3], [3, 67, 4], [7, 7, 3], [10, 29, 4], [14, 87, 3], [17, 47, 3], [20, 48, 2], [22, 47, 3], [25, 48, 3], [28, 47, 3], [31, 29, 5], [36, 7, 2], [38, 29, 4], [42, 68, 2], [44, 69, 3], [47, 8, 5], [52, 47, 3], [55, 8, 4], [59, 29, 5], [64, 7, 4], [68, 29, 4], [72, 7, 3], [75, 67, 2], [77, 29, 5], [82, 8, 4], [86, 47, 3], [89, 87, 1], [90, 29, 4], [94, 7, 5], [99, 29, 2], [101, 8, 3], [104, 7, 3], [107, 29, 4], [111, 7, 2], [113, 88, 2], [115, 89, 3], [118, 8, 4], [122, 29, 5], [127, 7, 4], [131, 8, 4], [135, 7, 4], [139, 29, 4], [143, 7, 3]]

    print("camera sequence: ", path)

    t = 0
    for cam in path:
        start = cam[0]
        cam_id = cam[1]
        end = start + cam[2]
        for i in range(start, end):
            cam_setting = project_data.defaultCameras[cam_id]
            cam_index = cam_setting['camIndex']
            cam_char = cam_setting['charIndex']
            talking_char = project_data.talking_char_t[t]
            print("Use Cam: {} shotting Character {} while Character {} is talking"
                  .format(cam_index, cam_char, talking_char))
            t += 1


    return path


if __name__ == "__main__":
    camera_optimization_main(32)
