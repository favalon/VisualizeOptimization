import math
import numpy as np
import matplotlib.pyplot as plt

# simplified cost curve for aligned and perpendicular lookroom
def lookRoomCostCurve(lookroom, theta):
    # thetas will be [-pi, +pi]
    # if theta >= 0 and theta <= math.pi / 4:
    #     # aligned
    #     if lookroom < .5:
    #         cost = reverseSigmoid(lookroom, .2, 20)
    #     else:
    #         cost = sigmoid(lookroom, .8, 20)
    # else:
    #     if lookroom < .7:
    #         cost = reverseSigmoid(lookroom, .3, 20)
    #     else:
    #         cost = sigmoid(lookroom, .9, 40)

    if lookroom < .5:
        cost = reverseSigmoid(lookroom, .2, 20)
    else:
        cost = sigmoid(lookroom, .8, 20)

    return cost


def headRoomCostCurve(headroom):
    if headroom < .3:
        return reverseSigmoid(headroom, .1, 40)
    else:
        return sigmoid(headroom, .7, 20)


def durationCurve(duration):
    return round(convex(duration, 3, 9), 2)

def positionChangeCurve(pos1, pos2):
    if pos1 == pos2:
        return 0
    l = math.sqrt((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2) / math.sqrt(2)
    return reverseSigmoid(l, .5, 20)

def shotOrderCurve(dist):
    return reverseSigmoid(dist, 1, 10)



def sigmoid(x, xoffset, scale):
    return 1 / (1 + math.exp(-(x - xoffset) * scale))


def reverseSigmoid(x, xoffset, scale):
    return 1 / (1 + math.exp((x - xoffset) * scale))


def convex(x, xoffset, yscale):
    return (x-xoffset) ** 2 / yscale






if __name__ == "__main__":
    x1 = np.arange(0, 1, .005)
    x2 = np.arange(0, 1, .005)
    x3 = np.arange(0, 1, .005)
    sig1 = [lookRoomCostCurve(x, 0) for x in x1]
    sig2 = [lookRoomCostCurve(x, math.pi / 2) for x in x2]
    sig3 = [headRoomCostCurve(x) for x in x3]
    sig4 = [reverseSigmoid(x, 1, 10) for x in x1]
    # plt.plot(x1, sig1, "g")
    # plt.plot(x2, sig2, "r")
    # plt.plot(x3, sig3, "b")
    plt.plot(x1, sig1, "b")
    plt.show()