import pandas as pd
from camera_optimization.data import load_data
from camera_optimization.data import db_update
from camera_optimization.data import action_preprocess
import operator
import os



def getTotalTime(script):
    """
    :param script: script sequence list
    :return: total animation time
    """
    return min(script[-1]["startTime"]) + max(script[-1]["duration"])

def validateTime(totalTime, startTime, endTime):
    """
    :param totalTime: expected total time
    :param startTime: user defined start time
    :param endTime: user defined end time
    :return: None
    """
    if startTime < 0 or startTime > endTime or startTime >= totalTime:
        print("Invalid start time!")
        exit(-1)
    if endTime < 0 or endTime >= totalTime:
        print("Invalid end time!")

def getNodesByTime(t, max_duration, numCameras, startTime, endTime):
    """
    :param t: animation time
    :param max_duration: animation total duration
    :param numCameras: number of default cameras
    :param startTime: animation start time
    :param endTime: animation end time
    :return: graph node
    """
    nodes = []
    if t == -1:
        # start node can only go to start of first second
        return [[startTime, i, 1] for i in range(numCameras)]
    for i in range(1, max_duration + 1):
        if t + i > endTime + 1:
            break
        if t + i == endTime + 1:
            nodes.append([endTime + 1, numCameras, i])
        if t + i < endTime + 1:
            nodes.extend([[t + i, k, i] for k in range(numCameras)])
    return nodes


def getSOImportance(action):
    """
    :param action: action
    :return: action subject object importance
    """
    return action_preprocess.getActionSOImportance(action)

def getBodyImportance(action):
    """
    :param action: action
    :return: action different body parts importance
    """
    return action_preprocess.getActionBodyImportance(action)

def getObjectImportance():
    """
    :return: items only have one importance distribution for now
    """
    return action_preprocess.getItemImportance()

def getCharacterImportance(char, df):
    pass

def getActionIndex(t, script):
    """
    :param t: time
    :param script: action sequence
    :return: sequence index
    """
    p = 0
    while p < len(script):
        if min(script[p]["startTime"]) < t:
            p += 1
        elif min(script[p]["startTime"]) > t:
            return p-1
        else:
            return p
    return -1


def getActions(t, seqIndex, script):
    """
    :param t: time
    :param seqIndex: sequence index
    :param script: action sequence
    :return: actions under this sequence
    """
    actions = script[seqIndex]['action']
    actions_exist = []
    for i in range(len(actions)):
        # not all actions under the same sequence are happenning at time t
        # some might stop earlier
        if t >= script[seqIndex]["startTime"][i] and t < script[seqIndex]["startTime"][i] + script[seqIndex]["duration"][i]:
            # actions[i] is still happening at time t
            actions_exist.append(actions[i])
    # return actions happening at time t, if action is unknown, put ""
    return actions_exist

def getSubjects(t, seqIndex, script, characterIndex, objIndex):
    """
    :param t: time
    :param seqIndex: sequence index
    :param script: action sequence
    :param characterIndex: character index from character list
    :param objIndex: item index from item list
    :return: subjects lists
    """
    subjects = script[seqIndex]["subjects"]
    subjects_exist = []
    # for each action
    for i in range(len(script[seqIndex]["action"])):
        # if this action is happening at time t
        if t >= script[seqIndex]["startTime"][i] and t < script[seqIndex]["startTime"][i] + script[seqIndex]["duration"][i]:
            if subjects[i]:
                # subject can be character or item
                temp = [x for x in subjects[i] if x in characterIndex.keys()]
                if objIndex:
                    temp.extend([x for x in subjects[i] if x in objIndex.keys()])
                subjects_exist.append(temp)
            else:
                subjects_exist.append("")
    return subjects_exist

def getObjects(t, seqIndex, script, characterIndex, objIndex):
    """
    :param t: time
    :param seqIndex: sequence index
    :param script: action sequence
    :param characterIndex: character index from character list
    :param objIndex: item index from items list
    :return: objects list
    """
    objects = script[seqIndex]["objects"]
    objects_exist = []
    for i in range(len(script[seqIndex]["action"])):
        if t >= script[seqIndex]["startTime"][i] and t < script[seqIndex]["startTime"][i] + script[seqIndex]["duration"][i]:
            # if this action is happening at time t
            if objects[i]:
                # if objects list is not empty
                temp = [x for x in objects[i] if x in characterIndex.keys()]
                if objIndex:
                    # if also consider items as objects
                    temp.extend([x for x in objects[i] if x in objIndex.keys()])
                objects_exist.append(temp)
            else:
                # if this action has no objects
                objects_exist.append("")
    return objects_exist

def getCharVisibility(char, time, cam, charVis):
    """
    :param char: character
    :param time: time
    :param cam: camera index
    :param charVis: character visibility list
    :return: character visibility
    """
    return charVis[time][cam][char]

def getObjVisibility(obj, time, cam, objVis):
    """
    :param obj: item
    :param time: time
    :param cam: camera index
    :param objVis: item visibility list
    :return: item visibility
    """
    return objVis[time][cam][obj]


def getDefaultEyePos(char, t, cam, eyePosData):
    """
    :param char: character
    :param t: time
    :param cam: camera index
    :param eyePosData: eye position data
    :return: character eye position for node [t, cam]
    """
    eyePos = eyePosData[t][cam][char]
    if eyePos == ["NA", "NA"]:
        return eyePos
    else:
        return [int(x) for x in eyePos]


def getUserEyePos(charIndex, t, userCamData, startEnd):
    """
    :param charIndex: character index
    :param t: time
    :param userCamData: user added camera data
    :param startEnd: flag, indicating whether to get the first node from user add camera sequence or last node from user add camera sequence
    :return: user added cameras eye position for node [t, cam]
    """
    if startEnd == "start":
        result = []
        for eyepos in userCamData[t]["start_eyePosition"][charIndex]:
            if eyepos == "NA":
                result.append("NA")
            else:
                result.append(int(eyepos))
        return result
    if startEnd == "end":
        result = []
        for eyepos in userCamData[t]["end_eyePosition"][charIndex]:
            if eyepos == "NA":
                result.append("NA")
            else:
                result.append(int(eyepos))
        return result


def getFaceThetas(t, cam, char, df):
    pass


def getHeadRoom(t, cam, char, headroomData):
    """
    :param t: time
    :param cam: camera index
    :param char: character
    :param headroomData: head room data
    :return: character headroom for node [t, cam]
    """
    headroom = headroomData[t][cam][char]
    if headroom == "NA":
        return headroom
    else:
        return int(headroom)

def getDefaultLeftRightOrder(t, cam, leftRightOrder):
    """
    :param t: time
    :param cam: camera index
    :param leftRightOrder: left right order data
    :return: character on screen left to right order for node [t, cam]
    """
    return leftRightOrder[t][cam]

def getUserLeftRightOrder(t, userCamData, startEnd):
    """
    :param t: time
    :param userCamData: user added camera data
    :param startEnd: flag, indicating whether to get the first node from user add camera sequence or last node from user add camera sequence
    :return: character left to right order for user added node
    """
    if startEnd == "start":
        return userCamData[t]["start_leftToRight"]
    if startEnd == "end":
        return userCamData[t]["end_leftToRight"]


def isPOV(cam, sub, cameraIndex, characterIndex):
    return int(cameraIndex.iloc[0, cam][-1]) == 1 and characterIndex[cameraIndex.iloc[0, cam][0]] == sub

# def getDist(cam, cameraIndex):
#     """
#     :param cam: camera index
#     :param cameraIndex: camera description
#     :return: camera to human distance for default camera cam
#     """
#     return cameraIndex[cam]["dist"]


def getProtagonist(script):
    # find protagonist from script
    # characters appear in subject have weight 1
    # characters appear in object have weight .5
    characters = dict()
    for i, row in enumerate(script):
        subs_list = row["subjects"] # 2D list
        objs_list = row["objects"] # 2D list
        duration = [int(x) for x in row["duration"]] # 1D list
        for idx, subs in enumerate(subs_list):
            for sub in subs:
                if sub != "NA":
                    if sub in characters:
                        characters[sub] += 1 * duration[idx]
                    else:
                        characters[sub] = 1*duration[idx]
                else:
                    continue


        for idx, objs in enumerate(objs_list):
            for obj in objs:
                if obj != "NA":
                    if obj in characters:
                        characters[obj] += .5 * duration[idx]
                    else:
                        characters[obj] = .5*duration[idx]
                else:
                    continue
    print(characters)
    protagonist = max(characters.items(), key=operator.itemgetter(1))[0]
    return protagonist


# def getProtagonist(df):
#     # find protagonist character
#     # subject get 1 credit
#     # object get .5 credit
#     characters = dict()
#     for i, row in df.iterrows():
#         subs = row["Subjects"]
#         subs = subs.split("|")
#         objs = row["Objects"]
#         objs = objs.split("|")
#         duration = int(row["Duration"])
#         for sub in subs:
#             if sub in characters:
#                 characters[sub] += 1 * duration
#             else:
#                 characters[sub] = 0
#         for obj in objs:
#             if obj in characters:
#                 characters[obj] += .5 * duration
#             else:
#                 characters[obj] = 0
#     protagonist = max(characters.items(), key=operator.itemgetter(1))[0]
#     return protagonist

def saveCamSequence(dir, path):
    path = {x[0]: [x[1]] for x in path}
    df = pd.DataFrame.from_dict(path)
    # print(df)
    df.to_csv(dir)
    # with open(dir, "w") as fp:
    #     w = csv.DictWriter(fp, path.keys())
    #     w.writeheader()
    #     w.writerow(path)
    # df = pd.DataFrame()
    # for i in range(len(path)):
    #     df.insert(len(df.columns), column=path[i][0], value=path[i][1])
    # print(df)
    # df.to_csv(dir)
    print("finish save optimized camera sequence!")


# def isMove(index, scriptDf):
#     # index = getIndex(t, scriptDf)
#     action = getActions(index, scriptDf)
#     if action == "move":
#         return True

# def getRelativeAngle(index, cam, moveAngleDf):
#     # print("move angle: ", moveAngleDf.iloc[index, cam])
#     return moveAngleDf.iloc[index, cam].split("|")

def getDist(index, cam, dist):
    """
    :param index: time
    :param cam: camera index
    :param dist: camera characters distance data
    :return: camera character distance for node [index, cam]
    """
    return [float(x) for x in dist[index][cam]]

# def getExist(index, cam, existDf):
#     return [int(x) for x in existDf.iloc[index, cam].split("|")]


def getAnimationStartTime(t, index, scriptDf):
    animation_time = t - int(scriptDf.iloc[index]["NewStartTime"]) + int(scriptDf.iloc[index]["StartTime"])
    # print("animation for new time {} is {}".format(t, animation_time))
    return animation_time

def cam_sequence_to_json(dir):
    cam_seq = pd.read_csv(dir)
    result = []
    for i in range(len(cam_seq.columns)):
        temp_dict = {}
        temp_dict["time"] = cam_seq.columns[i]
        temp_dict["duration"] = cam_seq.iloc[1, i]
        temp_dict["camera"] = cam_seq.iloc[2, i]
        temp_dict["tracking"] = cam_seq.iloc[3, i]
        result.append(temp_dict)
    json_temp = {"camera_index": result}
    # with open("../result/demo_{}_clip.json".format())


# def loadFixedNodes(dir, totalTime, numCameras):
#     # load user defind cameras in step 3
#     df = pd.read_csv(dir)
#     fixedNodes = {}
#     for i, row in fixedNodes.iterrows():
#         key = fixedNodes["actionIndex"]
#         fixedNodes[key] = [row["StartTime"], row["Duration"], row["CameraIndex"]]
#     return fixedNodes

def getValidNextNodesWoUserCam(t, max_duration, numDefaultCams, startTime, endTime):
    if t == -1:
        # dummy start node
        return [[startTime, i, 1] for i in range(numDefaultCams)]

    nodes = []
    for d in range(1, max_duration+1):
        if t + d > endTime + 1:
            break
        elif t + d == endTime + 1:
            # dummy end node
            nodes.append([t+d, numDefaultCams, d])
        else:
            nodes.extend([[t+d, i, d] for i in range(numDefaultCams)])

    return nodes

def getValidNextNodesWUserCam(t, max_duration, fixedNodes, numDefaultCams, startTime, endTime):
    if t == -1:
        # dummy start node can only go to startTime with default cams or user defined cams
        if startTime in fixedNodes.keys():
            # [time, camIndex, duration]
            return [[startTime, fixedNodes[startTime]["camIndex"], 1]]
        else:
            return [[startTime, i, 1] for i in range(numDefaultCams)]

    nodes = []
    for d in range(1, max_duration+1):
        if t + d > endTime + 1:
            break
        elif (t + d) in fixedNodes.keys():
            # if a node can go to start of a user defined time period, it can't go through or jump though this time period
            # it must either go to other time nodes before this start time or stop at this time node
            nodes.append([t+d, fixedNodes[t+d]["camIndex"], d])
            break
        elif t+d == endTime + 1:
            # dummy end node
            # print("dummy end node!")
            nodes.append([t+d, numDefaultCams, d])
        else:
            nodes.extend([[t+d, i, d] for i in range(numDefaultCams)])
    return nodes


def getUserDefinedNextNodes(t, userCamData, num_cameras):
    duration = userCamData[t]["duration"]
    nextNodeTime = t + duration
    if nextNodeTime in userCamData.keys():
        # if this user defined node's next node is also a user defined node
        return [[nextNodeTime, userCamData[nextNodeTime]["camIndex"], duration]]
    else:
        # if this user defined node's next node are default cam nodes
        return [[t+duration, i, duration] for i in range(num_cameras)]



if __name__ == "__main__":
    db, cursor = db_update.db_connect("mysql.minestoryboard.com", "minestory", "2870", "minestory")
    script = load_data.loadScript(8, cursor)
    print(script)
    protagonist = getProtagonist(script)
    print(protagonist)



