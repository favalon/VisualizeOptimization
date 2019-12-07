import os
import sys
from utils import utils
from cost_functions import cost_functions


MAX_DURATION = 6


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


def camera_optimization_main(project_data):
    optimizeDuration = project_data.endTime -project_data.startTime + 1
    # 从任意点开始到end的cost
    DefaultCamCostHash = [[None for i in range(project_data.numDefaultCameras)] for j in range(optimizeDuration)]
    DefaultCamNextCamHash = [[[None, None] for i in range(project_data.numDefaultCameras)] for j in range(optimizeDuration)]
    # node cost
    DefaultQualityHash = [[sys.maxsize for i in range(project_data.numDefaultCameras)] for j in range(optimizeDuration)]
    cost_functions.prepareQualityHashWUserCam(DefaultQualityHash, project_data.totalTime, project_data.startTime, project_data.endTime,
                                              project_data.defaultCameras,
                                              project_data.characters, project_data.protagonist, project_data.script, project_data.charVisibility,
                                              project_data.headRoom,
                                              project_data.eyePos, project_data.distMap, project_data.objects, project_data.objVisibility,
                                              userCamData=None)
    print(DefaultQualityHash)

    cost_functions.prepareQualityHashWoUserCam(DefaultQualityHash, project_data.totalTime, project_data.startTime, project_data.endTime,
                                               project_data.defaultCameras,
                                               project_data.characters, project_data.protagonist, project_data.script, project_data.charVisibility,
                                               project_data.headRoom,
                                               project_data.eyePos, project_data.distMap, project_data.objects, project_data.objVisibility)
    print(DefaultQualityHash)
    minCost = helper(project_data, -1, -1, DefaultCamCostHash, DefaultCamNextCamHash, DefaultQualityHash)

    path = []
    startIndex = DefaultCamCostHash[0].index(min(DefaultCamCostHash[0]))
    startNode = [project_data.startTime, startIndex]
    while startNode[0] < project_data.endTime + 1:
        duration = DefaultCamNextCamHash[startNode[0] - project_data.startTime][startNode[1]][0] - startNode[0]
        path.append([startNode[0], startNode[1], duration])
        startNode = DefaultCamNextCamHash[startNode[0] - project_data.startTime][startNode[1]]

    print("camera sequence: ", path)
    return path


if __name__ == "__main__":
    camera_optimization_main(32)
