"""cost functions for camera optimization
   Lin Sun
   May 16 2019
"""
import math
from utils import utils
from cost_functions import cost_curve

"""
cost functions can be divided into:
current quality functions (node cost)
transfer functions (edge cost)
duration function (hops cost)
"""

FRAMEX = 1024
FRAMEY = 768
FRAMESIZE = FRAMEX*FRAMEY
FRAME_DIAGONAL = math.sqrt(FRAMEX ** 2 + FRAMEY ** 2)
QUALITY_WEIGHTS = [0.4, 0.5, 0.2, 0.1, 2, 0.2]
TRANSFER_WEIGHTS = [0.2, 0.2, 0.3, 0.3]

def getVisibilityCost(subVis, objVis):
    """
    :param subVis: subject visibilities
    :param objVis: object visibilities
    :return: visibility proximity cost
    description:
    visibility cost is one of the node cost
    subject: action subject, object: action object
    subVis: onscreen visibility of all subjects for this node
    objVis: onscreen visibility of all objects for this node
    FRAMESIZE: actual frame size after rendering
    1 - (subject visibility + object visibility)/FRAMESIZE is the normalized cost for how much of the current action
    can be seen after rendering for this node
    """
    # TODO: Should it consider object or character actual size?
    cost = 1 - (sum(map(sum, subVis)) + sum(map(sum, objVis))) / FRAMESIZE
    return cost



def getHitchCockCost(actions_list, subVis_list, objVis_list):
    """
    :param actions_list: action list
    :param subVis_list: subject visibility list
    :param objVis_list: object visibility list
    :return: hitchcock cost
    description:
    Hitchcock mentioned "the size of an object in the frame should be equal to its importance in the story at that momentum"
    hitchcock cost is measuring whether the character/item onscreen visibility is proportional to its importance in the action
    For visibility of characters, it is divided into 6 parts: [front head, back head, front upper body, back upper body, front lower body, back lower body]
    For visibility of items, it is divided into 2 parts: [front, back]
    for a single action, the importance between subject and object are different
    for a single action, the importance of body parts are different
    In order to calculate hitchcock cost, first find the action, then get the action SO (subject object importance distribution), then get the body (different body part importance distribution)
    The main purpose is to see whether different part of different characters/items visibility is proportional to its importance
    """
    hcCosts = []
    for i in range(len(actions_list)):
        objVis = objVis_list[i]
        subVis = subVis_list[i]
        action = actions_list[i]
        if not objVis:
            cost = 0
            # subVis can include character vis and object vis
            totalVis = sum(map(sum, subVis))
            if totalVis == 0:
                hcCosts.append(1)
            else:
                # subjects can be characters or items
                for i in range(len(subVis)):
                    if len(subVis[i]) == 6:
                        for j in range(6):
                            cost += abs(
                                (utils.getSOImportance(action)[0] / len(subVis)) * utils.getBodyImportance(action)[j] - subVis[i][j] / totalVis)

                    if len(subVis[i]) == 2:
                        for j in range(2):
                            cost += abs(
                                (utils.getSOImportance(action)[0] / len(subVis)) * utils.getObjectImportance()[j] - subVis[i][j] / totalVis)
                hcCosts.append(cost / len(subVis))

        # if this action has objects
        else:
            cost = 0
            totalVis = sum(map(sum, subVis)) + sum(map(sum, objVis))
            if totalVis == 0:
                hcCosts.append(1)
            else:
                subjectImportance = utils.getSOImportance(action)[0] / len(subVis)
                objectImportance = utils.getSOImportance(action)[1] / len(objVis)
                bodyImportance = utils.getBodyImportance(action)
                itemImportance = utils.getObjectImportance()
                for i in range(len(subVis)):
                    if len(subVis[i]) == 6:
                        # this subject is a character subject
                        for j in range(6):
                            cost += abs(subjectImportance * bodyImportance[j] - subVis[i][j] / totalVis)

                    if len(subVis[i]) == 2:
                        # this subject is a item subject
                        for j in range(2):
                            cost += abs(subjectImportance * bodyImportance[j] - subVis[i][j] / totalVis)


                for i in range(len(objVis)):
                    if len(objVis[i]) == 6:
                        for j in range(6):
                            cost += abs(objectImportance * bodyImportance[j] - objVis[i][j] / totalVis)

                    if len(objVis[i]) == 2:
                        for j in range(2):
                            cost += abs(objectImportance * bodyImportance[j] - objVis[i][j] / totalVis)

                hcCosts.append(cost / (len(subVis) + len(objVis)))
    return sum(hcCosts) / len(hcCosts)


def getLookRoomCost(eyepos, eyeThetas):
    """
    :param eyepos: human on screen eye position
    :param eyeThetas: human on screen eye direction
    :return: lookroom cost
    description:
    look room is the distance from left boundary to character eye's onscreen position and the eye's onscreen position's distance to right boundary
    if the character is looking to right, then the lookroom to right boundary should be larger
    if the character is looking to left, then the lookroom to left boundary should be larger
    curve is the weight function curve, a combination of two sigmoid function.
    But here because the character's eye orientation is not concerned in animation, we assume all eyes are looking perpendicular to viewers
    """
    cost = 0
    # print(eyepos)
    for i, pos in enumerate(eyepos):
        if pos != ["NA", "NA"]:
            # not using eye direction now, character models are not considering eye orientations
            theta = eyeThetas[i]
            [x, y] = eyepos[i]
            leftRoom = x
            rightRoom = FRAMESIZE - x
            cost += cost_curve.lookRoomCostCurve(leftRoom / FRAMEX, 0)
            # TODO: lookroom cost should consider eye thetas, but our model has limited gaze orientation, ignore for now
            # use right-hand coordinate system
            # if theta <= 0:
            #     # face facing left in 2D
            #     cost += lookRoomCostCurve(leftRoom / FRAMEX, theta)
            # else:
            #     # face facing right in 2D
            #     cost += lookRoomCostCurve(rightRoom / FRAMEX, theta)
        else:
            cost += 1
    return cost / len(eyepos)



def getHeadRoomCost(headTop):
    """
    :param headTop: character on screen headroom
    :return: headroom cost
    description:
    characters' heads should not be too close or too far from the top boundary of frame
    """
    cost = 0
    for top in headTop:
        if top != "NA":
            cost += cost_curve.headRoomCostCurve(top)
    # normalize
    return cost / len(headTop)



def getGazeContinuityCost(faceThetas1, faceThetas2, charImportance):
    """
    :param faceThetas1: character on screen face orientation in first node
    :param faceThetas2: character on screen face orientation in second node
    :param charImportance: character importance
    :return: gaze continuity cost
    description:
    NOT USED IN CURRENT VERSION
    character's gaze direction should be consistent between shots
    """
    cost = 0
    for i in range(len(faceThetas1)):
        if faceThetas1[i] and faceThetas2[i]:
            if (faceThetas1 > math.pi / 2 and faceThetas2 > pi / 2) or (faceThetas1 < pi / 2 and faceThetas2 < pi / 2):
                cost += charImportance[i] * 1
    return cost



def getPosContinuityCost(eyepos1, eyepos2):
    """
    :param eyepos1: character eye position in first node
    :param eyepos2: character eye position in second node
    :return: character eye position continuity cost
    description:
    character's eye position should be consistent between shots
    """
    cost = cost_curve.positionChangeCurve(eyepos1, eyepos2)
    return cost


def getMotionContinuityCost(motion1, motion2):
    """
    :param motion1: character on screen moving direction in first node
    :param motion2: character on screen moving direction in second node
    :return: motion continuity cost
    description:
    character's on screen moving direction should be consistent between shots
    """
    if motion1 != motion2:
        return 1
    return 0


def getLeftRightContinuityCost(order1, order2):
    """
    :param order1: characters on screen order in first node
    :param order2: characters on screen order in second node
    :return: characters on screen order continuity
    description:
    character's on screen position should be consistent between shots
    180 theory
    """
    if len(order1) == len(order2) and len(order1) != 0:
        cost = 0
        for i in range(len(order1)):
            cost += (order1[i] != order2[i])
        return cost / len(order1)
    else:
        return 0


def getShotOrderCost(dist):
    """
    :param dist:
    :return: shot order cost
    description:
    expose background information at the beginning of a scene
    cameras with higher shot size should have higher probability to show at the beginning
    """
    return cost_curve.shotOrderCurve(dist)


def getDurationCost(node1, node2, d):
    """
    :param node1: first node
    :param node2: second node
    :param d: duration
    :return: duration cost
    description:
    in patent I mentioned shot intensity should be proportional to user sepecified story intensity. Because the director's hint idea is not
    considered in project for now, we use average duration = 3 seconds
    """
    if node1[1] == node2[1]:
        return cost_curve.durationCurve(0)
    return cost_curve.durationCurve(d)


def getCharacterConflictsCost(node, conflict_int):
    """
    :param node: graph node
    :param conflict_int: user defined character conflict intensity
    :return: conflict cost
    """
    pass


def getCharacterEmotionCost(node, emotion_int):
    """
    :param node: graph mode
    :param emotion_int: user defined emotion intensity
    :return: emotion cost
    """
    pass

def getCameraMovementCost(node, handheld_int):
    """
    :param node: graph node
    :param handheld_int: user defined handheld intensity
    :return: handheld cost
    """
    pass

def getPOVCost(t, cam, protagonist, cameraIndex, characterIndex):
    """
    :param t: node time
    :param cam: node camera
    :param protagonist: story protagonist
    :param cameraIndex: camera description list
    :param characterIndex: character description list
    :return: POV cost
    description:
    In patent POV is one the user input for fixing default cameras. Here due to the imcomplete of user input, of the character is mentioned
    to "look" something, and this character has high importance (calculated protagonist), try to trigger this character's POV camera
    """
    return 1 - utils.isPOV(cam, protagonist, cameraIndex, characterIndex)


def getEscapeFactor(node):
    """
    :param node: camera node
    :return: escape cost
    """
    pass

def getQualityCost(t, cam, qualityHash, startTime, endTime):
    """
    :param t: time
    :param cam: camera
    :param qualityHash: qualish Hash
    :param startTime: user defined animation start time
    :param endTime: user defined animation end time
    :return: node quality cost
    """
    if t == -1 or t == endTime + 1:
        return 0
    return qualityHash[t - startTime][cam]

def getDurationQualityCost(node, duration, qualityHash, startTime, endTime):
    """
    :param node: graph node
    :param duration: duration
    :param qualityHash: qualish Hash
    :param startTime: user defined animation start time
    :param endTime: user defined animation end time
    :return: node accumulated quality cost inside "duration" of time
    """
    cost = 0
    for i in range(duration):
        cost += getQualityCost(node[0] + i, node[1], qualityHash, startTime, endTime)
    return cost

def getInterActionCost(t1, t2, script):
    """
    Not implemented now. If content trim is done before optimization, then this part is needed.
    Because for similar actions in a row, the algorithm will treat these actions evenly and switch shot in any possible positions in this sequence.
    This might due to shot switch inside a complete sentence. Adding a inter action cost in this situation is helpful.
    """
    index1 = utils.getActionIndex(t1, script)
    index2 = utils.getActionIndex(t2, script)
    if index1 != index2:
        # cross action shoot
        if t2 == script.iloc[index2]["startTime"]:
            return 0
        else:
            # print("from time {} to time {} is cross action".format(t1, t2))
            return 1
    return 0

# prepare node cost for graph nodes when no user free cameras are added
def prepareQualityHashWoUserCam(qualityHash, totalTime, startTime, endTime, cameraIndex, characterIndex, protagonist, script, vis, headRoom, eye, distMap, objIndex = None, objVisibility = None):
    """
    description: prepare node cost (no user free cameras considered)
    Node quality costs are calculated before dynamic programming. This ease the process of calculating node cost because they only need to consider
    features related the node itself. Once the node quality costs are calculated, save them in qualith hash for dynamic programming.
    """
    if objIndex:
        for i in range(len(qualityHash)):
            for j in range(len(qualityHash[0])):
                print("prepare quality hash for time {} cam {}".format(i, j))
                qualityHash[i][j] = getWeightedQualityCostWObj([startTime + i, j], totalTime, startTime, endTime,
                                                           cameraIndex, characterIndex, protagonist, script,
                                                           vis, headRoom, eye, distMap, objIndex=objIndex,
                                                           objVisibility=objVisibility)

    else:
        for i in range(len(qualityHash)):
            for j in range(len(qualityHash[0])):
                print("prepare quality hash for time {} cam {}".format(i, j))
                qualityHash[i][j] = getWeightedQualityCostWoObj([startTime + i, j], totalTime, startTime, endTime,
                                                           cameraIndex, characterIndex, protagonist, script,
                                                           vis, headRoom, eye, distMap)


# prepare node cost for graph nodes when there are user free cameras added
def prepareQualityHashWUserCam(qualityHash, totalTime, startTime, endTime, cameraIndex, characterIndex, protagonist, scriptDf, visDf, headRoomDf, eyeDf, distMap, objIndex = None, objVisibility = None, userCamData = None):
    """
    description: prepare node cost (user free cameras considered)
    Node quality costs are calculated before dynamic programming. This ease the process of calculating node cost because they only need to consider
    features related the node itself. Once the node quality costs are calculated, save them in qualith hash for dynamic programming.
    No need to calculate user free cameras because they must cover that user specified time period. But knowing the time when user free cameras
    are added can reduce the workload for generating node cost for default nodes in these time intervals.
    """
    if objIndex:
        for i in range(len(qualityHash)):
            if userCamData:
                if i in userCamData.keys():
                    # skip user added cam times
                    continue
            for j in range(len(qualityHash[0])):
                print("prepare quality hash for time {} cam {}".format(i, j))
                qualityHash[i][j] = getWeightedQualityCostWObj([startTime + i, j], totalTime, startTime, endTime, cameraIndex, characterIndex, protagonist, scriptDf,
                                           visDf, headRoomDf, eyeDf, distMap, objIndex=objIndex, objVisibility=objVisibility)
        print("finish generating default quality cost hash!!!")
    else:
        for i in range(len(qualityHash)):
            if userCamData:
                if i in userCamData.keys():
                # skip user added cam times
                    continue
            for j in range(len(qualityHash[0])):
                print("prepare quality hash for time {} cam {}".format(i, j))
                qualityHash[i][j] = getWeightedQualityCostWoObj([startTime + i, j], totalTime, startTime, endTime, cameraIndex, characterIndex, protagonist, scriptDf,
                                           visDf, headRoomDf, eyeDf, distMap)
        print("finish generating default quality cost hash!!!")


# prepare quality cost with user specified items added
def getWeightedQualityCostWObj(node, totalTime, startTime, endTime, cameraIndex, characterIndex, protagonist, script, charVisibility, headRoomData, eyePosData, distMap, objIndex, objVisibility):
    """
    quality cost == node cost
    This is considering node cost when no user interested items are considered.
    So all subjects, objectes are characters during the calculation
    """
    # dummy start node and dummy end node has 0 quality cost
    if node[0] == -1 or node[0] == endTime + 1:
        return 0


    # action proximity cost
    index = utils.getActionIndex(node[0], script) #action sequence index
    actions_list = utils.getActions(node[0], index, script) #action
    if len(actions_list) > 1:
        print("parallel actions happen at time: {}, actions: {}".format(node[0], actions_list))
    subs_list = utils.getSubjects(node[0], index, script, characterIndex, objIndex)
    # subs = [characters[x] for x in subs]
    objs_list = utils.getObjects(node[0], index, script, characterIndex, objIndex)
    # objs = [characters[x] for x in objs]
    # print("subs: ", subs)
    # print("objs: ", objs)
    assert len(actions_list) == len(subs_list) == len(objs_list), "for script at time {}, number of actions is not compatible with number of subjects and objects".format(node[0])
    visCosts = []
    subVis_list = []
    objVis_list = []
    for i in range(len(actions_list)):
        subVis = []
        objVis = []
        # animation_time = getAnimationStartTime(node[0], index, script)
        for sub in subs_list[i]:
            if sub in objIndex.keys():
                # sub is an object
                sub = objIndex[sub]
                subVis.append(utils.getObjVisibility(sub, node[0], node[1], objVisibility))
            else:
                sub = characterIndex[sub]
                subVis.append(utils.getCharVisibility(sub, node[0], node[1], charVisibility))
        for obj in objs_list[i]:
            if obj in objIndex.keys():
                # sub is an object
                obj = objIndex[obj]
                objVis.append(utils.getObjVisibility(obj, node[0], node[1], objVisibility))
            else:
                obj = characterIndex[obj]
                objVis.append(utils.getCharVisibility(obj, node[0], node[1], charVisibility))

        visCosts.append(getVisibilityCost(subVis, objVis))
        subVis_list.append(subVis)
        objVis_list.append(objVis)
    visCost = sum(visCosts) / len(visCosts)

    # hitchcock cost
    hitchCockCost = getHitchCockCost(actions_list, subVis_list, objVis_list)

    # lookroom cost
    lookRoomCosts = []
    for i in range(len(actions_list)):
        eyePos = []
        for sub in subs_list[i]:
            if sub in characterIndex.keys():
                sub = characterIndex[sub]
                eyePos.append(utils.getDefaultEyePos(sub, node[0], node[1], eyePosData))

        # for obj in objs:
        #     eyePos.append(getEyePos(node[0], node[1], obj, eyeDf))
        # face thetas not ready yet, for lookroom cost assume all have 0 thetas
        eyeThetas = [0] * len(eyePos)
        # for sub in subs:
        #     eyeThetas.append(getFaceThetas(node[0], node[1], sub, faceThetaDf))
        # for obj in objs:
        #     eyeThetas.append(getFaceThetas(node[0], node[1], obj, faceThetasDf))
        lookRoomCosts.append(getLookRoomCost(eyePos, eyeThetas))
    lookRoomCost = sum(lookRoomCosts) / len(lookRoomCosts)

    # headroom cost
    headRoomCosts = []
    for i in range(len(actions_list)):
        headRoom = []
        # only characters have eyes related cost
        for sub in subs_list[i]:
            if sub in characterIndex.keys():
                sub = characterIndex[sub]
                headRoom.append(utils.getHeadRoom(node[0], node[1], sub, headRoomData))
        for obj in objs_list[i]:
            if obj in characterIndex.keys():
                obj = characterIndex[obj]
                headRoom.append(utils.getHeadRoom(node[0], node[1], obj, headRoomData))
        headRoomCosts.append(getHeadRoomCost(headRoom))
    headRoomCost = sum(headRoomCosts) / len(headRoomCosts)
    povCost = 1
    # print("action is {}".format(actions_list))
    # print("protagonist; ", protagonist)
    if "look" in actions_list and (any(characterIndex[protagonist] in sublist for sublist in subs_list)):
        # possibly trigger POV
        print("possible POV trigger!")
        povCost = getPOVCost(node[0], node[1], characterIndex[protagonist], cameraIndex, characterIndex)
    # print("POV COST: ", povCost)


    shotOrderCost = 1
    if node[0] < totalTime * .1:
        # if time is in the first 10%
        dist = cameraIndex[node[1]]["distance"]
        if dist != "NA":
            dist = distMap[dist]
            shotOrderCost = getShotOrderCost(dist)
        else:
            # no POV camera at the beginning of video to avoid confusion
            shotOrderCost = 1


    # weighted node cost summation
    qualityCost = visCost * QUALITY_WEIGHTS[0] + \
                  hitchCockCost * QUALITY_WEIGHTS[1] + \
                  lookRoomCost * QUALITY_WEIGHTS[2] + \
                  headRoomCost * QUALITY_WEIGHTS[3] + \
                  povCost * QUALITY_WEIGHTS[4] + \
                  shotOrderCost * QUALITY_WEIGHTS[5]
    return qualityCost

# prepare quality cost with out user specified items added
def getWeightedQualityCostWoObj(node, totalTime, startTime, endTime, cameraIndex, characterIndex, protagonist, script, charVisibility, headRoomData, eyePosData, distMap):
    """
    quality cost == node cost
    This is considering node cost when there exist user interested items.
    Subjects and objects of actions can be characters or items in this case.
    """
    # dummy start node and dummy end node has 0 quality cost
    if node[0] == -1 or node[0] == endTime + 1:
        return 0

    # action proximity cost
    index = utils.getActionIndex(node[0], script) #action sequence index
    actions_list = utils.getActions(node[0], index, script) #action
    # print("action: ", actions_list)
    subs_list = utils.getSubjects(node[0], index, script, characterIndex, objIndex=None)
    # subs = [characters[x] for x in subs]
    objs_list = utils.getObjects(node[0], index, script, characterIndex, objIndex=None)
    # objs = [characters[x] for x in objs]
    # print("subs: ", subs)
    # print("objs: ", objs)
    subVis_list = []
    objVis_list = []
    visCosts = []
    # animation_time = getAnimationStartTime(node[0], index, script)
    for i in range(len(actions_list)):
        subVis = []
        objVis = []
        for sub in subs_list[i]:
            if sub in characterIndex.keys():
                sub = characterIndex[sub]
                subVis.append(utils.getCharVisibility(sub, node[0], node[1], charVisibility))
        for obj in objs_list[i]:
            if obj in characterIndex.keys():
                obj = characterIndex[obj]
                objVis.append(utils.getCharVisibility(obj, node[0], node[1], charVisibility))

        # print("t: {}, cam: {} sub visibility: {}".format(node[0], node[1], subVis))
        # print("t: {}, cam: {} obj visibility: {}".format(node[0], node[1], objVis))
        subVis_list.append(subVis)
        objVis_list.append(objVis)
        # print(subVis, objVis)
        if subVis:
            visCosts.append(getVisibilityCost(subVis, objVis))
        else:
            visCosts.append(0)
    print(subs_list)
    print(objs_list)
    print(subVis_list)
    print(objVis_list)
    visCost = sum(visCosts) / len(visCosts)
    # hitchcock cost
    hitchCockCost = getHitchCockCost(actions_list, subVis_list, objVis_list)


    # lookroom cost
    lookRoomCosts = []
    for i in range(len(actions_list)):
        eyePos = []
        for sub in subs_list[i]:
            if sub in characterIndex.keys():
                sub = characterIndex[sub]
                eyePos.append(utils.getDefaultEyePos(sub, node[0], node[1], eyePosData))

        # for obj in objs:
        #     eyePos.append(getEyePos(node[0], node[1], obj, eyeDf))
        # face thetas not ready yet, for lookroom cost assume all have 0 thetas
        eyeThetas = [0] * len(eyePos)
        # for sub in subs:
        #     eyeThetas.append(getFaceThetas(node[0], node[1], sub, faceThetaDf))
        # for obj in objs:
        #     eyeThetas.append(getFaceThetas(node[0], node[1], obj, faceThetasDf))
        lookRoomCosts.append(getLookRoomCost(eyePos, eyeThetas))
    lookRoomCost = sum(lookRoomCosts) / len(lookRoomCosts)

    # headroom cost
    headRoomCosts = []

    # only characters have eyes related cost
    for i in range(len(actions_list)):
        headRoom = []
        for sub in subs_list[i]:
            if sub in characterIndex.keys():
                sub = characterIndex[sub]
                headRoom.append(utils.getHeadRoom(node[0], node[1], sub, headRoomData))
        for obj in objs_list[i]:
            if obj in characterIndex.keys():
                obj = characterIndex[obj]
                headRoom.append(utils.getHeadRoom(node[0], node[1], obj, headRoomData))
        if headRoom:
            headRoomCosts.append(getHeadRoomCost(headRoom))
    headRoomCost = sum(headRoomCosts) / len(headRoomCosts)
    povCost = 1
    povCosts = []
    # print("action is {}".format(actions_list))
    # print("protagonist; ", protagonist)
    for i in range(len(actions_list)):
        if actions_list[i] == "look" and any(characterIndex[protagonist] in sublist for sublist in subs_list):
            print("possible POV trigger!")
            povCosts.append(getPOVCost(node[0], node[1], characterIndex[protagonist], cameraIndex, characterIndex))
    if povCosts:
        povCost = sum(povCosts) / len(povCosts)
    shotOrderCost = 1
    if node[0] < totalTime * .1:
        # if time is in the first 10%
        dist = cameraIndex[node[1]]["distance"]
        if dist != "NA":
            dist = distMap[dist]
            shotOrderCost = getShotOrderCost(dist)
        else:
            # no POV camera at the beginning of video to avoid confusion
            shotOrderCost = 1

    # weighted node cost summation
    qualityCost = visCost * QUALITY_WEIGHTS[0] + \
                  hitchCockCost * QUALITY_WEIGHTS[1] + \
                  lookRoomCost * QUALITY_WEIGHTS[2] + \
                  headRoomCost * QUALITY_WEIGHTS[3] + \
                  povCost * QUALITY_WEIGHTS[4] + \
                  shotOrderCost * QUALITY_WEIGHTS[5]
    return qualityCost

# get edge cost when there are user added free cameras
def getWeightedTransferCostWithUserCams(node1, node2, endTime, characters, script, eyePosData, leftRightOrderData, userCamData, objects):
    """
    description:
    transfer cost == edge cost
    This is calculating edge cost between nodes considering user added cameras.
    So the transfer can be categorized into 4 groups: 1. default -> default, 2. default -> user 3. user -> default 4. user -> user
    For user added cameras, since we do not consider their node cost but only edge cost and hop cost, we retrieve their start node and end node data
    and calculate based on these data.
    """
    if node1[0] == -1 or node2[0] == endTime + 1:
        return 0
    # 4 conditions for node1, node2 pairs
    # 1. default -> default 2. default -> user 3. user -> default 4. user -> user
    user1 = (node1[0] in userCamData.keys())
    user2 = (node2[0] in userCamData.keys())
    if user1 and user2:
        # user defined cameras to user defined cameras, no need to consider transfer cost
        return 0

    duration = node2[0] - node1[0]
    index1 = utils.getActionIndex(node1[0], script)
    index2 = utils.getActionIndex(node2[0], script)
    subs1 = utils.getSubjects(node1[0], index1, script, characters, objects)
    subs2 = utils.getSubjects(node2[0], index2, script, characters, objects)
    objs1 = utils.getObjects(node1[0], index1, script, characters, objects)
    objs2 = utils.getObjects(node2[0], index2, script, characters, objects)

    posCost = 0
    posCount = 0

    if user1 and user2:
        # user defined cameras to user defined cameras, no need to consider transfer cost
        return 0

    # eye position change cost
    for sub in (item for sublist in subs1 for item in sublist):
        if any(sub in sublist for sublist in subs2):
            if sub in characters.keys():
                sub = characters[sub]
                if not user1 and user2:
                    eyePos1 = utils.getDefaultEyePos(sub, node1[0] + duration - 1, node1[1], eyePosData)
                    eyePos2 = utils.getUserEyePos(sub, node2[0], userCamData, "start")

                if user1 and not user2:
                    eyePos1 = utils.getUserEyePos(sub, node1[0], userCamData, "end")
                    eyePos2 = utils.getDefaultEyePos(sub, node2[0], node2[1], eyePosData)

                if not user1 and not user2:
                    eyePos1 = utils.getDefaultEyePos(sub, node1[0] + duration - 1, node1[1], eyePosData)
                    eyePos2 = utils.getDefaultEyePos(sub, node2[0], node2[1], eyePosData)

                if eyePos1 != ["NA", "NA"] and eyePos2 != ["NA", "NA"]:
                    eyePos1 = [eyePos1[0] / FRAMEX, eyePos1[1] / FRAMEY]
                    eyePos2 = [eyePos2[0] / FRAMEX, eyePos2[1] / FRAMEY]
                    posCount += 1
                    posCost += getPosContinuityCost(eyePos1, eyePos2)

    for obj in (item for sublist in objs1 for item in sublist):
        if any(obj in sublist for sublist in objs2):
            if obj in characters.keys():
                obj = characters[obj]
                if not user1 and user2:
                    eyePos1 = utils.getDefaultEyePos(obj, node1[0] + duration - 1, node1[1], eyePosData)
                    eyePos2 = utils.getUserEyePos(obj, node2[0], userCamData, "start")

                if user1 and not user2:
                    eyePos1 = utils.getUserEyePos(obj, node1[0], userCamData, "end")
                    eyePos2 = utils.getDefaultEyePos(obj, node2[0], node2[1], eyePosData)

                if not user1 and not user2:
                    eyePos1 = utils.getDefaultEyePos(obj, node1[0] + duration - 1, node1[1], eyePosData)
                    eyePos2 = utils.getDefaultEyePos(obj, node2[0], node2[1], eyePosData)

                if eyePos1 != ["NA", "NA"] and eyePos2 != ["NA", "NA"]:
                    eyePos1 = [eyePos1[0] / FRAMEX, eyePos1[1] / FRAMEY]
                    eyePos2 = [eyePos2[0] / FRAMEX, eyePos2[1] / FRAMEY]
                    posCount += 1
                    posCost += getPosContinuityCost(eyePos1, eyePos2)
    if posCount != 0:
        posCost = posCost / posCount


    # left right order cost
    if user1 and not user2:
        leftRight1 = utils.getUserLeftRightOrder(node1[0], userCamData, "end")
        leftRight2 = utils.getDefaultLeftRightOrder(node2[0], node2[1], leftRightOrderData)
    if not user1 and user2:
        leftRight1 = utils.getDefaultLeftRightOrder(node1[0] + duration - 1, node1[1], leftRightOrderData)
        leftRight2 = utils.getUserLeftRightOrder(node2[0], userCamData, "start")
    if not user1 and not user2:
        leftRight1 = utils.getDefaultLeftRightOrder(node1[0] + duration - 1, node1[1], leftRightOrderData)
        leftRight2 = utils.getDefaultLeftRightOrder(node2[0], node2[1], leftRightOrderData)

    leftRightCost = getLeftRightContinuityCost(leftRight1, leftRight2)


    # weighted edge cost summation
    transferCost = posCost * TRANSFER_WEIGHTS[1] + \
                   leftRightCost * TRANSFER_WEIGHTS[3]

    return transferCost


# get edge cost when there are no user added free cameras
def getWeightedTransferCostWoUserCam(node1, node2, endTime, characterIndex, script, eyePosData, leftRightData, items):
    """
    description:
    transfer cost == edge cost
    This is calculating edge cost between nodes without considering user added cameras. So the transfer are only between default cameras.
    """
    # dummy nodes input output edge has 0 transfer cost
    if node1[0] == -1 or node2[0] == endTime + 1:
        return 0

    index1 = utils.getActionIndex(node1[0], script)
    # action1 = getAction(index1, scriptDf)
    # animationTime1 = getAnimationStartTime(node1[0], index1, scriptDf)
    subs1 = utils.getSubjects(node1[0], index1, script, characterIndex, items)
    objs1 = utils.getObjects(node1[1], index1, script, characterIndex, items)

    index2 = utils.getActionIndex(node2[0], script)
    # action2 = getAction(index2, scriptDf)
    # animationTime2 = getAnimationStartTime(node2[0], index2, scriptDf)
    subs2 = utils.getSubjects(node2[0], index2, script, characterIndex, items)
    # subs2 = [characterIndex[x] for x in subs2]
    objs2 = utils.getObjects(node2[0], index2, script, characterIndex, items)
    # objs2 = [characterIndex[x] for x in objs2]

    posCost = 0
    posCount = 0
    for sub in (item for sublist in subs1 for item in sublist):
        if any(sub in sublist for sublist in subs2):
            if sub in characterIndex.keys():
                sub = characterIndex[sub]
                posCount += 1
                eyePos1 = utils.getDefaultEyePos(sub, node1[0], node1[1], eyePosData)
                eyePos2 = utils.getDefaultEyePos(sub, node2[0], node2[1], eyePosData)
                # print(eyePos1, eyePos2)
                if eyePos1 != ["NA", "NA"] and eyePos2 != ["NA", "NA"]:
                    eyePos1 = [eyePos1[0] / FRAMEX, eyePos1[1] / FRAMEY]
                    eyePos2 = [eyePos2[0] / FRAMEX, eyePos2[1] / FRAMEY]
                    posCost += getPosContinuityCost(eyePos1, eyePos2)

    for obj in (item for sublist in objs1 for item in sublist):
        if any(obj in sublist for sublist in objs2):
            if obj in characterIndex.keys():
                obj = characterIndex[obj]
                posCount += 1
                eyePos1 = utils.getDefaultEyePos(obj, node1[0], node1[1], eyePosData)
                eyePos2 = utils.getDefaultEyePos(obj, node2[0], node2[1], eyePosData)
                if eyePos1 != ["NA", "NA"] and eyePos2 != ["NA", "NA"]:
                    eyePos1 = [eyePos1[0] / FRAMEX, eyePos1[1] / FRAMEY]
                    eyePos2 = [eyePos2[0] / FRAMEX, eyePos2[1] / FRAMEY]
                    posCost += getPosContinuityCost(eyePos1, eyePos2)
    if posCount != 0:
        posCost = posCost / posCount


    # Gaze Continuity, our modules don't have gaze features for now
    # faceTheta1 = getFaceThetas(node1, faceThetasDf)
    # faceTheta2 = getFaceThetas(node2, faceThetasDf)
    # gazeCost = getGazeContinuityCost(faceTheta1, faceTheta2)


    # moving motion continuity, not considered now
    # motion1 = getMotion(node1, motionDf)
    # motion2 = getMotion(node2, motionDf)
    # motionCost = getMotionContinuityCost(motion1, motion2)

    leftRight1 = utils.getDefaultLeftRightOrder(node1[0], node1[1], leftRightData)
    leftRight2 = utils.getDefaultLeftRightOrder(node2[0], node2[1], leftRightData)
    leftRightCost = getLeftRightContinuityCost(leftRight1, leftRight2)

    # weighted edge cost summation
    transferCost = posCost * TRANSFER_WEIGHTS[1] + \
                   leftRightCost * TRANSFER_WEIGHTS[3]
    return transferCost